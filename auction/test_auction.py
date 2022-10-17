#import copy
import pytest
#import typing
from algosdk.atomic_transaction_composer import (
#    AtomicTransactionComposer,
    TransactionWithSigner,
    AccountTransactionSigner,
)
from algosdk.future import transaction
#from algosdk.v2client.algod import AlgodClient
from algosdk.encoding import encode_address, decode_address
from beaker import client, sandbox, testing
from beaker.client import ApplicationClient
from beaker.sandbox import get_algod_client, get_accounts
from beaker.client.logic_error import LogicException
from beaker import *
from algosdk import transaction
from asset_auction import Auction

MIN_FEE = 1000


# Take accounts from sandbox
accts = get_accounts()
acct1 = accts.pop()                                         # smart contract creator (derived from sandbox accounts)
owner_addr, owner_sk, owner_sign = acct1.address, acct1.private_key, acct1.signer
acct2 = accts.pop()                                         # 1st user account (derived from sandbox accounts)
addr2, sk2, signer2 = acct2.address, acct2.private_key, acct2.signer
acct3 = accts.pop()                                         # 2st user account (derived from sandbox accounts)
addr3, sk3, signer3 = acct3.address, acct3.private_key, acct3.signer

# get sandbox client
client = get_algod_client()

# Create an Application client containing both an algod client and my app
#app_client = ApplicationClient(client, Auction(), signer = owner_sign)


######################
# app creation test
######################

@pytest.fixture(scope = "module")
def create_app():
    global accounts
    global creator_acct
    global app_client
    accounts = sorted(
        accts,
        key = lambda a: client.account_info(a.address)["amount"]
    )

    creator_acct = accounts.pop()

    app_client = client.ApplicationClient(
        client = client,
        app = Auction(version = 6),
        signer = creator_acct.signer,
    )

    app_client.create()


######################
# auction setup test
######################
""""
@pytest.fixture(scope = "module")
def auction_setup():
    sp = app_client.get_suggested_params()
    pay_txn = TransactionWithSigner(
        txn = transaction.PaymentTxn(
            sender = creator_acct.address,
            receiver = app_client.app_addr,
            amt = 1*consts.algo,
            fee = sp.fee,
#            gh = sp.gh                                 #TO BE VALIDATED ONCE ON TestNet NETWORK
        ),
        signer = creator_acct.signer
    )

    app_client.call(Auction.setup, payment = pay_txn, starting_price = 1*consts.algo, length = 120)


######################
# first account: first bid test
######################

@pytest.fixture(scope = "module")
def send_first_bid_first_addr():
    global first_bidder
    first_bidder = accounts.pop()
    sp = app_client.get_suggested_params()
    pay_txn = TransactionWithSigner(
        txn = transaction.PaymentTxn(
            sender = first_bidder.address,
            receiver = app_client.app_addr,
            amt = 2*consts.algo,
            fee = sp.fee,
#            gh = sp.gh                                  #TO BE VALIDATED ONCE ON TestNet NETWORK
        ),
        signer = first_bidder.signer
    )

    app_client.call(Auction.bid, payment = pay_txn, previous_bidder = first_bidder.address, signer = first_bidder.signer)


######################
# second account: first bid test
######################

@pytest.fixture(scope = "module")
def send_first_bid_second_addr():
    global second_bidder
    global first_bidder_amount
    second_bidder = accounts.pop()
    sp = app_client.get_suggested_params()
    first_bidder_amount = app_client.client.account_info(first_bidder.address)["amount"]
    pay_txn = TransactionWithSigner(
        txn = transaction.PaymentTxn(
            sender = second_bidder.address,
            receiver = app_client.app_addr,
            amt = 3*consts.algo,
            fee = sp.fee,
            gh = sp.gh                                  #TO BE VALIDATED ONCE ON TestNet NETWORK
        ),
        signer = second_bidder.signer
    )

    app_client.call(Auction.bid, payment = pay_txn, previous_bidder = first_bidder.address, signer = second_bidder.signer)


######################
# first account: second bid test
######################

@pytest.fixture(scope = "module")
def send_second_bid_first_addr():
    global first_bidder
    first_bidder = accounts.pop()
    sp = app_client.get_suggested_params()
    pay_txn = TransactionWithSigner(
        txn = transaction.PaymentTxn(
            sender = first_bidder.address,
            receiver = app_client.app_addr,
            amt = 2*consts.algo,
            fee = sp.fee,
#            gh = sp.gh                                  #TO BE VALIDATED ONCE ON TestNet NETWORK
        ),
        signer = first_bidder.signer
    )

    app_client.call(Auction.bid, payment = pay_txn, previous_bidder = first_bidder.address, signer = first_bidder.signer)


######################
# second account: first bid test
######################

@pytest.fixture(scope = "module")
def send_second_bid():
    global second_bidder
    global first_bidder_amount
    second_bidder = accounts.pop()
    sp = app_client.get_suggested_params()
    first_bidder_amount = app_client.client.account_info(first_bidder.address)["amount"]
    pay_txn = TransactionWithSigner(
        txn = transaction.PaymentTxn(
            sender = second_bidder.address,
            receiver = app_client.app_addr,
            amt = 3*consts.algo,
            fee = sp.fee,
            gh = sp.gh                                  #TO BE VALIDATED ONCE ON TestNet NETWORK
        ),
        signer = second_bidder.signer
    )

    app_client.call(Auction.bid, payment = pay_txn, previous_bidder = first_bidder.address, signer = second_bidder.signer)


##############
# end auction test
##############

@pytest.fixture(scope = "module")
def end_auction():
    global creator_acct
    sp = app_client.get_suggested_params()
#    pay_txn = TransactionWithSigner(                        #DA SOSTITUIRE NEL CASO DI PAYMENT CON LOGIC SIG
#        txn = transaction.PaymentTxn(
#            sender = second_bidder.address,
#            receiver = app_client.app_addr,
#            amt = 2000000,
#            fee = MIN_FEE*2,                                #????           <<<---
#            first = sp.first,                               #????           <<<---
#            last = sp.last,                                 #????           <<<---
#            gh = sp.gh,                                     #????           <<<---
#        ),
#        signer = second_bidder.signer,
#    )
    txn = transaction.PaymentTxn(
        sender = app_client.app_addr,
        receiver = creator_acct,
#        amt = 2000000,
        amt = app_client.get_application_state()["highest_bid"],
#        fee = sp.fee,
        fee = MIN_FEE*2,                                    #????           <<<---
        first = sp.first,                                   #????           <<<---
        last = sp.last,                                     #????           <<<---
        gh = sp.gh,                                         #????           <<<---
    ),

    app_client.call(Auction.end_auction, payment = txn)

"""

