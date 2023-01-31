import pandas as pd
import config
from lib.utils.commons import read_yaml
import lib.data.chain.fetch_from_flipside as chain_data
from lib.utils.db import add_entries_to_contributor_wallets

RISK_CONFIG_FILE = config.RISK_CONFIG_FILE


def load_risk_scores():

    risk_config = read_yaml(RISK_CONFIG_FILE)
    tag_scores = {}
    for c in risk_config['scores']:
        if c['name'] == 'Contributor':
            for tag in c['tags']:
                tag_scores[tag['name']] = {
                    'value' : tag['value'],
                    'points' : tag['points']
                }

    return tag_scores

def get_tags(row, tag_cols):

    tags = []
    for tag in tag_cols:
        if row[tag]:
            tags.append(tag + " ✅")
        else:
            tags.append(tag + " ❌")

    return { "tags" : tags }

def get_risk_score(row, tag_scores):
    score = 0
    
    for tag in tag_scores.keys():
        if row[tag] == tag_scores[tag]['value']:
            score = score + tag_scores[tag]['points']
    return score

def update(df_grant_votes, df_contributor_wallets):
    """ 
    """
    #filter only contributors

    df_contributor_wallets = df_contributor_wallets[df_contributor_wallets.wallet.isin(set(df_grant_votes.source_wallet.unique()))].reset_index(drop=True)

    #TODO all cols are tags except wallet
    tag_cols =[c for c in df_contributor_wallets.columns if c != 'wallet']

    df_contributor_wallets["tags"] = df_contributor_wallets.apply(
        lambda x: get_tags(
            x, tag_cols
        ), axis=1
    )

    tag_scores = load_risk_scores()
    df_contributor_wallets["risk_score"] = df_contributor_wallets.apply(
        lambda x: get_risk_score(
            x[tag_cols], tag_scores
        ), axis=1
    )

    #RENAME cols as per db
    rename_cols = {
        'wallet' : 'id'
    }

    df_contributor_wallets.rename(columns=rename_cols, inplace=True)

    db_cols = [
        "id",
        "tags",
        "risk_score"
    ]

    add_entries_to_contributor_wallets(df_contributor_wallets[db_cols].to_dict(orient="records"))
