from shroomdk import ShroomDK
import config
import logging
import pandas as pd
import sys
from lib.utils.commons import split

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

FLIPSIDE_SDK = ShroomDK(config.FLIPSIDE_API_KEY)

def run_query(query):
    """
    function to run a query and retrieve the records using flipside sdk
    """

    try:
        response = FLIPSIDE_SDK.query(query,timeout_minutes=15)
        logger.info(f'{response.run_stats.record_count} fetched in {response.run_stats.elapsed_seconds} seconds ')
        return response.records

    except Exception as e:
        logger.info(f"error: {e.message}")

def erc20_assets_count_gte(wallets, value):
    """
    counts the unique assets of given wallet address and return Y/N if it matches the criteria
    """

    logger.info("executing query: {}".format(sys._getframe().f_code.co_name))

    chunk_size = 10000 #to avoid timeout & max limit of 16000

    full_query_records = []

    for wallets_chunk in split(wallets, chunk_size):

        wallets_concatenated= ",".join(["'" + w.lower() + "'" for w in wallets_chunk])

        query_num_assets = """
        SELECT
            user_address AS wallet,
            COUNT(DISTINCT contract_address) AS num_assets
        FROM
            ethereum.core.fact_token_balances
        WHERE
            user_address IN (%s)
        GROUP BY
            user_address
            HAVING num_assets >= %d
        """ % ( wallets_concatenated, value )

        query_records = run_query(query_num_assets)

        full_query_records +=  query_records if query_records != None else []

    return full_query_records


def eth_transactions_value_lte(wallets, value):
    """
    counts the unique assets of given wallet address and return Y/N if it matches the criteria
    """
    
    chunk_size = 10000 #to avoid timeout & max limit of 16000

    full_query_records = []

    for wallets_chunk in split(wallets, chunk_size):

        wallets_concatenated= ",".join(["'" + w.lower() + "'" for w in wallets_chunk])

        query_avg_tx_value = """
        SELECT
            from_address AS wallet
        FROM
            ethereum.core.fact_transactions
        WHERE
            from_address IN (%s)
        GROUP BY
            from_address
        HAVING 
            AVG(eth_value) < %f
        """ % ( wallets_concatenated, value )

        query_records = run_query(query_avg_tx_value)

        full_query_records +=  query_records if query_records != None else []

    return full_query_records


def eth_wallet_age_gte(wallets, value):
    """
    check the age of given wallet address and return Y/N if it matches the criteria
    """
    
    logger.info("executing query: {}".format(sys._getframe().f_code.co_name))

    chunk_size = 10000 #to avoid timeout & max limit of 16000

    full_query_records = []

    for wallets_chunk in split(wallets, chunk_size):

        wallets_concatenated= ",".join(["'" + w.lower() + "'" for w in wallets_chunk])

        query_wallet_age = """
        SELECT
            from_address AS wallet
        FROM
            ethereum.core.fact_transactions
        WHERE
            from_address IN (%s)
        GROUP BY
            from_address
        HAVING
            MIN(block_timestamp) < CURRENT_DATE - INTERVAL '%d YEARS'
        """ % ( wallets_concatenated, value )

        query_records = run_query(query_wallet_age)

        full_query_records +=  query_records if query_records != None else []

    return full_query_records


def interact_with_contracts_call_from_wallet(wallets, contracts):
    """
    check if the wallets have interacted with the given address
    """

    logger.info("executing query: {}".format(sys._getframe().f_code.co_name))

    contracts_concatenated = ",".join(["'" + c.lower() + "'" for c in contracts])

    chunk_size = 10000 #to avoid timeout & max limit of 16000

    full_query_records = []

    for wallets_chunk in split(wallets, chunk_size):

        wallets_concatenated= ",".join(["'" + w.lower() + "'" for w in wallets_chunk])

        query_contract_interactions_from_wallet = """
        SELECT
            DISTINCT from_address AS wallet
        FROM
            ethereum.core.fact_transactions
        WHERE
            from_address IN (%s)
            AND to_address IN (%s)
        """ % ( wallets_concatenated, contracts_concatenated)

        query_records = run_query(query_contract_interactions_from_wallet)

        full_query_records +=  query_records if query_records != None else []

    return full_query_records

def interact_with_contracts_call_to_wallet_eth(wallets, contracts):
    """
    check if the wallets have interacted with the given address
    """

    logger.info("executing query: {}".format(sys._getframe().f_code.co_name))

    contracts_concatenated = ",".join(["'" + c.lower() + "'" for c in contracts])

    chunk_size = 10000 #to avoid timeout & max limit of 16000

    full_query_records = []

    for wallets_chunk in split(wallets, chunk_size):

        wallets_concatenated= ",".join(["'" + w.lower() + "'" for w in wallets_chunk])

        query_contract_interactions_from_wallet = """
        SELECT
            DISTINCT eth_to_address AS wallet
        FROM
            ethereum.core.ez_eth_transfers
        WHERE
            eth_from_address IN ( %s )
            AND eth_to_address IN (%s )
        """ % ( contracts_concatenated, wallets_concatenated )

        query_records = run_query(query_contract_interactions_from_wallet)

        full_query_records +=  query_records if query_records != None else []

    return full_query_records

def interact_with_contracts_call_to_wallet_erc20(wallets, contracts):
    """
    check if the wallets have interacted with the given address
    """

    logger.info("executing query: {}".format(sys._getframe().f_code.co_name))

    contracts_concatenated = ",".join(["'" + c.lower() + "'" for c in contracts])

    chunk_size = 10000 #to avoid timeout & max limit of 16000

    full_query_records = []

    for wallets_chunk in split(wallets, chunk_size):

        wallets_concatenated= ",".join(["'" + w.lower() + "'" for w in wallets_chunk])

        query_contract_interactions = """
        SELECT
            to_address AS wallet
        FROM
            ethereum.core.ez_token_transfers
        WHERE
            from_address IN (%s)
            AND to_address IN (%s) 
            
        """ % ( contracts_concatenated, wallets_concatenated )

        query_records = run_query(query_contract_interactions)

        full_query_records +=  query_records if query_records != None else []

    return full_query_records


def interact_with_contracts(wallets, contracts):


    logger.info("executing query: {}".format(sys._getframe().f_code.co_name))

    query_records = interact_with_contracts_call_from_wallet(wallets, contracts)

    query_records += interact_with_contracts_call_to_wallet_eth(wallets, contracts)

    query_records += interact_with_contracts_call_to_wallet_erc20(wallets, contracts)

    return query_records


def get_token_prices(tokens):
    """
    retrieve pricing information for the given token symbols
    """
    logger.info("executing query: {}".format(sys._getframe().f_code.co_name))
    
    tokens_concatenated = ",".join(["'" + t + "'" for t in tokens])

    query_token_prices = """
    SELECT
        DATE_TRUNC('DAY', HOUR) day,
        symbol,
        MEDIAN(price) AS price_usd
    FROM
        ethereum.core.fact_hourly_token_prices
    WHERE
        symbol IN (%s)
    GROUP BY
        day,
        symbol
    """ % (tokens_concatenated)

    return run_query(query_token_prices)