##############
# create tests
##############

@pytest.mark.create
def test_create_owner(create_app):                                              # CHECK: PARAMETRO create_app NON CARICATO  <<<---
    addr = bytes.fromhex(app_client.get_application_state()["owner"])
    assert encode_address(addr) == creator_acct.address

@pytest.mark.create
def test_create_highest_bidder(create_app):                                     # CHECK: PARAMETRO create_app NON CARICATO  <<<---
    assert app_client.get_application_state()["highest_bidder"] == ""

@pytest.mark.create
def test_create_highest_bid(create_app):                                        # CHECK: PARAMETRO create_app NON CARICATO  <<<---
    assert app_client.get_application_state()["highest_bid"] == 0

@pytest.mark.create
def test_create_auction_end(create_app):                                        # CHECK: PARAMETRO create_app NON CARICATO  <<<---
    assert app_client.get_application_state()["auction_end"] == 0

"""
#####################
# auction setup tests
#####################

@pytest.mark.start_auction
def test_start_auction_end(create_app, start_auction):                          # CHECK: PARAMETRI NON CARICATI  <<<---
    assert app_client.get_application_state()["auction_end"] != 0

@pytest.mark.start_auction
def test_start_auction_highest_bid(create_app, start_auction):
#    assert app_client.get_application_state()["highest_bid"] == 10_000
    assert app_client.get_application_state()["highest_bid"] == 1000000

#################
# first_bid tests
#################

@pytest.mark.first_bid
def test_first_bid_highest_bid(create_app, start_auction, send_first_bid):      # CHECK: PARAMETRI NON CARICATI  <<<---
#    assert app_client.get_application_state()["highest_bid"] == 20_000
    assert app_client.get_application_state()["highest_bid"] == 2000000

@pytest.mark.first_bid
def test_first_bid_highest_bidder(create_app, start_auction, send_first_bid):   # CHECK: PARAMETRI NON CARICATI  <<<---
    addr = bytes.fromhex(app_client.get_application_state()["highest_bidder"])
    assert encode_address(addr) == first_bidder.address

@pytest.mark.first_bid
def test_first_bid_app_balance(create_app, start_auction, send_first_bid):       # CHECK: PARAMETRI NON CARICATI  <<<---
    assert app_client.client.account_info(app_client.app_addr)["amount"] == app_client.get_application_state()["highest_bid"]

##################
# second_bid tests
##################

@pytest.mark.second_bid
def test_second_bid_highest_bid(create_app, start_auction, send_first_bid, send_second_bid):        # CHECK: PARAMETRI NON CARICATI  <<<---
#    assert app_client.get_application_state()["highest_bid"] == 30_000
    assert app_client.get_application_state()["highest_bid"] == 3000000

@pytest.mark.second_bid
def test_second_bid_highest_bidder(create_app, start_auction, send_first_bid, send_second_bid):     # CHECK: PARAMETRI NON CARICATI  <<<---
    addr = bytes.fromhex(app_client.get_application_state()["highest_bidder"])
    assert encode_address(addr) == second_bidder.address

@pytest.mark.second_bid                                                                                 # SOLDI TORNATI INDIETRO AL PREVIOUS ACCOUNT
def test_second_bid_first_bidder_balance(create_app, start_auction, send_first_bid, send_second_bid):   # CHECK: PARAMETRI NON CARICATI  <<<---
#    assert (app_client.client.account_info(first_bidder.address)["amount"] == first_bidder_amount + 20_000
    assert (app_client.client.account_info(first_bidder.address)["amount"] == first_bidder_amount + 2000000)    # PUNTATA DA RENDERE DINAMICA

@pytest.mark.second_bid
def test_second_bid_app_balance(create_app, start_auction, send_first_bid, send_second_bid):        # CHECK: PARAMETRI NON CARICATI  <<<---
#    assert (app_client.client.account_info(app_client.app_addr)["amount"] == 30_000 + 100_000)
    assert (app_client.client.account_info(app_client.app_addr)["amount"] == 3000000 + 1000000)

"""



