import argparse
import logging
from lib.utils.commons import read_yaml
import numpy as np
import pandas as pd
import os

import importlib

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

TAG_MODULE = "lib.wallet.tag"

def run_step(step, wallets):

    module = importlib.import_module(TAG_MODULE)
    function = getattr(module, step['call'])
    step['params']['wallets'] = wallets
    result = function(**step['params'])
    return result


def tag(wallets, tags):

    tag_results = {}
    for tag in tags:

        step_results = [True for i in range(len(wallets))] #assume True to start with
        for step in tag['steps']:
            step_result = run_step(step, wallets)
            step_results = np.logical_and(step_results, step_result)
        
        tag_results[tag['name']] = step_results
    
    df_result = pd.DataFrame(tag_results)
    df_result['wallet'] = wallets
    return df_result
