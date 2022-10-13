from typing import Final
from beaker import *
from pyteal import *
#import os
#import json
#from algosdk.future import transaction
#from algosdk.atomic_transaction_composer import (TransactionWithSigner)

MIN_FEE = Int(1000)                                     # minimum fee on Algorand is currently 1000 microAlgos

class SecretAuction(Application):

    ##############
    # Application State
    ##############

    # Declare Application state, marking `Final` here so the python class var doesn't get changed
    # Marking a var `Final` does _not_ change anything at the AVM level

    # Global Bytes (2)
    governor: Final[ApplicationStateValue] = ApplicationStateValue(
        stack_type = TealType.bytes,
        key = Bytes("g"),
        default = Global.creator_address(),
        descr = "The current governor of this contract, allowed to do admin type actions"
    )

    highest_bidder: Final[ApplicationStateValue] = ApplicationStateValue(
        stack_type = TealType.bytes
    )

    # Global Ints (2)
    highest_bid: Final[ApplicationStateValue] = ApplicationStateValue(
        stack_type = TealType.uint64
    )

    auction_end: Final[ApplicationStateValue] = ApplicationStateValue(
        stack_type = TealType.uint64
    )


    ##############
    # Administrative Actions
    ##############

    # Call this only on create
#    @create    
#    @create(authorize = Authorize.only(governor))
#    def create(self):
#        return self.initialize_application_state()

    @create
#    @create(authorize = Authorize.only(governor))
    def create(self):
        return Seq(
            [
                self.governor.set(Txn.sender()),
                self.highest_bidder.set(Bytes("")),
                self.highest_bid.set(Int(0)),
                self.auction_end.set(Int(0))
            ]
        )

    @external(authorize = Authorize.only(governor))
    def set_governor(self, new_governor: abi.Account):
        """sets the governor of the contract, may only be called by the current governor"""
        return self.governor.set(new_governor.address())


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
#                    TxnField.fee: Int(1000),
                    TxnField.fee: MIN_FEE,
#                    TxnField.close_remainder_to: Bytes(None),
#                    TxnField.rekey_to: Bytes(None)
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
#                    TxnField.fee: Int(1000),
                    TxnField.fee: MIN_FEE,
                    TxnField.close_remainder_to: Global.creator_address(),
#                    TxnField.rekey_to: Bytes(None)
                }
            ),
            InnerTxnBuilder.Submit()
        )


    ##############
    # Start auction
    ##############

    #TRANSACTION IMPLEMENTATION (FROM BEAKER-ACUTION EXAMPLE)
    @external(authorize = Authorize.only(governor))
    def start_auction(self, payment: abi.PaymentTransaction, starting_price: abi.Uint64, duration: abi.Uint64):
        payment = payment.get()
        return Seq(
            # Verify payment txn
            Assert(payment.receiver() == Global.current_application_address()),
            Assert(payment.amount() == Int(1000000)),
#            Assert(payment.amount() == Int(100_000)),
            # Set global state
            self.auction_end.set(Global.latest_timestamp() + duration.get()),
            self.highest_bid.set(starting_price.get()),
            self.highest_bidder.set(Bytes(""))
        )

    #NO TRANSACTION IMPLEMENTATION                          <<<--- SE SERVONO FONDI INZIALI ALL'APP, SI POTREBBE CHIAMARE FUND E LASCIARE QUESTA COSI'?
#    @external(authorize = Authorize.only(governor))
#    def start_auction(self, starting_price: abi.Uint64, duration: abi.Uint64):
#        return Seq(
#            # Set global state
#            self.auction_end.set(Global.latest_timestamp() + duration.get()),
#            self.highest_bid.set(starting_price.get()),
#            self.highest_bidder.set(Bytes(""))
#        )


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
            Assert(payment.amount() > highest_bid),
            Assert(Txn.sender() == payment.sender()),
            # Return money to previous bidder
            #If(highest_bidder != Bytes(""), Seq(self.pay(highest_bidder, highest_bid))),
            If(highest_bidder != Bytes(""), Seq(Assert(highest_bidder == previous_bidder.address()), self.pay_bidder(highest_bidder, highest_bid))),
            # Set global state
            self.highest_bid.set(payment.amount()),
            self.highest_bidder.set(payment.sender())
        )


    ##############
    # End auction
    ##############

    #PREVIOUS IMPLEMENTATION (FROM BEAKER-ACUTION EXAMPLE)
#    @external
#    def end_auction(self):
#        auction_end = self.auction_end.get()
#        highest_bid = self.highest_bid.get()
#        owner = self.governor.get()
#        highest_bidder = self.highest_bidder.get()
#
#        return Seq(
#            Assert(Global.latest_timestamp() > auction_end),
#            self.pay_owner(owner, highest_bid),
#            # Set global state
#            self.auction_end.set(Int(0)),                          #PERCHE' INIZIALIZZARE DI NUOVO?    <<<---
#            self.governor.set(highest_bidder),                     #PERCHE' CAMBIARE DI VOLTA IN VOLTA IL GOVERNOR CHE ACQUISISCE DIRITTI RISTRETTI (governor = highest_bidder)
#            self.highest_bidder.set(Bytes("")),                    #PERCHE' INIZIALIZZARE DI NUOVO?    <<<---
#        )

    #OUR CURRENT IMPLEMENTATION
    @external
    def end_auction(self):
        auction_end = self.auction_end.get()
        highest_bid = self.highest_bid.get()
        owner = self.governor.get()

        return Seq(
            Assert(Global.latest_timestamp() > auction_end),
            self.pay_owner(owner, highest_bid)
        )

#    @close_out
#    def close_out(self):
#        return Approve()

#    @delete
#    def delete(self, app_balance: abi.Uint64):
#        auction_end = self.auction_end.get()
#        return Seq(
#            Assert(Global.latest_timestamp() > auction_end),
#            Assert(app_balance == Int(0)),
#            Approve()
#        )



if __name__ == "__main__":
    SecretAuction().dump("artifacts")

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
