from typing import Final
from webbrowser import get
from beaker import *
from pyteal import *
#import os
#import json

MIN_FEE = Int(1000)                                         # minimum fee on Algorand is currently 1000 microAlgos


class Auction(Application):

    ##############
    # Application State
    ##############

    # Declare Application state, marking `Final` here so the python class var doesn't get changed
    # Marking a var `Final` does _not_ change anything at the AVM level

    ##############
    # Global State
    ##############

    # Global Bytes (2)
    owner: Final[ApplicationStateValue] = ApplicationStateValue(
        stack_type = TealType.bytes,
        key = Bytes("o"),
        default = Global.creator_address(),
        descr = "The current owner of this contract, allowed to do admin type actions"
    )

    highest_bidder: Final[ApplicationStateValue] = ApplicationStateValue(
        stack_type = TealType.bytes,
        default = Bytes("")
    )

    # Global Ints (6)
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

    commit_end: Final[ApplicationStateValue] = ApplicationStateValue(
        stack_type = TealType.uint64,
        default = Int(0)
    )

    auction_end: Final[ApplicationStateValue] = ApplicationStateValue(
        stack_type = TealType.uint64,
        default = Int(0)
    )

    deposit: Final[ApplicationStateValue] = ApplicationStateValue(              # escrow amount to partecipate in the auction
        stack_type = TealType.uint64,
        default = Int(0)
    )

    ##############
    # Local State
    ##############

    # Local Bytes (1)
    # to enable the contract writing the commitment (bid hashed value) into local state -> TealType.bytes (hashed amount)
    # Enabling max_keys = 1, only one commitment is allowed
    commitment: Final[DynamicAccountStateValue] = DynamicAccountStateValue(
        stack_type = TealType.bytes,
        max_keys = 1
    )

    # Local Ints (1)
    # to enable the contract writing the bid (revealed) into local state -> TealType.uint64 (amount)
    # max_keys(open_commitment) == max_keys(commitment) to map commit and corrispondent bid
    open_commitment: Final[DynamicAccountStateValue] = DynamicAccountStateValue(
        stack_type = TealType.uint64,
        max_keys = 1
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


    ##############
    # Opt-in
    ##############

    @opt_in
    def opt_in(self):                               # opt-in for commitment
        return self.initialize_account_state()

    @external
    def nft_opt_in(self, nft: abi.Asset):           # opt-in the nft into the smart contract
        return self.do_opt_in(nft.asset_id())


    ##############
    # Auction setup
    ##############
    @external(authorize = Authorize.only(owner))
    def setup(self, asset: abi.AssetTransferTransaction, starting_price: abi.Uint64, nft: abi.Asset,
                start_offset : abi.Uint64, commit_duration: abi.Uint64, duration: abi.Uint64, deposit: abi.Uint64):
        asset = asset.get()
        return Seq(
            # Set global state
            self.highest_bid.set(starting_price.get()),
            self.nft_id.set(nft.asset_id()),
            self.auction_start.set(Global.latest_timestamp() + start_offset.get()),
            self.commit_end.set(Global.latest_timestamp() + start_offset.get() + commit_duration.get()),
            self.auction_end.set(Global.latest_timestamp() + start_offset.get() + duration.get()),
            self.deposit.set(deposit.get()),
            Assert(
                And(
                    Global.latest_timestamp() < self.auction_start.get(),
                    self.auction_start.get() < self.auction_end.get(),
                    self.auction_start.get() < self.commit_end.get(),
                    self.commit_end.get() < self.auction_end.get(),
                    asset.type_enum() == TxnType.AssetTransfer,
                    asset.xfer_asset() == self.nft_id.get(),
#                    asset.asset_amount() == Int(1),
                    asset.asset_receiver() == Global.current_application_address()
                )
            )
        )


    ##############
    # Commitment
    ##############

    @external()
#    def commit(self, k: abi.Uint8, commitment: abi.DynamicBytes, payment: abi.PaymentTransaction, nft: abi.Asset):
    def commit(self, k: abi.Uint8, commitment: abi.DynamicBytes, payment: abi.PaymentTransaction):
        payment = payment.get()
        return Seq(
            Assert(And(
                    Global.latest_timestamp() < self.commit_end.get(),
                    Global.latest_timestamp() >= self.auction_start.get()
                ), comment = "timestamp"),
            Assert(And(
                    payment.type_enum() == TxnType.Payment,
                    payment.sender() == Txn.sender(),
                    payment.receiver() == Global.current_application_address(),
                    payment.amount() == self.deposit.get()                              # check the user has deposited the escrow funds
                ), comment = "payment"),
            self.commitment[k][payment.sender()].set(commitment.get())                  # hence, commitment stored correctly
        )


    ##############
    # Bid
    ##############
    
    @external
#    def bid(self, payment: abi.PaymentTransaction, highest_bidder: abi.Account, old_k: abi.Uint8, new_k: abi.Uint8):
    def bid(self, payment: abi.PaymentTransaction, highest_bidder: abi.Account, k: abi.Uint8):
#    def bid(self, payment: abi.PaymentTransaction, k: abi.Uint8):
        payment = payment.get()
#        nft = self.nft_id.get()
#        on_bid_nft_holding = AssetHolding.balance(
#            Global.current_application_address(), App.globalGet(nft))
        return Seq(
#            on_bid_nft_holding,
#            Assert(And(
#                # the auction has been set up
#                on_bid_nft_holding.hasValue(),
#                on_bid_nft_holding.value() > Int(0),
#                # the auction has started
#            )),
            Assert(And(
                # Checking (current time) >= (commit end) is fundamental. Every user can do just one commit (max_keys = 1)
                # in the commitment phase. Every other commitment (if submitted) from the same user is going to be overwritten
                # during the commit phase (hence, before bids are revealed).
                Global.latest_timestamp() < self.auction_end.get(),
                Global.latest_timestamp() >= self.commit_end.get()
            ), comment="timestamp"),
            Assert(And(
                payment.type_enum() == TxnType.Payment,
                payment.sender() == Txn.sender(),
                payment.receiver() == Global.current_application_address(),
#                Sha256(Itob(payment.amount())) == self.commitment[old_k][payment.sender()]  # verify corrispondence among bid and commit values
                Sha256(Itob(payment.amount())) == self.commitment[k][payment.sender()]
#                Sha256(Itob(payment.amount())) == self.commitment[old_k][payment.sender()].get
            ), comment="payment"),

            Log(Sha256(Itob(payment.amount()))),
#            self.commitment[old_k][payment.sender()].delete(),
#            self.open_commitment[new_k][payment.sender()].set(payment.amount()),
            self.commitment[k][payment.sender()].delete(),
            self.open_commitment[k][payment.sender()].set(payment.amount()),

            If(payment.amount() > self.highest_bid.get())                                   # current bid > previous bid
            .Then(
                Seq(
                    self.pay_bidder(Txn.sender(), self.deposit.get()),                      # give back the deposit (commit and the bid are valid)
                    If(self.highest_bidder != Bytes(""))                                    # there was a previous highest bidder
                    .Then(
                        self.pay_bidder(self.highest_bidder.get(), self.highest_bid.get())  # give back to the previous bidder bid + deposit
                    ),
                    # Set global state
                    self.highest_bidder.set(Txn.sender()),
                    self.highest_bid.set(payment.amount()),
                    Approve()                                                               # <<<---
                )
            ).Else(                                                                         # current bid <= previous bid
                self.pay_bidder(Txn.sender(), self.deposit.get() + payment.amount())        # give back bid + deposit to the current bidder (temporal order rule)
            )
        )


    ##############
    # End auction
    ##############

    @external
#    def end_auction(self, highest_bidder: abi.Account, nft: abi.Asset):
    def end_auction(self, nft: abi.Asset):
        auction_end = self.auction_end.get()
        highest_bid = self.highest_bid.get()
        owner = self.owner.get()
        highest_bidder = self.highest_bidder.get()

        return Seq(
            Assert(Global.latest_timestamp() > auction_end),
            If(self.highest_bidder == Global.zero_address())
            .Then(
                Seq(
                    self.do_aclose(owner, self.nft_id, Int(1)),
                    self.pay_owner(owner, highest_bid)
                )
            )
            .Else(
                Seq(
                    self.do_aclose(highest_bidder, self.nft_id, Int(1)),
                    self.pay_owner(owner, highest_bid)
                )
            )
        )


    ##############
    # Smart Contract payment functions
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
                    TxnField.fee: Int(0),
#                    TxnField.fee: MIN_FEE,                     #it seems to be a bit more expensive if set
#                    TxnField.close_remainder_to: Global.zero_address(),                                        # <<<---
#                    TxnField.rekey_to: Global.zero_address()                                                   # <<<---
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
#                    TxnField.fee: MIN_FEE,
                    TxnField.fee: Int(0),
                    TxnField.close_remainder_to: Global.creator_address(),
#                    TxnField.close_remainder_to: Global.zero_address(),                                        # <<<---
#                    TxnField.rekey_to: Global.zero_address()                                                   # <<<---
                }
            ),
            InnerTxnBuilder.Submit()
        )


    # Asset transfer to the smart contract
    @internal(TealType.none)
    def do_axfer(self, receiver, asset_id, amount):
        return InnerTxnBuilder.Execute(
            {
                TxnField.type_enum: TxnType.AssetTransfer,
                TxnField.xfer_asset: asset_id,
                TxnField.asset_amount: amount,
                TxnField.asset_receiver: receiver,
                TxnField.fee: MIN_FEE
            }
        )


    # Asset close out from the smart contract to the receiver
    @internal(TealType.none)
    def do_aclose(self, receiver, asset_id, amount):
        return InnerTxnBuilder.Execute(
            {
                TxnField.type_enum: TxnType.AssetTransfer,
                TxnField.xfer_asset: asset_id,
                TxnField.asset_close_to: receiver,
                TxnField.fee: MIN_FEE
            }
        )

    
    # Asset opt-in for the smart contract
    @internal(TealType.none)
    def do_opt_in(self, asset_id):
        return self.do_axfer(self.address, asset_id, Int(0))


    # Reject updates
#    @update(TealType.none)
#    def update_contract(self):
#        return Reject()



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
