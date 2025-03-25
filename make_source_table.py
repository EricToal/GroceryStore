import pandas as pd

source_df = pd.DataFrame({
    'source': [1, 2],
    'definition': ["Categories automatically assigned by product_canonicalizer.py.", "Categories manually assigned by Eric Toal."]
})

source_df.to_csv('source_table.txt', sep='|', encoding='ISO-8859-1', index=False)