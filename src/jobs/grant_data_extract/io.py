from lib.utils.ocean import get_value_from_data_nft
from lib.utils.storage import get_json_from_ipfs, get_csv_from_ipfs, get_json
import logging
import config
import pandas as pd

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

NETWORK = config.NETWORK
DATA_NFT_ADDRESS = config.DATA_NFT_ADDRESS #data store

def get_data(lego_id):
    """
    reads the ipfs location of application & vote files
    zips them & uploads it to ocean marketplace
    """

    if config.LOCAL_MODE:

        grants_data = get_json(lego_id)
    
    else:

        input_file_hash = get_value_from_data_nft(lego_id, NETWORK, DATA_NFT_ADDRESS)

        if input_file_hash=='':
            logger.error('Input empty.')
            return
        else:
            grants_data = get_json_from_ipfs(input_file_hash)

    votes_df_list = []
    applications_df_list = []

    for _ , round_info in grants_data.items():

        votes_file_location = round_info['votes']
        df_vote = get_csv_from_ipfs(votes_file_location)
        votes_df_list.append(df_vote)

        grants_file_location = round_info['applications']
        df_applications = get_csv_from_ipfs(grants_file_location)
        applications_df_list.append(df_applications)

    df_votes = pd.concat(votes_df_list)
    df_applications = pd.concat(applications_df_list)

    return df_applications, df_votes