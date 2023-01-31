
from lib.utils.storage import upload_df_to_ipfs, get_csv_from_ipfs, get_json_from_ipfs
from lib.data.chain.fetch_from_thegraph import get_all_votes, get_rounds_info, get_round_applications
from datetime import datetime
import pandas as pd
import logging
import config

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

TOKENS = config.TOKENS
ROUNDS = config.ROUNDS

def fetch_past_grants_data(file_hash):
    """
    fetches past grant votes data for the round, if available
    """

    #read the last updated file & get the block number to start the processing from
    if file_hash != '':
        logger.info('fetched last updated data')
        df_grants_data = get_csv_from_ipfs(file_hash)
        start_block_number = int(df_grants_data.created_at_block.max())
        return df_grants_data, start_block_number
    else:
        logger.info('no records to fetch')
        return None, 0


def map_token_to_symbol(token):
    """
    token address are stored on chain
    this function maps the token address to symbol
    """

    if token in TOKENS:
        return TOKENS[token]
    else:
        return token

def map_round_to_name(round_address):
    """
    round address are stored on chain
    this function maps the round address to the configured round name
    """

    if round_address in ROUNDS:
        return ROUNDS[round_address]
    else:
        return round_address

def fetch_latest_vote_information(round_address, start_block_number):
    """
    fetches latest vote information from subgraph
    """

    #fetch votes information for the given round from the graph network
    logger.info('fetching votes from {}'.format(start_block_number))

    fetched_votes = get_all_votes(round_address, start_block_number)

    if len(fetched_votes) == 0:
        logger.info('No new votes')
        return None

    df_fetched_votes = pd.DataFrame(fetched_votes).drop_duplicates()

    #map token to symbol
    df_fetched_votes['token'] = df_fetched_votes['token'].map(lambda x: map_token_to_symbol(x))

    #map token to symbol
    df_fetched_votes['round_name'] = df_fetched_votes['roundAddress'].map(lambda x: map_round_to_name(x))

    #convert amount: TODO
    df_fetched_votes['amount'] = df_fetched_votes['amount'].map(lambda x: int(x)/1e18)

    #convert created_at to date format
    df_fetched_votes['blockTimestamp'] = df_fetched_votes['blockTimestamp'].map(lambda x:  datetime.fromtimestamp(int(x)).strftime('%Y-%m-%d %H:%M:%S'))

    df_fetched_votes['application_id'] = df_fetched_votes.projectId.str.cat(df_fetched_votes.roundAddress, sep='-') 

    #rename as per the expected schema
    cols = {
        'voter' : 'source_wallet',
        'grantAddress' : 'destination_wallet',
        'roundAddress': 'round',
        'blockTimestamp' : 'created_at',
        'blockNumber' : 'created_at_block',
        'transactionHash' : 'transaction_hash',
        'projectId' : 'project_id'
    }

    df_fetched_votes.rename(columns=cols, inplace=True)
    logger.info('{} votes fetched'.format(df_fetched_votes.shape[0]))

    output_cols = ['id', 'application_id', 'project_id', 'round', 'round_name', 'token', 'amount', 'source_wallet', 'destination_wallet', 'created_at_block', 'created_at', 'transaction_hash']

    return df_fetched_votes[output_cols]


