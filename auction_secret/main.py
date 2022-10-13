from hashlib import sha256
from algosdk.future import transaction
from algosdk.atomic_transaction_composer import (
    AtomicTransactionComposer,
    TransactionWithSigner,
)
from algosdk import account, mnemonic
from algosdk.encoding import decode_address
from pyteal import *
from beaker import consts
from beaker.sandbox import get_accounts, get_algod_client
from beaker.client import ApplicationClient
from beaker.client.logic_error import LogicException
import beaker.testing
import time
from auction_secret import SecretAuction
import test_auction_secret


MIN_FEE = 1000                                              # minimum fee on Algorand is currently 1000 microAlgos


# Take accounts from sandbox
accts = get_accounts()
print(f"\nNumber of accounts derived from sandbox:", len(accts))
acct1 = accts.pop()                                         #smart contract creator (derived from sandbox accounts)
addr1, sk1, signer1 = acct1.address, acct1.private_key, acct1.signer
print("\nAccount n.1:", addr1)
print("Address Secret key =", sk1)
acct2 = accts.pop()                                         # 1st user account (derived from sandbox accounts)
addr2, sk2, signer2 = acct2.address, acct2.private_key, acct2.signer
print("\nAccount n.2:", addr2)
print("Address Secret key =", sk2)
acct3 = accts.pop()                                         # 2st user account (derived from sandbox accounts)
addr3, sk3, signer3 = acct3.address, acct3.private_key, acct3.signer
print("\nAccount n.3:", addr3)
print("Address Secret key =", sk3)

# Generate standalone account
sk4, addr4 = account.generate_account()
#print("Account n.4: {}".format(addr4))
print("\nAccount n.3:", addr4)
#print("Address Secret key = {}".format(mnemonic.from_private_key(sk4)))
print("Address Secret key =", sk4)

# get sandbox client
client = get_algod_client()

# Check account balances
#balances = beaker.testing.get_balances(client, accts)       # PRINT dict! HA SENSO FARE QUESTO TESTING QUA SE POI GIRANO GLI ALTRI TEST?
#print(balances.items())
#for key,value in balances.items():
#	print(key, ':', value)

# Create an Application client containing both an algod client and my app
app_client = ApplicationClient(client, SecretAuction(), signer = signer1)


def demo():

    # Transaction parameters
    sp = client.suggested_params()
#    sp.first =
#    sp.last =
#    sp.gh = "wGHE2Pwdvd7S12BL5FaOP20EGYesN73ktiC1qzkkit8="         #TO BE VALIDATED ONCE ON release NETWORK (MainNet)
#    sp.flat_fee = True
    sp.fee = 1*consts.milli_algo                                    # minimum fee on Algorand is currently 1000 microAlgos
#    sp.fee = MIN_FEE = 1000

    ##############
    # APP CREATION
    ##############

    # Create the applicatiion on chain, set the app id for the app client
    print("\nCREATING AND DEPLOYING THE SMART CONTRACT...")
    app_id, app_addr, txid = app_client.create()
    print(f"Created App with id: {app_id} and address: {app_addr} in tx: {txid}\n")


    ##############
    # START SECRET AUCTION
    ##############

    print("STARTING AUCTION BY THE GOVERNOR...")

    # Start auction by the governor (WITH TRANSACTION BY SMART CONTRACT CREATOR ADDRESS)
    tx = TransactionWithSigner(
        txn = transaction.PaymentTxn(addr1, sp, app_addr, 1*consts.algo), signer = signer1
#        txn = transaction.PaymentTxn(addr1, sp, app_addr, 1*consts.algo, None, None, None, None), signer = signer1
    )
    try:
        result = app_client.call(
            SecretAuction.start_auction,
            payment = tx,
            starting_price = 1*consts.algo,
#            starting_price = tx.txn.Balance,
#            starting_price = tx.txn.sender["amount"],
            duration = 60
        )

    # Start auction by the governor (NO TRANSACTION BY SMART CONTRACT CREATOR ADDRESS)
    # Fund the app account with 1 algo              #CARICATI ALGO SULLO SMART CONTRACT, MA DA CHI?     <<<---
#   app_client.fund(1*consts.algo)                          

