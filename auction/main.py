from algosdk.future import transaction
from algosdk.atomic_transaction_composer import (
    AtomicTransactionComposer,
    TransactionWithSigner,
)
from beaker import consts
from beaker.sandbox import get_accounts, get_algod_client
from beaker.client import ApplicationClient

from .auction import Auction


# Take first account from sandbox
accts = get_accounts()
#print(type(accts))
#print(len(accts))
#print(accts[0])
#print(accts[1])
#print(accts[2])
#print(Global.creator_address())
#beaker.testing.get_balances(accts)
acct1 = accts.pop()
addr, sk, signer = acct1.address, acct1.private_key, acct1.signer

# get sandbox client
client = get_algod_client()

# Create an Application client containing both an algod client and my app
app_client = ApplicationClient(client, Auction(), signer=acct.signer)

# Prendo il secondo account                                                     <<<<-----
acct2 = accts.pop()


def demo():
    # Recupero degli account da sandbox

    # Prendo il client per interagire con la sandbox
    client = get_algod_client()

    # Creo lo smart contract
    app = Auction()

    # Metto insieme client, smart contract e account
    app_client = ApplicationClient(client, app, signer=acct1.signer)

    # Faccio il deploy dello smart contract sulla rete
    app_id, app_address, transaction_id = app_client.create()

    print(
        f"DEPLOYED: App ID: {app_id} Address: {app_address} Transaction ID: {transaction_id}"
    )

    print(f"Current app state: {app_client.get_application_state()}")

    # Preparo la transazione che invia gli algo allo smart contract
    interaction_client = app_client.prepare(signer=acct1.signer)

    # Creo i suggested params (non so cosa siano, credo sia una cosa di default)
    sp = client.suggested_params()

    # creo la transazione che manda gli algo allo smartcontract
    tx=TransactionWithSigner(
        txn=transaction.PaymentTxn(acct1.address, sp, app_address, 1 * consts.algo),
        signer=acct1.signer,
    )

    # INTERAZIONE VERA E PROPRIA CON SMART CONTRACT
    try:
        result = interaction_client.call(
            app.start_auction,
            payment=tx,
            starting_price=1*consts.algo,
            length=1000000
        )

    except LogicException as e:
        print(f"\n{e}\n")
    

    print(f"Current app state: {app_client.get_application_state()}")

    # Preparo una nuova transazione dal secondo account per inserire una nuova puntata
    bid_client = app_client.prepare(signer=acct2.signer)
    tx2=TransactionWithSigner(
        txn=transaction.PaymentTxn(acct2.address, sp, app_address, 2 * consts.algo),
        signer=acct2.signer,
    )

    try:
        result = bid_client.call(
            app.bid,
            payment=tx2,
            previous_bidder=acct1.address
        )

    except LogicException as e:
        print(f"\n{e}\n")

    print(f"Current app state: {app_client.get_application_state()}")