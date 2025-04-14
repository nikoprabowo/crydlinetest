{{ config(materialized='table') }}

with source_eth as (
    select 
        id,
        date(market_date) as market_date,
        open as price_open,
        close as price_close,
        volume,
        sma10,
        sma100,
        rsi,
        macd,
        CASE
            WHEN sma10 > sma100 AND macd > -1.2 AND rsi < 60 THEN 'BUY'
            WHEN sma10 < sma100 AND macd < -1.2 AND rsi > 30 THEN 'SELL'
            ELSE 'HOLD'
        END AS signal
    from your_data.eth_mediumrare
    where market_date >= DATE_SUB(CURRENT_DATETIME(), INTERVAL 3 MONTH)
    order by id asc
)

select *
from source_eth