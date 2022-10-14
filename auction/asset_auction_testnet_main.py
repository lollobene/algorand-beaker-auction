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
from asset_auction import Auction
from util import *
import time


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
offset = 10                             # start time is 10 seconds in the future
length = 70                             # auction duration

client = algod.AlgodClient(algod_token, algod_address, headers)

def main():


    tx_params = client.suggested_params()
    tx_params.fee = MIN_FEE


    app = Auction()

    app_client = ApplicationClient(client, app, signer=governor_signer)

    print("\nCREATING AND DEPLOYING THE SMART CONTRACT...")
    try:
            app_id, app_addr, txid = app_client.create()

    except LogicException as e:
            print(f"\n{e}\n")

    print(f"Created App with id: {app_id} and address: {app_addr} in tx: {txid}\n")
    print(f"Current app state: {app_client.get_application_state()}")
    print_balances(app_addr, governor_public_key, bidder1_public_key, bidder2_public_key)


    ##############
    # NFT CREATION
    ##############

    nft = create_asset(governor_public_key, governor_private_key, "dummyNFT")

    # Check if the accounts hold the asset, otherwise opt-in
    # optInToAsset(client, governor_public_key, governor_private_key, nft)
    optInToAsset(client, bidder1_public_key, bidder1_private_key, nft)
    optInToAsset(client, bidder2_public_key, bidder2_private_key, nft)

    ##############
    # START AUCTION
    ##############

    print("\n\n\n--------------------------------------------------------------------------------")
    print("Bob is creating an auction that lasts 60 seconds to auction off the NFT...")
    print("--------------------------------------------------------------------------------")
    print("\nSetup the Auction application......")
    
    sp = client.suggested_params()
    ptxn = TransactionWithSigner(
        txn=transaction.PaymentTxn(governor_public_key, sp, app_addr, 1*consts.algo), signer=governor_signer
    )

    try:
        result = app_client.call(
            Auction.setup,
            payment=ptxn,
            starting_price = 1*consts.algo,
            nft = nft,
            start_offset = offset,
            duration = length
        )

    except LogicException as e:
        print(f"\n{e}\n")

    print(f"Current app state: {app_client.get_application_state()}")

    ##############
    # SENDING NFT TO THE SMART CONTRACT
    ##############
    
    txn=transaction.AssetTransferTxn(governor_public_key, sp, app_addr, 1, nft)
    signed_txn = txn.sign(governor_private_key)

    try:
        txid = client.send_transaction(signed_txn)
        if txid: print("\nNFT TRANSFERRED TO SMART CONTRACT\n")
    except Exception as err:
        print(err)

    
    ##############
    # START BIDDING - USER 2
    ##############

    print("\nSTART BIDDING: USER 2\n")

    bidder_client = app_client.prepare(bidder1_signer)
    tx1 = TransactionWithSigner(
        txn = transaction.PaymentTxn(bidder1_public_key, tx_params, app_addr, 2*consts.algo), signer = bidder1_signer
    )


    try:
        result = bidder_client.call(
        Auction.bid,
        payment = tx1,
        previous_bidder = governor_public_key
    )
    except LogicException as e:
        print(f"\n{e}\n")
    

    # print("Global state:", read_global_state(client, app_id))
    print(f"Current app state: {app_client.get_application_state()}")


#    for res in result.tx_ids:
#        print(res)

    print(f"Current app state: {app_client.get_application_state()}\n")
    print(f"Current app address info: {app_client.get_application_account_info()}\n")
