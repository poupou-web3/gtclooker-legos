import logging

from lib.utils.job import read_job_output
from lib.utils.commons import read_yaml
from lib.utils.storage import upload_df_to_ipfs
from lib.utils.ocean import create_update_key_value_pair
from lib.utils.twitter import get_followers_count
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
    return df_grant_applications, df_grant_votes


def compute_twitter_votes_ratio(df_grant_applications, df_grant_votes):
    """
    TODO: make the tags configurable
    """

    df_grant_applications['twitter_followers'] = df_grant_applications['project_twitter'].map(lambda x:get_followers_count(x))

    df_grouped_by_app_id = df_grant_votes.groupby(["application_id"])["id"].count().reset_index()
    df_grouped_by_app_id.columns = ['project', 'votes_count']

    df_merged = df_grant_applications[['id','twitter_followers']].merge(df_grouped_by_app_id, left_on="id", right_on="project")

    df_merged['metric_twitter_votes_ratio'] = df_merged['votes_count'] / df_merged['twitter_followers']

    df_merged['VoteTwitterImbalance'] = df_merged['metric_twitter_votes_ratio'].map(lambda x: x > 1)

    return df_merged[['project','VoteTwitterImbalance']]


def run_job(lego_id, inputs, params):

    logger.info("starting job:{}".format(lego_id))


    df_grant_applications, df_grant_votes = get_input_data(inputs)

    #result <project,tag_name_boolean>
    df_result = compute_twitter_votes_ratio(df_grant_applications, df_grant_votes)

    if config.LOCAL_MODE:
        df_result.to_csv(lego_id, index=False)
    else:
        ipfs_hash = upload_df_to_ipfs(df_result)
        create_update_key_value_pair(lego_id, ipfs_hash, NETWORK, DATA_NFT_ADDRESS)

        