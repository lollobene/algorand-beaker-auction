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
        default = Bytes("")
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
    # Start auction
    ##############

    @external(authorize = Authorize.only(owner))
    def setup(self, payment: abi.PaymentTransaction, starting_price: abi.Uint64, nft: abi.Asset, start_offset : abi.Uint64, duration: abi.Uint64):
        payment = payment.get()
        return Seq(
            # Set global state
            self.highest_bid.set(starting_price.get()),
            self.nft_id.set(nft.asset_id()),
            self.auction_start.set(Global.latest_timestamp() + start_offset.get()),
            self.auction_end.set(Global.latest_timestamp() + start_offset.get() + duration.get()),
            Assert(
                And(
                    Global.latest_timestamp() < self.auction_start.get(),
                    self.auction_start.get() < self.auction_end.get(),
                    #payment.type_enum() == TxnType.Payment,                                    # SERVE?        <<<---
                    #payment.sender() == Txn.sender(),                                          # SERVE?        <<<---
                    #payment.receiver() == Global.current_application_address(),                # SERVE?        <<<---
                    #payment.close_remainder_to() == Global.zero_address(),                     # SERVE?        <<<---
                    #payment.rekey_to: Global.zero_address()                                    # SERVE?        <<<---
                )
            ),
            self.do_opt_in(self.nft_id)
        )


    ##############
    # Bidding
    ##############

    @external
    def bid(self, payment: abi.PaymentTransaction, previous_bidder: abi.Account):
        payment = payment.get()
        auction_end = self.auction_end.get()
        highest_bidder = self.highest_bidder.get()
        highest_bid = self.highest_bid.get()

        return Seq(
            Assert(Global.latest_timestamp() < auction_end),
            # Verify payment transaction
            Assert(                                                                 # CHIAMARE PIU' ASSERT E' COSTOSO?  <<<---
                And(
                    payment.amount() > highest_bid,
                    Txn.sender() == payment.sender()
                )
            ),
            # Return money to previous bidder
            If(highest_bidder != Bytes(""), Seq(Assert(highest_bidder == previous_bidder.address()), self.pay_bidder(highest_bidder, highest_bid))),
            # Set global state
            self.highest_bid.set(payment.amount()),
            self.highest_bidder.set(payment.sender())
        )


    ##############
    # End auction
    ##############

    @external
    def end_auction(self, highest_bidder: abi.Account, nft: abi.Asset):             # nft: abi.Asset SERVE?     <<<---
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
#                    TxnField.close_remainder_to: Global.zero_address(),                    # SERVE?        <<<---
#                    TxnField.rekey_to: Global.zero_address()                               # SERVE?        <<<---
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
#                    TxnField.rekey_to: Global.zero_address()                               # SERVE?        <<<---
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
