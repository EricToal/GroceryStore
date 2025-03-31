import pandas as pd
import numpy as np
import random as rand
import datetime as dt

# Constants provided by instructor
MIN_CUSTOMERS = 1070
MAX_CUSTOMERS = 1100
PRICE_MULTIPLIER = 1.15
START_DATE = dt.date(2024, 1, 1)
MAX_ITEMS = 65
WEEKEND_INCREASE = 50
SPECIAL_ITEMS = ['Milk', 'Cereal', 'Baby Food', 'Diapers', 'Bread', 'Peanut Butter', 'Jelly/Jam']
ASSUMPTIONS = {
    "Milk": 0.70,
    "Cereal": 0.50 * 0.70 + 0.05 * 0.30,
    "Baby Food": 0.20,
    "Diapers": 0.80 * 0.20 + 0.01 * 0.80,
    "Bread": 0.50,
    "Peanut Butter": 0.10,
    "Jelly/Jam": 0.90 * 0.10 + 0.05 * 0.90,
}

def calc_cust_count(current_day: dt.date) -> int:
    cust_count = rand.randint(MIN_CUSTOMERS, MAX_CUSTOMERS)
    day_of_week = current_day.strftime("%A")
    if day_of_week == 'Saturday' or day_of_week == 'Sunday':
            cust_count += WEEKEND_INCREASE
    
    return cust_count

def is_item_type_chosen(probability_int: int) -> bool:
    return rand.randint(1, 100) <= probability_int

def get_item(grouped_products: dict, item_type: str, daily_cust_num: int, current_date: dt.date, inventory: dict) -> tuple:
    """
    Description: This function will return a random item of the specified item type from the grouped_products dictionary.
    Side Effect: This function will decrement the current_count of the item in the inventory dictionary.
    
    Parameters:
        grouped_products: A dictionary where the keys are the item types and the values are the corresponding dataframes
        item_type: The item type of the item to be selected
        daily_cust_num: The current customer number for the day
        current_date: The current date
        inventory: A dictionary where the keys are the SKU and the values are dictionaries containing the target_count, current_count, and cases_ordered
        
    Returns: A tuple containing the current_date, daily_cust_num, product name, item type, SKU, and price of the selected item
    """
    formatted_date = current_date.strftime("%Y%m%d")
    row = grouped_products[item_type].sample(n=1).iloc[0]
    while (inventory[row['SKU']]['current_count'] == 0):
        row = grouped_products[item_type].sample(n=1).iloc[0]
    inventory[row['SKU']]['current_count'] -= 1
        
    return (formatted_date, daily_cust_num,
                row['Product Name'],
                row['itemType'],
                row['SKU'],
                row['BasePrice'],
                round(row['BasePrice'] * PRICE_MULTIPLIER, 2),
                inventory[row['SKU']]['current_count'],
                inventory[row['SKU']]['cases_ordered']
            )

def get_item_batch(filtered_products: pd.DataFrame, grouped_products: dict, daily_cust_num: int, current_date: dt.date, item_count: int, inventory: dict) -> list[tuple]:
    '''
    Description: This function will return a list of random items from the products dataframe.
    Side Effect: This function will decrement the current_count of the item in the inventory dictionary.
    
    Parameters:
        products: A dataframe containing all the products
        daily_cust_num: The current customer number for the day
        current_date: The current date
        item_count: The number of items to be selected
        inventory: A dictionary where the keys are the SKU and the values are dictionaries containing the target_count, current_count, and cases_ordered
        
    Returns: A list of tuples containing the current_date, daily_cust_num, product name, item type, SKU, and price of the selected items
    '''
    formatted_date = current_date.strftime("%Y%m%d")
    transaction_list = []
    selected_products = filtered_products.sample(n=item_count, replace=True)

    for _, row in selected_products.iterrows():
        if (inventory[row['SKU']]['current_count'] == 0):
            item_type = row['itemType']
            result = get_item(grouped_products, item_type, daily_cust_num, current_date, inventory)
        else:
            inventory[row['SKU']]['current_count'] -= 1
            result = (formatted_date, daily_cust_num,
                                row['Product Name'],
                                row['itemType'],
                                row['SKU'],
                                row['BasePrice'],
                                round(row['BasePrice'] * PRICE_MULTIPLIER, 2),
                                inventory[row['SKU']]['current_count'],
                                inventory[row['SKU']]['cases_ordered']
                      )
        transaction_list.append(result)

    return transaction_list

