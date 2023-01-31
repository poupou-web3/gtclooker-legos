

from lib.utils.ocean import get_value_from_data_nft
from lib.utils.storage import get_json_from_ipfs, get_csv_from_ipfs
import logging
import config
import pandas as pd

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

NETWORK = config.NETWORK
DATA_NFT_ADDRESS = config.DATA_NFT_ADDRESS  # data store

"""
Stefi provided this insights as a csv in the discord channel
Created a unique id(lego_id) for this insight & uploaded the csv to IPFS
"""


def get_data(lego_id):
    """
    Every job needs to provide this interface to allow other jobs to parse its output
    """

    if config.LOCAL_MODE:
        df_wallet_tags = pd.read_csv(lego_id)
    else:
        input_file_hash = get_value_from_data_nft(lego_id, NETWORK, DATA_NFT_ADDRESS)
        df_wallet_tags = get_csv_from_ipfs(input_file_hash)
    
    return df_wallet_tags[df_wallet_tags.first_trx_d_round==True].rename(columns={'wallets':'wallet', 'first_trx_d_round' : 'FirstTxDuringRound'})[['wallet','FirstTxDuringRound']]
