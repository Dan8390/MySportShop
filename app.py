from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.utils import redirect

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clothes_shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


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


@app.route("/")
def index():
    return render_template("welcome_page.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/clothes")
def clothes():
    products = Product.query.all()
    return render_template("clothes_a.html", products=products)


@app.route("/orders")
def show_orders():
    orders = Order.query.all()
    return render_template("orders.html", orders=orders)


@app.route('/clothes/create', methods=['POST', 'GET'])
def create_clothes():
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
            return "Помилка при додаванні статті"
    else:
        return render_template("product_create.html")


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


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