def create_inventory_dict(filtered_products: pd.DataFrame, grouped_products: dict) -> dict:
    inventory = {}
    avg_daily_custs = np.ceil((((MIN_CUSTOMERS + MAX_CUSTOMERS) * 5) + ((MIN_CUSTOMERS + 75 + MAX_CUSTOMERS + 75) * 2)) / 7)
    avg_items_cust = 50 # instructor provided
    avg_daily_items = avg_daily_custs * avg_items_cust
    
    for item in SPECIAL_ITEMS:
        unique_products = grouped_products[item]['SKU'].nunique()
        daily_items_of_type = np.ceil(avg_daily_custs * ASSUMPTIONS[item])
        daily_items_of_product = np.ceil(daily_items_of_type / unique_products)
        avg_daily_items -= daily_items_of_type
        
        num_days_stocked = 1.5 if item == 'Milk' else 3
        cases = np.ceil((daily_items_of_product * num_days_stocked) / 12)
        for _, row in grouped_products[item].iterrows():
            inventory[row['SKU']] = {'target_count': cases * 12, 'current_count': cases * 12, 'cases_ordered': cases}
    
    unique_products = filtered_products['SKU'].nunique()
    general_probability = 1 / unique_products
    daily_items_of_product = np.ceil(avg_daily_items * general_probability)
    num_days_stocked = 3
    cases = np.ceil((daily_items_of_product * num_days_stocked) / 12)
    for _, row in filtered_products.iterrows():
        inventory[row['SKU']] = {'target_count': cases * 12, 'current_count': cases * 12, 'cases_ordered': cases}
        
    return inventory

def restock_inventory(inventory: dict, grouped_products: dict, item_types: list[str]) -> dict:
    for item_type in item_types:
        for sku in grouped_products[item_type]['SKU']:
            if (inventory[sku]['current_count'] < inventory[sku]['target_count']):
                cases = np.ceil((inventory[sku]['target_count'] - inventory[sku]['current_count']) / 12)
                inventory[sku]['cases_ordered'] += cases
                inventory[sku]['current_count'] += cases * 12
                 
    return inventory

def is_delivery_day(current_day: dt.date) -> bool:
    day_of_week = current_day.strftime("%A")
    return day_of_week == 'Monday' or day_of_week == 'Wednesday' or day_of_week == 'Friday'

            
if __name__ == "__main__":
    rand.seed(42)
    products = pd.read_csv(r"Products1.txt", sep='|', encoding='ISO-8859-1')
    products['BasePrice'] = products['BasePrice'].str.replace('$', '', regex=False).astype(float)
    products['itemType'] = products['itemType'].fillna('Missing')
    grouped_products = {item: df for item, df in products.groupby('itemType')}
    all_item_types = products['itemType'].unique().tolist()
    
    filtered_products = products[~products['itemType'].isin(SPECIAL_ITEMS)]
    
    transaction_list = []
    inventory_dict = create_inventory_dict(filtered_products, grouped_products)
    
    # Range 0 ... 365
    for i in range(366):
        current_date = START_DATE + dt.timedelta(days=i)
        
        cust_count = calc_cust_count(current_date)
        
        if is_delivery_day(current_date):
            inventory_dict = restock_inventory(inventory_dict, grouped_products, all_item_types)
        else:
            inventory_dict = restock_inventory(inventory_dict, grouped_products, ['Milk'])
        
        for j in range(cust_count):
            daily_cust_num = j + 1
            cust_item_count =  rand.randint(1, MAX_ITEMS)
            k = 0
            
            milk = is_item_type_chosen(70)
            cereal = is_item_type_chosen(50) if milk else is_item_type_chosen(5)
            baby_food = is_item_type_chosen(20)
            diapers = is_item_type_chosen(80) if baby_food else is_item_type_chosen(1)
            bread = is_item_type_chosen(50)
            peanut_butter = is_item_type_chosen(10)
            jam_jelly = is_item_type_chosen(90) if peanut_butter else is_item_type_chosen(5)
            
            conditional_items = [milk, cereal, baby_food, diapers, bread, peanut_butter, jam_jelly]
            
            
            for m, item_type in enumerate(conditional_items):
                if item_type:
                    transaction_list.append(get_item(grouped_products, SPECIAL_ITEMS[m], daily_cust_num, current_date, inventory_dict))
                    k += 1
            
            if k < cust_item_count:
                transaction_list.extend(get_item_batch(filtered_products, grouped_products, daily_cust_num, current_date, cust_item_count - k, inventory_dict))
            
    transaction_df = pd.DataFrame(transaction_list, columns=['Date', 
                                                             'Daily Customer Number', 
                                                             'Product Name', 
                                                             'Item Type', 
                                                             'SKU',
                                                             'Base Price', 
                                                             'Price',
                                                             'Items Left', 
                                                             'Total Cases Ordered'
                                                             ])
    print(transaction_df)
    transaction_df.to_csv(r'transaction_store_5.txt', sep='|', index=False, encoding='ISO-8859-1')
            
            
                    