CREATE OR REPLACE PROCEDURE snapshot_inventory_fact_quarterly (
    target_quarter INT,
    target_year INT
)
RETURNS STRING
LANGUAGE SQL
AS
$$
BEGIN
    INSERT INTO inventory_fact_quarterly (
        product_key,
        store_key,
        quarter,
        year,
        quarter_year,
        num_cases_purchased_to_date,
        num_cases_purchased_this_quarter,
        num_cases_on_hand,
        total_cost_to_store_this_quarter,
        total_sold_by_store_this_quarter,
        total_cost_to_store_ytd,
        total_sold_by_store_ytd
    )
    WITH
    params AS (
        SELECT :target_quarter AS quarter, :target_year AS year
    ),
    quarter_dates AS (
        SELECT
            MIN(CASE WHEN dd.quarter = p.quarter THEN dd.date END) AS quarter_start,
            MAX(CASE WHEN dd.quarter = p.quarter THEN dd.date END) AS quarter_end,
            MIN(CASE WHEN EXTRACT(MONTH FROM dd.date) = 1 THEN dd.date END) AS jan_1
        FROM date_dim dd
        JOIN params p ON dd.year = p.year
    ),
    latest_quarter_row AS (
        SELECT d.*
        FROM inventory_fact_daily d
        JOIN date_dim dd ON d.date_key = dd.date_key
        JOIN params p ON dd.quarter = p.quarter AND dd.year = p.year
        QUALIFY ROW_NUMBER() OVER (
            PARTITION BY d.product_key, d.store_key
            ORDER BY d.date_key DESC
        ) = 1
    ),
    last_before_quarter AS (
        SELECT d.*
        FROM inventory_fact_daily d
        JOIN date_dim dd ON d.date_key = dd.date_key
        WHERE dd.date < (SELECT quarter_start FROM quarter_dates)
        QUALIFY ROW_NUMBER() OVER (
            PARTITION BY d.product_key, d.store_key
            ORDER BY d.date_key DESC
        ) = 1
    ),
    jan_1_snapshot AS (
        SELECT d.*
        FROM inventory_fact_daily d
        JOIN date_dim dd ON d.date_key = dd.date_key
        WHERE dd.date = (SELECT jan_1 FROM quarter_dates)
    ),
    sold_this_quarter AS (
        SELECT d.product_key, d.store_key, COUNT(*) AS total_sold_by_store_this_quarter
        FROM inventory_fact_daily d
        JOIN date_dim dd ON d.date_key = dd.date_key
        JOIN params p ON dd.quarter = p.quarter AND dd.year = p.year
        GROUP BY d.product_key, d.store_key
    ),
    sold_ytd AS (
        SELECT d.product_key, d.store_key, COUNT(*) AS total_sold_by_store_ytd
        FROM inventory_fact_daily d
        JOIN date_dim dd ON d.date_key = dd.date_key
        JOIN quarter_dates qd ON dd.date BETWEEN qd.jan_1 AND qd.quarter_end
        GROUP BY d.product_key, d.store_key
    )
    SELECT
        lqr.product_key,
        lqr.store_key,
        (SELECT quarter FROM params),
        (SELECT year FROM params),
        'Q' || (SELECT quarter FROM params) || ' ' || (SELECT year FROM params) AS quarter_year,
        lqr.num_cases_purchased_to_date,
        COALESCE(lqr.num_cases_purchased_to_date - lbq.num_cases_purchased_to_date, lqr.num_cases_purchased_to_date),
        lqr.num_available / 12,
        COALESCE(lqr.num_cases_purchased_to_date - lbq.num_cases_purchased_to_date, lqr.num_cases_purchased_to_date) * lqr.case_cost_to_store,
        stq.total_sold_by_store_this_quarter,
        COALESCE(lqr.num_cases_purchased_to_date - j1.num_cases_purchased_to_date, lqr.num_cases_purchased_to_date) * lqr.case_cost_to_store,
        syd.total_sold_by_store_ytd
    FROM latest_quarter_row lqr
    LEFT JOIN last_before_quarter lbq
        ON lqr.product_key = lbq.product_key AND lqr.store_key = lbq.store_key
    LEFT JOIN jan_1_snapshot j1
        ON lqr.product_key = j1.product_key AND lqr.store_key = j1.store_key
    LEFT JOIN sold_this_quarter stq
        ON lqr.product_key = stq.product_key AND lqr.store_key = stq.store_key
    LEFT JOIN sold_ytd syd
        ON lqr.product_key = syd.product_key AND lqr.store_key = syd.store_key;

    RETURN 'Snapshot inserted for Q' || target_quarter || ' ' || target_year;
END;
$$;
