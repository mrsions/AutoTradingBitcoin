SELECT 
    timestamp,
    round(total / 10000, 4) AS total, 
    CASE 
        WHEN round((total / 8520118 - 1) * 100, 4) >= 0 
        THEN '+' || round((total / 8520118 - 1) * 100, 4) || '%' 
        ELSE round((total / 8520118 - 1) * 100, 4) || '%'
    END AS rating, 
    round((total - 8520118) / 10000, 4) AS earning
FROM (
    SELECT (after_currency_balance + after_coin_balance * after_coin_avg_buy_price *0.9995 - 1000) AS total, timestamp 
    FROM trades 
    ORDER BY timestamp DESC 
    LIMIT 20
) 
ORDER BY timestamp