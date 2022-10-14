from algosdk.future import transaction
from algosdk.atomic_transaction_composer import TransactionWithSigner
from pyteal import *
from beaker import consts
from beaker.sandbox import get_accounts, get_algod_client
from beaker.client import ApplicationClient
from beaker.client.logic_error import LogicException
import time
from asset_auction import Auction
from util import *
import test_auction


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

# get sandbox client
client = get_algod_client()


##startTime = int(time()) + 10            # start time is 10 seconds in the future


# Auction settings
offset = 10                             # start time is 10 seconds in the future
length = 120                             # auction duration
##commitTime = startTime + 10
##endTime = start_offset + duration       # end time is 60 seconds after start
reserve = 1*consts.algo                 # 1 Algo
##increment = 100000                      # 0.1 Algo
#deposit = 100000                        # 0.1 Algo

# Create an Application client containing both an algod client and my app
app_client = ApplicationClient(client, Auction(), signer = owner_sign)


def demo():

    # Transaction parameters
    tx_params = client.suggested_params()
#    tx_params.first =
#    tx_params.last =
#    tx_params.gh = "wGHE2Pwdvd7S12BL5FaOP20EGYesN73ktiC1qzkkit8="         #TO BE VALIDATED ONCE ON release NETWORK (MainNet)
#    tx_params.flat_fee = True
#    tx_params.fee = 1*consts.milli_algo                                    # minimum fee on Algorand is currently 1000 microAlgos
    tx_params.fee = MIN_FEE
#    tx_params.min_fee   
    
    ##############
    # APP CREATION
    ##############

    # Create the applicatiion on chain, set the app id for the app client
    print("\nCREATING AND DEPLOYING THE SMART CONTRACT...")
    try:
        app_id, app_addr, txid = app_client.create()

    except LogicException as e:
        print(f"\n{e}\n")

    print(f"Created App with id: {app_id} and address: {app_addr} in tx: {txid}\n")
    print(f"Current app state: {app_client.get_application_state()}")


    ##############
    # NFT CREATION
    ##############

    nft = create_asset(owner_addr, owner_sk, "dummyNFT")

    # Check if the accounts hold the asset, otherwise opt-in
    # optInToAsset(client, owner_addr, owner_sk, nft)
    optInToAsset(client, addr2, sk2, nft)
    optInToAsset(client, addr3, sk3, nft)

    ##############
    # START AUCTION
    ##############

    print("\n\n\n--------------------------------------------------------------------------------")
    print("Bob is creating an auction that lasts 60 seconds to auction off the NFT...")
    print("--------------------------------------------------------------------------------")
    print("\nSetup the Auction application......")
    
    sp = client.suggested_params()
    ptxn = TransactionWithSigner(
        txn=transaction.PaymentTxn(owner_addr, sp, app_addr, 1*consts.algo), signer=owner_sign
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
    
    txn=transaction.AssetTransferTxn(owner_addr, sp, app_addr, 1, nft)
    signed_txn = txn.sign(owner_sk)

    try:
        txid = client.send_transaction(signed_txn)
        if txid: print("\nNFT TRANSFERRED TO SMART CONTRACT\n")
    except Exception as err:
        print(err)

    
    ##############
    # START BIDDING - USER 2
    ##############

    print("\nSTART BIDDING: USER 2\n")

    bidder_client = app_client.prepare(signer2)
    tx1 = TransactionWithSigner(
        txn = transaction.PaymentTxn(addr2, tx_params, app_addr, 2*consts.algo), signer = signer2
    )


    try:
        result = bidder_client.call(
        Auction.bid,
        payment = tx1,
        previous_bidder = owner_addr
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
    # START BIDDING - USER 3
    ##############

    print("START BIDDING: USER 3")

    # Execute bidding
    bidder_client_2 = app_client.prepare(signer3)
    tx2 = TransactionWithSigner(
        txn = transaction.PaymentTxn(addr3, tx_params, app_addr, 3*consts.algo), signer = signer3
    )
    try:
        result = bidder_client_2.call(
            Auction.bid,
            payment = tx2,
            previous_bidder = addr2
        )
    except LogicException as e:
        print(f"\n{e}\n")

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
        txn = transaction.PaymentTxn(addr2, tx_params, app_addr, 4*consts.algo), signer = signer2
    )

    try:
        result = bidder_client.call(
        Auction.bid,
        payment = tx1,
        previous_bidder = addr3
        )
    except LogicException as e:
        print(f"\n{e}\n")

    print(f"Current app state: {app_client.get_application_state()}\n")
    print(f"Current app address info: {app_client.get_application_account_info()}\n")
    print(f"Current address info: {app_client.get_account_state()}\n")
    print_balances(app_addr, owner_addr, addr2, addr3)

    ##############
    # RE-BID - USER 3
    ##############

    print("RE-BID: USER 3")

    # Execute bidding
    bidder_client_2 = app_client.prepare(signer3)
    tx2 = TransactionWithSigner(
        txn = transaction.PaymentTxn(addr3, tx_params, app_addr, 5*consts.algo), signer = signer3
    )
    try:
        result = bidder_client_2.call(
            Auction.bid,
            payment = tx2,
            previous_bidder = addr2
        )
    except LogicException as e:
        print(f"\n{e}\n")

    print(f"Current app state: {app_client.get_application_state()}\n")
    print(f"Current app address info: {app_client.get_application_account_info()}\n")
    print(f"Current address info: {app_client.get_account_state()}\n")
    print_balances(app_addr, owner_addr, addr2, addr3)


    ##############
    # END AUCTION
    ##############

    print("CLOSING AUCTION BY THE GOVERNOR...")
    time.sleep(5)
    try:
        result = app_client.call(
            Auction.end_auction,
            highest_bidder = addr3,
            nft=nft
        )
    except LogicException as e:
        print(f"\n{e}\n")

    print(f"Current app state: {app_client.get_application_state()}\n")
    print(f"Current app address info: {app_client.get_application_account_info()}\n")
#    print(f"Current address info: {app_client.get_account_state()}\n")
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
    create_txn = transaction.AssetCreateTxn(
        addr, sp, 1, 0, False, asset_name="dummyNFT", unit_name=unitname
    )
    # Ship it
    txid = client.send_transaction(create_txn.sign(pk))
    # Wait for the result so we can return the app id
    result = transaction.wait_for_confirmation(client, txid, 4)
    return result["asset-index"]

if __name__ == "__main__":
#    test_auction
    demo()
    