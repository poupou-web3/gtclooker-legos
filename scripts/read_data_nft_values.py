import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../', 'src')) #relative import

import argparse
import logging

from lib.utils.ocean import get_key_value_pair
import config

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

NETWORK=os.environ['NETWORK']
DATA_NFT_ADDRESS=os.environ['DATA_NFT_ADDRESS']

if __name__ == "__main__":
    """
    used to read key-value pairs for specific rounds
    """

    parser = argparse.ArgumentParser(description='creates data url asset')
    parser.add_argument('-k', '--key', default="", help='Data NFT Key')

    args = parser.parse_args()

    logger.info('{}:{}'.format(args.key,get_key_value_pair(args.key, NETWORK, DATA_NFT_ADDRESS)))
    
        
