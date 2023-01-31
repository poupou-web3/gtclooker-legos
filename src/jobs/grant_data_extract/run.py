
from lib.utils.ocean import get_value_from_data_nft, set_value_to_data_nft
from lib.utils.storage import get_json_from_ipfs, upload_dict_to_ipfs, get_json, write_json
from lib.data.chain.fetch_grants_data import extract_latest_grants_data
import logging
import config

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

NETWORK = config.NETWORK
DATA_NFT_ADDRESS = config.DATA_NFT_ADDRESS #data store


#mode.local read and write to local directory
#mode.local with wallet_info provided

def run_job(lego_id, inputs, params):
    """
    - extracts past collected grant data
    - reads the delta from chain
    - writes back the combined file
    """
    #TODO: The grants will be processed only after the project status is updated


    if len(inputs) != 0:
        logger.error("This job is not configured to take inputs")
        return

    if config.LOCAL_MODE:
        grants_data = get_json(lego_id) #expects a csv with the given name
    else:
        #get output of the last lego run
        output_file_hash = get_value_from_data_nft(lego_id, NETWORK, DATA_NFT_ADDRESS)
        grants_data = get_json_from_ipfs(output_file_hash) if output_file_hash !='' else {}

    #updates the data with new information since last run
    updated_grants_data = extract_latest_grants_data(grants_data)
    
    if config.LOCAL_MODE:
        
        #write it to local file system
        write_json(updated_grants_data, lego_id)
    
    else:

        #upload the file to IPFS
        grants_data_ipfs_hash = upload_dict_to_ipfs(updated_grants_data)

        #reset the key(lego_id) value to the new IPFS file location
        set_value_to_data_nft(lego_id, grants_data_ipfs_hash, NETWORK, DATA_NFT_ADDRESS)