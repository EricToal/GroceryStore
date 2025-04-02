INSERT INTO sales_fact_daily (
    date_key,
    product_key,
    store_key,
    sold_today,
    cost_of_items_sold,
    sales_total,
    gross_profit
)
SELECT
    date_key,
    product_key,
    store_key,
    COUNT(*) AS sold_today,
    SUM(total_cost_to_store) AS cost_of_items_sold,
    SUM(total_dollar_sales) AS sales_total,
    SUM(gross_profit) AS gross_profit
FROM sales_fact_transaction
GROUP BY
    date_key,
    product_key,
    store_key;
