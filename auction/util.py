import base64
from algosdk import account, mnemonic, encoding
from random import choice, randint
from algosdk.atomic_transaction_composer import *
from algosdk.abi import Method, Contract
import json

# create new application
def create_app(
        client, private_key, approval_program, clear_program, global_schema, local_schema, args=[]
):
    # define sender as creator
    sender = account.address_from_private_key(private_key)

    # declare on_complete as NoOp
    on_complete = transaction.OnComplete.NoOpOC.real

    # get node suggested parameters
    params = client.suggested_params()

    # create unsigned transaction
    txn = transaction.ApplicationCreateTxn(
        sender,
        params,
        on_complete,
        approval_program,
        clear_program,
        global_schema,
        local_schema,
        args,
    )

    # sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()
    client.send_transactions([signed_txn])

    # wait for confirmation
    try:
        transaction_response = transaction.wait_for_confirmation(client, tx_id, 10)
        print("TXID: ", tx_id)
        print(
            "Result confirmed in round: {}".format(
                transaction_response["confirmed-round"]
            )
        )

    except Exception as err:
        print(err)
        return

    # display results
    transaction_response = client.pending_transaction_info(tx_id)
    app_id = transaction_response["application-index"]
    print("Created new app-id:", app_id)

    return app_id

# Utility function to get the Method object for a given method name
def get_method(name: str, js: str) -> Method:
    c = Contract.from_json(js)
    for m in c.methods:
        if m.name == name:
            return m
    raise Exception("No method with the name {}".format(name))


# call application
def call_app(client, private_key, index, contract, method_name="increment", method_args=[]):
    # get sender address
    sender = account.address_from_private_key(private_key)
    # create a Signer object
    signer = AccountTransactionSigner(private_key)

    # get node suggested parameters
    sp = client.suggested_params()

    # Create an instance of AtomicTransactionComposer
    atc = AtomicTransactionComposer()
    atc.add_method_call(
        app_id=index,
        method=contract.get_method_by_name(method_name),
        sender=sender,
        sp=sp,
        signer=signer,
        method_args=method_args,  # No method args needed here
    )

    # send transaction
    results = atc.execute(client, 2)

    # wait for confirmation
    print("TXID: ", results.tx_ids[0])
    print("Result confirmed in round: {}".format(results.confirmed_round))











# helper function that converts a mnemonic passphrase into a private signing key
def get_private_key_from_mnemonic(mn):
    private_key = mnemonic.to_private_key(mn)
    return private_key


# helper function that formats global state for printing
def format_state(state):
    formatted = {}
    for item in state:
        key = item["key"]
        value = item["value"]
        formatted_key = base64.b64decode(key).decode("utf-8")
        if value["type"] == 1:
            # byte string
            formatted_value = base64.b64decode(value["bytes"])
            formatted[formatted_key] = formatted_value
        else:
            # integer
            formatted[formatted_key] = value["uint"]
    return formatted


# helper function to read app global state
def read_global_state(client, app_id):
    app = client.application_info(app_id)
    global_state = (
        app["params"]["global-state"] if "global-state" in app["params"] else []
    )
    return format_state(global_state)


# helper function to read app local state
def read_local_state(client, addr, app_id) :
    results = client.account_info(addr)
    local_state = results['apps-local-state'][0]
    for index in local_state:
        if local_state[index] == app_id :
            local = local_state['key-value']
    return format_state(local)


# opting-in asset
def optInToAsset(client: algod.AlgodClient, account: str, sk: str, asset_id: int):

    # Check if asset_id is in account's asset holdings prior to opt-in
    account_info = client.account_info(account)
    holding = None
    idx = 0
    for my_account_info in account_info['assets']:
        scrutinized_asset = account_info['assets'][idx]
        idx = idx + 1    
        if (scrutinized_asset['asset-id'] == asset_id):
            holding = True
            break

    print("\nAccount:", account, end = "")
    print(" is holding the asset?", holding)

    if not holding:
        print("\nOpting-in the asset for the account...")
        txn = transaction.AssetOptInTxn(
            sender = account,
            index = asset_id,
            sp = client.suggested_params(),
        )
        signedTxn = txn.sign(sk)

        # Send the transaction to the network and retrieve the txid.
        try:
            txid = client.send_transaction(signedTxn)
            print("Signed transaction with txID: {}".format(txid))

            # Wait for the transaction to be confirmed
            response = transaction.wait_for_confirmation(client, signedTxn.get_txid(), 4)
            print("\nResponse:\n", response)                                                #CHECK: confirmed round != asset id <<<---
            print("\nResult confirmed in round: {}".format(response['confirmed-round']))
        
            assert response['asset-index'] is not None and response['asset-index'] > 0

        except Exception as err:
            print(err)
        
    # Now check the asset holding for that account.
    # This should now show a holding with a balance of 0.
    print_asset_holding(client, account, asset_id)

    return 0


