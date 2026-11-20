import os
from flask import Flask, render_template_string, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///khaled_store.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='Pending')

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Khaled Store</title>
    <style>
        body { background-color: #121212; color: white; font-family: sans-serif; margin: 0; padding: 15px; }
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
        .header h1 { margin: 0; font-size: 22px; color: #a855f7; }
        .stats { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 20px; }
        .card { background: #1E1E24; padding: 15px; border-radius: 12px; text-align: center; }
        .card h3 { margin: 0; font-size: 12px; color: #888; }
        .card p { margin: 5px 0 0; font-size: 20px; font-weight: bold; color: #fff; }
        .order-card { background: #1E1E24; padding: 15px; border-radius: 12px; margin-bottom: 10px; border-left: 4px solid #a855f7; }
        .order-card h4 { margin: 0 0 5px; font-size: 16px; }
        .order-card p { margin: 2px 0; font-size: 12px; color: #aaa; }
        .badge { display: inline-block; padding: 4px 8px; border-radius: 6px; font-size: 10px; font-weight: bold; margin-top: 5px; }
        .pending { background: #f59e0b; color: black; }
        .delivered { background: #10b981; color: white; }
        input { width: 100%; padding: 12px; border-radius: 8px; border: 1px solid #333; background: #121212; color: white; box-sizing: border-box; margin-bottom: 10px; }
        button { width: 100%; padding: 12px; background: #a855f7; color: white; border: none; border-radius: 8px; font-weight: bold; font-size: 16px; }
        a { text-decoration: none; color: #a855f7; font-size: 14px; }
        .btn-action { background: #2B2B36; padding: 8px; border-radius: 6px; text-align: center; color: white; display: block; margin-top: 5px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Khaled Store</h1>
        <a href="/add">+ Add Order</a>
    </div>
    <div class="stats">
        <div class="card"><h3>Total Orders</h3><p>{{ total }}</p></div>
        <div class="card"><h3>Pending</h3><p style="color: #f59e0b;">{{ pending }}</p></div>
        <div class="card"><h3>Delivered</h3><p style="color: #10b981;">{{ delivered }}</p></div>
        <div class="card"><h3>Total Sales</h3><p>{{ sales }} DZD</p></div>
    </div>
    <h2 style="font-size: 18px;">Recent Orders</h2>
    {% for order in orders %}
    <div class="order-card">
        <h4>{{ order.customer }}</h4>
        <p>📍 {{ order.address }}</p>
        <p>📞 {{ order.phone }}</p>
        <p>💰 {{ order.amount }} DZD</p>
        <span class="badge {% if order.status == 'Pending' %}pending{% else %}delivered{% endif %}">{{ order.status }}</span>
        {% if order.status == 'Pending' %}
        <a href="/deliver/{{ order.id }}" class="btn-action" style="background: #10b981; color: black;">Mark as Delivered</a>
        {% endif %}
    </div>
    {% endfor %}
</body>
</html>
"""

HTML_ADD = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { background-color: #121212; color: white; font-family: sans-serif; padding: 20px; }
        input { width: 100%; padding: 12px; margin-bottom: 10px; border-radius: 8px; border: 1px solid #333; background: #1E1E24; color: white; box-sizing: border-box;}
        button { width: 100%; padding: 12px; background: #a855f7; color: white; border: none; border-radius: 8px; font-weight: bold; }
    </style>
</head>
<body>
    <h2>Add New Order</h2>
    <form method="POST">
        <input type="text" name="customer" placeholder="Customer Name" required>
        <input type="text" name="phone" placeholder="Phone Number" required>
        <input type="text" name="address" placeholder="Address" required>
        <input type="number" name="amount" placeholder="Amount (DZD)" required>
        <button type="submit">Save Order</button>
    </form>
    <br><a href="/" style="color:#a855f7;">← Back</a>
</body>
</html>
"""

@app.route('/')
def index():
    orders = Order.query.order_by(Order.id.desc()).all()
    total = len(orders)
    pending = len([o for o in orders if o.status == 'Pending'])
    delivered = len([o for o in orders if o.status == 'Delivered'])
    sales = sum([o.amount for o in orders if o.status == 'Delivered'])
    return render_template_string(HTML, orders=orders, total=total, pending=pending, delivered=delivered, sales=sales)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        new_order = Order(customer=request.form['customer'], phone=request.form['phone'], address=request.form['address'], amount=float(request.form['amount']))
        db.session.add(new_order)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template_string(HTML_ADD)

@app.route('/deliver/<int:id>')
def deliver(id):
    order = Order.query.get_or_404(id)
    order.status = 'Delivered'
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
