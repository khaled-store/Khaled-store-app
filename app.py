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

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    product = db.Column(db.String(100), nullable=True)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='Pending')

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
        
        .badge { padding: 4px 8px; border-radius: 12px; font-size: 10px; font-weight: bold; }
        .badge-pending { background: #fff3cd; color: #856404; }
        .badge-delivered { background: #d4edda; color: #155724; }
        
        .action-btn { width: 26px; height: 26px; border-radius: 50%; display: inline-flex; justify-content: center; align-items: center; color: white; text-decoration: none; margin-left: 4px; font-size: 11px; }
        .btn-whatsapp { background: #25d366; }
        .btn-call { background: #007bff; }
        
        .btn-primary { font-size: 12px; padding: 6px 12px; }
        
        /* مخفي زر القائمة في الحاسوب، و كيبان في الهاتف */
        .mobile-menu-btn { display: none; background: transparent; border: none; font-size: 20px; color: #a855f7; cursor: pointer; }

        /* تصميم الهواتف (Responsive) */
        @media (max-width: 768px) {
            .sidebar { right: -220px; /* مخفية على اليمين */ }
            .sidebar.show { right: 0; } /* كتظهر كي نضغطو على الزر */
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
                <button class="mobile-menu-btn" onclick="toggleMenu()"><i class="fas fa-bars"></i></button>
                <h4>{{ page_title }}</h4>
            </div>
        </div>
        {{ content|safe }}
    </div>

    <script>
        function toggleMenu() {
            document.getElementById('sidebar').classList.toggle('show');
        }
    </script>
</body>
</html>
"""

@app.route('/orders')
def orders():
    all_orders = Order.query.order_by(Order.id.desc()).all()
    rows = ""
    for order in all_orders:
        status_class = "badge-pending" if order.status == 'Pending' else "badge-delivered"
        phone = order.phone if order.phone else ""
        wa_phone = phone[1:] if phone.startswith('0') else phone
        
        rows += f"""
        <tr>
            <td style="direction: ltr; text-align: right;">{order.phone}</td>
            <td>{order.customer}</td>
            <td>{order.product or '-'}</td>
            <td>{order.amount} د.ج</td>
            <td><span class="badge {status_class}">{order.status}</span></td>
            <td style="direction: ltr; text-align: right;">
                <a href="tel:{order.phone}" class="action-btn btn-call"><i class="fas fa-phone"></i></a>
                <a href="https://wa.me/213{wa_phone}" target="_blank" class="action-btn btn-whatsapp"><i class="fab fa-whatsapp"></i></a>
            </td>
        </tr>
        """
    
    if not rows:
        rows = '<tr><td colspan="6" class="text-center text-muted">لا توجد طلبات حالياً.</td></tr>'

    content = f"""
    <div class="card-custom">
        <div class="mb-3"><a href="/add" class="btn btn-primary" style="background:#a855f7; border:none;">+ طلب جديد</a></div>
        <div style="overflow-x: auto;">
            <table>
                <thead><tr><th>الهاتف</th><th>الاسم</th><th>المنتج</th><th>المبلغ</th><th>الحالة</th><th>إجراء</th></tr></thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
    </div>
    """
    return render_template_string(BASE_HTML, sidebar=get_sidebar('orders'), page_title="الطلبات", content=content)

ADD_ORDER_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
<style>body { font-family: 'Cairo'; background: #f4f6f9; padding: 15px; font-size: 13px; } .form-container { background: white; padding: 20px; border-radius: 10px; max-width: 500px; margin: 0 auto; }</style></head>
<body>
    <div class="form-container">
        <h4 class="mb-3" style="color:#a855f7;">إضافة طلب جديد</h4>
        <form method="POST">
            <div class="mb-2"><label class="form-label" style="font-size:12px;">اسم العميل</label><input type="text" name="customer" class="form-control form-control-sm" required></div>
            <div class="mb-2"><label class="form-label" style="font-size:12px;">رقم الهاتف</label><input type="text" name="phone" class="form-control form-control-sm" required></div>
            <div class="mb-2"><label class="form-label" style="font-size:12px;">العنوان</label><input type="text" name="address" class="form-control form-control-sm" required></div>
            <div class="mb-2"><label class="form-label" style="font-size:12px;">المنتج</label><input type="text" name="product" class="form-control form-control-sm"></div>
            <div class="mb-2"><label class="form-label" style="font-size:12px;">المبلغ</label><input type="number" name="amount" class="form-control form-control-sm" required></div>
            <button type="submit" class="btn btn-primary w-100 mt-2" style="background:#a855f7; border:none; font-size:13px;">حفظ</button>
        </form>
        <a href="/orders" class="d-block text-center mt-3 text-decoration-none" style="font-size:12px;">رجوع للطلبات</a>
    </div>
</body></html>
"""

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        new_order = Order(
            customer=request.form['customer'], 
            phone=request.form['phone'], 
            address=request.form['address'], 
            product=request.form.get('product'), 
            amount=float(request.form['amount'])
        )
        db.session.add(new_order)
        db.session.commit()
        return redirect(url_for('orders'))
    return render_template_string(ADD_ORDER_HTML)

@app.route('/')
def dashboard():
    content = """
    <div class="card-custom" style="text-align: center; padding: 30px;">
        <h4 style="color: #a855f7;">أهلاً بك يا خالد!</h4>
        <p style="font-size: 13px;">مرحباً بك في لوحة التحكم الخاصة بمتجرك.</p>
        <a href="/orders" class="btn btn-primary mt-2" style="background:#a855f7; border:none; font-size:12px;">الذهاب للطلبات</a>
    </div>
    """
    return render_template_string(BASE_HTML, sidebar=get_sidebar('home'), page_title="لوحة التحكم", content=content)

@app.route('/<page_name>')
def generic_page(page_name):
    titles = {
        'kpi': 'مؤشرات الأداء', 'channels': 'قنوات البيع', 'products': 'المنتجات',
        'pos': 'نقطة البيع', 'barcode': 'الماسح الضوئي', 'inventory': 'المخزون',
        'supply': 'التوريد', 'expenses': 'المصاريف', 'finance': 'المالية',
        'users': 'المستخدمون', 'customers': 'العملاء', 'delivery': 'شريك التوصيل',
        'analytics': 'التحليلات', 'sendpilot': 'Sendpilot', 'ads': 'محل الإعلانات', 'ai': 'الذكاء الاصطناعي'
    }
    title = titles.get(page_name, "صفحة")
    
    content = f"""
    <div class="card-custom" style="text-align: center; padding: 30px;">
        <i class="fas fa-tools" style="font-size: 40px; color: #a855f7; margin-bottom: 15px;"></i>
        <h4>مرحباً بك في قسم {title}</h4>
        <p class="text-muted" style="font-size: 12px;">هذه الصفحة جاهزة للربط مع قاعدة البيانات قريباً.</p>
    </div>
    """
    return render_template_string(BASE_HTML, sidebar=get_sidebar(page_name), page_title=title, content=content)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
