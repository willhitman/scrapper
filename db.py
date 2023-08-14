from app import bcrypt
from pymongo.mongo_client import MongoClient
import pymongo.errors
import re
from bson.objectid import ObjectId


uri = "mongodb+srv://willred:coaVzZGGIhHhUO0O@willhitman.epihcui.mongodb.net/?retryWrites=true&w=majority"
# Create a new client and connect to the server
client = MongoClient(uri)
# ___________________________________________________________________________________________________________
# Send a ping to confirm a successful connection
# try:
#     client.admin.command('ping')
#     print("Pinged your deployment. You successfully connected to MongoDB!")
# except Exception as e:
#     print(e)
#___________________________________________________________________________________________________________

# db connection
db = client.get_database('websrcrapper1_0')

# user document connection
users = db.users
products = db.products
cart = db.cart
seller_location = db.seller_location
docs = db.docs
status = db.status
watch_tb = db.watch_tb
from datetime import datetime


# test
# user = users.find_one({'name':'Gift'})
# print(user)

def register_user(name,email,password):
    user_found = users.find_one({"name": name})
    email_found = users.find_one({"email": email})
    if user_found:
        return("User Name already used")
    if email_found:
        return("Email already in use")
    hashed = bcrypt.generate_password_hash(password).decode('utf-8')
    user = {'name': name, 'email': email, 'password': hashed, 'role':"user"}
    try:
        users.insert_one(user)
        return("Done")
    except Exception as e:
        print(e)
        return("Error")

def login_user(email, password):
    user_found = users.find_one({"email":email})
    if user_found is not None:
        password_check = user_found['password']
        print(password_check)
        print(user_found['email'])
        if bcrypt.check_password_hash(password_check, password):
            return "true"
        return "false"
    return "false"

def get_user_role(email):
    try:
        user_found = users.find_one({"email":email})
    except Exception as e:
        print(e)
    if user_found is not None:
        role = user_found['role']
        print(role)
        return role
    else:
        print("Error")
        return

def add_products(email, name, price, image):
    product = {'user': email, 'name':name, 'price': price, 'image': image}
    try:
        products.insert_one(product)
        return("Done")
    except Exception as e:
        print(e)
        return("Error")
    

def find_one_product(id):
    try:
        return products.find_one({"_id": ObjectId(id)})
    except Exception as e:
        print(e)
        return("Error")

def get_old_image(id):
    try:
        product =  products.find_one({"_id": ObjectId(id)})
        if product:
            return product['image']
        return None
    except Exception as e:
        print(e)
        return "Error"

def get_all_products():
    try:
        products_list = products.find()
        return products_list
    except Exception as e:
        print(e)
        return "Error"
    # for x in products_list:
    #     print(x)


def get_user_products(email):
    try:
        product_list = list(products.find({"user":email}))
        return product_list
    except Exception as e:
        print(e)
        return "Error"
    
def search_products(search):
    product_list = []
    try:
        regex = re.compile('.*' + re.escape(search) + '.*', re.IGNORECASE)
        product_list = list(products.find({"name": regex}))
        for r in product_list:
            seller_loc = seller_location.find_one({'email':(r['user'])})
            r['location'] = seller_loc['location']
        product_list.sort(key = lambda x:float(x["price"]))
        return product_list
    except Exception as e:
        print(e)
        return "Error"
    
def search_watched_products(email):
    regex = re.compile('.*' + re.escape(email) + '.*', re.IGNORECASE)
    product_list = list(products.find({"user": regex}))
    for r in product_list:
        id = ObjectId(r['_id'])
        watch_count=watch_tb.count_documents({'product':id})
        r['count'] = watch_count
    return product_list

def check_application(email):
    try:
        stat = status.find_one({'user':email})
        if stat:
            print(stat)
            return "Pending"
        return "None"
    except Exception as e:
        print(e)
        return "Error"
    
check_application("giftwt9wt@gmail.com")

def get_one_product(search):
    product_list = []
    try:
        product_list = list(products.find({"_id": search}))
        return product_list
    except Exception as e:
        print(e)
        return []

def update_products_no_image(id,name,price,user):  # type: ignore
    try:
        id_object = ObjectId(id)
        products.update_one({'_id': id_object}, {"$set":{'name':name, 'price':price}})
        if price:
            pr = watch_tb.find_one({"product": id_object})
            if pr:
                watch_tb.delete_one({'product':id_object})
            current_datetime = datetime.now()
            watch = {'product':id_object, 'date':current_datetime,'user':user}
            watch_tb.insert_one(watch)
        print("updating")
        return "Done"
    except Exception as e:
        print(e)
        return "Error"
    
def update_product_function(id,name,price,image):
    try:
        id_object = ObjectId(id)
        products.update({'_id':id_object}, {"$set":{'name':name, 'price':price, 'image':image}})
        return "Done"
    except Exception as e:
        print(e)
        return "Error"

def delete_one_product(id):
    id_object = ObjectId(id)
    try:
        products.delete_one({'_id': id_object})
        return "Done"
    except Exception as e:
        print(e)
        return("Error")
    # Delete the document that matches the _id value
    # result = products.delete_one({'_id': id_object})

def add_product_to_cart(id,user, count):
    id = ObjectId(id)
    product = {'product_id': id, 'user': user, 'count': count}
    try:
        cart.insert_one(product)
        return "Done"
    except Exception as e:
        print(e)
        return "Error"
    
def get_notifications(email):
    regex = re.compile('.*' + re.escape(email) + '.*', re.IGNORECASE)
    try:
        product_list = list(watch_tb.find({'user':email}))
        for r in product_list:
            id = ObjectId(r['product'])
            pr = products.find_one({'_id':id})
            r['name'] = pr['name']
            r['price'] = pr['price']
            loc = seller_location.find_one({'email':email})
            r['location'] = loc['location']
            del r['_id']
            del r['product']
            del r['user']
        print(product_list)
        return product_list
    except Exception as e:
        print(e)
        return"Error"
def add_user_location(email, location):
    loc = {'email':email, 'location':location}
    try:    
        seller_loc = seller_location.find_one({"email": email})
        if seller_loc:
            seller_location.delete_one(email)
        seller_location.insert_one(loc)
        return "Done"
    except Exception as e:
        print(e)
        return "Error"
    
def add_docs(user,bl,tc,hc,tl,sl,mc):
    doc = {'user':user, 'bl':bl,'tc':tc,'hc':hc,'tl':tl,'sl':sl,'mc':mc}
    try:
        docs.insert_one(doc)
        statee = {'user':user,'status':'pending'}
        status.insert_one(statee)
        return "Done"
    except Exception as e:
        print(e)
        return "Error"
    

def get_user_cart(email):
    product_list = []
    try:
        cart_list = list(cart.find({"user":email}))
        for r in cart_list:
            pr = []
            id_object = ObjectId(r["product_id"])
            pr = get_one_product(id_object)
            # print(pr)
            for h in pr:
                r["name"] = h["name"]
                r["calprice"] =   "{:.2f}".format(float(h["price"]) * int(r["count"])) 
                r["image"] = h["image"]
                r["price"] = h["price"]
                product_list.append(r)
        return product_list
    except Exception as e:
        print(e)
        return "Error"
    
def update_product_cart(id, count):
    id_object = ObjectId(id)
    try:
        cart.update_one({'_id': id_object}, {"$set":{'count':count}})
        return "Done"
    except Exception as e:
        print(e)
        return "Error"

def delete_product_cart(id):
    id_object = ObjectId(id)
    try:
        cart.delete_one({'_id': id_object})
        return "Done"
    except Exception as e:
        print(e)
        return "Error"
    
