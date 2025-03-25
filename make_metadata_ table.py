import pandas as pd

products_df = pd.read_csv(
    "products_table.txt",
    sep="|",
    encoding="ISO-8859-1",
    dtype=str
)

with open("manually_assigned_categories.txt", "r", encoding="ISO-8859-1") as f:
    ids_raw = f.read().replace("\n", "").replace(".", "")
    manually_assigned_ids = set(id.strip() for id in ids_raw.split(",") if id.strip().isdigit())

products_df["source"] = products_df["product_key"].apply(
    lambda pid: "2" if pid in manually_assigned_ids else "1"
)

metadata_df = products_df[["sku", "source"]]
metadata_df.to_csv("metadata_table.txt", sep="|", index=False, encoding="ISO-8859-1")
