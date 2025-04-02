-- This will populate the inventory_fact_daily table with data
-- from staging as long as it follows team 6's format.
INSERT INTO inventory_fact_daily (
    date_key,
    product_key,
    store_key,
    num_available,
    item_cost_to_store,
    case_cost_to_store,
    num_cases_purchased_to_date
)
SELECT
    d.date_key,
    p.product_key,
    6 AS store_key,
    t.items_left AS num_available,
    t.base_price AS item_cost_to_store,
    t.base_price * 12 AS case_cost_to_store,
    t.total_cases_ordered AS num_cases_purchased_to_date
FROM (
    SELECT *
    FROM stage_transaction_store6
    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY raw_date_str, sku
        ORDER BY daily_customer_number DESC
    ) = 1
) t
JOIN product_dim p
    ON t.product_name = p.product_name AND t.sku = p.sku
JOIN date_dim d
    ON d.date = TO_DATE(t.raw_date_str, 'YYYYMMDD');
