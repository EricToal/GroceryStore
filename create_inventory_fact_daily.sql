CREATE OR REPLACE TABLE inventory_fact_daily (
    date_key INT NOT NULL,
    product_key INT NOT NULL,
    store_key INT NOT NULL,
    num_available INT,
    item_cost_to_store FLOAT,
    case_cost_to_store FLOAT,
    num_cases_purchased_to_date INT,
    PRIMARY KEY (product_key, date_key, store_key)
);
