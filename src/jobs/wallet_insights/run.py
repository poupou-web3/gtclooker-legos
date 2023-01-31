import logging

from lib.utils.job import read_job_output
from lib.utils.commons import read_yaml
from lib.utils.storage import upload_df_to_ipfs
from lib.utils.ocean import create_update_key_value_pair
import lib.wallet.tagger as tagger
import config

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

TAG_FILE = config.TAG_FILE
NETWORK = config.NETWORK
DATA_NFT_ADDRESS = config.DATA_NFT_ADDRESS


def get_input_data(inputs):

    #READ output of dependent jobs
    job_grant_data = [i for i in inputs if i['name'] == 'grant_data_extract'][0]
    df_grant_applications , df_grant_votes = read_job_output(job_grant_data['name'], job_grant_data['id'])

    #GET derived values
    wallets = list(set(list(df_grant_votes.source_wallet.unique()) + list(df_grant_applications.wallet_address.unique())))

    return wallets

def run_job(lego_id, inputs, params):

    logger.info("starting job:{}".format(lego_id))

    #read tag configurations & load only the required ones
    all_tags = read_yaml(TAG_FILE)['tags']
    provided_tag_names = params.get('tags',[])
    seleced_tags = [tag for tag in all_tags if tag['name'] in provided_tag_names]

    wallets = get_input_data(inputs)

    logger.info("retrieved {} wallets".format(len(wallets)))

    df_result = tagger.tag(wallets, seleced_tags)

    if config.LOCAL_MODE:
        df_result.to_csv(lego_id, index=False)
    else:
        ipfs_hash = upload_df_to_ipfs(df_result)
        create_update_key_value_pair(lego_id, ipfs_hash, NETWORK, DATA_NFT_ADDRESS)

        