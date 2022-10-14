
#############################
# IMPLEMENTAZIONE CON HTLC
#############################

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

    # Global Bytes (1)
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


    # Call this only on create
#    @create    
#    def create(self):
#        return self.initialize_application_state()

    @create
    def create(self):
        return Seq(
            [
                self.highest_bidder.set(Bytes("")),
                self.highest_bid.set(Int(0)),
                self.auction_end.set(Int(0))
            ]
        )


    ##############
    # Bidding
    ##############

#    @external
#    def bid(self, payment: abi.PaymentTransaction, duration: abi.Uint64):
#        highest_bid = self.highest_bid.get()
#        self.auction_end.set(Global.latest_timestamp() + duration.get())
#        auction_end = self.auction_end.get()
#        payment = payment.get()

#        while (Assert(Global.latest_timestamp() < auction_end)):
#            payment = payment.get()
#            # Verify payment amount
#            Assert(payment.amount() > highest_bid),
#            Assert(Txn.sender() == payment.sender()),
##            If(payment.amount() > highest_bid), Seq(self.highest_bid.set(payment.amount()), self.highest_bidder.set(payment.sender())),
#            # Set global state
#            self.highest_bid.set(payment.amount()),
#            self.highest_bidder.set(payment.sender())

#        return Seq(
#            # Set global state
#            self.highest_bid.set(payment.amount()),
#            self.highest_bidder.set(payment.sender())
#        )




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
