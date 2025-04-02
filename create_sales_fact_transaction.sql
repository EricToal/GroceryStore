CREATE OR REPLACE TABLE sales_fact_transaction (
    date_key INT NOT NULL,
    daily_customer_num INT NOT NULL,
    product_key INT NOT NULL,
    store_key INT NOT NULL,
    quantity_sold INT NOT NULL DEFAULT 1,
    total_dollar_sales FLOAT,
    total_cost_to_store FLOAT,
    gross_profit FLOAT,
    PRIMARY KEY (date_key, daily_customer_num, product_key)
);
