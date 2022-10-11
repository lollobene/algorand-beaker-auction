from algosdk import mnemonic
from algosdk import transaction

from algosdk.v2client import algod
from algosdk.future import transaction
from algosdk.atomic_transaction_composer import (
  AccountTransactionSigner,
  TransactionWithSigner,
)

from beaker import *
from beaker.client import ApplicationClient, LogicException

from pyteal import *

from dotenv import load_dotenv
import os

from auction import Auction


load_dotenv()

# APP_ID = 
# APP_ADDRESS = ""
# TX_ID = ""

PURESTAKE_API_KEY = os.getenv("PURESTAKE_API_KEY")
GOVERNOR_MNEMONIC_PHRASE = os.getenv("GOVERNOR_MNEMONIC_PHRASE")
BIDDER1_MNEMONIC_PHRASE = os.getenv("BIDDER1_MNEMONIC_PHRASE")
BIDDER2_MNEMONIC_PHRASE = os.getenv("BIDDER2_MNEMONIC_PHRASE")

algod_address = "https://testnet-algorand.api.purestake.io/ps2"
algod_token = PURESTAKE_API_KEY
headers = {
  "X-API-Key": algod_token,
}

governor_private_key = mnemonic.to_private_key(GOVERNOR_MNEMONIC_PHRASE)
bidder1_private_key = mnemonic.to_private_key(BIDDER1_MNEMONIC_PHRASE)
bidder2_private_key = mnemonic.to_private_key(BIDDER2_MNEMONIC_PHRASE)

governor_public_key = mnemonic.to_public_key(GOVERNOR_MNEMONIC_PHRASE)
bidder1_public_key = mnemonic.to_public_key(BIDDER1_MNEMONIC_PHRASE)
bidder2_public_key = mnemonic.to_public_key(BIDDER2_MNEMONIC_PHRASE)

governor_signer = AccountTransactionSigner(governor_private_key)
bidder1_signer = AccountTransactionSigner(bidder1_private_key)
bidder2_signer = AccountTransactionSigner(bidder2_private_key)

def main():

  client = algod.AlgodClient(algod_token, algod_address, headers)

  app = Auction()

  app_client = ApplicationClient(client, app, signer=governor_signer)

  app_id, app_address, transaction_id = app_client.create()

  print(
    f"DEPLOYED: App ID: {app_id} Address: {app_address} Transaction ID: {transaction_id}"
  )

  print(f"Current app state: {app_client.get_application_state()}")

  sp = client.suggested_params()

  tx=TransactionWithSigner(
    txn=transaction.PaymentTxn(governor_public_key, sp, app_address, 1 * consts.algo),
    signer=governor_signer,
  )

  try:
    result = app_client.call(
      app.start_auction,
      payment=tx,
      starting_price=1*consts.algo,
      length= 5*60 # 5 minutes assuming duration
    )

  except LogicException as e:
    print(f"\n{e}\n")

  print(f"Current app state: {app_client.get_application_state()}")

  # First bid
  bidder1_client = app_client.prepare(signer=bidder1_signer)
  tx2=TransactionWithSigner(
    txn=transaction.PaymentTxn(bidder1_public_key, sp, app_address, 2 * consts.algo),
    signer=bidder1_signer,
  )

  try:
    result = bidder1_client.call(
      app.bid,
      payment=tx2,
      previous_bidder=governor_public_key
    )

  except LogicException as e:
    print(f"\n{e}\n")

  print(f"Current app state: {app_client.get_application_state()}")

  # Second bid
  bidder2_client = app_client.prepare(signer=bidder2_signer)
  sp.fee=10
  tx3=TransactionWithSigner(
    txn=transaction.PaymentTxn(bidder2_public_key, sp, app_address, 3 * consts.algo),
    signer=bidder2_signer,
  )

  try:
    result = bidder2_client.call(
      app.bid,
      payment=tx3,
      previous_bidder=bidder1_public_key
    )

  except LogicException as e:
    print(f"\n{e}\n")

  print(f"Current app state: {app_client.get_application_state()}")

  # Close auction
  # TODO close auction


  

if __name__ == "__main__":
  main()