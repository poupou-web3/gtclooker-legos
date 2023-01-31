from lib.utils.ocean import get_value_from_data_nft, update_asset_url
from lib.utils.storage import get_json_from_ipfs, zip_files, upload_file_to_ipfs
from lib.data.chain.fetch_grants_data import map_round_to_name
from lib.utils.job import read_job_output
import logging
import os
import config
import tempfile

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

NETWORK = config.NETWORK
DATA_NFT_ADDRESS = config.DATA_NFT_ADDRESS #data store
DATA_ASSET_DID = config.DATA_ASSET_DID #data asset in ocean marketplace
IPFS_OUTPUT_URL_GATEWAY = config.IPFS_GATEWAYS[0]

def run_job(lego_id, inputs, params):
    """
    reads the ipfs location of application & vote files
    zips them & uploads it to ocean marketplace
    """

    if len(inputs) != 1:
        logger.error("Inputs not configured properly in job.yaml")
    
    job_grant_data = [i for i in inputs if i['name'] == 'grant_data_extract'][0]
    df_grant_applications, df_grant_votes = read_job_output(job_grant_data['name'], job_grant_data['id'])

    #ZIP the file grant applications & votes
    temp_dir = tempfile.TemporaryDirectory()
    df_grant_applications.to_csv(os.path.join(temp_dir.name,'grant_applications.csv'),index=False)
    df_grant_votes.to_csv(os.path.join(temp_dir.name,'grant_votes.csv'), index=False)

    zip_files(temp_dir.name, lego_id)

    if config.LOCAL_MODE == False:

        ipfs_file_hash = upload_file_to_ipfs("{}.zip".format(lego_id))
        ipfs_file_location = "{}/ipfs/{}".format(IPFS_OUTPUT_URL_GATEWAY, ipfs_file_hash)
        logger.info('zip file uploaded to IPFS: {}'.format(ipfs_file_location))

        #update asset url in ocean marketplace
        update_asset_url(DATA_ASSET_DID, ipfs_file_location, NETWORK)

    #cleanup
    temp_dir.cleanup()
    