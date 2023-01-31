#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
File: fetch_from_thegraph.py
Author: kikura
Description: fetches gitcoin grants data from the subgraph
"""

import requests
import logging
import pandas as pd
import config

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

GRAPH_GITCOIN_GRANTS_URL = config.GRAPH_GITCOIN_GRANTS_URL

#TODO: pagination
def get_round_applications(round_address):

  applications_query = """{
    applications(first: 1000, where: {roundAddress: "%s"}) {
      id
      projectId
      roundAddress
      metaPtrProtocol
      metaPtrPointer
      blockNumber
    }
  }
  """ % ( round_address )

  response = requests.post(GRAPH_GITCOIN_GRANTS_URL, json={'query': applications_query})

  if response.ok:

    #since the project can be updated multiple times, retrieve information from latest update
    df_applications = pd.DataFrame(response.json()['data']['applications'])
    idx = df_applications.groupby(['projectId'])['blockNumber'].transform(max) == df_applications['blockNumber']
    return df_applications[idx].to_dict(orient="records")

  else:
    logger.info(response.text)
    return None


#TODO: More than 100 rounds needs pagination
def get_rounds_info():

  projects_query = """{
    projects(first:1000){
      roundAddress
      metaPtrProtocol
      metaPtrPointer
      blockNumber
    }
  }
  """

  response = requests.post(GRAPH_GITCOIN_GRANTS_URL, json={'query': projects_query})

  if response.ok:
    #since the project can be updated multiple times, retrieve the latest one
    df_projects = pd.DataFrame(response.json()['data']['projects'])
    idx = df_projects.groupby(['roundAddress'])['blockNumber'].transform(max) == df_projects['blockNumber']
    return df_projects[idx].to_dict(orient="records")
  else:
    logger.info(response.text)
    return None

#TODO: Sequential ID to be generated from the subgraph to make pagination easier
def get_all_votes(round_address, from_block_number):

  votes_query_template = """{
    votes(first: %d, skip: %d, orderBy: blockNumber, where: {blockNumber_gte: %d, roundAddress: "%s"}) {
      id
      token
      amount
      voter
      blockNumber
      blockTimestamp
      grantAddress
      projectId
      roundAddress
      transactionHash
    }
  }
  """ 

  first = 1000 #max records supported by thegraph network
  skip = 0
  block_number = from_block_number

  votes = []

  
  while True:

    votes_query = votes_query_template % (first, skip, block_number, round_address)
    response = requests.post(GRAPH_GITCOIN_GRANTS_URL, json={'query': votes_query})

    if response.ok:
      fetched_votes = response.json()['data']['votes']

      if len(fetched_votes) == 0: #retrieved all the records
        break
      
      votes += fetched_votes

      #TODO bad assumption : a single block will not have more than 1000 votes
      #skip is not working beyond 6000 entries
      last_read_block_number = int(max([v['blockNumber'] for v in votes]))
      if block_number == last_read_block_number:
        break

      block_number = last_read_block_number
          
    else:
        logger.info(response.text)
        break

  #remove duplicates due to the assumption
  votes = [dict(vote) for vote in {tuple(vote.items()) for vote in votes}]

  return votes
