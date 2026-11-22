import os
import requests
from flask import Flask, render_template_string, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "khaled_store_super_secret_key_123")

db_url = os.environ.get('DATABASE_URL', 'sqlite:///khaled_store.db')
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ================== إعدادات Google OAuth ==================
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "YOUR_CLIENT_ID.apps.googleusercontent.com")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "YOUR_CLIENT_SECRET")
REDIRECT_URI = os.environ.get("REDIRECT_URI", "https://khaled-store-app.onrender.com/login/callback")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_email' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ================== قاعدة البيانات ==================
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    wilaya = db.Column(db.String(50), nullable=False)
    baladiya = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False, default=0.0)
    status = db.Column(db.String(20), default='جديد')

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)

# ================== صفحة تسجيل الدخول ==================
LOGIN_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>تسجيل الدخول - Khaled Store</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');
        * { font-family: 'Cairo', sans-serif; box-sizing: border-box; }
        body { background-color: #f8f9fa; height: 100vh; display: flex; align-items: center; justify-content: center; margin: 0; }
        .login-card { background: #fff; padding: 40px 30px; border-radius: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.05); text-align: center; width: 90%; max-width: 400px; }
        .logo { width: 80px; height: 80px; background: #ede9fe; color: #8b5cf6; border-radius: 20px; display: flex; align-items: center; justify-content: center; font-size: 35px; margin: 0 auto 20px; }
        .btn-google { background: #fff; color: #333; border: 1px solid #ddd; padding: 12px; border-radius: 15px; font-weight: 600; width: 100%; display: flex; align-items: center; justify-content: center; gap: 10px; text-decoration: none; transition: 0.3s; }
        .btn-google:hover { background: #f1f1f1; }
    </style>
</head>
<body>
    <div class="login-card">
        <div class="logo"><i class="fas fa-store"></i></div>
        <h4 class="fw-bold mb-2">Khaled Store</h4>
        <p class="text-muted mb-4" style="font-size: 14px;">مرحباً بك، يرجى تسجيل الدخول للمتابعة</p>
        
        <a href="{{ auth_url }}" class="btn-google">
            <img src="https://upload.wikimedia.org/wikipedia/commons/5/53/Google_%22G%22_Logo.svg" width="20">
            المتابعة باستخدام Google
        </a>
        
        <p class="text-muted mt-4" style="font-size: 11px;">تطبيق محمي و آمن 100%</p>
    </div>
</body>
</html>
"""

BASE_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Khaled Store - {{ title }}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');
        * { font-family: 'Cairo', sans-serif; box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
        body { background-color: #f8f9fa; margin: 0; padding-bottom: 80px; color: #333; }
        .topbar { display: flex; justify-content: space-between; align-items: center; padding: 20px; background: #fff; border-bottom: 1px solid #eee; position: sticky; top: 0; z-index: 100; }
        .topbar h4 { margin: 0; font-weight: 700; font-size: 18px; }
        .bottom-nav { position: fixed; bottom: 0; left: 0; right: 0; background: #fff; display: flex; justify-content: space-around; padding: 10px 0 20px 0; box-shadow: 0 -2px 10px rgba(0,0,0,0.05); border-top-left-radius: 25px; border-top-right-radius: 25px; z-index: 1000; }
        .nav-item { text-align: center; color: #9ca3af; font-size: 11px; text-decoration: none; display: flex; flex-direction: column; align-items: center; gap: 5px; transition: 0.2s; }
        .nav-item.active { color: #8b5cf6; font-weight: 700; }
        .nav-item i { font-size: 20px; }
        .nav-item.add-btn { background: #8b5cf6; color: #fff; width: 50px; height: 50px; border-radius: 50%; display: flex; justify-content: center; align-items: center; margin-top: -25px; box-shadow: 0 4px 10px rgba(139, 92, 246, 0.4); }
        .nav-item.add-btn i { font-size: 24px; color: #fff; }
        .stat-card { border-radius: 20px; padding: 15px; text-align: right; position: relative; height: 100%; box-shadow: 0 2px 10px rgba(0,0,0,0.02); }
        .stat-card h6 { font-size: 12px; color: #6b7280; margin-bottom: 5px; font-weight: 600; }
        .stat-card h3 { font-size: 24px; font-weight: 800; margin: 0; }
        .stat-card .icon { position: absolute; top: 15px; left: 15px; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; border-radius: 50%; background: rgba(255,255,255,0.6); }
        .order-card { background: #fff; border-radius: 20px; padding: 15px; margin-bottom: 15px; box-shadow: 0 2px 10px rgba(0,0,0,0.03); border: 1px solid #f1f1f1; }
        .order-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
        .order-header h5 { margin: 0; font-size: 16px; font-weight: 700; }
        .order-header span { font-size: 12px; color: #9ca3af; }
        .badge-status { padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: bold; }
        .bg-new { background: #fef3c7; color: #d97706; }
        .bg-confirmed { background: #d1fae5; color: #059669; }
        .bg-delivered { background: #e0f2fe; color: #0284c7; }
        .btn-action { background: #8b5cf6; color: #fff; border-radius: 30px; padding: 6px 20px; font-size: 12px; font-weight: 600; border: none; text-decoration: none; display: inline-flex; align-items: center; gap: 5px;}
        .btn-call { background: #8b5cf6; color: #fff; width: 35px; height: 35px; border-radius: 50%; display: inline-flex; justify-content: center; align-items: center; text-decoration: none; }
        .form-control, .form-select { border-radius: 15px; padding: 12px 15px; border: 1px solid #e5e7eb; background: #f9fafb; font-size: 14px; margin-bottom: 15px; }
        .form-control:focus, .form-select:focus { box-shadow: none; border-color: #8b5cf6; background: #fff; }
        .form-label { font-size: 13px; font-weight: 600; color: #374151; margin-bottom: 8px; }
    </style>
</head>
<body>
    {{ content|safe }}
    <div class="bottom-nav">
        <a href="/" class="nav-item {% if active == 'home' %}active{% endif %}"><i class="fas fa-home"></i> لوحة التحكم</a>
        <a href="/orders" class="nav-item {% if active == 'orders' %}active{% endif %}"><i class="fas fa-box"></i> الطلبات</a>
        <a href="/add" class="nav-item add-btn"><i class="fas fa-plus"></i></a>
        <a href="/products" class="nav-item {% if active == 'products' %}active{% endif %}"><i class="fas fa-cubes"></i> المخزون</a>
        <a href="/profile" class="nav-item {% if active == 'profile' %}active{% endif %}"><i class="fas fa-user"></i> حسابي</a>
    </div>
</body>
</html>
"""

# ================== مسارات الدخول (OAuth) ==================
@app.route('/login')
def login():
    if 'user_email' in session:
        return redirect(url_for('dashboard'))
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?client_id={GOOGLE_CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope=openid%20email%20profile"
    return render_template_string(LOGIN_HTML, auth_url=auth_url)

@app.route('/login/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return redirect(url_for('login'))
    
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    res = requests.post(token_url, data=data).json()
    
    if 'access_token' in res:
        user_info = requests.get("https://www.googleapis.com/oauth2/v1/userinfo", headers={"Authorization": f"Bearer {res['access_token']}"}).json()
        session['user_email'] = user_info.get('email')
        session['user_name'] = user_info.get('name')
        return redirect(url_for('dashboard'))
    return "فشل تسجيل الدخول. حاول مرة أخرى.", 400

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ================== 1. لوحة التحكم ==================
@app.route('/')
@login_required
def dashboard():
    total = Order.query.count()
    delivered = Order.query.filter_by(status='منجز').count()
    confirmed = Order.query.filter_by(status='مؤكد').count()
    sales = db.session.query(db.func.sum(Order.amount)).scalar() or 0
    content = f"""
    <div class="topbar"><h4>لوحة التحكم</h4><span class="text-muted" style="font-size:12px;">{session.get('user_name')}</span></div>
    <div class="p-3">
        <div class="row g-3 mb-4">
            <div class="col-6"><div class="stat-card" style="background: #fef3c7;"><div class="icon"><i class="fas fa-shopping-cart text-warning"></i></div><h6>إجمالي الطلبات</h6><h3>{total}</h3></div></div>
            <div class="col-6"><div class="stat-card" style="background: #d1fae5;"><div class="icon"><i class="fas fa-truck text-success"></i></div><h6>الطلبات المسلمة</h6><h3>{delivered}</h3></div></div>
            <div class="col-6"><div class="stat-card" style="background: #ede9fe;"><div class="icon"><i class="fas fa-check-circle" style="color:#8b5cf6;"></i></div><h6>طلب مؤكد</h6><h3>{confirmed}</h3></div></div>
            <div class="col-6"><div class="stat-card" style="background: #e0f2fe;"><div class="icon"><i class="fas fa-wallet text-primary"></i></div><h6>المبيعات</h6><h3>{sales} <span style="font-size:12px;">د.ج</span></h3></div></div>
        </div>
    </div>
    """
    return render_template_string(BASE_HTML, content=content, active='home', title='لوحة التحكم')

# ================== 2. الطلبات ==================
@app.route('/orders')
@login_required
def orders():
    all_orders = Order.query.order_by(Order.id.desc()).all()
    orders_html = ""
    for o in all_orders:
        if o.status == 'جديد': bg = "bg-new"
        elif o.status == 'مؤكد': bg = "bg-confirmed"
        else: bg = "bg-delivered"
        orders_html += f"""
        <div class="order-card">
            <div class="order-header">
                <div><h5>{o.customer}</h5><span>{o.wilaya} - {o.baladiya}</span></div>
                <div class="text-end"><h6 class="fw-bold m-0">{o.amount} <span style="font-size:10px;">د.ج</span></h6><span class="badge-status {bg}">{o.status}</span></div>
            </div>
            <div class="d-flex justify-content-between align-items-center mt-3">
                <a href="/order/{o.id}" class="btn-action"><i class="fas fa-eye"></i> تفاصيل</a>
                <a href="tel:{o.phone}" class="btn-call"><i class="fas fa-phone"></i></a>
            </div>
        </div>
        """
    content = f"""
    <div class="topbar"><h4>الطلبات</h4><i class="fas fa-filter text-secondary"></i></div>
    <div class="p-3">{orders_html or '<div class="text-center text-muted mt-5">لا توجد طلبات حالياً.</div>'}</div>
    """
    return render_template_string(BASE_HTML, content=content, active='orders', title='الطلبات')

@app.route('/order/<int:id>', methods=['GET', 'POST'])
@login_required
def order_details(id):
    o = Order.query.get_or_404(id)
    if request.method == 'POST':
        new_status = request.form.get('status')
        if new_status:
            o.status = new_status
            db.session.commit()
        return redirect(url_for('orders'))
    
    sel_new = 'selected' if o.status == 'جديد' else ''
    sel_conf = 'selected' if o.status == 'مؤكد' else ''
    sel_del = 'selected' if o.status == 'منجز' else ''

    content = f"""
    <div class="topbar"><a href="/orders" class="text-dark"><i class="fas fa-arrow-right"></i></a><h4>تفاصيل الطلب</h4><div style="width:20px;"></div></div>
    <div class="p-4">
        <div class="bg-white p-4 rounded-4 shadow-sm mb-4">
            <h5 class="fw-bold mb-1">{o.customer}</h5>
            <p class="text-muted mb-3" style="font-size:13px;">{o.phone}</p>
            <div class="mb-2"><i class="fas fa-map-marker-alt text-secondary ms-2"></i> {o.wilaya} - {o.baladiya}</div>
            <h4 class="fw-bold text-primary mt-3">{o.amount} د.ج</h4>
        </div>
        <div class="bg-white p-4 rounded-4 shadow-sm">
            <h6 class="fw-bold mb-3">تغيير حالة الطلب</h6>
            <form method="POST">
                <select name="status" class="form-select">
                    <option value="جديد" {sel_new}>جديد</option>
                    <option value="مؤكد" {sel_conf}>مؤكد</option>
                    <option value="منجز" {sel_del}>منجز</option>
                </select>
                <button type="submit" class="btn w-100 mt-2" style="background:#8b5cf6; color:white; border-radius:15px;">تحديث الحالة</button>
            </form>
        </div>
    </div>
    """
    return render_template_string(BASE_HTML, content=content, active='orders', title='تفاصيل')

# ================== 3. إضافة طلب ==================
@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        new = Order(customer=request.form['customer'], phone=request.form['phone'], wilaya=request.form['wilaya'], baladiya=request.form['baladiya'], amount=float(request.form.get('amount', 0)))
        db.session.add(new)
        db.session.commit()
        return redirect(url_for('orders'))
    content = """
    <div class="topbar"><a href="/orders" class="text-dark"><i class="fas fa-arrow-right"></i></a><h4>معلومات العميل</h4><div style="width:20px;"></div></div>
    <div class="p-4 bg-white" style="min-height: 100vh;">
        <form method="POST">
            <label class="form-label">اسم العميل</label><input type="text" name="customer" class="form-control" required>
            <label class="form-label">هاتف العميل</label><input type="text" name="phone" class="form-control" required>
            <label class="form-label">اختر الولاية</label>
            <select name="wilaya" class="form-select" required><option value="" disabled selected>اختر الولاية</option><option value="الجزائر">الجزائر</option><option value="وهران">وهران</option><option value="قسنطينة">قسنطينة</option><option value="سطيف">سطيف</option></select>
            <label class="form-label">اختر البلدية</label><input type="text" name="baladiya" class="form-control" placeholder="اكتب البلدية" required>
            <label class="form-label">المبلغ (د.ج)</label><input type="number" name="amount" class="form-control" required>
            <button type="submit" class="btn w-100 mt-4" style="background:#8b5cf6; color:white; border-radius:15px; padding:14px; font-weight:bold; font-size:16px;">حفظ الطلب</button>
        </form>
    </div>
    """
    return render_template_string(BASE_HTML, content=content, active='orders', title='طلب جديد')

# ================== 4. المخزون ==================
@app.route('/products', methods=['GET', 'POST'])
@login_required
def products():
    if request.method == 'POST':
        db.session.add(Product(name=request.form['name'], price=float(request.form['price']), stock=int(request.form['stock'])))
        db.session.commit()
        return redirect(url_for('products'))
    all_p = Product.query.all()
    rows = "".join([f"<tr><td>{p.name}</td><td>{p.price} د.ج</td><td>{p.stock}</td></tr>" for p in all_p])
    content = f"""
    <div class="topbar"><h4>المخزون</h4><i class="fas fa-plus text-secondary"></i></div>
    <div class="p-3">
        <form method="POST" class="row g-2 mb-4 bg-white p-3 rounded-4 shadow-sm">
            <div class="col-6"><input type="text" name="name" class="form-control" placeholder="اسم المنتج" required></div>
            <div class="col-3"><input type="number" name="price" class="form-control" placeholder="السعر" required></div>
            <div class="col-3"><input type="number" name="stock" class="form-control" placeholder="الكمية" required></div>
            <div class="col-12"><button type="submit" class="btn w-100" style="background:#8b5cf6; color:white; border-radius:10px;">إضافة منتج</button></div>
        </form>
        <table class="table bg-white rounded-4 shadow-sm text-center">
            <thead class="table-light"><tr><th>المنتج</th><th>السعر</th><th>الكمية</th></tr></thead>
            <tbody>{rows or '<tr><td colspan=3>لا توجد منتجات.</td></tr>'}</tbody>
        </table>
    </div>
    """
    return render_template_string(BASE_HTML, content=content, active='products', title='المخزون')

# ================== 5. حسابي ==================
@app.route('/profile')
@login_required
def profile():
    content = f"""
    <div class="topbar"><h4>حسابي</h4><i class="fas fa-bars text-secondary"></i></div>
    <div class="p-4 text-center bg-white" style="min-height: 100vh;">
        <div class="bg-secondary bg-opacity-10 rounded-circle d-inline-flex justify-content-center align-items-center mb-3" style="width: 90px; height: 90px;"><i class="fas fa-user fa-3x text-secondary"></i></div>
        <h5 class="fw-bold m-0">{session.get('user_name', 'Khaled Store')}</h5>
        <p class="text-muted" style="font-size: 13px;">{session.get('user_email')}</p>
        <div class="rounded-4 shadow-sm text-start mt-4 overflow-hidden border" style="border-color: #eee !important;">
            <a href="/logout" class="p-3 border-bottom d-flex justify-content-between align-items-center bg-white text-decoration-none text-danger">
                <div><i class="fas fa-sign-out-alt ms-2"></i> تسجيل الخروج</div>
                <i class="fas fa-chevron-left" style="font-size: 10px;"></i>
            </a>
        </div>
    </div>
    """
    return render_template_string(BASE_HTML, content=content, active='profile', title='حسابي')

# ================== التحديث التلقائي للداتا ==================
with app.app_context():
    try:
        db.create_all()
        inspector = inspect(db.engine)
        if 'order' in inspector.get_table_names():
            columns = [c['name'] for c in inspector.get_columns('order')]
            if 'wilaya' not in columns:
                db.drop_all()
                db.create_all()
    except Exception as e:
        print("DB Auto-Reset:", e)
        db.drop_all()
        db.create_all()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
