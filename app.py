from flask import Flask, redirect
from flask import render_template
from flask import request
from flask import session
from bson.json_util import loads, dumps
from flask import make_response
import database as db
import authentication
import ordermanagement as om
import logging

app = Flask(__name__)

app.secret_key = b's@g@d@c0ff33!'

if __name__ == '__main__':
    app.run(debug=True)


logging.basicConfig(level=logging.DEBUG)
app.logger.setLevel(logging.INFO)


navbar = """
         <a href='/'>Home</a> | <a href='/products'>Products</a> |
         <a href='/branches'>Branches</a> | <a href='/aboutus'>About Us</a>
         <p/>
         """

@app.route('/')
def index():
    return render_template('index.html', page="Index")

@app.route('/products')
def products():
    product_list = db.get_products()
    return render_template('products.html', page="Products", product_list=product_list)

@app.route('/productdetails')
def productdetails():
    code = request.args.get('code', '')
    product = db.get_product(int(code))

    return render_template('productdetails.html', code=code, product=product)

@app.route('/branches')
def branches():
    branch_list = db.get_branches()
    return render_template('branches.html', page="Branches", branches=branch_list)

@app.route('/branchdetails')
def branchdetails():
    code = request.args.get('code', '')
    branch = db.get_branch(int(code))
    print("Branch:", branch)  
    return render_template('branchdetails.html', code=code, branch=branch)

@app.route('/privacypolicy')
def privacypolicy():
    return render_template('privacypolicy.html', page="Privacy Policy")


@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html', page="About Us")

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@app.route('/auth', methods=['GET', 'POST'])
def auth():
    username = request.form.get('username')
    password = request.form.get('password')

    user, error_message = authentication.login(username, password)

    if user is not None:
        session["user"] = user
        return redirect('/')
    else:
        return render_template('login.html', error=error_message)

@app.route('/changepassword', methods=['GET', 'POST'])
def changepassword():
    if "user" not in session:
        return redirect('/login')

    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        user = session["user"]
        username = user["username"]

        temp_user = db.get_user(username)

        if temp_user is not None and temp_user["password"] == old_password:
            if new_password == confirm_password:
                db.update_password(username, new_password)
                return render_template('changepasswordsuccess.html', page="Change Password")
            else:
                return render_template('changepassword.html', error="New password and confirm password do not match.")
        else:
            return render_template('changepassword.html', error="Incorrect old password. Please try again.")

    return render_template('changepassword.html', page="Change Password")

@app.route('/logout')
def logout():
    session.pop("user",None)
    session.pop("cart",None)
    return redirect('/')

@app.route('/addtocart')
def addtocart():
    code = request.args.get('code', '')
    product = db.get_product(int(code))
    item = dict()

    item["qty"] = int(request.args.get('quantity', 1))
    item["name"] = product["name"]
    item["subtotal"] = product["price"] * item["qty"]

    if session.get("cart") is None:
        session["cart"] = {}

    cart = session["cart"]
    cart[code] = item
    session["cart"] = cart
    return redirect('/cart')

@app.route('/cart')
def cart():
    cart = session.get("cart", {})
    return render_template('cart.html')

@app.route('/updatecart', methods=['POST'])
def updatecart():
    cart = session.get("cart", {})

    for code, quantity in request.form.items():
        if code.startswith('quantity_'):
            code = code.replace('quantity_', '')
            cart[code]["qty"] = int(quantity)
            cart[code]["subtotal"] = db.get_product(int(code))["price"] * int(quantity)
            
    session["cart"] = cart
    return redirect('/cart')

@app.route('/removefromcart')
def removefromcart():
    code = request.args.get('code', '')
    
    cart = session.get("cart", {})
    if code in cart:
        del cart[code]
        session["cart"] = cart
    
    return redirect('/cart')

@app.route('/clearcart')
def clearcart():
    session.pop("cart", None)
    return redirect('/cart')

@app.route('/checkout')
def checkout():
    om.create_order_from_cart()
    session.pop("cart",None)
    return redirect('/ordercomplete')

@app.route('/ordercomplete')
def ordercomplete():
    return render_template('ordercomplete.html')

@app.route('/pastorders')
def pastorders():
    if "user" in session:
        username = session["user"]["username"]
        past_orders = om.get_past_orders(username)
        return render_template('pastorders.html', page="Past Orders", past_orders=past_orders)
    else:
        return redirect('/login')

@app.route('/api/products',methods=['GET'])
def api_get_products():
    resp = make_response( dumps(db.get_products()) )
    resp.mimetype = 'application/json'
    return resp

@app.route('/api/products/<int:code>',methods=['GET'])
def api_get_product(code):
    resp = make_response(dumps(db.get_product(code)))
    resp.mimetype = 'application/json'
    return resp

