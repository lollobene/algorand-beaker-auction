from beaker.client import ApplicationClient, LogicException
from beaker.sandbox import get_algod_client, get_accounts
from beaker import *
from pyteal import *

from algosdk.future import transaction
from algosdk.atomic_transaction_composer import (
    TransactionWithSigner,
)

from auction import Auction

APP_ID = 62
APP_ADDRESS = "NDBRJYD5KXUA6K5Q456OM6JLC5SRKQJ7ME6MK2NCE5VX3WGGEAB5LOYFVQ"
TX_ID = "R726ZBMRWKU7DBURD2KGYC4VP7YG7C4UCH3VTJXCDCI32UDTVB4A"

def main():

	accts = get_accounts()

	acct1 = accts.pop()
	acct2 = accts.pop()
	acct3 = accts.pop()

	client = get_algod_client()

	app = Auction()

	app_client = ApplicationClient(client, app, app_id=APP_ID, signer=acct3.signer)

	print(
		f"ITERACTING: App ID: {APP_ID} Address: {APP_ADDRESS} Transaction ID: {TX_ID}"
	)

	print(f"Current app state: {app_client.get_application_state()}")

	sp = client.suggested_params()

	# Preparo una nuova transazione dal secondo account per inserire una nuova puntata
	sp.fee=10
	tx3=TransactionWithSigner(
		txn=transaction.PaymentTxn(acct3.address, sp, APP_ADDRESS, 3 * consts.algo),
		signer=acct3.signer,
	)

	try:
		result = app_client.call(
			app.bid,
			payment=tx3,
			previous_bidder=acct2.address
		)

	except LogicException as e:
		print(f"\n{e}\n")

	print(f"Current app state: {app_client.get_application_state()}")
	

if __name__ == "__main__":
	main()