import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src')) #relative import

import argparse
from lib.utils.ocean import create_data_nft
import logging
import os
from ocean_lib.web3_internal.utils import connect_to_network


import config
from ocean_lib.example_config import get_config_dict
from ocean_lib.ocean.ocean import Ocean
from brownie.network import accounts

NETWORK=config.NETWORK
ACCOUNT_PRIVATE_KEY=config.ACCOUNT_PRIVATE_KEY

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    """
    creates data nft based on the inputs provided
    reads the account info from the environment variable
    """

    parser = argparse.ArgumentParser(description='creates data url asset')
    parser.add_argument('-n', '--name', default="Gitcoin Grants Dataset", help='Data NFT Name')
    parser.add_argument('-u', '--url', default="https://gateway.pinata.cloud/ipfs/Qmb1sUe9cQkhP5tKusGRebQj7GqDwg254Y6uwX8xmqMocQ", help='Asset URL')

    args = parser.parse_args()
    
    connect_to_network(NETWORK)
    ocean_config = get_config_dict(NETWORK)
    ocean = Ocean(ocean_config)

    accounts.clear()
    job_account = accounts.add(ACCOUNT_PRIVATE_KEY)

    #create data asset
    (data_nft, datatoken, ddo) = ocean.assets.create_url_asset(args.name, args.url, {"from": job_account})

    logger.info("Just published asset:")
    logger.info(f"  data_nft: symbol={data_nft.symbol}, address={data_nft.address}")
    logger.info(f"  datatoken: symbol={datatoken.symbol}, address={datatoken.address}")
    logger.info(f"  did={ddo.did}")

    datatoken.create_dispenser({"from": job_account})
    logger.info("data asset pricing schema set as free")
