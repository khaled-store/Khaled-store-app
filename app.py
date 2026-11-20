import os
from flask import Flask, render_template_string, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

db_url = os.environ.get('DATABASE_URL', 'sqlite:///khaled_store.db')
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ================== قاعدة البيانات ==================
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    product = db.Column(db.String(100), nullable=True)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='Pending')

class Ad(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    budget = db.Column(db.Float, nullable=False)
    platform = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='Active')

# ================== القائمة الجانبية (Sidebar) ==================
def get_sidebar(active_page):
    links = [
        ("/", "home", "fas fa-home", "لوحة التحكم"),
        ("/kpi", "kpi", "fas fa-chart-line", "مؤشرات الأداء (KPI)"),
        ("/channels", "channels", "fas fa-store", "قنوات البيع"),
        ("/products", "products", "fas fa-box", "المنتجات"),
        ("/orders", "orders", "fas fa-clipboard-list", "الطلبات"),
        ("/pos", "pos", "fas fa-cash-register", "نقطة البيع"),
        ("/barcode", "barcode", "fas fa-barcode", "الماسح الضوئي"),
        ("/inventory", "inventory", "fas fa-warehouse", "المخزون"),
        ("/supply", "supply", "fas fa-truck-loading", "التوريد"),
        ("/expenses", "expenses", "fas fa-money-bill-wave", "المصاريف"),
        ("/finance", "finance", "fas fa-wallet", "المالية"),
        ("/users", "users", "fas fa-users", "المستخدمون"),
        ("/customers", "customers", "fas fa-user-friends", "العملاء"),
        ("/delivery", "delivery", "fas fa-truck", "شريك التوصيل"),
        ("/analytics", "analytics", "fas fa-chart-bar", "التحليلات"),
        ("/sendpilot", "sendpilot", "fas fa-paper-plane", "Sendpilot"),
        ("/ads", "ads", "fas fa-bullhorn", "محل الإعلانات"),
        ("/ai", "ai", "fas fa-robot", "AI"),
    ]
    html = '<div class="sidebar"><h4>Khaled Store</h4>'
    for url, page, icon, name in links:
        active = 'active' if active_page == page else ''
        html += f'<a href="{url}" class="{active}"><i class="{icon}"></i> {name}</a>'
    html += '</div>'
    return html

