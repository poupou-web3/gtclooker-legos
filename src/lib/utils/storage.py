import os
import time
import csv
import requests
import pandas as pd
import logging
import random
import config
import tempfile
import shutil
import json

from itertools import cycle


logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Connect to the IPFS cloud service
IPFS_INFURA_PROJECT_ID = config.IPFS_INFURA_PROJECT_ID
IPFS_INFURA_SECRET_KEY = config.IPFS_INFURA_SECRET_KEY
IPFS_INFURA_GATEWAY = config.IPFS_INFURA_GATEWAY
IPFS_INFURA_ENDPOINT = config.IPFS_INFURA_ENDPOINT
IPFS_GATEWAYS = config.IPFS_GATEWAYS


def upload_to_ipfs(file_path):
    """
    uploads files to IPFS using Pinata Cloud
    """

    files = {"file": open(file_path, "rb")}

    response = requests.post(
        IPFS_INFURA_ENDPOINT,
        files=files,
        auth=(IPFS_INFURA_PROJECT_ID, IPFS_INFURA_SECRET_KEY),
    )

    response_ipfs = json.loads(response.text)

    return response_ipfs["Hash"]


def get_file_from_ipfs(file_hash, local_file_name):

    retry = 0
    gateway_iterator = cycle(IPFS_GATEWAYS)

    while retry < 3:
        try:
            file_path = "{}/ipfs/{}".format(next(gateway_iterator), file_hash)
            logger.info(file_path)

            response = requests.get(file_path)

            if response.ok:
                with open(os.path.join(local_file_name), "wb") as f:
                    f.write(response.content)
                return True
            else:
                logger.info(response.text)
        except Exception as e:
            logger.info(e)
            pass

        retry = retry + 1
        time.sleep(60)

    return False


def get_csv_from_ipfs(file_hash):

    tmp_file_name = file_hash + ".csv"
    get_file_from_ipfs(file_hash, tmp_file_name)
    df = pd.read_csv(tmp_file_name)
    os.remove(tmp_file_name)
    return df


def get_json_from_ipfs(file_hash):

    tmp_file_name = file_hash + ".json"
    get_file_from_ipfs(file_hash, tmp_file_name)
    with open(tmp_file_name) as f:
        json_data = json.load(f)
    os.remove(tmp_file_name)
    return json_data


def upload_df_to_ipfs(df_data):
    """
    writes the file
    """

    tmp_file_path = "tmp.csv"
    df_data.to_csv(tmp_file_path, index=False)

    ipfs_hash = upload_to_ipfs(tmp_file_path)

    os.remove(tmp_file_path)  # cleanup
    logger.info("data updated to {}".format(ipfs_hash))

    return ipfs_hash


def zip_files(dir_name, zip_file_name_without_ext):
    
    shutil.make_archive(zip_file_name_without_ext, "zip", dir_name)
    


def upload_file_to_ipfs(file, remove=True):

    ipfs_hash = upload_to_ipfs(file)

    if remove:
        os.remove(file)  # cleanup

    return ipfs_hash


def upload_dict_to_ipfs(dict_data):
    tmp_file = "dict.json"
    with open(tmp_file, "w") as fp:
        json.dump(dict_data, fp)

    ipfs_hash = upload_to_ipfs(tmp_file)
    os.remove(tmp_file)

    return ipfs_hash


def get_json(file):

    try:
        with open(file) as f:
            json_data = json.load(f)

        return json_data
    except:
        logger.info("local file doesn't exist. setting to empty")
        return {}

def write_json(data, file):

    with open(file, 'w') as fp:
        json.dump(data, fp)