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
#import test_auction


MIN_FEE = 1000                                              # minimum fee on Algorand is currently 1000 microAlgos


# Take accounts from sandbox
accts = get_accounts()
print(f"\nNumber of accounts derived from sandbox:", len(accts))
acct1 = accts.pop()                                         # smart contract creator (derived from sandbox accounts)
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
length = 120                             # auction duration


# get sandbox client
client = get_algod_client()

# Create an Application client containing both an algod client and my app
app_client = ApplicationClient(client, Auction(), signer = owner_sign)


def demo():

    # Transaction parameters
    tx_params = client.suggested_params()
#    tx_params.first =
#    tx_params.last =
#    tx_params.gh = "wGHE2Pwdvd7S12BL5FaOP20EGYesN73ktiC1qzkkit8="          #TO BE VALIDATED ONCE ON TestNet NETWORK
#    tx_params.flat_fee = True
    tx_params.fee = MIN_FEE                                                 # minimum fee on Algorand is currently 1000 microAlgos
#    tx_params.min_fee = MIN_FEE
    
    
    print("\n\n**********************************")
    print("SMART CONTRACT CREATION AND DEPLOYMENT")
    print("**********************************\n")

    # Create the applicatiion on chain, set the app id for the app client
    try:
        app_id, app_addr, txid = app_client.create()

    except LogicException as e:
        print(f"\n{e}\n")

    print(f"Created App with id: {app_id} and address: {app_addr} in tx: {txid}")
    print(f"\nCurrent app state: {app_client.get_application_state()}")
    print_balances(client, app_addr, owner_addr, addr2, addr3)
        

    print("\n**********************************")
    print("NFT CREATION")
    print("**********************************\n")

    nft = create_asset(client, owner_addr, owner_sk, "dummyNFT")
    print_created_asset(client, owner_addr, nft)
    print_asset_holding(client, owner_addr, nft)
    print_balances(client, app_addr, owner_addr, addr2, addr3)


    print("\n\n--------------------------------------------------------------------------------")
    print("Bob is creating an auction that lasts 2 minutes to sell the NFT...")
    print("--------------------------------------------------------------------------------\n\n")


    print("\n**********************************")
    print("AUCTION SETUP")
    print("**********************************\n")

    ptxn = TransactionWithSigner(
        txn=transaction.PaymentTxn(owner_addr, tx_params, app_addr, 1*consts.algo), signer = owner_sign
    )

    try:
        result = app_client.call(
            Auction.setup,
            payment = ptxn,
            starting_price = 1*consts.algo,
            nft = nft,
            start_offset = offset,
            duration = length,
            note= "START_AUCTION".encode()
        )

    except LogicException as e:
        print(f"\n{e}\n")

    # for res in result.tx_ids:
    #    print(res)    

    print(f"Current app state: {app_client.get_application_state()}")
    print_balances(client, app_addr, owner_addr, addr2, addr3)


    print("\n**********************************")
    print("NFT TRANSFER TO THE SMART CONTRACT...")
    print("**********************************\n")
    
    txn = transaction.AssetTransferTxn(owner_addr, tx_params, app_addr, 1, nft)
    signed_txn = txn.sign(owner_sk)

    try:
        txid = client.send_transaction(signed_txn)
        if txid: print("NFT TRANSFERRED TO SMART CONTRACT")

    except LogicException as e:
        print(f"\n{e}\n")

    # for res in result.tx_ids:
    #    print(res)

    print_asset_holding(client, app_addr, nft)
    print_balances(client, app_addr, owner_addr, addr2, addr3)

    
    print("\n**********************************")
    print("BID: USER 2")
    print("**********************************\n")

    # Execute bidding
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

    # for res in result.tx_ids:
    #    print(res)            
    
    print(f"Current app state: {app_client.get_application_state()}\n")
    print(f"Current app address info: {app_client.get_application_account_info()}")
    print_balances(client, app_addr, owner_addr, addr2, addr3)


    print("\n**********************************")
    print("BID: USER 3")
    print("**********************************\n")

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

    # for res in result.tx_ids:
    #    print(res)          

    print(f"Current app state: {app_client.get_application_state()}\n")
    print(f"Current app address info: {app_client.get_application_account_info()}")
    #print(f"Current address info: {bidder_client_2.get_account_state()}\n")
    print_balances(client, app_addr, owner_addr, addr2, addr3)


    print("\n**********************************")
    print("RE-BID: USER 2")
    print("**********************************\n")

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

    # for res in result.tx_ids:
    #    print(res)          

    print(f"Current app state: {app_client.get_application_state()}\n")
    print(f"Current app address info: {app_client.get_application_account_info()}")
    #print(f"Current address info: {bidder_client.get_account_state()}\n")
    print_balances(client, app_addr, owner_addr, addr2, addr3)


    print("\n**********************************")
    print("RE-BID: USER 3")
    print("**********************************\n")

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

    # for res in result.tx_ids:
    #    print(res)               

    print(f"Current app state: {app_client.get_application_state()}\n")
    print(f"Current app address info: {app_client.get_application_account_info()}")
    #print(f"Current address info: {bidder_client_2.get_account_state()}\n")
    print_balances(client, app_addr, owner_addr, addr2, addr3)


    print("\n**********************************")
    print("END AUCTION.")
    print("**********************************\n")

    print("Winning address:", addr3)

    # Check if the winning account hold the asset, otherwise opt-in
    optInToAsset(client, addr3, sk3, nft)

    time.sleep(10)

    try:
        result = app_client.call(
            Auction.end_auction,
            highest_bidder = addr3,
            nft = nft,
            note="END_AUCTION".encode()
        )

    except LogicException as e:
        print(f"\n{e}\n")

    # for res in result.tx_ids:
    #    print(res)         

    print(f"\nCurrent app state: {app_client.get_application_state()}\n")
    print(f"Current app address info: {app_client.get_application_account_info()}")
    print_asset_holding(client, addr3, nft)
    #print(f"Current address info: {app_client.get_account_state()}\n")
    print_balances(client, app_addr, owner_addr, addr2, addr3)




if __name__ == "__main__":
#    test_auction
    demo()
    