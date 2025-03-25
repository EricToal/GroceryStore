import pandas as pd

store_df = pd.DataFrame({
    'store_key': [5, 6, 7],
    'store_manager': ["Margi Yogeshkumar Thakar", "Eric Toal", "Jaydev Parmar"],
    'store_street_addr': ["123 Main St", "456 Elm St", "789 Oak St"],
    'store_town': ["Wilmington", "Carneys Point", "Chester"],
    'store_zip_code': ["19801", "08069", "19013"],
    'store_phone_num': ["555-1234", "555-5678", "555-4321"],
    'store_state': ["DE", "NJ", "PA"]
})

store_df.to_csv('store_table.txt', sep='|', encoding='ISO-8859-1', index=False)