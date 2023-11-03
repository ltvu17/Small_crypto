from scripts.service import get_account, get_contract
from brownie import ApexToken, TokenFarm
from web3 import Web3
import yaml
import json
import os
import shutil

KEPT_BALANCE = Web3.toWei(100, "ether")


def deploy_token_farm_and_apex_token(is_update_front_end=False):
    account = get_account()
    apex_token = ApexToken.deploy({"from": account})
    token_farm = TokenFarm.deploy(apex_token.address, {"from": account})
    tx = apex_token.transfer(
        token_farm.address, apex_token.totalSupply() - KEPT_BALANCE, {"from": account}
    )
    tx.wait(1)
    weth_token = get_contract("weth_token")
    dai_token = get_contract("dai_token")
    dict_of_allowed_tokens = {
        apex_token: get_contract("dai_usd_price_feed"),
        dai_token: get_contract("dai_usd_price_feed"),
        weth_token: get_contract("eth_usd_price_feed"),
    }
    add_allowed_token(token_farm, dict_of_allowed_tokens, account)
    if is_update_front_end:
        update_front_end()
    return token_farm, apex_token


def add_allowed_token(token_farm, dict_of_allowed_tokens, account):
    for token in dict_of_allowed_tokens:
        add_tx = token_farm.addAllowedToken(token.address, {"from": account})
        add_tx.wait(1)
        set_tx = token_farm.setPriceFeedContract(
            token.address, dict_of_allowed_tokens[token], {"from": account}
        )
        set_tx.wait(1)
    return token_farm


def update_front_end():
    copy_folder_to_front_end("./build", "./front-end/src/chain-info")
    with open("brownie-config.yaml", "r") as brownie_config:
        config_dict = yaml.load(brownie_config, Loader=yaml.FullLoader)
        with open("./front-end/src/brownie-config.json", "w") as brownie_config_json:
            json.dump(config_dict, brownie_config_json)
        print("Front end updated!")


def copy_folder_to_front_end(src, dest):
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.copytree(src, dest)


def main():
    deploy_token_farm_and_apex_token(is_update_front_end=True)
