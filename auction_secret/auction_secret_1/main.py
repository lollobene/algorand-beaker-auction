
#############################
# IMPLEMENTAZIONE CON HTLC
#############################

from hashlib import sha256
from algosdk.future import transaction
from algosdk.atomic_transaction_composer import (
    AtomicTransactionComposer,
    TransactionWithSigner,
)
from algosdk import account, mnemonic, transaction, template
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
sk4, addr4 = account.generate_account()                     # 3rd user account (derived from sandbox accounts)
#print("Account n.4: {}".format(addr4))
print("\nAccount n.4:", addr4)
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
app_client = ApplicationClient(client, SecretAuction(), signer1)

def demo():

    # Create the applicatiion on chain, set the app id for the app client
    print("\nCREATING AND DEPLOYING THE SMART CONTRACT...")
    app_id, app_addr, txid = app_client.create()
    print(f"Created App with id: {app_id} and address: {app_addr} in tx: {txid}\n")

    # Get suggested parameters from the network
    tx_params = client.suggested_params()
    #tx_params.first =
    #tx_params.last =
    #tx_params.gh = "wGHE2Pwdvd7S12BL5FaOP20EGYesN73ktiC1qzkkit8="      #TO BE VALIDATED ONCE ON release NETWORK (MainNet)
    #tx_params.flat_fee = True
    #tx_params.fee = MIN_FEE = 1000

    # Set a common expiry round
    expiry = 10000

    # Specify TLHC-related template params                              #FOR LOOP PER OGNI ACCOUNT?
    template_data_1 = {
        "owner": addr1,                                                 #address to refund funds to on timeout
        "receiver": app_addr,                                           #address to send funds to when the preimage is supplied
        "hash_function": "sha256",                                      #specific hash function (sha256 or keccak256) to use
        "hash_image": "QzYhq9JlYbn2QdOMrhyxVlNtNjeyvyJc/I8d8VAGfGc=",   #image of the hash function for which knowing the preimage under TMPL_HASHFN will release the funds
        "expiry_round": expiry,                                         #round after which funds may be closed out to TMPL_OWN
        "max_fee": 2000
    }

    # Inject template data into HTLC template
    c = template.HTLC(**template_data_1)

    # Get the address for the escrow account associated with the logic
    addr_escrow_1 = c.get_address()
    print("Escrow Address: {}\n".format(addr_escrow_1))

    # Fund the escrow account
    tx1 = TransactionWithSigner(
        txn = transaction.PaymentTxn(addr1, tx_params, addr_escrow_1, 1*consts.algo, None, None, None, None), signer = signer1
    )

    # Retrieve the program bytes
    program = c.get_program()

    # Get the program and parameters and use them to create an lsig for the contract account to be used in a transaction
    # Used the hero wisdom green split loop element vote belt' string to be hashed with sha256 to produce our image hash (passcode for the HTLC)
    args = [
        "hero wisdom green split loop element vote belt".encode()       #CHECK PHRASE TO BE HASHED      <<<---
    ]

    # Add the program bytes and args to a LogicSig object 
    lsig = transaction.LogicSig(program, args)

    # Before submitting this transaction, you must first make sure the escrow account is sufficiently funded.
    # Once it is funded, create and submit transactions from the escrow account.        #INSERIRE UN Assert DI VERIFICA PRIMA CHE VERIFICHI FONDI SUFFICIENTI (SULLA BASE DELLO STARTING_PRICE COMUNICATO IN PRECEDENZA)        <<<---
    # Transaction data
    tx1_data = {
        "sender": addr_escrow_1,
        "receiver": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAY5HFKQ",
        "amt": 0,
        "close_remainder_to": app_addr,
#        "rekey": None,
        "fee": MIN_FEE,
        "flat_fee": True,
        "first": tx_params.get('lastRound'),
        "last": tx_params.get('lastRound') + 1000,
        "gen": tx_params.get('genesisID'),
        "gh": tx_params.get('genesishashb64')
#        "gh": tx_params.gh
    }
    
    # Instantiate a payment transaction type
    txn = transaction.PaymentTxn(**tx1_data)
    
    # Instantiate a LogicSigTransaction with the payment txn and the logicsig
    logicsig_txn = transaction.LogicSigTransaction(txn, lsig)

    # Send the transaction to the network
    txid = client.send_transaction(logicsig_txn, headers={'content-type': 'application/x-binary'})
    print("Transaction ID: {}".format(txid))

    appbal = client.account_info(app_addr)
    print("App Balance = {}\n".format(appbal["amount"]))

    addrbal1 = client.account_info(addr1)
    print("Participant:", addr1, end = "")
    print("\tAddress Balance = {}\n".format(addrbal1["amount"]))

#    try:
#        result = app_client.call(
#            SecretAuction.bid,
#            payment = txn,
#            duration = expiry
#        )

#    except LogicException as e:
#        print(f"\n{e}\n")
    
#    print(f"Current app state: {app_client.get_application_state()}\n")
#    print_balances(app_addr, addr1, addr2, addr3)












if __name__ == "__main__":
#    test_auction_secret
    demo()
