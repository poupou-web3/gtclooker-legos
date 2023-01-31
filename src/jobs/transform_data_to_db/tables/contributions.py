import pandas as pd


import lib.data.chain.fetch_from_flipside as chain_data
from lib.utils.db import add_entries_to_contributions

def get_token_prices(tokens):

    #TODO when both WETH/ETH is present
    tokens = ['WETH' if t=='ETH' else t.upper() for t in tokens]

    token_prices = chain_data.get_token_prices(tokens)
    df_token_prices = pd.DataFrame(token_prices)

    #switch back WETH to ETH
    df_token_prices['symbol'] = df_token_prices['symbol'].map(lambda x: 'ETH' if x=='WETH' else x)

    return df_token_prices

def add_token_prices_to_votes(df_grant_votes):

    tokens = list(df_grant_votes.token.unique())
    df_token_prices = get_token_prices(tokens) #TODO : add it to grant data extract
    df_grant_votes.loc[:,'created_at'] = pd.to_datetime(df_grant_votes['created_at']).dt.date
    df_token_prices['day'] = pd.to_datetime(df_token_prices['day']).dt.date

    df_grant_votes_merged = df_grant_votes.merge(df_token_prices, left_on=['created_at','token'], right_on=['day','symbol'])
    df_grant_votes_merged['amount_usd'] = df_grant_votes_merged['amount'] * df_grant_votes_merged['price_usd']
    return df_grant_votes_merged

def add_tags_to_projects(df_grant_applications, df_wallets):

    tag_cols =[c for c in df_wallets.columns if c!= 'wallet']
    df_grant_data =  df_grant_applications.merge(df_wallets, left_on="wallet_address", right_on="wallet")
    return df_grant_data, tag_cols

def update(df_grant_votes):
    """ 
    """
    
    #ADD token prices to votes
    df_contributions = add_token_prices_to_votes(df_grant_votes)

    #RENAME cols as per db
    rename_cols = {
        'application_id' : 'project_id',
        'project_id' : 'project',
        'source_wallet' : 'wallet_id',
        'amount_usd' : 'amount_contributed_usd',
    }
    df_contributions.rename(columns=rename_cols, inplace=True)

    #COMBINE multiple contributions into one
    df_contributions = df_contributions.groupby(["id", "project_id","wallet_id"])["amount_contributed_usd"].sum().reset_index()


    db_cols = [
        "id",
        "project_id",
        "wallet_id",
        "amount_contributed_usd"
    ]

    
    add_entries_to_contributions(df_contributions[db_cols].to_dict(orient="records"))
