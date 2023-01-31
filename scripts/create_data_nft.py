import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src')) #relative import

import argparse
from lib.utils.ocean import create_data_nft
import logging
import os
import config

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    """
    creates data nft based on the inputs provided
    reads the account info from the environment variable
    """

    if "ACCOUNT_PRIVATE_KEY" not in os.environ:
        logger.info("Please set env var ACCOUNT_PRIVATE_KEY to proceed")
        exit(1)

    
    parser = argparse.ArgumentParser(description='creates data nft')
    parser.add_argument('-n', '--name', default="GitcoinGrantsData", help='Data NFT Name')
    parser.add_argument('-s', '--symbol', default="GRDATA", help='Data NFT Symbol')
    args = parser.parse_args()

    network = config.NETWORK
    logger.info('network:{}'.format(network))
    
    data_nft = create_data_nft(args.name, args.symbol, network)
    logger.info("data nft created : {}".format(data_nft.address))