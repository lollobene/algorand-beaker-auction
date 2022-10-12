from algosdk.future import transaction
from algosdk.atomic_transaction_composer import (
    AtomicTransactionComposer,
    TransactionWithSigner,
)
#from algosdk.encoding import decode_address
from pyteal import *
from beaker import consts
from beaker.sandbox import get_accounts, get_algod_client
from beaker.client import ApplicationClient
from beaker.client.logic_error import LogicException
import beaker.testing
import time

from auction import Auction
import test_auction


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

# get sandbox client
client = get_algod_client()

# Check account balances
balances = beaker.testing.get_balances(client, accts)       # PRINT dict! HA SENSO FARE QUESTO TESTING QUA SE POI GIRANO GLI ALTRI TEST?
#print(balances.items())
#for key,value in balances.items():
#	print(key, ':', value)

# Create an Application client containing both an algod client and my app
app_client = ApplicationClient(client, Auction(), signer = signer1)


def demo():

    ##############
    # APP CREATION
    ##############

    # Create the applicatiion on chain, set the app id for the app client
    print("CREATING AND DEPLOYING THE SMART CONTRACT...")
    app_id, app_addr, txid = app_client.create()
    print(f"Created App with id: {app_id} and address: {app_addr} in tx: {txid}\n")


    ##############
    # START AUCTION
    ##############

    print("STARTING AUCTION BY THE GOVERNOR...")

    # Start auction by the governor (WITH TRANSACTION BY SMART CONTRACT CREATOR ADDRESS)
    sp = client.suggested_params()
#    sp.first =                                     #???        <<<---
#    sp.last =                                      #???        <<<---
#    sp.gh =                                        #???        <<<---
#    sp.flat_fee = True                             #???        <<<---
#    sp.fee = 1*consts.milli_algo
    sp.fee = 2*consts.milli_algo
    tx = TransactionWithSigner(
        txn = transaction.PaymentTxn(addr1, sp, app_addr, 1*consts.algo), signer = signer1,
    )
    try:
        result = app_client.call(
            Auction.start_auction,
            payment = tx,
            starting_price = 1*consts.algo,
#            starting_price = tx.txn.Balance,
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
    print_balances(app_addr, addr1, addr2, addr3)


    ##############
    # START BIDDING - 1st USER
    ##############

    print("START BIDDING: FIRST USER")

    # Cover any fees incurred by inner transactions, maybe overpaying but thats ok
    sp = client.suggested_params()
#    sp.first =                                     #???        <<<---
#    sp.last =                                      #???        <<<---
#    sp.gh =                                        #???        <<<---
#    sp.flat_fee = True                             #???        <<<---
#    sp.fee = 1*consts.milli_algo
    sp.fee = 2*consts.milli_algo

    # Execute bidding
    bidder_client = app_client.prepare(signer2)
    tx1 = TransactionWithSigner(
                txn = transaction.PaymentTxn(addr2, sp, app_addr, 2*consts.algo), signer = signer2
            )
    try:
        result = bidder_client.call(
            Auction.bid,
            payment = tx1,
            previous_bidder = addr1                 # CHECK: NON SETTARE AUTOMATICAMENTE addr1 (SE PUNTATE INFERIORI, NELLA SEQUENZIALITA' RIMANE SEMPRE L'addr DI QUELLO INIZIALE)
#            previous_bidder = bytes.fromhex(app_client.get_application_state()["highest_bidder"])
        )

    except LogicException as e:
        print(f"\n{e}\n")

    print(f"Current app state: {app_client.get_application_state()}\n")
    print_balances(app_addr, addr1, addr2, addr3)


    ##############
    # START BIDDING - 2nd USER
    ##############

    print("START BIDDING: SECOND USER")

    # Cover any fees incurred by inner transactions, maybe overpaying but thats ok 
    sp = client.suggested_params()
#    sp.first =                                     #???        <<<---
#    sp.last =                                      #???        <<<---
#    sp.gh =                                        #???        <<<---
#    sp.flat_fee = True                             #???        <<<---
#    sp.fee = 1*consts.milli_algo
    sp.fee = 2*consts.milli_algo

    # Execute bidding
    bidder_client_2 = app_client.prepare(signer3)
    tx2 = TransactionWithSigner(
                txn = transaction.PaymentTxn(addr3, sp, app_addr, 3*consts.algo), signer = signer3
            )
    try:
        result = bidder_client_2.call(
            Auction.bid,
            payment = tx2,
            previous_bidder = addr2                 # CHECK: NON SETTARE AUTOMATICAMENTE addr1 (SE PUNTATE INFERIORI, NELLA SEQUENZIALITA' RIMANE SEMPRE L'addr DI QUELLO INIZIALE)
                                                    # CHECK: POTREBBE ESSERE ANCORA addr1? PUNTATA PRECEDENTE INFERIORE -> RESPINTA? highest_bidder = addr1
#            previous_bidder = bytes.fromhex(app_client.get_application_state()["highest_bidder"])                                                    
        )

    except LogicException as e:
        print(f"\n{e}\n")

    print(f"Current app state: {app_client.get_application_state()}\n")
    print_balances(app_addr, addr1, addr2, addr3)


    # End auction
    print("CLOSING AUCTION BY THE GOVERNOR...")
#    time.sleep(60)

    try:                                            #PAYMENT INTERNO CON LOGIC SIG?
        result = app_client.call(
            Auction.end_auction,
            suggested_params = sp                   # CHECK     <<<---
        )

    except LogicException as e:
        print(f"\n{e}\n")

    print(f"Current app state: {app_client.get_application_state()}\n")
    print_balances(app_addr, addr1, addr2, addr3)



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



def print_balances(app: str, addr1: str, addr2: str, addr3: str):           #SPECIFICARE CON abi?       <<<---

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
    test_auction
    demo()