#    print(f"Current address info: {app_client.get_account_state()}\n")
    print_balances(app_addr, governor_public_key, bidder1_public_key, bidder2_public_key)


    ##############
    # START BIDDING - USER 3
    ##############

    print("START BIDDING: USER 3")

    # Execute bidding
    bidder_client_2 = app_client.prepare(bidder2_signer)
    tx2 = TransactionWithSigner(
        txn = transaction.PaymentTxn(bidder2_public_key, tx_params, app_addr, 3*consts.algo), signer = bidder2_signer
    )
    try:
        result = bidder_client_2.call(
            Auction.bid,
            payment = tx2,
            previous_bidder = bidder1_public_key
        )
    except LogicException as e:
        print(f"\n{e}\n")

    print(f"Current app state: {app_client.get_application_state()}\n")
    print(f"Current app address info: {app_client.get_application_account_info()}\n")
    print(f"Current address info: {app_client.get_account_state()}\n")
    print_balances(app_addr, governor_public_key, bidder1_public_key, bidder2_public_key)

    ##############
    # RE-BID - USER 2
    ##############

    print("RE-BID: USER 2")

    # Execute bidding

    tx1 = TransactionWithSigner(
        txn = transaction.PaymentTxn(bidder1_public_key, tx_params, app_addr, 4*consts.algo), signer = bidder1_signer
    )

    try:
        result = bidder_client.call(
        Auction.bid,
        payment = tx1,
        previous_bidder = bidder2_public_key
        )
    except LogicException as e:
        print(f"\n{e}\n")

    print(f"Current app state: {app_client.get_application_state()}\n")
    print(f"Current app address info: {app_client.get_application_account_info()}\n")
    print(f"Current address info: {app_client.get_account_state()}\n")
    print_balances(app_addr, governor_public_key, bidder1_public_key, bidder2_public_key)

    ##############
    # RE-BID - USER 3
    ##############

    print("RE-BID: USER 3")

    # Execute bidding
    bidder_client_2 = app_client.prepare(bidder2_signer)
    tx2 = TransactionWithSigner(
        txn = transaction.PaymentTxn(bidder2_public_key, tx_params, app_addr, 5*consts.algo), signer = bidder2_signer
    )
    try:
        result = bidder_client_2.call(
            Auction.bid,
            payment = tx2,
            previous_bidder = bidder1_public_key
        )
    except LogicException as e:
        print(f"\n{e}\n")

    print(f"Current app state: {app_client.get_application_state()}\n")
    print(f"Current app address info: {app_client.get_application_account_info()}\n")
    print(f"Current address info: {app_client.get_account_state()}\n")
    print_balances(app_addr, governor_public_key, bidder1_public_key, bidder2_public_key)


    ##############
    # END AUCTION
    ##############

    print("CLOSING AUCTION BY THE GOVERNOR...")
    time.sleep(90)
    try:
        result = app_client.call(
            Auction.end_auction,
            highest_bidder = bidder2_public_key,
            nft=nft
        )
    except LogicException as e:
        print(f"\n{e}\n")

    print(f"Current app state: {app_client.get_application_state()}\n")
    print(f"Current app address info: {app_client.get_application_account_info()}\n")
#    print(f"Current address info: {app_client.get_account_state()}\n")
    print_balances(app_addr, governor_public_key, bidder1_public_key, bidder2_public_key)


def print_balances(app: str, addr1: str, bidder1_public_key: str, bidder2_public_key: str):

    appbal = client.account_info(app)
    print("App Balance = {}\n".format(appbal["amount"]))

    addrbal1 = client.account_info(addr1)
    print("Participant:", addr1, end = "")
    print("\tAddress Balance = {}\n".format(addrbal1["amount"]))

    addrbal2 = client.account_info(bidder1_public_key)
    print("Participant:", bidder1_public_key, end = "")
    print("\tAddress Balance = {}\n".format(addrbal2["amount"]))

    addrbal3 = client.account_info(bidder2_public_key)
    print("Participant:", bidder2_public_key, end = "")
    print("\tAddress Balance = {}\n".format(addrbal3["amount"]))


def create_asset(addr, pk, unitname):
    # Get suggested params from network
    sp = client.suggested_params()
    # Create the transaction
    create_txn = transaction.AssetCreateTxn(
        addr, sp, 1, 0, False, asset_name="dummyNFT", unit_name=unitname
    )
    # Ship it
    txid = client.send_transaction(create_txn.sign(pk))
    # Wait for the result so we can return the app id
    result = transaction.wait_for_confirmation(client, txid, 4)
    return result["asset-index"]
    

if __name__ == "__main__":
    main()