import pandas as pd
import config
from lib.utils.commons import read_yaml
import lib.data.chain.fetch_from_flipside as chain_data
from lib.utils.db import add_entries_to_projects

RISK_CONFIG_FILE = config.RISK_CONFIG_FILE


def load_risk_scores():

    risk_config = read_yaml(RISK_CONFIG_FILE)
    tag_scores = {}
    for c in risk_config['scores']:
        if c['name'] == 'Grantee':
            for tag in c['tags']:
                tag_scores[tag['name']] = {
                    'value' : tag['value'],
                    'points' : tag['points']
                }

    return tag_scores

def form_gitcoin_url(round, project):
    """
    form gitcoin url by convention
    TODO: need to validate so that it doesn't break in the future
    """

    return "https://grant-explorer.gitcoin.co/#/round/1/{}/{}-{}".format(
        round, project, round
    )



def get_num_votes(df_grant_votes):

    num_votes = df_grant_votes.shape[0]
    return num_votes


def get_num_contributors(df_grant_votes):

    num_contributors = len(df_grant_votes.source_wallet.unique())
    return num_contributors


def get_total_amount_contributed_usd(df_grant_votes):

    return df_grant_votes.amount_usd.sum()


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
    df_token_prices = get_token_prices(tokens)
    df_grant_votes.loc[:,'created_at'] = pd.to_datetime(df_grant_votes['created_at']).dt.date
    df_token_prices['day'] = pd.to_datetime(df_token_prices['day']).dt.date

    df_grant_votes_merged = df_grant_votes.merge(df_token_prices, left_on=['created_at','token'], right_on=['day','symbol'])
    df_grant_votes_merged['amount_usd'] = df_grant_votes_merged['amount'] * df_grant_votes_merged['price_usd']
    return df_grant_votes_merged


def add_tags_to_projects(df_grant_applications, df_project_wallet_tags, df_project_tags):

    project_wallet_tag_cols =[c for c in df_project_wallet_tags.columns if c!= 'wallet']
    df_grant_data =  df_grant_applications.merge(df_project_wallet_tags, left_on="wallet_address", right_on="wallet")

    project_tag_cols =[c for c in df_project_tags.columns if c!= 'project']
    df_grant_data =  df_grant_data.merge(df_project_tags, left_on="id", right_on="project", how="left")

    #temp fix
    df_grant_data = df_grant_data.rename(columns={"project_x": "project"})

    return df_grant_data, project_wallet_tag_cols + project_tag_cols

def update(df_projects, df_grant_votes, df_project_wallet_tags, df_project_tags):
    """ 
    """
    
    #ADD token prices to votes
    df_grant_votes = add_token_prices_to_votes(df_grant_votes)

    #ADD tags to project/applications
    df_projects, tag_cols = add_tags_to_projects(df_projects, df_project_wallet_tags, df_project_tags)

    tag_scores = load_risk_scores()

    #consider the ones that has been configured
    tag_cols = list(set(tag_scores.keys()).intersection(tag_cols))

    df_projects["profile_pic"] = ""
    df_projects["banner_pic"] = ""
    df_projects["gitcoin_url"] = df_projects.apply(
        lambda x: form_gitcoin_url(x["application_round"], x["project"]), axis=1
    )

    df_projects["num_votes"] = df_projects.id.map(
        lambda x: get_num_votes(df_grant_votes[df_grant_votes.application_id == x])
    )

    df_projects["num_contributors"] = df_projects.id.map(
        lambda x: get_num_contributors(
            df_grant_votes[df_grant_votes.application_id == x]
        )
    )

    df_projects["total_amount_contributed_usd"] = df_projects.id.map(
        lambda x: get_total_amount_contributed_usd(
            df_grant_votes[df_grant_votes.application_id == x]
        )
    )

    df_projects["tags"] = df_projects.apply(
        lambda x: get_tags(
            x, tag_cols
        ), axis=1
    )

    
    df_projects["risk_score"] = df_projects.apply(
        lambda x: get_risk_score(
            x[tag_cols], tag_scores
        ), axis=1
    )


    #RENAME cols as per db
    rename_cols = {
        'application_round' : 'round_id'
    }

    df_projects.rename(columns=rename_cols, inplace=True)

    db_cols = [
        "id",
        "project",
        "status",
        "created_at",
        "updated_at",
        "round_id",
        "wallet_address",
        "title",
        "profile_pic",
        "banner_pic",
        "gitcoin_url",
        "num_votes",
        "num_contributors",
        "total_amount_contributed_usd",
        "tags",
        "risk_score"
    ]

    df_projects = df_projects[db_cols].fillna('')

    add_entries_to_projects(df_projects.to_dict(orient="records"))
