
# Please read [this](https://www.canva.com/design/DAFZQUHbKc8/agH9xR62sv3k1rTnEV5Whw/view?) to get an understanding of this module

# The information from these legos are tied into [grantlooker.xyz](https://www.grantlooker.xyz/projects)

 ## Legos
--------

| Name               | Category         | Job                          | Description |
| -------------------| ------------ | ---------------------------- | ----- |
| Grant Data Extract | Data Extraction | [grant_data_extract](https://github.com/kikura3/gtclooker-legos/tree/master/src/jobs/grant_data_extract) | Extract Grant Applications and Votes Data from Chain, Update to IPFS      |
| Grant Data Aggregate | Data Extraction   | [grant_data_aggregate](https://github.com/kikura3/gtclooker-legos/tree/master/src/jobs/grant_data_aggregate)        |   Extract Data from IPFS, Aggregate and Update Asset in Ocean Protocol for Community's Near Real-Time Access    |
| Farmer | Metrics  | [wallet_insights](https://github.com/kikura3/gtclooker-legos/tree/master/src/jobs/wallet_insights) | Tag Grantee/Contributor Wallets Meeting Farmer Criteria |
| Money Mixer | Metrics | [wallet_insights](https://github.com/kikura3/gtclooker-legos/tree/master/src/jobs/wallet_insights)  | Tag Grantee/Contributor Wallets Interacted with Tornado Cash |
| On Chain History | Metrics | [wallet_insights](https://github.com/kikura3/gtclooker-legos/tree/master/src/jobs/wallet_insights) | Tag Grantee/Contributor Wallets with Onchain History |
| Vote Twitter Imbalance | Metrics | [project_insights](https://github.com/kikura3/gtclooker-legos/tree/master/src/jobs/project_insights)  | Tag Projects with More Votes Than Twitter Followers|
| Transform Insights to DB | Data Load | [transform_data_to_db](https://github.com/kikura3/gtclooker-legos/tree/master/src/jobs/transform_data_to_db)  | Collect Insights and Store in SQL Database for UI Display |

Jobs and their dependencies are configured in [jobs.yaml](https://github.com/kikura3/gtclooker-legos/blob/master/src/job.yaml)
-----
&nbsp;

# How to setup and run the legos?

[Setup Instructions](/docs/HowToRun.md)

&nbsp;

# How does the legos work?

## Grant Data Extract : Lego

![grant_data_extract](/docs/grant_data_extract.png)

&nbsp;

## Grant Data Aggregate : Lego

![grant_data_aggregate](/docs/grant_data_aggregate.png)

## Wallet Insights(Farmer, MoneyMixer etc) : Lego


![wallet_insights](/docs/wallet_configuration.png)

![wallet_insights](/docs/wallet_insights.png)

## Project Insights(Vote Twitter Imbalance etc) : Lego

![project_insights](/docs/project_insights.png)

## Transform Insights : Lego

![project_insights](/docs/transform_insights.png)

![dashboard_lego](/docs/dashboard_lego.png)

# How to integrate community lego?

![community_lego](/docs/community_adapter.png)


## FAQ

1. How to get new round data?
Modify [subgraph](https://github.com/kikura3/gitcoin-grant-data-subgraph) to include the new round address and voting address. The grant extract job will automatically fetch all the rounds available in the graph.

2. What are the contracts used by the deployed version?

```
Polygon Test:
0x9F34594703B35052c698DCF8cad0fBeEd9C90560 (Data store)
did:op:19890202b2f6625f068af1297def7e35fadabeb3466a31278bd0cd293ca8374a (Data Asset)

Polygon Prod:
0x9013a394028D5c0CCaaa7Bd751793ccaC5ce481B (Data store)
did:op:5e51587660fc4b58f1626e2d675d6094ce2562313d67f4808206ae11bb143dcf (Data Asset)
```

----------




