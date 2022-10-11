from algosdk.future import transaction
from algosdk.atomic_transaction_composer import (
    AtomicTransactionComposer,
    TransactionWithSigner,
)
from pyteal import *
from beaker import consts
from beaker.sandbox import get_accounts, get_algod_client
from beaker.client import ApplicationClient
from beaker.client.logic_error import LogicException

from auction import Auction


# Take first account from sandbox
accts = get_accounts()
print(f"\nNumber of accounts derived from sandbox:", len(accts))
#beaker.testing.get_balances(accts)
acct1 = accts.pop()                                         #smart contract creator (derived from sandbox accounts)     #????                       <<<---
addr1, sk1, signer1 = acct1.address, acct1.private_key, acct1.signer
print("\nAccount n.1:", addr1)
print("Address Secret key =", sk1)
acct2 = accts.pop()                                         # 1st user account (derived from sandbox accounts)
addr2, sk2, signer2 = acct2.address, acct2.private_key, acct2.signer
print("\nAccount n.2:", addr2)
print("Address Secret key =", sk2)
acct3 = accts.pop()                                         # 2st user account (derived from sandbox accounts)          #TEST bid < previous_bid    <<<---
addr3, sk3, signer3 = acct3.address, acct3.private_key, acct3.signer
print("\nAccount n.3:", addr3)
print("Address Secret key =", sk3)

# get sandbox client
client = get_algod_client()

# Create an Application client containing both an algod client and my app
app_client = ApplicationClient(client, Auction(), signer=acct1.signer)


def demo():

    # Create the applicatiion on chain, set the app id for the app client
    app_id, app_addr, txid = app_client.create()
    print(f"\nCreated App with id: {app_id} and address: {app_addr} in tx: {txid}\n")
    print(f"Current app state: {app_client.get_application_state()}\n")
    print(Global.creator_address(),"?????\n")                                           #DIVERSO DAL PRIMO DEGLI ACCOUNT SANDBOX?       <<<---
    print_balances(app_addr, addr1, addr2, addr3)

    # Cover any fees incurred by inner transactions, maybe overpaying but thats ok      # CHECK suggested parameters                    <<<---
    sp = client.suggested_params()
    #sp.flat_fee = True
    #sp.fee = 3*consts.milli_algo

    # Fund the app account with 1 algo                      #CARICA ALGO SULLO SMART CONTRACT, ANCHE SE DOPO FATTO IN "start_auction"?  <<<---
#   app_client.fund(1*consts.algo)

    # Preparing transaction
    tx1 = TransactionWithSigner(
                txn=transaction.PaymentTxn(addr1, sp, app_addr, 1*consts.algo), signer=signer1
            )

    # Sending funds to the smart contract to start auction
    try:
        result = app_client.call(
            Auction.start_auction,
            payment=tx1,
            starting_price=1*consts.algo,
            length=1000000
        )

    except LogicException as e:
        print(f"\n{e}\n")
    
    print(f"Current app state: {app_client.get_application_state()}\n")
    print_balances(app_addr, addr1, addr2, addr3)


    # 1st user bidding
    # Preparing transaction
#    tx2 = TransactionWithSigner(
#        txn=transaction.PaymentTxn(addr2, sp, app_addr, 2*consts.algo), signer=signer2
#    )

#    try:
#        result = app_client.call(
#            Auction.bid,
#            payment=tx2,
#            previous_bidder=addr1,
#        )

#    except LogicException as e:
#        print(f"\n{e}\n")

#    print(f"Current app state: {app_client.get_application_state()}\n")
#    print_balances(app_addr, addr1, addr2, addr3)


    ##############################################################
    #call(method: Union[Method, Callable[[...], Expr]],                     #ESPLORA ALTRI METODI CALL      <<<---
    #     sender: Optional[str] = None,
    #     signer: Optional[TransactionSigner] = None,
    #     suggested_params: Optional[SuggestedParams] = None,
    #     on_complete: OnComplete = OnComplete.NoOpOC,ù
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


def print_balances(app: str, addr1: str, addr2: str, addr3: str):                       #SPECIFICARE CON abi?       <<<---

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
    demo()
