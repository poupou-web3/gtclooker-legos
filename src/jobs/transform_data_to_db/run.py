import logging
import importlib
import config
import pandas as pd
from lib.utils.db import add_entries_to_projects
import jobs.transform_data_to_db.tables.projects as projects
import jobs.transform_data_to_db.tables.contributions as contributions
import jobs.transform_data_to_db.tables.contributor_wallets as contributor_wallets
from lib.utils.job import read_job_output

import lib.data.chain.fetch_from_flipside as chain_data
import os

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

#convention to call/write functions
RUN_MODULE = config.RUN_MODULE
RUN_METHOD = config.RUN_METHOD

IO_MODULE = config.IO_MODULE
IO_METHOD = config.IO_METHOD


def run_job(lego_id, inputs, params):
    logger.info("starting job:{}".format(lego_id))
    logger.info("starting job:{}".format(inputs))

    job_grant_data = [i for i in inputs if i['name'] == 'grant_data_extract'][0]
    df_grant_applications, df_grant_votes = read_job_output(job_grant_data['name'], job_grant_data['id'])

    job_wallet_insights = [i for i in inputs if i['name'] == 'wallet_insights'][0]
    df_wallet_tags_1 = read_job_output(job_wallet_insights['name'], job_wallet_insights['id'])

    job_stefi_insights_adapter = [i for i in inputs if i['name'] == 'community_stefi_insights_adapter'][0]
    df_wallet_tags_2 = read_job_output(job_stefi_insights_adapter['name'], job_stefi_insights_adapter['id'])

    df_wallet_tags = df_wallet_tags_1.merge(df_wallet_tags_2, on="wallet", how="left").fillna(False)

    job_project_insights = [i for i in inputs if i['name'] == 'project_insights'][0]
    df_project_tags = read_job_output(job_project_insights['name'], job_project_insights['id'])

    projects.update(df_grant_applications, df_grant_votes, df_wallet_tags, df_project_tags)
    contributor_wallets.update(df_grant_votes, df_wallet_tags)
    contributions.update(df_grant_votes)
    
    
