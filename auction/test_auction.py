import copy

import pytest
import typing

from algosdk.atomic_transaction_composer import (
    AtomicTransactionComposer,
    TransactionWithSigner,
    AccountTransactionSigner,
)
from algosdk.future import transaction
from algosdk.v2client.algod import AlgodClient
from algosdk.encoding import decode_address
from beaker import client, sandbox, testing
from beaker.client.application_client import ApplicationClient
from beaker.sandbox import get_algod_client, get_accounts
from beaker.client.logic_error import LogicException
from auction import Auction

accts = get_accounts()
client = get_algod_client()


@pytest.fixture(scope="session")
def creator_acct() -> tuple[str, str, AccountTransactionSigner]:
    return accts[0].address, accts[0].private_key, accts[0].signer


@pytest.fixture(scope="session")
def user_acct() -> tuple[str, str, AccountTransactionSigner]:
    return accts[1].address, accts[1].private_key, accts[1].signer                      #for loop for many users?   <<<---


@pytest.fixture(scope="session")
def creator_app_client(creator_acct) -> client.ApplicationClient:
    _, _, signer = creator_acct
    app = Auction()
    app_client = client.ApplicationClient(client, app, signer=signer)
    return app_client


def test_app_create(creator_app_client: client.ApplicationClient):
    creator_app_client.create()
    app_state = creator_app_client.get_application_state()
    sender = creator_app_client.get_sender()

    assert (
        app_state[Auction.governor.str_key()] == decode_address(sender).hex()
    ), "The governor should be my address"



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



#def test_app_fund(creator_app_client: ApplicationClient):
#    app_addr, addr, signer = (
#        creator_app_client.app_addr,
#        creator_app_client.sender,
#        creator_app_client.signer,
#    )

#    pool_asset, a_asset, b_asset = _get_tokens_from_state(creator_app_client)

#    assert addr
#    _opt_in_to_token(addr, signer, pool_asset)

#    balance_accts = [app_addr, addr]
#    balances_before = testing.get_balances(creator_app_client.client, balance_accts)

#    a_amount = 10000
#    b_amount = 3000

#    sp = creator_app_client.client.suggested_params()
#    creator_app_client.call(
#        ConstantProductAMM.mint,
#        suggested_params=minimum_fee_for_txn_count(sp, 2),
#        a_xfer=TransactionWithSigner(
#            txn=transaction.AssetTransferTxn(addr, sp, app_addr, a_amount, a_asset),
#            signer=signer,
#        ),
#        b_xfer=TransactionWithSigner(
#            txn=transaction.AssetTransferTxn(addr, sp, app_addr, b_amount, b_asset),
#            signer=signer,
#        ),
#        pool_asset=pool_asset,
#        a_asset=a_asset,
#        b_asset=b_asset,
#    )

#    balances_after = testing.get_balances(creator_app_client.client, balance_accts)
#    balance_deltas = testing.get_deltas(balances_before, balances_after)

#    assert balance_deltas[app_addr][a_asset] == a_amount
#    assert balance_deltas[app_addr][b_asset] == b_amount
#    assert_app_algo_balance(creator_app_client, app_algo_balance)

#    expected_pool_tokens = int((a_amount * b_amount) ** 0.5 - ConstantProductAMM._scale)
#    assert balance_deltas[addr][pool_asset] == expected_pool_tokens

#    ratio = _get_ratio_from_state(creator_app_client)
#    expected_ratio = int((a_amount * ConstantProductAMM._scale) / b_amount)
#    assert ratio == expected_ratio
