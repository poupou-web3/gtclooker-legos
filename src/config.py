import os
import json

#run mode
LOCAL_MODE = os.getenv("RUN_MODE","") == "local"

#convention to call/write functions
RUN_MODULE = "jobs.{}.run" #placeholder for the job name
RUN_METHOD = "run_job"

IO_MODULE = "jobs.{}.io"
IO_METHOD = "get_data"

# Job Configuration
JOB_CONFIG = "job.yaml"

# Off chain grants data:  TODO read from other source
with open('data/token_mapping.json') as content:
  TOKENS = json.loads(content.read())

#TODO check if this info can be obtained from chain
with open('data/grant_rounds_mapping.json') as content:
  ROUNDS = json.loads(content.read())

# read onchain data from flipside
FLIPSIDE_API_KEY=os.getenv("FLIPSIDE_API_KEY","")

# stores wallet tagging configuration
TAG_FILE = "configs/tag.yaml"

# stores risk score configuration for UI
RISK_CONFIG_FILE = "configs/risk_score.yaml"

# ocean protocol related env variables
NETWORK = os.getenv("NETWORK","")
ACCOUNT_PRIVATE_KEY = os.getenv("ACCOUNT_PRIVATE_KEY","")
DATA_NFT_ADDRESS = os.getenv("DATA_NFT_ADDRESS","") #to update data store
DATA_ASSET_DID = os.environ["DATA_ASSET_DID"] #to update data asset in marketplace

# IPFS file related env variables
IPFS_INFURA_PROJECT_ID = os.getenv("IPFS_INFURA_PROJECT_ID", "")#to upload files to ipfs
IPFS_INFURA_SECRET_KEY = os.getenv("IPFS_INFURA_SECRET_KEY", "") #to upload files to ipfs
IPFS_INFURA_GATEWAY = os.getenv("IPFS_INFURA_GATEWAY", "") #to read files from ipfs
IPFS_INFURA_ENDPOINT = "https://ipfs.infura.io:5001/api/v0/add" #static endpoint
IPFS_GATEWAYS = ["https://gateway.pinata.cloud", IPFS_INFURA_GATEWAY] #use multiple endpoints to avoid timeout errors

# UI related creds
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# Subgraph URL
GRAPH_GITCOIN_GRANTS_URL = os.getenv("GRAPH_GITCOIN_GRANTS_URL","")

# To get twitter info about projects
TWITTER_API_KEY=os.getenv("TWITTER_API_KEY", "")
TWITTER_API_KEY_SECRET=os.getenv("TWITTER_API_KEY_SECRET", "")
TWITTER_ACCESS_TOKEN=os.getenv("TWITTER_ACCESS_TOKEN", "")
TWITTER_ACCESS_TOKEN_SECRET=os.getenv("TWITTER_ACCESS_TOKEN_SECRET", "")
