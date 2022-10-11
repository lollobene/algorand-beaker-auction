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

APP_ID = 62
APP_ADDRESS = "NDBRJYD5KXUA6K5Q456OM6JLC5SRKQJ7ME6MK2NCE5VX3WGGEAB5LOYFVQ"
TX_ID = "R726ZBMRWKU7DBURD2KGYC4VP7YG7C4UCH3VTJXCDCI32UDTVB4A"

PURESTAKE_API_KEY = os.getenv("PURESTAKE_API_KEY")
MNEMONIC_PHRASE = os.getenv("MNEMONIC_PHRASE")

algod_address = "https://testnet-algorand.api.purestake.io/ps2"
algod_token = PURESTAKE_API_KEY
headers = {
  "X-API-Key": algod_token,
}

governor_private_key = mnemonic.to_private_key(MNEMONIC_PHRASE)

governor_signer = AccountTransactionSigner(governor_private_key)

def main():

  client = algod.AlgodClient(algod_token, algod_address, headers)

  app = Auction()

  app_client = ApplicationClient(client, app, app_id=APP_ID, signer=governor_signer)

  app_id, app_address, transaction_id = app_client.create()

  print(
    f"DEPLOYED: App ID: {app_id} Address: {app_address} Transaction ID: {transaction_id}"
  )

  print(f"Current app state: {app_client.get_application_state()}")
  

if __name__ == "__main__":
  main()