CREATE OR REPLACE TABLE inventory_fact_quarterly (
    product_key INT NOT NULL,
    store_key INT NOT NULL,
    quarter_year VARCHAR(50),
    quarter INT NOT NULL,
    year INT NOT NULL,
    num_cases_purchased_to_date INT,
    num_cases_purchased_this_quarter INT,
    num_cases_on_hand INT,
    total_cost_to_store_this_quarter FLOAT,
    total_sold_by_store_this_quarter FLOAT,
    total_cost_to_store_ytd FLOAT,
    total_sold_by_store_ytd FLOAT,
    PRIMARY KEY (product_key, store_key, quarter, year)
);
