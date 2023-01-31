import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src')) #relative import

import argparse
from lib.utils.ocean import create_update_key_value_pair
import logging
import os
import config

NETWORK=config.NETWORK
DATA_NFT_ADDRESS=config.DATA_NFT_ADDRESS

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    """
    creates data nft based on the inputs provided
    reads the account info from the environment variable
    python write_data_nft_values.py -k "key" -v "value"
    """

    parser = argparse.ArgumentParser(description='creates data url asset')
    parser.add_argument('-k', '--key', default="", help='Asset DID')
    parser.add_argument('-v', '--value', default="", help='Asset URL')

    args = parser.parse_args()
    
    create_update_key_value_pair(args.key, args.value, NETWORK, DATA_NFT_ADDRESS)

