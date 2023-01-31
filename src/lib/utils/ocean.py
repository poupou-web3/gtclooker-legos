#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
File: ocean_utils.py
Author: kikura
Description: utility functions to read/write from ocean data nft, data asset
"""

from ocean_lib.models.data_nft import DataNFTArguments
from ocean_lib.models.data_nft import DataNFT

from brownie.network import accounts
from ocean_lib.example_config import get_config_dict
from ocean_lib.ocean.ocean import Ocean
from ocean_lib.web3_internal.utils import connect_to_network
from ocean_lib.structures.file_objects import UrlFile
from web3.main import Web3
import config
import logging

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# This account will be used to create data NFTs
JOB_ACCOUNT_PRIVATE_KEY = config.ACCOUNT_PRIVATE_KEY

def create_data_nft(name, symbol, network):
    """
    creates a data nft contract
    """

    connect_to_network(network) 

    config = get_config_dict(network)
    ocean = Ocean(config)

    accounts.clear()
    job_account = accounts.add(JOB_ACCOUNT_PRIVATE_KEY)

    data_nft = ocean.data_nft_factory.create(DataNFTArguments(name, symbol), {"from": job_account})

    print(data_nft)

    return data_nft

def create_update_key_value_pair(key, value, network, data_nft_address):
    """
    creates key-value pair in the given nft token
    """

    connect_to_network(network) 

    config = get_config_dict(network)
    data_nft = DataNFT(config, data_nft_address)

    accounts.clear()
    job_account = accounts.add(JOB_ACCOUNT_PRIVATE_KEY)

    # prep key for setter
    key_hash = Web3.keccak(text=key)  # Contract/ERC725 requires keccak256 hash
    data_nft.setNewData(key_hash, str.encode(value), {"from": job_account})

def get_key_value_pair(key, network, data_nft_address):
    """
    retrieves key value pair from the NFT
    """

    connect_to_network(network) 

    ocean_config = get_config_dict(network)
    data_nft = DataNFT(ocean_config, data_nft_address)

    # prep key for setter
    key_hash = Web3.keccak(text=key)  # Contract/ERC725 requires keccak256 hash

    value_hex = data_nft.getData(key_hash)
    value = value_hex.decode('ascii')
    return value


def reset_key_value_pairs(keys, network, data_nft_address):
    """
    sets value to ''
    should be used only in development
    """
    for key in keys:
        create_update_key_value_pair(key, '', network, data_nft_address)


def update_asset_url(did, url, network):

    connect_to_network(network) 
    config = get_config_dict(network)

    accounts.clear()
    job_account = accounts.add(JOB_ACCOUNT_PRIVATE_KEY)

    ocean = Ocean(config)

    ddo = ocean.assets.resolve(did)

    files = [UrlFile(url)]
    ddo.services[0].files = files

    ocean.assets.update(ddo, {"from":job_account})

    logger.info("asset url updated to {}".format(url))

def get_value_from_data_nft(key, network, data_nft_address):
    """
    reads value from the data nft
    if key not available, '' is returned
    """
    value = get_key_value_pair(key, network, data_nft_address)
    return value

def set_value_to_data_nft(key, value, network, data_nft_address):
    """
    sets value to the data nft
    overwritten if key exists
    """
    retry = 0
    while retry < 2:
        try:
            create_update_key_value_pair(key, value, network, data_nft_address)
            logger.info("{}:{} updated to data nft".format(key,value))
            return
        except:
            logger.info("failed")
        retry - retry + 1
    
    logger.info("max attempts exceeded")