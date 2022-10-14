
#############################
# IMPLEMENTAZIONE ZECCHINI
#############################

import base64
from time import time, sleep
from hashlib import sha256
from auction_secret_2 import *
from algosdk.atomic_transaction_composer import (
    AtomicTransactionComposer,
    TransactionWithSigner
)
from algosdk.logic import get_application_address
from algosdk.future import transaction
from algosdk import account, mnemonic
from pyteal import *
from beaker import consts
from beaker import *
from beaker.sandbox import get_accounts, get_algod_client
from beaker.client import ApplicationClient
from beaker.client.logic_error import LogicException
from algosdk.v2client import algod
from util import *
from algosdk.abi import Contract, Method
from algosdk.logic import get_application_address


MIN_FEE = 1000                                              # minimum fee on Algorand is currently 1000 microAlgos

# user declared account mnemonics
creator_mnemonic = "employ spot view century canyon fossil upon hollow tone chicken behave bamboo cool correct vehicle mirror movie scrap budget join music then poverty ability gadget"



#def closeAuction(
#        client: algod.AlgodClient,
#        app_id: int,
#        closer: str,
#):
#    global_state = read_global_state(client, app_id)
#
#    nft_id = global_state['nft_id']
#
#    accounts: List[str] = [encoding.encode_address(global_state["seller"])]
#
#    if any(global_state["bid_account"]):
#        # if "bid_account" is not the zero address
#        accounts.append(encoding.encode_address(global_state["bid_account"]))
#
#
#    deleteTxn = transaction.ApplicationDeleteTxn(
#        sender=account.address_from_private_key(closer),
#        index=app_id,
#        accounts=accounts,
#        foreign_assets=[nft_id],
#        sp=client.suggested_params(),
#    )
#    signedDeleteTxn = deleteTxn.sign(closer)
#
#    client.send_transaction(signedDeleteTxn)
#    transaction.wait_for_confirmation(client, signedDeleteTxn.get_txid())
#    print(signedDeleteTxn.get_txid())


#def placeBid(
#        client: algod.AlgodClient,
#        app_id: int,
#        bidder_sk: str,
#        bid_amount: int
#) -> None:
#    app_addr = get_application_address(app_id)

#    suggestedParams = client.suggested_params()
#    global_state = read_global_state(client, app_id)
#    nft_id = global_state['nft_id']

#    if any(global_state["bid_account"]):
#        # if "bid_account" is not the zero address
#        prevBidLeader = global_state["bid_account"]
#    else:
#        prevBidLeader = None

#    atc = AtomicTransactionComposer()
#    bidder_addr = account.address_from_private_key(bidder_sk)
#    bidder_signer = AccountTransactionSigner(bidder_sk)

#    ptxn = transaction.PaymentTxn(bidder_addr, suggestedParams, app_addr, bid_amount)
#    tws = TransactionWithSigner(ptxn, bidder_signer)
#    atc.add_transaction(tws)

#    with open("./com_auction_contract.json") as f:
#        js = f.read()
#    if prevBidLeader == None:
#        atc.add_method_call(app_id=app_id,
#                            method=get_method('on_bid', js),
#                            sender=bidder_addr,
#                            sp=suggestedParams,
#                            signer=bidder_signer,
#                            foreign_assets=[nft_id],
#                            )
#    else:
#        atc.add_method_call(app_id=app_id,
#                            method=get_method('on_bid', js),
#                            sender=bidder_addr,
#                            sp=suggestedParams,
#                            signer=bidder_signer,
#                            foreign_assets=[nft_id],
#                            accounts=[prevBidLeader]
#                            )
#    result = atc.execute(client, 10)
#
#    print("Global state:", read_global_state(client, app_id))
#    print("Local state:", read_local_state(client, bidder_addr, app_id))






owner_sk = get_private_key_from_mnemonic(creator_mnemonic)
owner_addr = account.address_from_private_key(owner_sk)
print(owner_addr)

# get sandbox client
client = get_algod_client()

# Take accounts from sandbox                                # GENERATE ARRAY OF BIDDERS
accts = get_accounts()
print(f"\nNumber of accounts derived from sandbox:", len(accts))
acct1 = accts.pop()                                         #1st bidder (derived from sandbox accounts)
addr1, sk1, signer1 = acct1.address, acct1.private_key, acct1.signer
print("\nAccount n.1:", addr1)
print("Address Secret key =", sk1)
acct2 = accts.pop()                                         # 2nd bidder (derived from sandbox accounts)
addr2, sk2, signer2 = acct2.address, acct2.private_key, acct2.signer
print("\nAccount n.2:", addr2)
print("Address Secret key =", sk2)
acct3 = accts.pop()                                         # 3rd bidder (derived from sandbox accounts)
addr3, sk3, signer3 = acct3.address, acct3.private_key, acct3.signer
print("\nAccount n.3:", addr3)
print("Address Secret key =", sk3)

