import os
import google.generativeai as genai
from flask import Flask, render_template_string, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

db_url = os.environ.get('DATABASE_URL', 'sqlite:///khaled_store.db')
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ================== الذكاء الاصطناعي (Gemini) ==================
genai.configure(api_key=os.environ.get("GEMINI_API_KEY", "AIza..."))
ai_model = genai.GenerativeModel('gemini-1.5-flash')

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    product = db.Column(db.String(100), nullable=True)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='Pending')

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)

def get_sidebar(active_page):
    links = [
        ("/", "home", "fas fa-home", "لوحة التحكم"),
        ("/orders", "orders", "fas fa-clipboard-list", "الطلبات"),
        ("/products", "products", "fas fa-box", "المنتجات"),
        ("/customers", "customers", "fas fa-user-friends", "العملاء"),
        ("/expenses", "expenses", "fas fa-money-bill-wave", "المصاريف"),
        ("/ai", "ai", "fas fa-robot", "الذكاء الاصطناعي (AI)"),
    ]
    html = '<div class="sidebar" id="sidebar"><h4>Khaled Store</h4>'
    for url, page, icon, name in links:
        active = 'active' if active_page == page else ''
        html += f'<a href="{url}" class="{active}"><i class="{icon}"></i> {name}</a>'
    html += '</div>'
    return html

