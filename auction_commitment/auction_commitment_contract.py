from email.policy import default
from typing import Final
from beaker import *
from pyteal import *
#import os
#import json

MIN_FEE = Int(1000)                                     # minimum fee on Algorand is currently 1000 microAlgos

class Auction(Application):

    ##############
    # Application State
    ##############

    # Declare Application state, marking `Final` here so the python class var doesn't get changed
    # Marking a var `Final` does _not_ change anything at the AVM level

    # Global Bytes (2)
    owner: Final[ApplicationStateValue] = ApplicationStateValue(
        stack_type = TealType.bytes,
        key = Bytes("o"),
        default = Global.creator_address(),
        descr = "The current owner of this contract, allowed to do admin type actions"
    )

    highest_bidder: Final[ApplicationStateValue] = ApplicationStateValue(
        stack_type = TealType.bytes,
        default = Global.zero_address(),
    )

    # Global Ints (4)
    highest_bid: Final[ApplicationStateValue] = ApplicationStateValue(
        stack_type = TealType.uint64,
        default = Int(0)
    )

    nft_id: Final[ApplicationStateValue] = ApplicationStateValue(
        stack_type = TealType.uint64,
        default = Int(0)
    )

    auction_start: Final[ApplicationStateValue] = ApplicationStateValue(
        stack_type = TealType.uint64,
        default = Int(0)
    )

    auction_end: Final[ApplicationStateValue] = ApplicationStateValue(
        stack_type = TealType.uint64,
        default = Int(0)
    )

    commit_end: Final[ApplicationStateValue] = ApplicationStateValue(
        stack_type = TealType.uint64,
        default = Int(0)
    )

    deposit: Final[ApplicationStateValue] = ApplicationStateValue(
        stack_type = TealType.uint64,
        default = Int(0)
    )

    commitment: Final[DynamicAccountStateValue] = DynamicAccountStateValue(
        stack_type=TealType.bytes,
        max_keys=8,
    )

    open_commitment: Final[DynamicAccountStateValue] = DynamicAccountStateValue(
        stack_type=TealType.uint64,
        max_keys=8,
    )



    ##############
    # Administrative actions
    ##############

    @external(authorize = Authorize.only(owner))
    def set_owner(self, new_owner: abi.Account):
        """sets the owner of the contract, may only be called by the current owner"""
        return self.owner.set(new_owner.address())


    ##############
    # Application Create
    ##############

    @create
    def create(self):
        return self.initialize_application_state()

    @opt_in
    def opt_in(self):
        return self.initialize_account_state()

    @external
    def nft_opt_in(self, nft: abi.Asset):
        return self.do_opt_in(nft.asset_id())

    ##############
    # Start auction
    ##############

    @external(authorize = Authorize.only(owner))
    def setup(
        self,
        asset: abi.AssetTransferTransaction, 
        starting_price: abi.Uint64, 
        nft: abi.Asset, 
        start_offset : abi.Uint64, 
        duration: abi.Uint64,
        commit_duration: abi.Uint64,
        deposit: abi.Uint64,
    ):
        return Seq(
            # Set global state
            self.highest_bid.set(starting_price.get()),
            self.nft_id.set(nft.asset_id()),
            self.auction_start.set(Global.latest_timestamp() + start_offset.get()),
            self.auction_end.set(Global.latest_timestamp() + start_offset.get() + duration.get()),
            self.commit_end.set(Global.latest_timestamp() + start_offset.get() + commit_duration.get()),
            self.deposit.set(deposit.get()),
            Assert(
                And(
                    Global.latest_timestamp() < self.auction_start.get(),
                    self.auction_start.get() < self.auction_end.get(),
                    self.auction_start.get() < self.commit_end.get(),
                    self.commit_end.get() < self.auction_end.get(),
                )
            )
        )

    ##############
    # Commitment
    ##############


    @external()
    def commit(self, k: abi.Uint8, commitment: abi.DynamicBytes, payment: abi.PaymentTransaction, nft: abi.Asset):
        payment = payment.get()
        return Seq(
            # the auction has started
            Assert(And(
                Global.latest_timestamp() < self.commit_end.get(),
                Global.latest_timestamp() >= self.auction_start.get(),
            ), comment="timestamp"),
            Assert(And(
                payment.type_enum() == TxnType.Payment,
                payment.sender() == Txn.sender(),
                payment.receiver() == Global.current_application_address(),
                payment.amount() == self.deposit.get()
            ), comment="payment"),
            self.commitment[k][payment.sender()].set(commitment.get()),
        )


    ##############
    # Bidding
    ##############
    
    @external
    def bid(
        self, 
        payment: abi.PaymentTransaction, 
        highest_bidder: abi.Account,
        old_k: abi.Uint8, 
        new_k: abi.Uint8
    ):
        payment = payment.get()

        return Seq(
            # the auction has started
            Assert(And(
                Global.latest_timestamp() < self.auction_end.get(),
                Global.latest_timestamp() >= self.commit_end.get(),
            ), comment="timestamp"),
            Assert(And(
                payment.type_enum() == TxnType.Payment,
                payment.sender() == Txn.sender(),
                payment.receiver() == Global.current_application_address(),
                Sha256(Itob(payment.amount())) == self.commitment[old_k][payment.sender()]
            ), comment="payment"),

            Log(Sha256(Itob(payment.amount()))),
            self.pay_bidder(Txn.sender(), self.deposit.get()),

            self.commitment[old_k][payment.sender()].delete(),
            self.open_commitment[new_k][payment.sender()].set(payment.amount()),
            If(
                payment.amount() >= self.highest_bid.get()
            ).Then(
                Seq(
                    If(self.highest_bidder != Global.zero_address()).
                    Then(
                        self.pay_bidder(self.highest_bidder.get(), self.highest_bid.get())
                    ),
                    self.highest_bidder.set(Txn.sender()),
                    self.highest_bid.set(payment.amount()),
                    Approve()
                )
            ),
            Reject()
        )


    ##############
    # End auction
    ##############

    @external
    def end_auction(self, highest_bidder: abi.Account, nft: abi.Asset):
        auction_end = self.auction_end.get()
        highest_bid = self.highest_bid.get()
        owner = self.owner.get()
        highest_bidder = self.highest_bidder.get()

        return Seq(
            Assert(Global.latest_timestamp() > auction_end),
            self.do_aclose(highest_bidder, self.nft_id, Int(1)),
            self.pay_owner(owner, highest_bid)
        )

    ##############
    # Smart Contract payment
    ##############

    # Refund previous bidder
    @internal(TealType.none)
    def pay_bidder(self, receiver: Expr, amount: Expr):
        return Seq(
            InnerTxnBuilder.Begin(),                           
            InnerTxnBuilder.SetFields(
                {
                    TxnField.type_enum: TxnType.Payment,
                    TxnField.receiver: receiver,
                    TxnField.amount: amount - Global.min_txn_fee(),
 #                   TxnField.fee: Int(0),
#                    TxnField.fee: MIN_FEE,                     #it seems to be a bit more expensive if set
#                    TxnField.close_remainder_to: Global.zero_address(),
                }
            ),
            InnerTxnBuilder.Submit()
        )

    # Send total amount of smart contract back to the owner and close the account
    @internal(TealType.none)
    def pay_owner(self, receiver: Expr, amount: Expr):
        return Seq(
            InnerTxnBuilder.Begin(),                            #Inner transactions are only available in AVM version 5 or higher   <<<--- CHECK    (source: https://pyteal.readthedocs.io/en/stable/accessing_transaction_field.html)
            InnerTxnBuilder.SetFields(
                {
                    TxnField.type_enum: TxnType.Payment,
                    TxnField.receiver: receiver,
                    TxnField.amount: amount,
                    TxnField.fee: MIN_FEE,
                    TxnField.close_remainder_to: Global.creator_address(),
#                    TxnField.fee: Global.min_txn_fee,
#                    TxnField.rekey_to: Global.zero_address()
                }
            ),
            InnerTxnBuilder.Submit()
        )

    @internal(TealType.none)
    def do_axfer(self, receiver, asset_id, amount):
        return InnerTxnBuilder.Execute(
            {
                TxnField.type_enum: TxnType.AssetTransfer,
                TxnField.xfer_asset: asset_id,
                TxnField.asset_amount: amount,
                TxnField.asset_receiver: receiver,
                TxnField.fee: MIN_FEE,
            }
        )

    @internal(TealType.none)
    def do_aclose(self, receiver, asset_id, amount):
        return InnerTxnBuilder.Execute(
            {
                TxnField.type_enum: TxnType.AssetTransfer,
                TxnField.xfer_asset: asset_id,
                TxnField.asset_close_to: receiver,
                TxnField.fee: MIN_FEE,
            }
        )

    @internal(TealType.none)
    def do_opt_in(self, asset_id):
        return self.do_axfer(self.address, asset_id, Int(0))

if __name__ == "__main__":
    Auction().dump("artifacts")

#    if os.path.exists("approval.teal"):
#        os.remove("approval.teal")

#    if os.path.exists("approval.teal"):
#        os.remove("clear.teal")

#    if os.path.exists("abi.json"):
#        os.remove("abi.json")

#    if os.path.exists("app_spec.json"):
#        os.remove("app_spec.json")

#    with open("approval.teal", "w") as f:
#        f.write(app.approval_program)

#    with open("clear.teal", "w") as f:
#        f.write(app.clear_program)

#    with open("abi.json", "w") as f:
#        f.write(json.dumps(app.contract.dictify(), indent=4))

#    with open("app_spec.json", "w") as f:
#        f.write(json.dumps(app.application_spec(), indent=4))
