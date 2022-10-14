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
from dotenv_example import load_dotenv
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

MIN_FEE = 1000

def main():

    client = algod.AlgodClient(algod_token, algod_address, headers)

    tx_params = client.suggested_params()
    tx_params.fee = MIN_FEE


    app = Auction()

    app_client = ApplicationClient(client, app, signer=governor_signer)

    print("\nCREATING AND DEPLOYING THE SMART CONTRACT...")
    try:
            app_id, app_addr, txid = app_client.create()

    except LogicException as e:
            print(f"\n{e}\n")
    

if __name__ == "__main__":
    main()