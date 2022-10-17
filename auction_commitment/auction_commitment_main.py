from algosdk.future import transaction
from algosdk.atomic_transaction_composer import TransactionWithSigner, AtomicTransactionComposer
from pyteal import *
from beaker import consts
from beaker.sandbox import get_accounts, get_algod_client
from beaker.client import ApplicationClient
from beaker.client.logic_error import LogicException
import time
from auction_commitment_contract import Auction
from util import *
from hashlib import sha256
#import test_auction_commitment


MIN_FEE = 1000                                              # minimum fee on Algorand is currently 1000 microAlgos


# Take accounts from sandbox
accts = get_accounts()
print(f"\nNumber of accounts derived from sandbox:", len(accts))
acct1 = accts.pop()                                         #smart contract creator (derived from sandbox accounts)
owner_addr, owner_sk, owner_sign = acct1.address, acct1.private_key, acct1.signer
print("\nAccount n.1:", owner_addr)
print("Address Secret key =", owner_sk)
acct2 = accts.pop()                                         # 1st user account (derived from sandbox accounts)
addr2, sk2, signer2 = acct2.address, acct2.private_key, acct2.signer
print("\nAccount n.2:", addr2)
print("Address Secret key =", sk2)
acct3 = accts.pop()                                         # 2st user account (derived from sandbox accounts)
addr3, sk3, signer3 = acct3.address, acct3.private_key, acct3.signer
print("\nAccount n.3:", addr3)
print("Address Secret key =", sk3)


# Auction settings
offset = 10                             # start time is 10 seconds in the future
commitment_length = 100                 # commitment duration
auction_length = 160                    # auction duration
reserve = 1*consts.algo                 # 1 Algo
#increment = 100000                      # 0.1 Algo
#deposit = 100000                        # 0.1 Algo (minimum balance)                #CHECK (POCO?)  <<<---


# get sandbox client
client = get_algod_client()

# Create an Application client containing both an algod client and my app
app_client = ApplicationClient(client, Auction(), signer = owner_sign)


def demo():

    # Transaction parameters
    tx_params = client.suggested_params()
