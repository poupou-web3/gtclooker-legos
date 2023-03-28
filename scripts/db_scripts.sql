create table
  projects (
    id text primary key,
    project text,
    status text,
    round_id text,
    wallet_address text,
    title text,
    profile_pic text,
    banner_pic text,
    gitcoin_url text,
    tags jsonb,
    risk_score int,
    num_votes bigint,
    num_contributors bigint,
    total_amount_contributed_usd money,
    created_at timestamp with time zone default timezone ('utc'::text, now()) not null,
    updated_at timestamp with time zone default timezone ('utc'::text, now()) not null
  );

create table
  contributions (
    id text primary key,
    project_id text,
    wallet_id text,
    amount_contributed_usd money,
    created_at timestamp with time zone default timezone ('utc'::text, now()) not null,
    updated_at timestamp with time zone default timezone ('utc'::text, now()) not null
  );

create table
  contributor_wallets (
    id text primary key,
    tags jsonb,
    risk_score int,
    created_at timestamp with time zone default timezone ('utc'::text, now()) not null,
    updated_at timestamp with time zone default timezone ('utc'::text, now()) not null
  );


ALTER TABLE contributions
ADD CONSTRAINT fk_contribution_wallets FOREIGN KEY (wallet_id) 
    REFERENCES contributor_wallets(id);


CREATE OR REPLACE FUNCTION round_attributes() -- 1
RETURNS TABLE(farmer_count INT, money_mixer_count INT, on_chain_hist_count INT, first_tx_during_round_count INT, vote_imbalance_count INT)
language sql -- 3
as $$  -- 4

SELECT 
  SUM( CASE WHEN (tags->'tags')::jsonb ? ('Farmer ✅') THEN 1 ELSE 0 END ) AS farmer_count,
  SUM( CASE WHEN (tags->'tags')::jsonb ? ('MoneyMixer ✅') THEN 1 ELSE 0 END ) AS money_mixer_count,
  SUM( CASE WHEN (tags->'tags')::jsonb ? ('OnChainHistory ✅') THEN 1 ELSE 0 END ) AS on_chain_hist_count,
  SUM( CASE WHEN (tags->'tags')::jsonb ? ('FirstTxDuringRound ✅') THEN 1 ELSE 0 END ) AS first_tx_during_round_count,
  SUM( CASE WHEN (tags->'tags')::jsonb ? ('VoteTwitterImbalance ✅') THEN 1 ELSE 0 END ) AS vote_imbalance_count
FROM projects
$$;

CREATE 
OR replace FUNCTION unique_contributors() -- 1
RETURNS INT -- 2
language SQL -- 3
AS $$ -- 4
SELECT
   COUNT(DISTINCT wallet_id) 
FROM
   contributions;
$$ ;
--6


CREATE OR REPLACE FUNCTION wallet_attributes_v1(arg_project_id text default '') -- 1
RETURNS TABLE(farmer_count INT, money_mixer_count INT, on_chain_hist_count INT, first_tx_during_round_count INT)
language sql -- 3
as $$  -- 4

SELECT 
  COUNT(DISTINCT CASE WHEN (tags->'tags')::jsonb ? ('Farmer ✅') THEN cw.id ELSE '' END ) AS farmer_count,
  COUNT(DISTINCT CASE WHEN (tags->'tags')::jsonb ? ('MoneyMixer ✅') THEN cw.id ELSE '' END ) AS money_mixer_count,
  COUNT(DISTINCT CASE WHEN (tags->'tags')::jsonb ? ('OnChainHistory ✅') THEN cw.id ELSE '' END ) AS on_chain_hist_count,
  COUNT(DISTINCT CASE WHEN (tags->'tags')::jsonb ? ('FirstTxDuringRound ✅') THEN cw.id ELSE '' END ) AS first_tx_during_round_count
FROM contributor_wallets cw
INNER JOIN contributions c 
ON cw.id = c.wallet_id
WHERE c.project_id = arg_project_id 
OR arg_project_id = ''
$$;

CREATE OR REPLACE FUNCTION wallet_profile(arg_wallet_id text) -- 1
RETURNS TABLE(id text, tags text)
language sql -- 3
as $$  -- 4

SELECT 
  cw.id,
  cw.tags
FROM contributor_wallets cw
WHERE cw.id = arg_wallet_id
$$;

CREATE OR REPLACE FUNCTION wallet_projects(arg_wallet_id TEXT) -- 1
RETURNS TABLE(project_id TEXT, title TEXT, amount_contributed MONEY)
language sql -- 3
as $$  -- 4

SELECT 
  c.project_id,
  p.title,
  SUM(c.amount_contributed_usd) AS amount_contributed
FROM contributor_wallets cw
INNER JOIN contributions c 
ON cw.id = c.wallet_id
INNER JOIN projects p ON p.id = c.project_id
WHERE cw.id = arg_wallet_id
GROUP BY 
  cw.id,
  c.project_id,
  p.title
$$;

CREATE OR REPLACE FUNCTION wallet_stats() -- 1
RETURNS TABLE(wallet_id TEXT, num_projects_contributed INT, amount_contributed MONEY)
language sql -- 3
as $$  -- 4

SELECT 
  cw.id,
  COUNT(DISTINCT c.project_id),
  SUM(c.amount_contributed_usd)
FROM contributor_wallets cw
INNER JOIN contributions c 
ON cw.id = c.wallet_id
GROUP BY 
  cw.id
$$;