def read_application_metadata_from_protocol(application):
    """
    application metadata holds the project info
    fetches the application metadata from ipfs files
    """

    response = get_json_from_ipfs(application['metaPtrPointer'])
    application_info = response['application']

    application_metadata = {
        "id" : application['projectId'] + "-" + application_info['round'],
        "project" : application['projectId'] ,
        "status" : "NOT APPROVED",
        "created_at" : datetime.fromtimestamp(application_info.get('project',{}).get('createdAt',0)/1000).strftime('%Y-%m-%d %H:%M:%S'),
        "updated_at" : datetime.fromtimestamp(application_info.get('project',{}).get('createdAt',0)/1000).strftime('%Y-%m-%d %H:%M:%S'),
        "application_round": application_info['round'],
        "application_round_name" : map_round_to_name(application_info['round']),
        "wallet_address" : application_info['recipient'],
        "last_updated" : application_info.get('project',{}).get('lastUpdated',0),
        "project_id" : application_info.get('project',{}).get('id',''),
        "title" : application_info.get('project',{}).get('title',''),
        "description" : application_info.get('project',{}).get('description',''),
        "website" : application_info.get('project',{}).get('website',''),
        "github_user" : application_info.get('project',{}).get('userGithub',''),
        "project_github" : application_info.get('project',{}).get('projectGithub',''),
        "project_twitter" : application_info.get('project',{}).get('projectTwitter',''),
        "previous_funding" : [q['answer'] for q in application_info.get('answers') if q['question']=='Funding Sources'][0] if len([q['answer'] for q in application_info.get('answers') if q['question']=='Funding Sources']) > 0 else '' ,
        "team_size" : [q['answer'] for q in application_info.get('answers') if q['question']=='Team Size'][0] if len([q['answer'] for q in application_info.get('answers') if q['question']=='Team Size']) > 0 else '' ,
        "verified_twitter_or_github" : [q['answer'] for q in application_info.get('answers') if q['question']=='Have you verified your Github and/or Twitter on Grants Hub?'][0] if len([q['answer'] for q in application_info.get('answers') if q['question']=='Have you verified your Github and/or Twitter on Grants Hub?']) > 0 else '' 
    }

    return application_metadata


def fetch_application_information(round_address, status_meta_ptr):
    """
    fetches information for all applications in the given round
    """

    applications = get_round_applications(round_address)
    logger.info("fetched {} applications".format(len(applications)))

    #UPDATE project status
    application_status = get_json_from_ipfs(status_meta_ptr)

    def check_status(pid):
        for a in application_status:
            if pid == a['id'] and a['status']=='APPROVED':
                return 'APPROVED'
        return 'NOT APPROVED'
    
    #GET all project information
    grant_applications = []
    for application in applications:

        pid = application['projectId'] + '-' + application['roundAddress']

        if check_status(pid) == 'APPROVED':

            #TODO : check for protocol
            application_metadata = read_application_metadata_from_protocol(application)
            application_metadata['status'] = 'APPROVED'
            grant_applications.append(application_metadata)

    df_grant_applications = pd.DataFrame(grant_applications)

    #TODO: check how duplicates can occur
    df_grant_applications = df_grant_applications.drop_duplicates()

    logger.info("fetched {} approved applications".format(df_grant_applications.shape[0]))

    return df_grant_applications

def extract_latest_grants_data(grants_data):
    """
    - extracts past collected grant data
    - reads the delta from chain
    - writes back the combined file
    """
    
    grants = get_rounds_info()

    for grant in grants:

        round_address = grant['roundAddress']

        if round_address not in grants_data:
            grants_data[round_address] = {}

        logger.info('starting round {}'.format(round_address))

        last_updated_metaptr = grants_data[round_address].get('metaptr','')
    
        #load/reload application data if the metaptr is changed i.e the grant projects approval status is updated
        if last_updated_metaptr == '' or last_updated_metaptr != grant['metaPtrPointer']:
            
            df_grant_applications = fetch_application_information(round_address, grant['metaPtrPointer'])

            #write file to ipfs and update the ipfs location in data nft
            ipfs_file_hash = upload_df_to_ipfs(df_grant_applications)

            grants_data[round_address]['applications'] = ipfs_file_hash
            grants_data[round_address]['metaptr'] = grant['metaPtrPointer']
        
        #read past data and collect new data for the round
        last_updated_votes_file_hash = grants_data[round_address].get('votes','')
        df_grants_data, start_block_number = fetch_past_grants_data(last_updated_votes_file_hash)
        df_fetched_votes = fetch_latest_vote_information(round_address, start_block_number)

        if df_fetched_votes is not None:
            #write the combined data to the network
            df_updated_grants_data = pd.concat([df_grants_data, df_fetched_votes]).drop_duplicates()
            ipfs_file_hash = upload_df_to_ipfs(df_updated_grants_data)
            grants_data[round_address]['votes'] = ipfs_file_hash
        
    return grants_data