@pytest.fixture(scope = "session")
def creator_acct() -> tuple[str, str, AccountTransactionSigner]:
    return accts[0].address, accts[0].private_key, accts[0].signer


@pytest.fixture(scope = "session")
def user_acct() -> tuple[str, str, AccountTransactionSigner]:
    for i in range(len(accts) - 1):
        return accts[i+1].address, accts[i+1].private_key, accts[i+1].signer


#@pytest.fixture(scope="session")
#def creator_app_client(creator_acct) -> client.ApplicationClient:
#    _, _, signer = creator_acct
#    app = Auction()
#    app_client = client.ApplicationClient(client, app, signer=signer)
#    return app_client


#def test_app_create(creator_app_client: client.ApplicationClient):
#    creator_app_client.create()
#    app_state = creator_app_client.get_application_state()
#    sender = creator_app_client.get_sender()
#
#    assert (
#        app_state[Auction.governor.str_key()] == decode_address(sender).hex()
#    ), "The governor should be my address"


#def minimum_fee_for_txn_count(sp: transaction.SuggestedParams, txn_count: int) -> transaction.SuggestedParams:
#    """
#    Configures transaction fee _without_ considering network congestion.
#    Since the function does not account for network congestion, do _not_ use the function as-is in a production use-case.
#    """
#    s = copy.deepcopy(sp)
#    s.flat_fee = True
#    s.fee = transaction.constants.min_txn_fee * txn_count
#    return s


#def assert_app_algo_balance(c: client.ApplicationClient, expected_algos: int):
#    """
#    Verifies the app's algo balance is not unexpectedly drained during app interaction (e.g. paying inner transaction fees).
#    Due to the presence of rewards, the assertion tolerates actual > expected for small positive differences.
#    """
#    xs = testing.get_balances(c.client, [c.app_addr])
#    assert c.app_addr in xs
#    assert 0 in xs[c.app_addr]
#    actual_algos = xs[c.app_addr][0]

#    # Before accounting for rewards, confirm algos were not drained.
#    assert actual_algos >= expected_algos

#    # Account for rewards.
#    micro_algos_tolerance = 10
#    assert actual_algos - expected_algos <= micro_algos_tolerance

#app_algo_balance: typing.Final = int(1e7)
