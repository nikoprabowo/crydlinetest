WITH 
btc AS (
    SELECT id, market_date, volume
    FROM {{ ref('btc_welldone') }}
    ORDER BY id asc
),
eth AS (
    SELECT id, market_date, volume
    FROM {{ ref('eth_welldone') }}
    ORDER BY id asc
)
SELECT 
    "btc" AS coin,
    b.market_date AS market_date,
    b.volume AS volume
FROM btc b

UNION ALL

SELECT 
    "eth" AS coin,
    e.market_date AS market_date,
    e.volume AS volume
FROM eth e