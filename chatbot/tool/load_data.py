import pandas as pd
import pickle

# order data
order_data_path = "./chatbot/dataset/order_dataset.pkl"

# menu data
menu_data_path = "./chatbot/dataset/menu_dataset.csv"

# load the file data
def load_data(file_path):
    dataset = pd.read_csv(file_path, index_col = False, encoding='ISO-8859-1')
    return dataset

# load menu
def load_menu():
    try:
        data = load_data(menu_data_path)
    except Exception as e:
        print(e)
    return data

# load orders
def load_order():
    try:
        with open(order_data_path, mode='rb') as f:
            orders = pickle.load(f)
    except Exception as e:
        return {}
    if orders is None:
        orders = {}
    return orders

# save Orders
def save_order(orders):
    if orders == None:
        return None
    with open(order_data_path, mode='wb') as f:
            pickle.dump(orders, f)


    
   
    