BASE_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Khaled Store - {{ page_title }}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
        body { font-family: 'Cairo', sans-serif; background-color: #f4f6f9; margin: 0; font-size: 13px; }
        .sidebar { background: #1a1c2e; color: white; height: 100vh; width: 220px; position: fixed; right: 0; top: 0; overflow-y: auto; transition: 0.3s; z-index: 1000; }
        .sidebar h4 { padding: 15px; text-align: center; border-bottom: 1px solid #2d2f45; color: #a855f7; font-weight: bold; font-size: 16px; margin: 0; }
        .sidebar a { display: flex; align-items: center; padding: 10px 15px; color: #b0b3c6; text-decoration: none; font-size: 12px; transition: 0.2s; }
        .sidebar a:hover, .sidebar a.active { background: #2d2f45; color: white; border-right: 3px solid #a855f7; }
        .sidebar a i { margin-left: 10px; width: 18px; text-align: center; font-size: 14px; }
        .main-content { margin-right: 220px; padding: 15px; transition: 0.3s; }
        .topbar { display: flex; justify-content: space-between; align-items: center; background: white; padding: 10px 15px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 15px; }
        .topbar h4 { font-size: 16px; margin: 0; font-weight: bold; }
        .card-custom { background: white; border-radius: 8px; padding: 15px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        table { width: 100%; border-collapse: collapse; }
        th { background: #f8f9fa; padding: 10px; text-align: right; font-size: 12px; color: #6c757d; border-bottom: 1px solid #dee2e6; }
        td { padding: 10px; border-bottom: 1px solid #dee2e6; font-size: 12px; vertical-align: middle; }
        .badge-pending { background: #fff3cd; color: #856404; padding: 4px 8px; border-radius: 12px; font-size: 10px; }
        .btn-primary { background: #a855f7; border: none; font-size: 12px; padding: 6px 12px; }
        .mobile-menu-btn { display: none; background: transparent; border: none; font-size: 20px; color: #a855f7; cursor: pointer; }
        .chat-container { display: flex; flex-direction: column; height: calc(100vh - 120px); background: white; border-radius: 8px; overflow: hidden; }
        .chat-box { flex: 1; padding: 15px; overflow-y: auto; }
        .msg { margin-bottom: 10px; padding: 10px; border-radius: 8px; max-width: 80%; }
        .msg-user { background: #a855f7; color: white; align-self: flex-end; margin-right: auto; }
        .msg-ai { background: #f1f5f9; color: #333; align-self: flex-start; margin-left: auto; }
        .chat-input { display: flex; padding: 10px; border-top: 1px solid #eee; }
        @media (max-width: 768px) {
            .sidebar { right: -220px; }
            .sidebar.show { right: 0; }
            .main-content { margin-right: 0; }
            .mobile-menu-btn { display: block; }
        }
    </style>
</head>
<body>
    {{ sidebar|safe }}
    <div class="main-content">
        <div class="topbar">
            <div style="display:flex; align-items:center; gap:10px;">
                <button class="mobile-menu-btn" onclick="document.getElementById('sidebar').classList.toggle('show')"><i class="fas fa-bars"></i></button>
                <h4>{{ page_title }}</h4>
            </div>
        </div>
        {{ content|safe }}
    </div>
</body>
</html>
"""

@app.route('/')
def dashboard():
    total_orders = Order.query.count()
    total_products = Product.query.count()
    total_customers = Customer.query.count()
    total_sales = db.session.query(db.func.sum(Order.amount)).filter(Order.status == 'Delivered').scalar() or 0
    content = f"""
    <div class="row">
        <div class="col-6 col-md-3 mb-3"><div class="card-custom text-center"><h6>الطلبات</h6><h3 class="text-primary">{total_orders}</h3></div></div>
        <div class="col-6 col-md-3 mb-3"><div class="card-custom text-center"><h6>المنتجات</h6><h3 class="text-primary">{total_products}</h3></div></div>
        <div class="col-6 col-md-3 mb-3"><div class="card-custom text-center"><h6>العملاء</h6><h3 class="text-primary">{total_customers}</h3></div></div>
        <div class="col-6 col-md-3 mb-3"><div class="card-custom text-center"><h6>المبيعات</h6><h3 class="text-success">{total_sales} د.ج</h3></div></div>
    </div>
    """
    return render_template_string(BASE_HTML, sidebar=get_sidebar('home'), page_title="لوحة التحكم", content=content)

@app.route('/orders')
def orders():
    all_orders = Order.query.order_by(Order.id.desc()).all()
    rows = "".join([f"<tr><td>{o.phone}</td><td>{o.customer}</td><td>{o.product or '-'}</td><td>{o.amount} د.ج</td><td><span class='badge-pending'>{o.status}</span></td><td><a href='tel:{o.phone}' class='btn btn-sm btn-primary'><i class='fas fa-phone'></i></a></td></tr>" for o in all_orders])
    content = f"""
    <div class="card-custom">
        <div class="mb-3"><a href="/add" class="btn btn-primary">+ طلب جديد</a></div>
        <div style="overflow-x: auto;"><table><thead><tr><th>الهاتف</th><th>الاسم</th><th>المنتج</th><th>المبلغ</th><th>الحالة</th><th>إجراء</th></tr></thead><tbody>{rows or '<tr><td colspan=6>لا توجد طلبات.</td></tr>'}</tbody></table></div>
    </div>
    """
    return render_template_string(BASE_HTML, sidebar=get_sidebar('orders'), page_title="الطلبات", content=content)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        db.session.add(Order(customer=request.form['customer'], phone=request.form['phone'], address=request.form['address'], product=request.form.get('product'), amount=float(request.form['amount'])))
        db.session.commit()
        return redirect(url_for('orders'))
    return """
    <div class="card-custom" style="max-width:500px; margin:auto;">
        <h5 class="mb-3">إضافة طلب</h5>
        <form method="POST">
            <input type="text" name="customer" class="form-control mb-2" placeholder="اسم العميل" required>
            <input type="text" name="phone" class="form-control mb-2" placeholder="رقم الهاتف" required>
            <input type="text" name="address" class="form-control mb-2" placeholder="العنوان" required>
            <input type="text" name="product" class="form-control mb-2" placeholder="المنتج">
            <input type="number" name="amount" class="form-control mb-2" placeholder="المبلغ" required>
            <button type="submit" class="btn btn-primary w-100">حفظ</button>
        </form>
        <a href="/orders" class="d-block text-center mt-3">رجوع</a>
    </div>
    """

@app.route('/products', methods=['GET', 'POST'])
def products():
    if request.method == 'POST':
        db.session.add(Product(name=request.form['name'], price=float(request.form['price']), stock=int(request.form['stock'])))
        db.session.commit()
        return redirect(url_for('products'))
    all_products = Product.query.all()
    rows = "".join([f"<tr><td>{p.name}</td><td>{p.price} د.ج</td><td>{p.stock}</td></tr>" for p in all_products])
    content = f"""
    <div class="card-custom">
        <form method="POST" class="row g-2 mb-3">
            <div class="col-4"><input type="text" name="name" class="form-control" placeholder="اسم المنتج" required></div>
            <div class="col-3"><input type="number" name="price" class="form-control" placeholder="السعر" required></div>
            <div class="col-3"><input type="number" name="stock" class="form-control" placeholder="الكمية" required></div>
            <div class="col-2"><button type="submit" class="btn btn-primary w-100">إضافة</button></div>
        </form>
        <table><thead><tr><th>المنتج</th><th>السعر</th><th>الكمية</th></tr></thead><tbody>{rows or '<tr><td colspan=3>لا توجد منتجات.</td></tr>'}</tbody></table>
    </div>
    """
    return render_template_string(BASE_HTML, sidebar=get_sidebar('products'), page_title="المنتجات", content=content)

@app.route('/customers', methods=['GET', 'POST'])
def customers():
    if request.method == 'POST':
        db.session.add(Customer(name=request.form['name'], phone=request.form['phone']))
        db.session.commit()
        return redirect(url_for('customers'))
    all_customers = Customer.query.all()
    rows = "".join([f"<tr><td>{c.name}</td><td>{c.phone}</td></tr>" for c in all_customers])
    content = f"""
    <div class="card-custom">
        <form method="POST" class="row g-2 mb-3">
            <div class="col-5"><input type="text" name="name" class="form-control" placeholder="اسم العميل" required></div>
            <div class="col-5"><input type="text" name="phone" class="form-control" placeholder="رقم الهاتف" required></div>
            <div class="col-2"><button type="submit" class="btn btn-primary w-100">إضافة</button></div>
        </form>
        <table><thead><tr><th>الاسم</th><th>الهاتف</th></tr></thead><tbody>{rows or '<tr><td colspan=2>لا يوجد عملاء.</td></tr>'}</tbody></table>
    </div>
    """
    return render_template_string(BASE_HTML, sidebar=get_sidebar('customers'), page_title="العملاء", content=content)

@app.route('/expenses', methods=['GET', 'POST'])
def expenses():
    if request.method == 'POST':
        db.session.add(Expense(title=request.form['title'], amount=float(request.form['amount'])))
        db.session.commit()
        return redirect(url_for('expenses'))
    all_exp = Expense.query.all()
    rows = "".join([f"<tr><td>{e.title}</td><td>{e.amount} د.ج</td></tr>" for e in all_exp])
    content = f"""
    <div class="card-custom">
        <form method="POST" class="row g-2 mb-3">
            <div class="col-5"><input type="text" name="title" class="form-control" placeholder="اسم المصروف" required></div>
            <div class="col-5"><input type="number" name="amount" class="form-control" placeholder="المبلغ" required></div>
            <div class="col-2"><button type="submit" class="btn btn-primary w-100">إضافة</button></div>
        </form>
        <table><thead><tr><th>المصروف</th><th>المبلغ</th></tr></thead><tbody>{rows or '<tr><td colspan=2>لا توجد مصاريف.</td></tr>'}</tbody></table>
    </div>
    """
    return render_template_string(BASE_HTML, sidebar=get_sidebar('expenses'), page_title="المصاريف", content=content)

@app.route('/ai')
def ai_page():
    content = """
    <div class="chat-container">
        <div class="chat-box" id="chat-box">
            <div class="msg msg-ai">أهلاً بك يا خالد! أنا مساعدك الذكي (Gemini). كيفاش نقدر نعاونك في متجرك اليوم؟</div>
        </div>
        <div class="chat-input">
            <input type="text" id="user-input" class="form-control me-2" placeholder="اسألني أي حاجة..." onkeypress="if(event.key==='Enter') sendMessage()">
            <button class="btn btn-primary" onclick="sendMessage()">إرسال</button>
        </div>
    </div>
    <script>
        async function sendMessage() {
            const input = document.getElementById('user-input');
            const text = input.value.trim();
            if(!text) return;
            const chatBox = document.getElementById('chat-box');
            chatBox.innerHTML += `<div class="msg msg-user">${text}</div>`;
            input.value = '';
            chatBox.scrollTop = chatBox.scrollHeight;
            const res = await fetch('/ask_ai', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({prompt: text}) });
            const data = await res.json();
            chatBox.innerHTML += `<div class="msg msg-ai">${data.reply}</div>`;
            chatBox.scrollTop = chatBox.scrollHeight;
        }
    </script>
    """
    return render_template_string(BASE_HTML, sidebar=get_sidebar('ai'), page_title="الذكاء الاصطناعي", content=content)

@app.route('/ask_ai', methods=['POST'])
def ask_ai():
    data = request.json
    prompt = data.get('prompt')
    try:
        response = ai_model.generate_content(prompt)
        reply = response.text
    except Exception as e:
        reply = f"خطأ: {str(e)}"
    return jsonify({"reply": reply})

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