# ================== القالب الأساسي ==================
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
        body { font-family: 'Cairo', sans-serif; background-color: #f4f6f9; margin: 0; }
        .sidebar { background: #1a1c2e; color: white; height: 100vh; width: 250px; position: fixed; right: 0; top: 0; overflow-y: auto; }
        .sidebar h4 { padding: 20px; text-align: center; border-bottom: 1px solid #2d2f45; color: #a855f7; font-weight: bold; }
        .sidebar a { display: flex; align-items: center; padding: 12px 20px; color: #b0b3c6; text-decoration: none; font-size: 14px; transition: 0.3s; }
        .sidebar a:hover, .sidebar a.active { background: #2d2f45; color: white; border-right: 4px solid #a855f7; }
        .sidebar a i { margin-left: 10px; width: 20px; text-align: center; }
        .main-content { margin-right: 250px; padding: 20px; }
        .topbar { display: flex; justify-content: space-between; align-items: center; background: white; padding: 15px 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); margin-bottom: 20px; }
        .card-custom { background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
        table { width: 100%; border-collapse: collapse; }
        th { background: #f8f9fa; padding: 12px; text-align: right; font-size: 13px; color: #6c757d; border-bottom: 2px solid #dee2e6; }
        td { padding: 12px; border-bottom: 1px solid #dee2e6; font-size: 13px; vertical-align: middle; }
        .badge { padding: 5px 10px; border-radius: 20px; font-size: 11px; font-weight: bold; }
        .badge-pending { background: #fff3cd; color: #856404; }
        .badge-delivered { background: #d4edda; color: #155724; }
        .action-btn { width: 30px; height: 30px; border-radius: 50%; display: inline-flex; justify-content: center; align-items: center; color: white; text-decoration: none; margin-left: 5px; }
        .btn-whatsapp { background: #25d366; }
        .btn-call { background: #007bff; }
    </style>
</head>
<body>
    {{ sidebar|safe }}
    <div class="main-content">
        <div class="topbar">
            <h4 class="mb-0">{{ page_title }}</h4>
        </div>
        {{ content|safe }}
    </div>
</body>
</html>
"""

# ================== صفحة الطلبات ==================
ORDERS_CONTENT = """
<div class="card-custom">
    <table>
        <thead><tr><th>هاتف العميل</th><th>اسم العميل</th><th>المنتج</th><th>المبلغ</th><th>الحالة</th><th>إجراءات</th></tr></thead>
        <tbody>
            {% for order in orders %}
            <tr>
                <td style="direction: ltr; text-align: right;">{{ order.phone }}</td>
                <td>{{ order.customer }}</td>
                <td>{{ order.product or '-' }}</td>
                <td>{{ order.amount }} د.ج</td>
                <td><span class="badge {% if order.status == 'Pending' %}badge-pending{% else %}badge-delivered{% endif %}">{{ order.status }}</span></td>
                <td style="direction: ltr; text-align: right;">
                    <a href="tel:{{ order.phone }}" class="action-btn btn-call"><i class="fas fa-phone"></i></a>
                    <a href="https://wa.me/213{{ order.phone[1:] if order.phone.startswith('0') else order.phone }}" target="_blank" class="action-btn btn-whatsapp"><i class="fab fa-whatsapp"></i></a>
                </td>
            </tr>
            {% else %}
            <tr><td colspan="6" class="text-center text-muted">لا توجد طلبات حالياً.</td></tr>
            {% endfor %}
        </tbody>
    </table>
</div>
"""

# ================== صفحة الإعلانات ==================
ADS_CONTENT = """
<div class="card-custom">
    <div class="mb-3"><button class="btn btn-primary" style="background:#a855f7; border:none;">+ حملة إعلانية جديدة</button></div>
    <table>
        <thead><tr><th>اسم الحملة</th><th>المنصة</th><th>الميزانية</th><th>الحالة</th></tr></thead>
        <tbody>
            <tr><td>حملة رمضان</td><td>فيسبوك</td><td>50000 د.ج</td><td><span class="badge badge-delivered">Active</span></td></tr>
            <tr><td>ترويج المنتجات</td><td>تيك توك</td><td>20000 د.ج</td><td><span class="badge badge-delivered">Active</span></td></tr>
        </tbody>
    </table>
</div>
"""

# ================== صفحة عامة (لأي أيقونة أخرى) ==================
def generate_generic_page(page_title):
    return f"""
    <div class="card-custom" style="text-align: center; padding: 50px;">
        <i class="fas fa-tools" style="font-size: 50px; color: #a855f7; margin-bottom: 20px;"></i>
        <h3>مرحباً بك في قسم {page_title}</h3>
        <p class="text-muted">هذه الصفحة جاهزة للربط مع قاعدة البيانات قريباً.</p>
    </div>
    """

# ================== المسارات (Routes) ==================
@app.route('/')
def dashboard():
    return render_template_string(BASE_HTML, sidebar=get_sidebar('home'), page_title="لوحة التحكم", content="<h3>أهلاً بك يا خالد!</h3>")

@app.route('/orders')
def orders():
    all_orders = Order.query.order_by(Order.id.desc()).all()
    html_content = render_template_string(ORDERS_CONTENT, orders=all_orders)
    return render_template_string(BASE_HTML, sidebar=get_sidebar('orders'), page_title="الطلبات", content=html_content)

@app.route('/ads')
def ads():
    return render_template_string(BASE_HTML, sidebar=get_sidebar('ads'), page_title="محل الإعلانات", content=ADS_CONTENT)

@app.route('/<page_name>')
def generic_page(page_name):
    titles = {
        'kpi': 'مؤشرات الأداء', 'channels': 'قنوات البيع', 'products': 'المنتجات',
        'pos': 'نقطة البيع', 'barcode': 'الماسح الضوئي', 'inventory': 'المخزون',
        'supply': 'التوريد', 'expenses': 'المصاريف', 'finance': 'المالية',
        'users': 'المستخدمون', 'customers': 'العملاء', 'delivery': 'شريك التوصيل',
        'analytics': 'التحليلات', 'sendpilot': 'Sendpilot', 'ai': 'الذكاء الاصطناعي'
    }
    title = titles.get(page_name, "صفحة")
    return render_template_string(BASE_HTML, sidebar=get_sidebar(page_name), page_title=title, content=generate_generic_page(title))

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