#    try:
#        result = app_client.call(
#            Auction.start_auction,
#            starting_price = 1*consts.algo,
#            starting_price = app_client.client.account_info(app_client.app_addr)["amount"],
#            duration = 60
#        )

    except LogicException as e:
        print(f"\n{e}\n")
    
    print(f"Current app state: {app_client.get_application_state()}\n")
    print_balances(app_addr, addr1, addr2, addr3, addr4)


    ##############
    # START BIDDING - 1st USER WITH SECRET
    ##############

    print("START BIDDING: FIRST USER")

    # Execute bidding
    bidder_client = app_client.prepare(signer2)
    secret1 = sha256("Bianconiglio")
    print(secret1)
#    tx1 = TransactionWithSigner(
#        txn = transaction.PaymentTxn(addr2, sp, app_addr, 2*consts.algo), signer = signer2
#        txn = transaction.PaymentTxn(addr2, sp, app_addr, 2*consts.algo, None, None, None, None), signer = signer2
#    )
#    try:
#        result = bidder_client.call(
#            Auction.bid,
#            payment = tx1,
#            previous_bidder = addr1                 # CHECK: NON SETTARE AUTOMATICAMENTE addr1 (SE PUNTATE INFERIORI, NELLA SEQUENZIALITA' RIMANE SEMPRE L'addr DI QUELLO INIZIALE)
#            previous_bidder = bytes.fromhex(app_client.get_application_state()["highest_bidder"])
#        )

#    except LogicException as e:
#        print(f"\n{e}\n")

#    print(f"Current app state: {app_client.get_application_state()}\n")
#    print_balances(app_addr, addr1, addr2, addr3)


    ##############
    # START BIDDING - 2nd USER
    ##############

#    print("START BIDDING: SECOND USER")

    # Execute bidding
#    bidder_client_2 = app_client.prepare(signer3)
#    tx2 = TransactionWithSigner(
#        txn = transaction.PaymentTxn(addr3, sp, app_addr, 3*consts.algo), signer = signer3
#        txn = transaction.PaymentTxn(addr3, sp, app_addr, 3*consts.algo, None, None, None, None), signer = signer3        
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

#    print(f"Current app state: {app_client.get_application_state()}\n")
#    print_balances(app_addr, addr1, addr2, addr3)


    ##############
    # END AUCTION
    ##############

#    print("CLOSING AUCTION BY THE GOVERNOR...")
#    time.sleep(60)

#    try:                                            #PAYMENT INTERNO CON LOGIC SIG?
#        result = app_client.call(
#            Auction.end_auction
#        )

#    except LogicException as e:
#        print(f"\n{e}\n")

#    print(f"Current app state: {app_client.get_application_state()}\n")
#    print_balances(app_addr, addr1, addr2, addr3)
    

#    print("\nDELETING APPLICATION...")
#    print(f"\nApp id: {app_id}\tApp address: {app_addr}\n")
#    app_balance = client.account_info(app_addr["amount"])
#    try:
#        app_id, app_addr, txid = app_client.delete(app_balance)
#
#    except LogicException as e:
#        print(f"\n{e}\n")
#
#    print(f"\nApp id: {app_id}\tApp address: {app_addr}\n")



    ##############################################################
    #call(method: Union[Method, Callable[[...], Expr]],                     #ESPLORA ALTRI METODI CALL      <<<---
    #     sender: Optional[str] = None,
    #     signer: Optional[TransactionSigner] = None,
    #     suggested_params: Optional[SuggestedParams] = None,
    #     on_complete: OnComplete = OnComplete.NoOpOC,
    #     local_schema: Optional[StateSchema] = None,
    #     global_schema: Optional[StateSchema] = None,
    #     approval_program: Optional[bytes] = None,
    #     clear_program: Optional[bytes] = None,
    #     extra_pages: Optional[int] = None,
    #     accounts: Optional[list[str]] = None,
    #     foreign_apps: Optional[list[int]] = None,
    #     foreign_assets: Optional[list[int]] = None,
    #     note: Optional[bytes] = None,
    #     lease: Optional[bytes] = None,
    #     rekey_to: Optional[str] = None, **kwargs)→ ABIResult
    ##############################################################



def print_balances(app: str, addr1: str, addr2: str, addr3: str, addr4: str):           #SPECIFICARE CON abi?       <<<---

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

    addrbal4 = client.account_info(addr4)
    print("Participant:", addr4, end = "")
    print("\tAddress Balance = {}\n".format(addrbal4["amount"]))



if __name__ == "__main__":
#    test_auction_secret
    demo()
