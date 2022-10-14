from re import A
from typing import get_args
from algosdk.future import transaction
from algosdk.atomic_transaction_composer import TransactionWithSigner
from pyteal import *
from beaker import consts
from beaker.sandbox import get_accounts, get_algod_client
from beaker.client import ApplicationClient
from beaker.client.logic_error import LogicException
import time
from auction_final import Auction
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

# NFT auction settings
#nftAmount = 1
#nftID = createDummyAsset(client, nftAmount, owner_addr, owner_sk)
##startTime = int(time()) + 10            # start time is 10 seconds in the future
offset = 10                             # start time is 10 seconds in the future
length = 60                             # auction duration
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

    # Check if the accounts hold the asset, otherwise opt-in
#    optInToAsset(client, owner_addr, owner_sk, nftID)
#    optInToAsset(client, addr2, sk2, nftID)
#    optInToAsset(client, addr3, sk3, nftID)

    
    ##############
    # APP CREATION
    ##############

    # Create the applicatiion on chain, set the app id for the app client
    print("\nCREATING AND DEPLOYING THE SMART CONTRACT...")
    try:
        app_id, app_addr, txid = app_client.create(
            start_offset = offset,
            duration = length,
        )

    except LogicException as e:
        print(f"\n{e}\n")

    print(f"Created App with id: {app_id} and address: {app_addr} in tx: {txid}\n")
    print("Global state:", read_global_state(client, app_id))
    #print("Local state:", read_local_state(client, owner_addr, app_id))


    ##############
    # START AUCTION
    ##############

    print("\n\n\n--------------------------------------------------------------------------------")
    print("Bob is creating an auction that lasts 60 seconds to auction off the NFT...")
    print("--------------------------------------------------------------------------------")
    print("\nSetup the Auction application......")

    # Start auction by the owner (MORE FEE PAYED)
#    tx = TransactionWithSigner(
##        txn = transaction.PaymentTxn(addr1, sp, app_addr, 1*consts.algo), signer = signer1
#        txn = transaction.PaymentTxn(addr1, sp, app_addr, 1*consts.algo, None, None, None, None), signer = signer1
#    )
#    try:
#        result = app_client.call(
#            Auction.start_auction,
#            payment = tx,
#            starting_price = 1*consts.algo,
##            starting_price = tx.txn,
#            duration = 60
#        )

    app_fund = 100000 + 100000 + 3*1000             # min account balance + additional min balance to opt into NFT + 3*min_txn_fee
    app_client.fund(app_fund)                       # with this command: LESS FEE PAYED

    # Transfer the asset into the smart contract
#    txn = transaction.AssetTransferTxn(
#        sender = owner_addr,
#        sp = tx_params,
#        receiver = app_addr,
#        amt = nftAmount,
#        index = nftID,
##        close_assets_to = ,
##        revocation_target = ,
##        note = ,
##        lease = ,
##        rekey_to = ,
#    )
#    signedTxn = txn.sign(owner_sk)

#    try:
##        result = app_client.call(
#        result = app_client.opt_in(
##            Auction.opt_in,
##            payment = signedTxn,
##            nft_id = nftID,
#        )
#        txid = client.send_transaction(signedTxn)
#        print("Signed transaction with txID: {}".format(txid))

        # Wait for the transaction to be confirmed
#        response = transaction.wait_for_confirmation(client, signedTxn.get_txid(), 4)
#        print("\nResponse:\n", response)                                                #CHECK: confirmed round != asset id <<<---
#        print("\nResult confirmed in round: {}".format(response['confirmed-round']))

#    except LogicException as e:
#        print(f"\n{e}\n")

#    for res in result.tx_ids:
#        print(res)




    try:
        result = app_client.call(
            Auction.setup,
#            payment = signedTxn,
#            nft_id = nftID,
#            start_T = startTime,
#            commit_T = commitTime,
#            end_T = endTime,
            starting_price = reserve
        )

    except LogicException as e:
        print(f"\n{e}\n")

#    for res in result.tx_ids:
#        print(res)
    
    print(f"\nCurrent app state: {app_client.get_application_state()}\n")
    print(f"Current app address info: {app_client.get_application_account_info()}\n")
#    print(f"Current address info: {app_client.get_account_state()}\n")
    print_balances(app_addr, owner_addr, addr2, addr3)

    ##############
    # START BIDDING - 1st USER
    ##############

    print("START BIDDING: FIRST USER")

    # Execute bidding
    global_state = read_global_state(client, app_id)
