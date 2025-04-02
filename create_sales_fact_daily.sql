CREATE OR REPLACE TABLE sales_fact_daily (
    date_key INT NOT NULL,
    product_key INT NOT NULL,
    store_key INT NOT NULL,
    sold_today INT,
    cost_of_items_sold FLOAT,
    sales_total FLOAT,
    gross_profit FLOAT,
    PRIMARY KEY (date_key, product_key, store_key)
);
