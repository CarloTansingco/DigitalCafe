import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")

products_db = myclient["products"]

order_management_db = myclient["order_management"]



def get_product(code):
    products_coll = products_db["products"]

    product = products_coll.find_one({"code":code},{"_id":0})

    return product

def get_products():
    product_list = []

    products_coll = products_db["products"]

    for p in products_coll.find({},{"_id":0}):
        product_list.append(p)

    return product_list

def get_branch(code):
    branches_coll = products_db['branches']

    branch = branches_coll.find_one({"code":code})

    return branch

def get_branches():
    branches_list = []

    branches_coll = products_db['branches']

    for x in branches_coll.find({}):
        branches_list.append(x)

    return branches_list

def get_user(username):
    customers_coll = order_management_db['customers']
    user=customers_coll.find_one({"username":username})
    return user

def update_password(username, new_password):
    customers_coll = order_management_db['customers']
    customers_coll.update_one({"username": username}, {"$set": {"password": new_password}})

def get_orders_by_username(username):
    orders_coll = order_management_db['orders']
    orders = list(orders_coll.find({"username": username}))
    return orders

def create_order(order):
    orders_coll = order_management_db['orders']
    orders_coll.insert(order)
    return orders_coll

