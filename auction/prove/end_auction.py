from beaker.client import ApplicationClient, LogicException
from beaker.sandbox import get_algod_client, get_accounts
from beaker import *
from pyteal import *
from algosdk.future import transaction
#from algosdk.atomic_transaction_composer import (
#    TransactionWithSigner,
#)
from auction import Auction

APP_ID = 147
APP_ADDRESS = "GBOCGMWXDET4ZN6YAZBMEP3RCSNQRPHZHV7SQ3DGJRDRXUK35XFEHTHXWA"
TX_ID = "XNE3XGMPKLMY2FHMLTTPCSEESUAXPERQ4DK64N7EARBHJM3BWKHA"

def main():

	accts = get_accounts()

	acct1 = accts.pop()

	client = get_algod_client()

	app = Auction()

	app_client = ApplicationClient(client, app, app_id=APP_ID, signer=acct1.signer)

	print(
		f"Ending Auction: App ID: {APP_ID} Address: {APP_ADDRESS} Transaction ID: {TX_ID}"
	)

	print(f"Current app state: {app_client.get_application_state()}")

	sp = client.suggested_params()

	# Preparo una nuova transazione dal secondo account per inserire una nuova puntata
	sp.fee=100

	try:
		result = app_client.call(
			app.end_auction,
		)

	except LogicException as e:
		print(f"\n{e}\n")

	print(f"Current app state: {app_client.get_application_state()}")
	

if __name__ == "__main__":
	main()