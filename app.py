import os
from flask import Flask, render_template_string, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect

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
    wilaya = db.Column(db.String(50), nullable=False)
    baladiya = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(200), nullable=True)
    amount = db.Column(db.Float, nullable=False, default=0.0)
    status = db.Column(db.String(20), default='جديد')

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
        .nav-tabs { border-bottom: none; gap: 10px; }
        .nav-tabs .nav-link { border: none; color: #9ca3af; font-weight: 600; padding: 10px 0; font-size: 14px; }
        .nav-tabs .nav-link.active { color: #8b5cf6; border-bottom: 3px solid #8b5cf6; background: transparent; }
        .progress-circle { width: 90px; height: 90px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 20px; margin: 0 auto 10px; }
    </style>
</head>
<body>
    {{ content|safe }}
    <div class="bottom-nav">
        <a href="/" class="nav-item {% if active == 'home' %}active{% endif %}"><i class="fas fa-home"></i> لوحة التحكم</a>
        <a href="/orders" class="nav-item {% if active == 'orders' %}active{% endif %}"><i class="fas fa-box"></i> الطلبات</a>
        <a href="/add" class="nav-item add-btn"><i class="fas fa-plus"></i></a>
        <a href="/stats" class="nav-item {% if active == 'stats' %}active{% endif %}"><i class="fas fa-chart-pie"></i> التحليلات</a>
        <a href="/profile" class="nav-item {% if active == 'profile' %}active{% endif %}"><i class="fas fa-user"></i> حسابي</a>
    </div>
</body>
</html>
"""

@app.route('/')
def dashboard():
    total = Order.query.count()
    delivered = Order.query.filter_by(status='منجز').count()
    confirmed = Order.query.filter_by(status='مؤكد').count()
    sales = db.session.query(db.func.sum(Order.amount)).scalar() or 0
    content = f"""
    <div class="topbar"><h4>لوحة التحكم</h4><i class="fas fa-bell text-secondary"></i></div>
    <div class="p-3">
        <div class="row g-3 mb-4">
            <div class="col-6"><div class="stat-card" style="background: #fef3c7;"><div class="icon"><i class="fas fa-shopping-cart text-warning"></i></div><h6>إجمالي الطلبات</h6><h3>{total}</h3></div></div>
            <div class="col-6"><div class="stat-card" style="background: #d1fae5;"><div class="icon"><i class="fas fa-truck text-success"></i></div><h6>الطلبات المسلمة</h6><h3>{delivered}</h3></div></div>
            <div class="col-6"><div class="stat-card" style="background: #ede9fe;"><div class="icon"><i class="fas fa-check-circle" style="color:#8b5cf6;"></i></div><h6>طلب مؤكد</h6><h3>{confirmed}</h3></div></div>
            <div class="col-6"><div class="stat-card" style="background: #e0f2fe;"><div class="icon"><i class="fas fa-wallet text-primary"></i></div><h6>المبيعات</h6><h3>{sales} <span style="font-size:12px;">د.ج</span></h3></div></div>
        </div>
        <h6 class="fw-bold mb-3" style="border-right: 4px solid #8b5cf6; padding-right: 10px;">أفضل المنتجات</h6>
        <div class="bg-white p-4 rounded-4 shadow-sm text-center text-muted" style="font-size:13px;"><i class="fas fa-box-open fa-2x mb-2 text-secondary opacity-50"></i><br>لا توجد مبيعات كافية لعرض المنتجات الأكثر طلباً.</div>
    </div>
    """
    return render_template_string(BASE_HTML, content=content, active='home', title='لوحة التحكم')

@app.route('/orders')
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
    <div class="bg-white px-3 pt-2">
        <ul class="nav nav-tabs nav-justified mb-0">
            <li class="nav-item"><a class="nav-link active" href="/orders">الكل</a></li>
            <li class="nav-item"><a class="nav-link" href="#">جديد</a></li>
            <li class="nav-item"><a class="nav-link" href="#">مؤكد</a></li>
        </ul>
    </div>
    <div class="p-3">{orders_html or '<div class="text-center text-muted mt-5">لا توجد طلبات حالياً.</div>'}</div>
    """
    return render_template_string(BASE_HTML, content=content, active='orders', title='الطلبات')

@app.route('/order/<int:id>', methods=['GET', 'POST'])
def order_details(id):
    o = Order.query.get_or_404(id)
    if request.method == 'POST':
        new_status = request.form.get('status')
        if new_status:
            o.status = new_status
            db.session.commit()
        return redirect(url_for('orders'))
    
    content = f"""
    <div class="topbar">
        <a href="/orders" class="text-dark"><i class="fas fa-arrow-right"></i></a>
        <h4>تفاصيل الطلب</h4>
        <div style="width:20px;"></div>
    </div>
    <div class="p-4">
        <div class="bg-white p-4 rounded-4 shadow-sm mb-4">
            <h5 class="fw-bold mb-1">{o.customer}</h5>
            <p class="text-muted mb-3" style="font-size:13px;">{o.phone}</p>
            <div class="mb-2"><i class="fas fa-map-marker-alt text-secondary ms-2"></i> {o.wilaya} - {o.baladiya}</div>
            <div class="mb-3"><i class="fas fa-home text-secondary ms-2"></i> {o.address or 'بدون عنوان'}</div>
            <h4 class="fw-bold text-primary">{o.amount} د.ج</h4>
        </div>
        
        <div class="bg-white p-4 rounded-4 shadow-sm">
            <h6 class="fw-bold mb-3">تغيير حالة الطلب</h6>
            <form method="POST">
                <select name="status" class="form-select">
                    <option value="جديد" {% if o.status == 'جديد' %}selected{% endif %}>جديد</option>
                    <option value="مؤكد" {% if o.status == 'مؤكد' %}selected{% endif %}>مؤكد</option>
                    <option value="منجز" {% if o.status == 'منجز' %}selected{% endif %}>منجز</option>
                </select>
                <button type="submit" class="btn w-100 mt-2" style="background:#8b5cf6; color:white; border-radius:15px;">تحديث الحالة</button>
            </form>
        </div>
    </div>
    """
    return render_template_string(BASE_HTML, content=content, active='orders', title='تفاصيل')

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        new = Order(customer=request.form['customer'], phone=request.form['phone'], wilaya=request.form['wilaya'], baladiya=request.form['baladiya'], address=request.form.get('address', ''), amount=float(request.form.get('amount', 0)))
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
            <label class="form-label">عنوان العميل</label><input type="text" name="address" class="form-control">
            <label class="form-label">المبلغ (د.ج)</label><input type="number" name="amount" class="form-control" required>
            <button type="submit" class="btn w-100 mt-4" style="background:#8b5cf6; color:white; border-radius:15px; padding:14px; font-weight:bold; font-size:16px;">حفظ الطلب</button>
        </form>
    </div>
    """
    return render_template_string(BASE_HTML, content=content, active='orders', title='طلب جديد')

@app.route('/stats')
def stats():
    content = """
    <div class="topbar"><h4>التحليلات</h4><i class="fas fa-filter text-secondary"></i></div>
    <div class="p-3">
        <ul class="nav nav-tabs nav-justified mb-4 bg-white rounded-3 shadow-sm p-1">
            <li class="nav-item"><a class="nav-link active" href="#">الأداء</a></li>
            <li class="nav-item"><a class="nav-link" href="#">التأكيد</a></li>
        </ul>
        <div class="row g-3 text-center">
            <div class="col-6"><div class="bg-white p-4 rounded-4 shadow-sm"><div class="progress-circle" style="border: 8px solid #10b981; border-left-color: #e5e7eb; border-bottom-color: #e5e7eb; color:#10b981;">62%</div><h6 class="fw-bold m-0" style="font-size:12px;">معدل التأكيد</h6></div></div>
            <div class="col-6"><div class="bg-white p-4 rounded-4 shadow-sm"><div class="progress-circle" style="border: 8px solid #f59e0b; border-left-color: #e5e7eb; border-top-color: #e5e7eb; color:#f59e0b;">54%</div><h6 class="fw-bold m-0" style="font-size:12px;">معدل التسليم</h6></div></div>
        </div>
    </div>
    """
    return render_template_string(BASE_HTML, content=content, active='stats', title='التحليلات')

@app.route('/profile')
def profile():
    content = """
    <div class="topbar"><h4>حسابي</h4><i class="fas fa-bars text-secondary"></i></div>
    <div class="p-4 text-center bg-white" style="min-height: 100vh;">
        <div class="bg-secondary bg-opacity-10 rounded-circle d-inline-flex justify-content-center align-items-center mb-3" style="width: 90px; height: 90px;"><i class="fas fa-user fa-3x text-secondary"></i></div>
        <h5 class="fw-bold m-0">Khaled Store</h5><p class="text-muted" style="font-size: 13px;">مدير المتجر</p>
        <div class="rounded-4 shadow-sm text-start mt-4 overflow-hidden border" style="border-color: #eee !important;">
            <div class="p-3 border-bottom d-flex justify-content-between align-items-center bg-white"><div><i class="fas fa-user text-secondary ms-2"></i> الاسم</div><div class="text-muted d-flex align-items-center" style="font-size: 13px;">Khaled <i class="fas fa-chevron-left ms-2" style="font-size: 10px;"></i></div></div>
            <div class="p-3 border-bottom d-flex justify-content-between align-items-center bg-white"><div><i class="fas fa-phone text-secondary ms-2"></i> رقم الهاتف</div><div class="text-muted d-flex align-items-center" style="font-size: 13px;">0550123456 <i class="fas fa-chevron-left ms-2" style="font-size: 10px;"></i></div></div>
            <div class="p-3 border-bottom d-flex justify-content-between align-items-center bg-white"><div><i class="fas fa-globe text-secondary ms-2"></i> اللغة</div><div class="text-muted d-flex align-items-center" style="font-size: 13px;">العربية <i class="fas fa-chevron-left ms-2" style="font-size: 10px;"></i></div></div>
        </div>
    </div>
    """
    return render_template_string(BASE_HTML, content=content, active='profile', title='حسابي')

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