#    tx_params.first =
#    tx_params.last =
#    tx_params.gh = "wGHE2Pwdvd7S12BL5FaOP20EGYesN73ktiC1qzkkit8="         #TO BE VALIDATED ONCE ON TestNet NETWORK
#    tx_params.flat_fee = True
#    tx_params.fee = MIN_FEE
#    tx_params.min_fee = MIN_FEE

    
    print("\n**********************************")
    print("NFT CREATION")
    print("**********************************\n")

    nft = create_asset(client, owner_addr, owner_sk, "dummyNFT")
    print_created_asset(client, owner_addr, nft)
    print_asset_holding(client, owner_addr, nft)
    print_balances(client, app_addr, owner_addr, addr2, addr3)


    print("\n\n**********************************")
    print("SMART CONTRACT CREATION AND DEPLOYMENT")
    print("**********************************\n")

    # Create the applicatiion on chain, set the app id for the app client
    try:
        app_id, app_addr, txid = app_client.create()

    except LogicException as e:
        print(f"\n{e}\n")

    print(f"Created App with id: {app_id} and address: {app_addr} in tx: {txid}\n")
    print(f"Current app state: {app_client.get_application_state()}")
    print_balances(client, app_addr, owner_addr, addr2, addr3)


    # Fund the app account with 1 algo (by the owner)
    app_client.fund(1*consts.algo)
    print_balances(app_addr, owner_addr, addr2, addr3)


    # Check if the accounts hold the asset, otherwise opt-in
    # optInToAsset(client, owner_addr, owner_sk, nft)
    # optInToAsset(client, addr2, sk2, nft)
    optInToAsset(client, addr3, sk3, nft)


    ##############
    # NFT OPT-IN FOR THE CONTRACT
    ##############


    try:
        result = app_client.call(
            Auction.nft_opt_in,
            nft = nft
        )

    except LogicException as e:
        print(f"\n{e}\n")

    print_balances(app_addr, owner_addr, addr2, addr3)
   

    ##############
    # START AUCTION
    ##############

    print("\n\n\n--------------------------------------------------------------------------------")
    print("Bob is creating an auction that lasts 60 seconds to auction off the NFT...")
    print("--------------------------------------------------------------------------------")
    print("\nSetup the Auction application......")
    
    print_balances(app_addr, owner_addr, addr2, addr3)

    sp = client.suggested_params()
    """
    ptxn = TransactionWithSigner(
        txn = transaction.PaymentTxn(owner_addr, tx_params, app_addr, 1*consts.algo), signer = owner_sign
    )
    """
    atxn = TransactionWithSigner(
      txn = transaction.AssetTransferTxn(owner_addr, tx_params, app_addr, 1, nft), signer=owner_sign
    )

    try:
        result = app_client.call(
            Auction.setup,
            #payment=ptxn,
            asset=atxn,
            starting_price = 1*consts.algo,
            nft = nft,
            start_offset = offset,
            duration = length,
            commit_duration = commitment_length,
            deposit = 1*consts.algo
        )

    except LogicException as e:
        print(f"\n{e}\n")

    print(f"Current app state: {app_client.get_application_state()}\n")
    print_balances(app_addr, owner_addr, addr2, addr3)


    ##############
    # COMMITTING - USER 2
    ##############

    print("\nCOMMITTING: USER 2\n")

    bidder_client = app_client.prepare(signer2)

    # Enable the smart contract to add a commitment field into user account                 CHECK       <<<---
    bidder_client.opt_in()

    tx1 = TransactionWithSigner(
        txn = transaction.PaymentTxn(addr2, tx_params, app_addr, 1*consts.algo), signer = signer2
    )

    value = 3*consts.algo

    # Hashing the bid value
    commitment = bytes(bytearray.fromhex(sha256(value.to_bytes(8, 'big')).hexdigest()))

    try:
        result = bidder_client.call(
        Auction.commit,
        k = 1,
        commitment = commitment,
        payment = tx1,
        nft = nft,
        #on_complete=transaction.OnComplete.OptInOC
    )
    except LogicException as e:
        print(f"\n{e}\n")

    # for res in result.tx_ids:
    #    print(res)

    print(f"Current app state: {app_client.get_application_state()}")
    print(f"Current account state: {bidder_client.get_account_state()}")


    ##############
    # COMMITTING - USER 3
    ##############

    print("\nCOMMITTING: USER 3\n")

    bidder_client2 = app_client.prepare(signer3)
    
    # Enable the smart contract to add a commitment field into user account                 CHECK       <<<---
    bidder_client2.opt_in()

    tx1 = TransactionWithSigner(
        txn = transaction.PaymentTxn(addr3, tx_params, app_addr, 1*consts.algo), signer = signer3
    )

    value = 4*consts.algo

    # Hashing the bid value
    commitment = bytes(bytearray.fromhex(sha256(value.to_bytes(8, 'big')).hexdigest()))

    try:
        result = bidder_client2.call(
        Auction.commit,
        k = 1,
        commitment = commitment,
        payment=tx1,
        nft=nft,
        #on_complete=transaction.OnComplete.OptInOC
    )
    except LogicException as e:
        print(f"\n{e}\n")

    # for res in result.tx_ids:
    #    print(res)

    print(f"Current app state: {app_client.get_application_state()}")
    print(f"Current account state: {bidder_client2.get_account_state()}")
    
    ##############
    # START BIDDING - USER 3
    ##############

    print("\nSTART BIDDING: USER 3\n")

    bidder_client = app_client.prepare(signer3)
    tx1 = TransactionWithSigner(
        txn = transaction.PaymentTxn(addr3, tx_params, app_addr, 4*consts.algo), signer = signer3
    )

    try:
        result = bidder_client.call(
        Auction.bid,
        payment = tx1,
        highest_bidder = owner_addr,
        old_k = 1,
        new_k = 2
    )
    except LogicException as e:
        print(f"\n{e}\n")
    
    # for res in result.tx_ids:
    #    print(res)    

    # print("Global state:", read_global_state(client, app_id))
    print(f"Current app state: {app_client.get_application_state()}")

    
    ##############
    # START BIDDING - USER 2
    ##############

    print("\nSTART BIDDING: USER 2\n")

    bidder_client = app_client.prepare(signer2)
    tx1 = TransactionWithSigner(
        txn = transaction.PaymentTxn(addr2, tx_params, app_addr, 3*consts.algo), signer = signer2
    )

    print(f"Current app state: {app_client.get_application_state()}\n")
    print(f"Current app address info: {app_client.get_application_account_info()}\n")
    print(f"Current address info: {app_client.get_account_state()}\n")
    print_balances(app_addr, owner_addr, addr2, addr3)

    ##############
    # RE-BID - USER 2
    ##############

    print("RE-BID: USER 2")

    # Execute bidding

    tx1 = TransactionWithSigner(
        txn = transaction.PaymentTxn(addr2, tx_params, app_addr, 3*consts.algo), signer = signer2
    )


    try:
        result = bidder_client.call(
        Auction.bid,
        payment = tx1,
        highest_bidder = addr3,
        old_k = 1,
        new_k = 2
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
    print_balances(app_addr, owner_addr, addr2, addr3)

    ##############
    # END AUCTION
    ##############

    print("CLOSING AUCTION BY THE GOVERNOR...")
    time.sleep(15)
    try:
        result = app_client.call(
            Auction.end_auction,
            highest_bidder = addr3,
            nft=nft
        )
    except LogicException as e:
        print(f"\n{e}\n")

    # for res in result.tx_ids:
    #    print(res)        

    print(f"Current app state: {app_client.get_application_state()}\n")
    print(f"Current app address info: {app_client.get_application_account_info()}\n")
    print(f"Current address info: {app_client.get_account_state()}\n")
    print_balances(app_addr, owner_addr, addr2, addr3)



def print_balances(app: str, addr1: str, addr2: str, addr3: str):

    appbal = client.account_info(app)
    print("App Balance = {}\n".format(appbal["amount"]))

    addrbal1 = client.account_info(addr1)
    print("Participant:", addr1, end = "")
    print("\tAddress Balance = {}\n".format(addrbal1["amount"]))

    addrbal2 = client.account_info(addr2)
    print("Participant:", addr2, end = "")
    print("\tAddress Balance = {}\n".format(addrbal2["amount"]))

    addrbal3 = client.account_info(addr3)
    print("Participant:", addr3, end = "")
    print("\tAddress Balance = {}\n".format(addrbal3["amount"]))


def create_asset(addr, pk, unitname):
    # Get suggested params from network
    sp = client.suggested_params()

    # Create the transaction
    create_txn = transaction.AssetCreateTxn(                                            #CHECK MISSING FIELDS TO BE SET     <<<---
        addr, sp, 1, 0, False, asset_name = "dummyNFT", unit_name = unitname
    )

    # Ship it
    txid = client.send_transaction(create_txn.sign(pk))

    # Wait for the result so we can return the app id
    result = transaction.wait_for_confirmation(client, txid, 4)
    return result["asset-index"]



if __name__ == "__main__":
#    test_auction_commitment
    demo()
    