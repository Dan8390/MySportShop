from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import hashlib
from werkzeug.utils import redirect

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clothes_shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


def compute_sha512_hash(input_string):
    sha512_hash = hashlib.sha512()
    sha512_hash.update(input_string.encode('utf-8'))
    return sha512_hash.hexdigest()


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tracker_code = db.Column(db.Integer, nullable=False)
    goods = db.Column(db.String(1000), nullable=False)
    client_phone = db.Column(db.String(20), nullable=False)
    date = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return '<Order %r>' % self.id


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    country = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return '<Product %r>' % self.id


class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    surname = db.Column(db.String(30), nullable=False)
    phone = db.Column(db.String(19), nullable=False)
    cart = db.Column(db.String(1000), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return '<Client %r>' % self.id


@app.route("/", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        hash_password = compute_sha512_hash(password)

        clients = Client.query.all()
        found_user = None
        for i in clients:
            if i.email == login:
                if i.password == hash_password:
                    found_user = i
                    break

        if found_user is None:
            return redirect("/")
        if found_user.email.endswith("admin"):
            return render_template("welcome_page.html")
        else:
            products = Product.query.all()
            return render_template("product_u.html", products=products, c_id=found_user.id)
    else:
        return render_template("login.html")


@app.route("/registration", methods=['POST', 'GET'])
def show_registration():
    if request.method == "POST":
        name = request.form['name']
        surname = request.form['surname']
        phone = request.form['phone']
        email = request.form['email']
        password = request.form['password']

        hash_password = compute_sha512_hash(password)

        new_client = Client(name=name, surname=surname, phone=phone, email=email, password=str(hash_password), cart="")

        try:
            db.session.add(new_client)
            db.session.commit()
            return redirect("/")
        except:
            return "Помилка при додаванні клієнта"
    else:
        return render_template("registration.html")


@app.route("/clients")
def show_clients():
    clients = Client.query.all()
    return render_template("clients.html", clients=clients)


@app.route("/clients/<int:client_id>")
def client_detail_view(client_id):
    client = Client.query.get_or_404(client_id)
    return render_template("client_detail_view.html", client=client)


@app.route("/<int:c_id>/buy/<int:p_id>")
def buy(c_id, p_id):
    client = Client.query.get_or_404(c_id)
    client.cart += Product.query.get_or_404(p_id).title + " "
    db.session.commit()
    products = Product.query.all()
    return render_template("product_u.html", products=products, id=client.id)


@app.route("/<int:id>/cart")
def show_cart(id):
    client = Client.query.get_or_404(id)
    client_cart = client.cart
    return render_template("cart.html", cart=client_cart, id=client.id)


@app.route("/<int:id>/buy/finish")
def finish(id):
    client = Client.query.get_or_404(id)
    client.cart = ""
    db.session.commit()
    products = Product.query.all()
    return render_template("product_u.html", products=products, id=client.id)


@app.route("/products")
def show_products():
    products = Product.query.all()
    return render_template("product_a.html", products=products)


@app.route('/product/create', methods=['POST', 'GET'])
def create_product():
    if request.method == "POST":
        title = request.form['title']
        price = request.form['price']
        country = request.form['country']

        new_product = Product(title=title, price=price, country=country)

        try:
            db.session.add(new_product)
            db.session.commit()
            return redirect("/")
        except:
            return "Помилка при додаванні товару"
    else:
        return render_template("product_create.html")


@app.route("/products/<int:product_id>")
def product_detail_view(product_id):
    product = Product.query.get(product_id)
    return render_template("product_detail_view.html", product=product)


@app.route("/products/<int:product_id>/update", methods=["POST", "GET"])
def product_update(product_id):
    product = Product.query.get(product_id)
    if request.method == "POST":
        product.title = request.form['title']
        product.price = request.form['price']
        product.country = request.form['country']
        try:
            db.session.commit()
            return redirect('/products')
        except:
            return "Сталася помилка редагування даних товару"
    else:
        return render_template("product_update.html", product=product)


@app.route("/products/<int:product_id>/delete", methods=['POST', 'GET'])
def product_delete(product_id):
    product = Product.query.get(product_id)
    try:
        db.session.delete(product)
        db.session.commit()
        return redirect('/products')
    except:
        return "Сталася помилка видалення товару"


@app.route("/orders")
def show_orders():
    orders = Order.query.all()
    return render_template("orders_a.html", orders=orders)


@app.route("/orders/create", methods=['POST', 'GET'])
def create_order():
    if request.method == "POST":
        tracker_code = request.form['tracker_code']
        goods = request.form['goods']
        client_phone = request.form['client_phone']
        date = datetime.fromisoformat(request.form['date'])

        new_order = Order(tracker_code=tracker_code, goods=goods, client_phone=client_phone, date=date)

        try:
            db.session.add(new_order)
            db.session.commit()
            return redirect("/")
        except:
            return "Помилка при додаванні замовлення"
    else:
        return render_template("order_create.html")


@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