# NFT auction settings
nftAmount = 1
nftID = createDummyAsset(client, nftAmount, owner_addr, owner_sk)
print("\nThe NFT ID is", nftID)
startTime = int(time()) + 10            # start time is 10 seconds in the future
commitTime = startTime + 10
endTime = startTime + 30                # end time is 30 seconds after start
reserve = 1000000                       # 1 Algo
#increment = 100000                      # 0.1 Algo
deposit = 100000                        # 0.1 Algo

# Create an Application client containing both an algod client and my app
app_client = ApplicationClient(client, SecretAuction(), owner_sk)


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

    # Create the applicatiion on chain, set the app id for the app client
    print("\nCREATING AND DEPLOYING THE SMART CONTRACT...")
    app_id, app_addr, txid = app_client.create(startTime, commitTime, endTime)
    print(f"Created App with id: {app_id} and address: {app_addr} in tx: {txid}\n")

    print("Global state:", read_global_state(client, app_id))
    print("Local state:", read_local_state(client, owner_addr, app_id))

    # Fund the app account
    app_fund = 100000 + 100000 + 3*1000             # min account balance + additional min balance to opt into NFT + 3*min_txn_fee
    app_client.fund(app_fund)

    print("\nBob is creating an auction that lasts 30 seconds to auction off the NFT...")

    print("--------------------------------------------")
    print("Setup the Auction application......")

    # Transfer the asset into the smart contract
    txn = transaction.AssetTransferTxn(
        sender = owner_addr,
        sp = tx_params,
        receiver = app_addr,
        amt = 1,
        index = nftID,
#        close_assets_to = ,
#        revocation_target = ,
#        note = ,
#        lease = ,
#        rekey_to = ,
    )
    signedTxn = txn.sign(owner_sk)
    client.send_transaction(signedTxn)
    transaction.wait_for_confirmation(client, signedTxn.get_txid())

#    try:
#        result = app_client.call(
#            SecretAuction.setup,
#            payment = signedTxn,
#            nft_id = nftID,
#            start_T = startTime,
#            commit_T = commitTime,
#            end_T = endTime,
#            starting_price = reserve
#        )
    
#    except LogicException as e:
#        print(f"\n{e}\n")

#    for res in result.tx_ids:
#        print(res)


#    print("--------------------------------------------")
#    print("Committing to the Auction application......")

#    global_state = read_global_state(client, app_id)                        # <<<---
#    nft_id = global_state['nft_id']                                         # <<<---

##    atc = AtomicTransactionComposer()
#    tx = TransactionWithSigner(
##        txn = transaction.PaymentTxn(addr1, sp, app_addr, 1*consts.algo), signer = signer1
#        txn = transaction.PaymentTxn(addr1, tx_params, app_addr, deposit, None, None, None, None), signer = signer1
#    )
##    atc.add_transaction(tx)






#    commitment = bytes(bytearray.fromhex(sha256(reserve.to_bytes(8,'big')).hexdigest()))
#    app_args = [
#        commitment
#    ]
#    print(commitment)
#
#    atc.add_method_call(
#        app_id=app_id,
#        method=get_method("on_commit", js),
#        sender=account.address_from_private_key(bidder_sk),
#        sp=suggestedParams,
#        signer=bidder_signer,
#        method_args=app_args,
#        on_complete=transaction.OnComplete.OptInOC,
#        foreign_assets=[nft_id]
#    )

#    result = atc.execute(client, 10)
#    print(transaction.wait_for_confirmation(client, result.tx_ids[1]))
#    print("Local state:", read_local_state(client, bidder_addr, app_id))

#    try:
#        result = app_client.call(
#            SecretAuction.commit,
#            payment = signedTxn,
#            starting_price = 1*consts.algo,
#            duration = endTime - startTime
#        )
    
#    except LogicException as e:
#        print(f"\n{e}\n")

#    for res in result.tx_ids:
#        print(res)

#    sleep(10)

#    print("--------------------------------------------")
#    print("Bidding the Auction application......")
#    placeBid(client, app_id, bidder_sk, reserve)
#    optInToAsset(client, nftID, bidder_sk)

#    sleep(10)
#    print("--------------------------------------------")
#    print("Closing the Auction application......")

#    closeAuction(client, app_id, seller_sk)



if __name__ == "__main__":
    demo()