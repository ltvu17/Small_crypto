from brownie import network, exceptions
from scripts.service import LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_account, get_contract
from scripts.deploy import deploy_token_farm_and_apex_token
import pytest
from web3 import Web3


def test_set_price_feed_contract():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")
    account = get_account()
    non_owner = get_account(index=1)
    token_farm, apex_token = deploy_token_farm_and_apex_token()
    token_farm.setPriceFeedContract(
        apex_token.address, get_contract("dai_usd_price_feed"), {"from": account}
    )
    assert token_farm.tokenPriceFeedMapping(apex_token.address) == get_contract(
        "dai_usd_price_feed"
    )
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.setPriceFeedContract(
            apex_token.address, get_contract("dai_usd_price_feed"), {"from": non_owner}
        )


def test_stake_token(amount_staked):
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")
    account = get_account()
    token_farm, apex_token = deploy_token_farm_and_apex_token()
    apex_token.approve(token_farm.address, amount_staked, {"from": account})
    token_farm.stakeToken(amount_staked, apex_token.address, {"from": account})
    assert (
        token_farm.stakingBalance(apex_token.address, account.address) == amount_staked
    )
    assert token_farm.uniqueTokenStaked(account.address) == 1
    assert token_farm.stakers(0) == account.address
    return token_farm, apex_token


def test_issue_token(amount_staked):
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")
    account = get_account()
    token_farm, apex_token = test_stake_token(amount_staked)
    starting_balance = apex_token.balanceOf(account.address)

    token_farm.issueToken({"from": account})
    assert apex_token.balanceOf(account.address) == starting_balance + Web3.toWei(
        1500, "ether"
    )
