import io
import os
import uuid
import secrets
from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from PIL import Image
from werkzeug.utils import secure_filename
import urllib.request

from config import Config
app = Flask(__name__)

CORS(app)
bcrypt = Bcrypt(app)


from functions import *
from db import *

app.config.from_object(Config)
app.config['ENV'] = 'development'
app.config['DEBUG'] = True
app.config['TESTING'] = True
UPLOAD_FOLDER = ('static/uploads')
app.config['MAX_CONTENT_LENGTH'] = 16*400*400


ALLOWED_EXTENSIONS = set(['png','jpeg'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_picture(image_name):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(image_name.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(os.path.abspath(app.root_path), 'static','products', picture_fn)
    # picture_path = os.path.join(app.root_path, 'static\\uploads', picture_fn)
    image_name.save(picture_path)
    return picture_fn

def delete_picture(image_name):
    picture_path = os.path.join(os.path.abspath(app.root_path), 'static','products', image_name)
    if os.path.exists(picture_path):
        os.remove(picture_path)


# root address
@app.route("/search", methods=["GET", 'POST'])
def home():
    """
    search page route
    """

    if request.method == 'POST':
        message = request.form['message']
        shopper_products = []
        products = []
        products.extend(getOkaySuperMarket(message))
        # products.append(getSpar(message))
        # products.extend(getFreshInABox(message))
        products.extend(getSpar(message))
        shopper_products.extend(search_products(message))
        print(shopper_products)
        for product in products:
            product[1] = product[1][1:]
        products.sort(key = lambda x:float(x[1]))
        if 'user' in session: 
            return render_template('products1.html', search = message, products = products, email = session['user'], shopper_products = shopper_products)
        return render_template('products.html', search = message, products = products, shopper_products = shopper_products)
    return render_template("index.html")


@app.route("/register", methods=["GET", 'POST'])
def register():
    """
    Home page route
    main route
    """
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirmpassword']
        # if not name or not email or not password or confirm_password:
        #     pass
        if password != confirm_password:
            return("passwords didnt match")
        result = register_user(name=name, email=email,password=password)
        if result == "Done":
            return render_template('login.html', message = "User Acount created Successfully, Login", message_type = "success")
        elif result == "Error":
            return render_template("registerpage.html", message = "That didnt work, Try Again", message_type = "danger")
        else:
            return render_template("registerpage.html", message = result, message_type = "danger")
    return render_template("registerpage.html")

@app.route("/login", methods=["GET", 'POST'])
def login():
    """
    Home page route no login needed
    anonymous route
    """
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        result = login_user(email=email, password=password)
        if result == "true":
            create_session(email)
            create_session_role(email)
            return redirect(url_for('dashboard'))
        elif result == "false":
            return render_template("login.html", message = "Incorrect username or password", message_type = "danger")
        else:
            return render_template("login.html", message = "Incorrect username or password", message_type = "danger")

    return render_template("login.html")

@app.route("/dashboard", methods=["GET"]) # type: ignore
def dashboard():

    """
    Home page route
    logged in route
    """

    if 'user' in session: 
        if session['role'] == "seller":
            watch_data = search_watched_products(session["user"])
            user_products = get_user_products(session['user'])
            return render_template("dashboard.html", email = session['user'], user_products = user_products, watch_data = watch_data)
        else:
            user_cart = get_user_cart(email=session['user'])
            user_notifications = get_notifications(email=session["user"])
            status = check_application(session['user'])
            total_cost = 0.00
            for product in user_cart:
                total_cost += float(product["calprice"])
            total_cost= "{:.2f}".format(total_cost)
            return render_template("dashboard1.html", email = session['user'], user_cart = user_cart, total_cost = total_cost,user_notifications = user_notifications, status = status)


    return redirect(url_for('login'))


@app.route("/update_product", methods=["PUT", "POST"])
def update_product():
    """
    Home page route
    logged in route
    """
    if request.method == "POST":
        print("inside")
        if 'user' in session: 
            print("here")
            name = request.form['name']
            id = request.form['id']
            price = request.form['price']
            file = request.files['image']
            print(id)
            
            if file:
                try:
                    old_image = get_old_image(id)
                    if old_image:
                        delete_picture(old_image)
                    product_image = save_picture(file)
                    update_product_function(id=id,name=name,price=price,image=product_image, user=session["user"])
                    flash(f'Product Updated Sucessfully')
                    return redirect(url_for("dashboard","success"))
                except Exception as e:
                    print(e)
                    flash(f'Product Update failed', "error")
            else:
                try:
                    
                    update_products_no_image(id=id,name=name,price=price,user=session["user"])
                    flash(f'Product Updated Sucessfully', "success")
                    return redirect(url_for("dashboard"))
                except Exception as e:
                    print(e)
                    flash(f'Product Updat Failed', "error")

            return redirect(url_for("dashboard"))

        else:
            return redirect(url_for("login"))
    return redirect(url_for("dashboard"))

@app.route("/addproduct", methods=['POST'])
def add_product():
    """
    Adding new product
    route
    """
    if request.method == 'POST':
        user = session['user']
        name = request.form['name']
        price = request.form['price']
        file = request.files['image']
        # Generate a random filename for the file
        # Generate a random filename for the file
        if file.filename == "":
            flash(f'Please select image', "error")
            return redirect(url_for("dashboard"))
        
        product_image = save_picture(file)
        try:
            add_products(email=user,name=name,price=price,image=product_image)
            flash(f'Product Added successfully', "success")
            return redirect(url_for('dashboard'))
        except Exception as e:
            print(e)
            flash(f'Product Add Failed', "error")
            return redirect(url_for('dashboard'))
    return redirect(url_for('dashboard'))

@app.route("/delete_product", methods=['POST'])
def delete_product():

    
    user = session['user']
    id = request.form['id']
    try:
        delete_one_product(id)
        flash(f'Product Deleted', "success")
        return redirect(url_for("dashboard"))
    except Exception as e:
        print(e)
        flash(f'Product Delete', "Failed")
        return redirect(url_for('dashboard'))

@app.route("/add_to_cart", methods = ['POST'])
def add_to_cart():
    if 'user' in session:
        id = request.form['id']
        count = request.form['count'] 
        if id and count:
            add_product_to_cart(id=id,count=count, user = session["user"])
            flash(f'Product Added to Cart', "success")
            return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route("/add_location", methods = ['POST'])
def add_location():
    if 'user' in session:
        loc = request.form['locationtext']
        user = session["user"]
        if loc and user:
            add_user_location(email=user, location=loc)
            flash(f'Product Added Successfully', "success")
            return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route("/logout", methods=["GET", 'POST'])
def logout():
    """
    Home page route
    main route
    """
    if request.method == 'POST':
        delete_session()
        return redirect(url_for('login'))
   

    return render_template("dashboard.html")


@app.route("/delete_cart", methods=["POST"])
def delete_cart():
    """
   delete product in cart route
    """
    if request.method == 'POST':
        if 'user' in session: 
            id = request.form['id']
            delete_product_cart(id=id)
            flash(f'Product Removed from Cart', "success")
    return redirect(url_for('dashboard'))

@app.route("/update_cart", methods=["POST"])
def update_cart():
    """
   delete product in cart route
    """
    if request.method == 'POST':
        if 'user' in session: 
            id = request.form['id']
            count = request.form['count']
            update_product_cart(id=id, count=count)
            flash(f'Product count Updated', "success")
    return redirect(url_for('dashboard'))



@app.route('/upload_docs', methods =["POST"])
def upload_docs():
    if "user" in session:
        user = session['user']
        # name = request.form['name']
        bl = request.files['blicense']
        tc = request.files['tclearance']
        hc = request.files['hcert']
        tl = request.files['tlicense']
        sl = request.files['slicense']
        mc = request.files['mcert']

        blname = save_picture(bl)
        tcname = save_picture(tc)
        hcname = save_picture(hc)
        tlname = save_picture(tl)
        slname = save_picture(sl)
        mcname = save_picture(mc)
        try:
            add_docs(user=user,bl=blname, tc=tcname,hc=hcname,tl=tlname,sl=slname, mc = mcname)
            flash(f'Documents Uploaded Successfully', "success")
            return redirect(url_for('dashboard'))
        except Exception as e:
            flash(f'Documents Upload Failed', "error")
            return redirect(url_for('dashboard'))

    return redirect(url_for("dashboard"))

def create_session(user):
    session['user'] = user
    return

def create_session_role(email):
    role = get_user_role(email)
    if role:
        session['role'] = role
        return
    else:
        print("No role")
        return

def delete_session():
    session.clear()
    return

def login_required():
    if not 'user' in session:
        return redirect(url_for('login'))
    
    
if __name__ == "__main__":
    app.run(debug=True,)