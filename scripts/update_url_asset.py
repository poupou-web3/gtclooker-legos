import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src')) #relative import

import argparse
from ocean_utils import create_data_nft
import logging
import os
from ocean_lib.web3_internal.utils import connect_to_network
from ocean_lib.structures.file_objects import UrlFile

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
    parser.add_argument('-d', '--did', default="did:op:5e51587660fc4b58f1626e2d675d6094ce2562313d67f4808206ae11bb143dcf", help='Asset DID')
    #TODO: change it to repo's readme
    parser.add_argument('-u', '--url', default="https://gateway.pinata.cloud/ipfs/Qmb1sUe9cQkhP5tKusGRebQj7GqDwg254Y6uwX8xmqMocQ", help='Asset URL')

    args = parser.parse_args()
    
    connect_to_network(NETWORK)
    ocean_config = get_config_dict(NETWORK)
    ocean = Ocean(ocean_config)

    accounts.clear()
    job_account = accounts.add(ACCOUNT_PRIVATE_KEY)

    ddo = ocean.assets.resolve(args.did)

    files = [UrlFile(args.url)]
    ddo.services[0].files = files

    ocean.assets.update(ddo, {"from":job_account})

    logger.info("asset url updated to {}".format(args.url))