#    nft_id = global_state['nft_id']

    if any(global_state["bid_account"]):
        # if "bid_account" is not the zero address
        previous_bidder = global_state["bid_account"]
    else:
        previous_bidder = None

    bidder_client = app_client.prepare(signer2)
    tx1 = TransactionWithSigner(
        txn = transaction.PaymentTxn(addr2, tx_params, app_addr, 2*consts.algo), signer = signer2
#        txn = transaction.PaymentTxn(addr2, sp, app_addr, 2*consts.algo, None, None, None, None), signer = signer2
    )

    if previous_bidder == None:
        try:
            result = bidder_client.call(
            Auction.bid,
            payment = tx1,
            account = Global.zero_address()
#            previous_bidder = owner_addr
#            foreign_assets = [nft_id]
        )
        except LogicException as e:
            print(f"\n{e}\n")
    else:
        try:
            result = bidder_client.call(
            Auction.bid,
            payment = tx1,
            account = [previous_bidder]
#            foreign_assets = [nft_id]
        )
        except LogicException as e:
            print(f"\n{e}\n")

    print("Global state:", read_global_state(client, app_id))

#    for res in result.tx_ids:
#        print(res)

    print(f"Current app state: {app_client.get_application_state()}\n")
    print(f"Current app address info: {app_client.get_application_account_info()}\n")
#    print(f"Current address info: {app_client.get_account_state()}\n")
    print_balances(app_addr, owner_addr, addr2, addr3)


    ##############
    # START BIDDING - 2nd USER
    ##############

#    print("START BIDDING: SECOND USER")

    # Execute bidding
#    bidder_client_2 = app_client.prepare(signer3)
#    tx2 = TransactionWithSigner(
#        txn = transaction.PaymentTxn(addr3, tx_params, app_addr, 3*consts.algo), signer = signer3
##        txn = transaction.PaymentTxn(addr3, sp, app_addr, 3*consts.algo, None, None, None, None), signer = signer3        
#    )
#    try:
#        result = bidder_client_2.call(
#            Auction.bid,
#            payment = tx2,
#            previous_bidder = addr2                 # CHECK: NON SETTARE AUTOMATICAMENTE addr1 (SE PUNTATE INFERIORI, NELLA SEQUENZIALITA' RIMANE SEMPRE L'addr DI QUELLO INIZIALE)
                                                    # CHECK: POTREBBE ESSERE ANCORA addr1? PUNTATA PRECEDENTE INFERIORE -> RESPINTA? highest_bidder = addr1
#            previous_bidder = bytes.fromhex(app_client.get_application_state()["highest_bidder"])                                                    
#        )

#    except LogicException as e:
#        print(f"\n{e}\n")

#    for res in result.tx_ids:
#        print(res)

#    print(f"Current app state: {app_client.get_application_state()}\n")
#    print(f"Current app address info: {app_client.get_application_account_info()}\n")
#    print(f"Current address info: {app_client.get_account_state()}\n")
#    print_balances(app_addr, owner_addr, addr2, addr3)


    ##############
    # END AUCTION
    ##############

#    print("CLOSING AUCTION BY THE GOVERNOR...")
#    time.sleep(60)

#    try:
#        result = app_client.call(
#            Auction.end_auction
#        )

#    except LogicException as e:
#        print(f"\n{e}\n")

#    for res in result.tx_ids:
#        print(res)

#    print(f"Current app state: {app_client.get_application_state()}\n")
#    print(f"Current app address info: {app_client.get_application_account_info()}\n")
##    print(f"Current address info: {app_client.get_account_state()}\n")
#    print_balances(app_addr, owner_addr, addr2, addr3)
    

#    print("\nDELETING APPLICATION...")
#    print(f"\nApp id: {app_id}\tApp address: {app_addr}\n")
#    try:
#        result = app_client.delete(app_addr)
#
#    except LogicException as e:
#        print(f"\n{e}\n")
#
#    print(f"\nApp id: {app_id}\tApp address: {app_addr}\n")



    # Show application account information
#    print("application acct info:")
#    app_acct_info = json.dumps(app_client1.get_application_account_info(), indent=4)
#    print(app_acct_info)

#    try:
#        app_client1.close_out()
#        app_client1.delete()
#    except Exception as e:
#        print(e)




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



if __name__ == "__main__":
#    test_auction
    demo()
    