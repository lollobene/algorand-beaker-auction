#!/usr/bin/env python3
from typing import Final
from beaker.client import ApplicationClient, LogicException
from beaker.sandbox import get_algod_client, get_accounts
from beaker import *
from pyteal import *
import os
import json
from algosdk.future import transaction
from algosdk.atomic_transaction_composer import (
  TransactionWithSigner,
)

class Auction(Application):
  # Global Bytes (2)
  owner: Final[ApplicationStateValue] = ApplicationStateValue(
    stack_type=TealType.bytes
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

  @create
  def create(self):
    return Seq(
      [
        self.owner.set(Txn.sender()),
        self.highest_bidder.set(Bytes("")),
        self.highest_bid.set(Int(0)),
        self.auction_end.set(Int(0)),
      ]
    )

  @external
  def start_auction(
    self,
    payment: abi.PaymentTransaction,
    starting_price: abi.Uint64,
    duration: abi.Uint64,
  ):
    payment = payment.get()

    return Seq(
      # Verify payment txn
      Assert(payment.receiver() == Global.current_application_address()),
      Assert(payment.amount() == Int(1000000)),
      # Set global state
      self.auction_end.set(Global.latest_timestamp() + duration.get()),
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
    owner = self.owner.get()
    highest_bidder = self.highest_bidder.get()

    return Seq(
      Assert(Global.latest_timestamp() > auction_end),
      self.pay(owner, highest_bid),
      # Set global state
      self.auction_end.set(Int(0)),
      self.owner.set(highest_bidder),
      self.highest_bidder.set(Bytes("")),
    )

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

def main():
  # Recupero degli account da sandbox
  accts = get_accounts()

  # Prendo il primo account
  acct1 = accts.pop()
  acct2 = accts.pop()
  acct3 = accts.pop()

  # Prendo il client per interagire con la sandbox
  client = get_algod_client()

  # Creo lo smart contract
  app = Auction()

  # Metto insieme client, smart contract e account
  app_client = ApplicationClient(client, app, signer=acct1.signer)

  # Faccio il deploy dello smart contract sulla rete
  app_id, app_address, transaction_id = app_client.create()

  print(
    f"DEPLOYED: App ID: {app_id} Address: {app_address} Transaction ID: {transaction_id}"
  )

  print(f"Current app state: {app_client.get_application_state()}")

  # Preparo la transazione che invia gli algo allo smart contract
  interaction_client = app_client.prepare(signer=acct1.signer)

  # Creo i suggested params (non so cosa siano, credo sia una cosa di default)
  sp = client.suggested_params()

  print(sp.fee)

  # creo la transazione che manda gli algo allo smartcontract
  tx=TransactionWithSigner(
    txn=transaction.PaymentTxn(acct1.address, sp, app_address, 1 * consts.algo),
    signer=acct1.signer,
  )

  # INTERAZIONE VERA E PROPRIA CON SMART CONTRACT
  try:
    result = interaction_client.call(
      app.start_auction,
      payment=tx,
      starting_price=1*consts.algo,
      duration= 5*60 # 5 minutes assuming duration
    )

  except LogicException as e:
    print(f"\n{e}\n")


  print(f"Current app state: {app_client.get_application_state()}")

  # Preparo una nuova transazione dal secondo account per inserire una nuova puntata
  bid_client = app_client.prepare(signer=acct2.signer)
  tx2=TransactionWithSigner(
    txn=transaction.PaymentTxn(acct2.address, sp, app_address, 2 * consts.algo),
    signer=acct2.signer,
  )

  try:
    result = bid_client.call(
      app.bid,
      payment=tx2,
      previous_bidder=acct1.address
    )

  except LogicException as e:
    print(f"\n{e}\n")

  print(f"Current app state: {app_client.get_application_state()}")


  #Seconda interazione con smart contract
  bid_client = app_client.prepare(signer=acct3.signer)
  sp = client.suggested_params()
  sp.fee = 10
  print(sp.fee)
  tx3=TransactionWithSigner(
    txn=transaction.PaymentTxn(acct3.address, sp, app_address, 3 * consts.algo),
    signer=acct3.signer,
  )

  try:
    result = bid_client.call(
      app.bid,
      payment=tx3,
      previous_bidder=acct2.address
    )

  except LogicException as e:
    print(f"\n{e}\n")
  
  print(f"Current app state: {app_client.get_application_state()}")


if __name__ == "__main__":
  main()