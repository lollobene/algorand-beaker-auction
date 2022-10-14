from typing import Final
from beaker import *
from pyteal import *
#import os
#import json

MIN_FEE = Int(1000)                                     # minimum fee on Algorand is currently 1000 microAlgos

owner_key = Bytes("seller")
#nft_id_key = Bytes("nft_id")
start_time_key = Bytes("start")
end_time_key = Bytes("end")
reserve_amount_key = Bytes("reserve_amount")
#min_bid_increment_key = Bytes("min_bid_inc")
num_bids_key = Bytes("num_bids")
highest_bid_key = Bytes("bid_amount")
highest_bidder_key = Bytes("bid_account")

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
        stack_type = TealType.bytes
    )

    # Global Ints (4)
    highest_bid: Final[ApplicationStateValue] = ApplicationStateValue(
        stack_type = TealType.uint64
    )

#    nft_id: Final[ApplicationStateValue] = ApplicationStateValue(
#        stack_type = TealType.uint64
#    )

    auction_start: Final[ApplicationStateValue] = ApplicationStateValue(
        stack_type = TealType.uint64
    )

    auction_end: Final[ApplicationStateValue] = ApplicationStateValue(
        stack_type = TealType.uint64
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
    def create(self, start_offset: abi.Uint64, duration: abi.Uint64):
        return Seq(
            self.owner.set(Txn.sender()),
#            self.nft_id.set(Int(0)),
            self.highest_bid.set(Int(0)),
            self.highest_bidder.set(Bytes("")),
            self.auction_start.set(Global.latest_timestamp() + start_offset.get()),
            self.auction_end.set(Global.latest_timestamp() + start_offset.get() + duration.get()),
            Assert(
                And(
                    Global.latest_timestamp() < self.auction_start.get(),
                    self.auction_start.get() < self.auction_end.get()
                )
            )
        )


#    @opt_in
#    def opt_in(self):
#        return self.initialize_account_state()


#    @external
#    def opt_in(self, payment: abi.PaymentTransaction, nft_id: abi.Uint64):
#    def opt_in(self, nft_id: abi.Uint64):
#    def opt_in(self):
#        return Seq(
#            self.nft_id.set(nft_id.get()),
            # opt into NFT asset -- because you can't opt in if you're already opted in, this is what
            # we'll use to make sure the contract has been set up
##            InnerTxnBuilder.Begin(),
##            InnerTxnBuilder.SetFields(
##                {
##                    TxnField.type_enum: TxnType.AssetTransfer,
##                    TxnField.xfer_asset: self.nft_id.get(),
##                    TxnField.asset_receiver: Global.current_application_address(),
##                }
##            ),
##            InnerTxnBuilder.Submit(),
##            Approve()
#        )


    #TRANSACTION IMPLEMENTATION (FROM BEAKER-ACUTION EXAMPLE)
#    @external(authorize = Authorize.only(owner))
#    def setup(self, payment: abi.PaymentTransaction, starting_price: abi.Uint64):
#        payment = payment.get()
#        return Seq(
#            Assert(payment.sender() == Txn.sender()),
#            Assert(payment.type() == TxnType.AssetTransfer()),
#            Assert(payment.index() == TxnType.xfer_asset),
#            Assert(payment.receiver() == Global.current_application_address()),
#            self.highest_bid.set(starting_price.get())
#        )


    ##############
    # Start auction
    ##############

    @external(authorize = Authorize.only(owner))
    def setup(self, starting_price: abi.Uint64):
        return Seq(
            # Set global state
            self.highest_bid.set(starting_price.get()),
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
#            Assert(Global.latest_timestamp() < auction_end),
            # Verify payment transaction
            Assert(payment.amount() > highest_bid),
            Assert(Txn.sender() == payment.sender()),
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
    def end_auction(self):
        auction_end = self.auction_end.get()
        highest_bid = self.highest_bid.get()
        owner = self.owner.get()

        return Seq(
            Assert(Global.latest_timestamp() > auction_end),
            self.pay_owner(owner, highest_bid)
        )


#    @close_out
#    def close_out(self):
#        return Approve()

#    @delete
#    def delete(self, app_addr: abi.Account):
#        auction_end = self.auction_end.get()
#        app_balance = client.account_info(app_addr)["amount"]
#        
#        return Seq(
#            Assert(Global.latest_timestamp() > auction_end),
#            Assert(Int(app_balance) == Int(0)),
##            Assert(payment.amount() == Int(1000000))
#            Approve()
#        )

    ##############
    # Smart Contract payment
    ##############

    # Refund previous bidder
    @internal(TealType.none)
    def pay_bidder(self, receiver: Expr, amount: Expr):
        return Seq(
            InnerTxnBuilder.Begin(),                            #Inner transactions are only available in AVM version 5 or higher   <<<--- CHECK    (source: https://pyteal.readthedocs.io/en/stable/accessing_transaction_field.html)
            InnerTxnBuilder.SetFields(
                {
                    TxnField.type_enum: TxnType.Payment,
                    TxnField.receiver: receiver,
                    TxnField.amount: amount,
                    TxnField.fee: Int(0),
#                    TxnField.fee: MIN_FEE,                     #it seems to be a bit more expensive if set
#                    TxnField.close_remainder_to: Global.zero_address(),
#                    TxnField.rekey_to: Global.zero_address
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
#                    TxnField.fee: Int(0),
                    TxnField.fee: MIN_FEE,
#                    TxnField.fee: Global.min_txn_fee,
                    TxnField.close_remainder_to: Global.creator_address(),
#                    TxnField.rekey_to: Global.zero_address()
                }
            ),
            InnerTxnBuilder.Submit()
        )



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
