
import os
import config
from supabase import create_client
from lib.utils.commons import split
import logging

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


SUPABASE_KEY = config.SUPABASE_KEY
SUPABASE_URL = config.SUPABASE_URL
SUPABASE_CLIENT = create_client(SUPABASE_URL, SUPABASE_KEY)


def add_entries_to_projects(projects):
    """
    """  
    data = SUPABASE_CLIENT.table('projects').upsert(projects).execute()
    logger.info("{} records inserted/updated".format(len(data.data)))

def add_entries_to_contributions(contributions):
    """
    """  
    chunk_size = 10000 #to avoid timeout

    for contributions_chunk in split(contributions, chunk_size):

        data = SUPABASE_CLIENT.table('contributions').upsert(contributions_chunk).execute()
        logger.info("{} records inserted/updated".format(len(data.data)))

def add_entries_to_contributor_wallets(contributor_wallets):
    """
    """  
    chunk_size = 10000 #to avoid timeout

    for contributor_wallets_chunk in split(contributor_wallets, chunk_size):

        data = SUPABASE_CLIENT.table('contributor_wallets').upsert(contributor_wallets_chunk).execute()
        logger.info("{} records inserted/updated".format(len(data.data)))