# Utility function used to print created asset for account and asset_id
def print_created_asset(client: algod.AlgodClient, account, asset_id):    
    # note: if you have an indexer instance available it is easier to just use this
    # response = myindexer.accounts(asset_id = asset_id)
    # then use 'account_info['created-assets'][0] to get info on the created asset
    account_info = client.account_info(account)
    idx = 0
    for my_account_info in account_info['created-assets']:
        scrutinized_asset = account_info['created-assets'][idx]
        idx = idx + 1       
        if (scrutinized_asset['index'] == asset_id):
            print("\nAsset ID: {}".format(scrutinized_asset['index']))
            print(json.dumps(my_account_info['params'], indent=4))
            break


# Utility function used to print asset holding for account and asset_id
def print_asset_holding(client: algod.AlgodClient, account, asset_id):
    # note: if you have an indexer instance available it is easier to just use this
    # response = myindexer.accounts(asset_id = asset_id)
    # then loop thru the accounts returned and match the account you are looking for
    account_info = client.account_info(account)
    idx = 0
    for my_account_info in account_info['assets']:
        scrutinized_asset = account_info['assets'][idx]
        idx = idx + 1        
        if (scrutinized_asset['asset-id'] == asset_id):
#            print("\nAsset ID: {}".format(scrutinized_asset['asset-id']))
            print("\nAccount:", account)
            print(json.dumps(scrutinized_asset, indent=4))
            break


# CREATE ASSET
def createDummyAsset(client: algod.AlgodClient, total: int, account: str, sk: str) -> int:

    randomNumber = randint(0, 999)
    # this random note reduces the likelihood of this transaction looking like a duplicate
    randomNote = bytes(randint(0, 255) for _ in range(20))

    print("\nCreating the asset...")

    # Asset Creation transaction
    txn = transaction.AssetCreateTxn(
        sender = account,
        total = total,
        decimals = 0,
        default_frozen = False,
        manager = account,
        reserve = account,
        freeze = account,
        clawback = account,                                                                                     #CHECK      <<<---
        unit_name = f"ALGOT",
        asset_name = f"AlgorandGOT",
        url = f"https://github.com/algorand-school/handson-contract/blob/main/image/algorand_throne.jpg",       # CHECK     <<<---
        note = randomNote,
        sp = client.suggested_params(),
    )
    # Sign with secret key of creator
    signedTxn = txn.sign(sk)

    # Send the transaction to the network and retrieve the txid.
    try:
        txid = client.send_transaction(signedTxn)
        print("Signed transaction with txID: {}".format(txid))

        # Wait for the transaction to be confirmed
        response = transaction.wait_for_confirmation(client, signedTxn.get_txid(), 4)
        print("\nResponse:\n", response)                                                #CHECK: confirmed round != asset id <<<---
        print("\nResult confirmed in round: {}".format(response['confirmed-round']))
        
        assert response['asset-index'] is not None and response['asset-index'] > 0

    except Exception as err:
        print(err)

    # Retrieve the asset ID of the newly created asset by first
    # ensuring that the creation transaction was confirmed,
    # then grabbing the asset id from the transaction.

    print("\nTransaction information: {}".format(
        json.dumps(response, indent = 4)))
#        print("Decoded note: {}".format(base64.b64decode(
#        confirmed_txn["txn"]["txn"]["note"]).decode()))

    try:
        # Pull account info for the creator account_info = algod_client.account_info(accounts[1]['pk'])
        # get asset_id from tx
        # Get the new asset's information from the creator account
        ptx = client.pending_transaction_info(txid)
        asset_id = ptx["asset-index"]
        print_created_asset(client, account, asset_id)
#        print_asset_holding(client, account, asset_id)

    except Exception as e:
        print(e)

    return response['asset-index']