#!/usr/bin/env python3
from typing import Final
from beaker.client import ApplicationClient, LogicException
from beaker.sandbox import get_algod_client, get_accounts
from beaker import *
from pyteal import *
import os
import json
from algosdk.future import transaction
from algosdk.atomic_transaction_composer import (TransactionWithSigner)

class Auction(Application):

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
        descr = "The current governor of this contract, allowed to do admin type actions",
    )

    highest_bidder: Final[ApplicationStateValue] = ApplicationStateValue(
        stack_type=TealType.bytes
    )

    # Global Ints (2)
    auction_end: Final[ApplicationStateValue] = ApplicationStateValue(
        stack_type=TealType.uint64
    )

    highest_bid: Final[ApplicationStateValue] = ApplicationStateValue(
        stack_type=TealType.uint64
    )

    ##############
    # Constants         <<<---- ????
    ##############

    ##############
    # Administrative Actions
    ##############

    # Call this only on create

    #@create
    #def create(self):
    #    return self.initialize_application_state()

    @create
    def create(self):
        return Seq(
            [
                self.governor.set(Txn.sender()),
                self.highest_bidder.set(Bytes("")),
                self.highest_bid.set(Int(0)),
                self.auction_end.set(Int(0)),
            ]
        )

    # Only the account set in app_state.owner may call this method
    @external(authorize=Authorize.only(governor))
    def set_governor(self, new_governor: abi.Account):
        """sets the governor of the contract, may only be called by the current governor"""
        return self.governor.set(new_governor.address())

    @external(authorize=Authorize.only(governor))
    def start_auction(
        self,
        payment: abi.PaymentTransaction,
        starting_price: abi.Uint64,
        length: abi.Uint64,
    ):
        payment = payment.get()

        return Seq(
            # Verify payment txn
            Assert(payment.receiver() == Global.current_application_address()),
            Assert(payment.amount() == Int(1000000)),
            # Set global state
            self.auction_end.set(Global.latest_timestamp() + length.get()),
            self.highest_bid.set(starting_price.get()),
        )

    @internal(TealType.none)
    def pay(self, receiver: Expr, amount: Expr):
        return Seq(
            InnerTxnBuilder.Begin(),
            InnerTxnBuilder.SetFields(
                {
                    TxnField.type_enum: TxnType.Payment,
                    TxnField.receiver: receiver,
                    TxnField.amount: amount,
                    TxnField.fee: Int(0),
                }
            ),
            InnerTxnBuilder.Submit(),
        )

    @external
    def end_auction(self):
        auction_end = self.auction_end.get()
        highest_bid = self.highest_bid.get()
        owner = self.governor.get()
        highest_bidder = self.highest_bidder.get()

        return Seq(
            Assert(Global.latest_timestamp() > auction_end),
            self.pay(owner, highest_bid),
            # Set global state
            self.auction_end.set(Int(0)),
            self.governor.set(highest_bidder),
            self.highest_bidder.set(Bytes("")),
        )

#    @external(bidders=Authorize.holds_token(asset_id: Expr))
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
            # Return previous bid
            If(highest_bidder != Bytes(""), Seq(Assert(highest_bidder == previous_bidder.address()), self.pay(highest_bidder, highest_bid))),
            # Set global state
            self.highest_bid.set(payment.amount()),
            self.highest_bidder.set(payment.sender()),
        )


if __name__ == "__main__":
#    main()
    Auction().dump("artifacts")