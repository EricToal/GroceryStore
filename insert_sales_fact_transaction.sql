-- This will populate the sales_fact_transaction table with data
-- from staging as long as it follows team 6's format.
INSERT INTO sales_fact_transaction (
    date_key,
    daily_customer_num,
    product_key,
    store_key,
    quantity_sold,
    total_dollar_sales,
    total_cost_to_store,
    gross_profit
)
SELECT
    d.date_key,
    t.daily_customer_number,
    p.product_key,
    5 AS store_key,
    1 AS quantity_sold,
    t.price,
    t.base_price,
    t.price - t.base_price AS gross_profit
FROM stage_transaction_store5 t
JOIN product_dim p
    ON t.product_name = p.product_name AND t.sku = p.sku
JOIN date_dim d
    ON d.date = TO_DATE(t.raw_date_str, 'YYYYMMDD');
