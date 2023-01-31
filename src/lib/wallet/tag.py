
import lib.data.chain.fetch_from_flipside as chain_data


def check_wallets(wallets, results):
    """
    This function takes in a query and a list of wallets as input, 
    and returns a list of boolean values indicating whether each wallet in the input list is present in the query results.
    
    Args:
    query (str) : The query to be run
    wallets (list) : A list of wallets to check against the query results

    Returns:
    list : A list of boolean values indicating whether each wallet in the input list is present in the query results.
    """

    matched_wallets = [w['wallet'] for w in results] if results is not None else []
    result = [w in matched_wallets for w in wallets]
    return result


def erc20_assets_count_gte(**kwargs):

    wallets = kwargs['wallets']
    value = kwargs['value']
    results = chain_data.erc20_assets_count_gte(wallets, value)
    return check_wallets(wallets, results)


def eth_transactions_value_lte(**kwargs):

    wallets = kwargs['wallets']
    value = kwargs['value']
    results = chain_data.eth_transactions_value_lte(wallets, value)
    return check_wallets(wallets, results)


def eth_wallet_age_gte(**kwargs):

    wallets = kwargs['wallets']
    value = kwargs['value']
    results = chain_data.eth_wallet_age_gte(wallets, value)
    return check_wallets(wallets, results)


def interact_with_contracts(**kwargs):

    wallets = kwargs['wallets']
    value = kwargs['value']
    results = chain_data.interact_with_contracts(wallets, value)
    return check_wallets(wallets, results)