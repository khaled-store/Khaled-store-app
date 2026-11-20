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

# زدنا Product و SKU باش نطابقو التصويرة
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    product = db.Column(db.String(100), nullable=True)
    sku = db.Column(db.String(50), nullable=True)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='Pending')

HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Khaled Store - لوحة التحكم</title>
    <!-- Bootstrap RTL & FontAwesome -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
        body { font-family: 'Cairo', sans-serif; background-color: #f4f6f9; margin: 0; }
        
        /* Sidebar */
        .sidebar { background: #1a1c2e; color: white; height: 100vh; width: 250px; position: fixed; right: 0; top: 0; overflow-y: auto; }
        .sidebar h4 { padding: 20px; text-align: center; border-bottom: 1px solid #2d2f45; color: #a855f7; font-weight: bold; }
        .sidebar a { display: flex; align-items: center; padding: 12px 20px; color: #b0b3c6; text-decoration: none; font-size: 14px; transition: 0.3s; }
        .sidebar a:hover, .sidebar a.active { background: #2d2f45; color: white; border-right: 4px solid #a855f7; }
        .sidebar a i { margin-left: 10px; width: 20px; text-align: center; }
        
        /* Main Content */
        .main-content { margin-right: 250px; padding: 20px; }
        .topbar { display: flex; justify-content: space-between; align-items: center; background: white; padding: 15px 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); margin-bottom: 20px; }
        .search-box { display: flex; align-items: center; background: #f4f6f9; padding: 8px 15px; border-radius: 20px; width: 300px; }
        .search-box input { border: none; background: transparent; outline: none; width: 100%; margin-right: 10px; }
        
        /* Table */
        .table-container { background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
        table { width: 100%; border-collapse: collapse; }
        th { background: #f8f9fa; padding: 12px; text-align: right; font-size: 13px; color: #6c757d; border-bottom: 2px solid #dee2e6; }
        td { padding: 12px; border-bottom: 1px solid #dee2e6; font-size: 13px; vertical-align: middle; }
        tr:hover { background: #f8f9fa; }
        
        /* Badges & Buttons */
        .badge { padding: 5px 10px; border-radius: 20px; font-size: 11px; font-weight: bold; }
        .badge-pending { background: #fff3cd; color: #856404; }
        .badge-delivered { background: #d4edda; color: #155724; }
        .action-btn { width: 30px; height: 30px; border-radius: 50%; display: inline-flex; justify-content: center; align-items: center; color: white; text-decoration: none; margin-left: 5px; }
        .btn-whatsapp { background: #25d366; }
        .btn-call { background: #007bff; }
        .btn-deliver { background: #a855f7; color: white; padding: 5px 10px; border-radius: 5px; text-decoration: none; font-size: 12px; }
    </style>
</head>
<body>

    <!-- Sidebar -->
    <div class="sidebar">
        <h4>Khaled Store</h4>
        <a href="#" class="active"><i class="fas fa-home"></i> لوحة التحكم</a>
        <a href="#"><i class="fas fa-chart-line"></i> مؤشرات الأداء (KPI)</a>
        <a href="#"><i class="fas fa-store"></i> قنوات البيع</a>
        <a href="#"><i class="fas fa-box"></i> المنتجات</a>
        <a href="#"><i class="fas fa-clipboard-list"></i> الطلبات</a>
        <a href="#"><i class="fas fa-cash-register"></i> نقطة البيع</a>
        <a href="#"><i class="fas fa-barcode"></i> الماسح الضوئي</a>
        <a href="#"><i class="fas fa-warehouse"></i> المخزون</a>
        <a href="#"><i class="fas fa-truck-loading"></i> التوريد</a>
        <a href="#"><i class="fas fa-money-bill-wave"></i> المصاريف</a>
        <a href="#"><i class="fas fa-wallet"></i> المالية</a>
        <a href="#"><i class="fas fa-users"></i> المستخدمون</a>
        <a href="#"><i class="fas fa-user-friends"></i> العملاء</a>
        <a href="#"><i class="fas fa-truck"></i> شريك التوصيل</a>
        <a href="#"><i class="fas fa-chart-bar"></i> التحليلات</a>
        <a href="#"><i class="fas fa-paper-plane"></i> Sendpilot</a>
        <a href="#"><i class="fas fa-bullhorn"></i> محل الإعلانات</a>
        <a href="#"><i class="fas fa-robot"></i> AI</a>
    </div>

    <!-- Main Content -->
    <div class="main-content">
        <div class="topbar">
            <div class="search-box">
                <i class="fas fa-search text-muted"></i>
                <input type="text" placeholder="ابحث عن الاسم، رقم الهاتف، أو SKU...">
            </div>
            <a href="/add" class="btn btn-primary" style="background: #a855f7; border: none;"><i class="fas fa-plus"></i> طلب جديد</a>
        </div>

        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>هاتف العميل</th>
                        <th>اسم العميل</th>
                        <th>SKU</th>
                        <th>المنتج</th>
                        <th>المبلغ</th>
                        <th>معرف الطلب</th>
                        <th>الحالة</th>
                        <th>إجراءات</th>
                    </tr>
                </thead>
                <tbody>
                    {% for order in orders %}
                    <tr>
                        <td style="font-weight: bold; direction: ltr; text-align: right;">{{ order.phone }}</td>
                        <td>{{ order.customer }}</td>
                        <td>{{ order.sku or '-' }}</td>
                        <td>{{ order.product or '-' }}</td>
                        <td>{{ order.amount }} د.ج</td>
                        <td>#{{ order.id }}000</td>
                        <td>
                            <span class="badge {% if order.status == 'Pending' %}badge-pending{% else %}badge-delivered{% endif %}">
                                {{ order.status }}
                            </span>
                        </td>
                        <td style="direction: ltr; text-align: right;">
                            <!-- أزرار تخدم أونلاين -->
                            <a href="tel:{{ order.phone }}" class="action-btn btn-call" title="اتصال"><i class="fas fa-phone"></i></a>
                            <a href="https://wa.me/213{{ order.phone[1:] if order.phone.startswith('0') else order.phone }}" target="_blank" class="action-btn btn-whatsapp" title="واتساب"><i class="fab fa-whatsapp"></i></a>
                            
                            {% if order.status == 'Pending' %}
                            <a href="/deliver/{{ order.id }}" class="btn-deliver" title="تأكيد التوصيل"><i class="fas fa-check"></i></a>
                            {% endif %}
                        </td>
                    </tr>
                    {% else %}
                    <tr>
                        <td colspan="8" style="text-align: center; color: #888;">لا توجد طلبات حالياً. اضغط على "طلب جديد" للإضافة.</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>

</body>
</html>
"""

HTML_ADD = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>إضافة طلب - Khaled Store</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
        body { font-family: 'Cairo', sans-serif; background-color: #f4f6f9; padding: 20px; }
        .form-container { background: white; padding: 30px; border-radius: 10px; max-width: 600px; margin: 0 auto; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; font-size: 14px; color: #333; margin-bottom: 8px; font-weight: 600; }
        .form-group input { width: 100%; padding: 12px; border-radius: 8px; border: 1px solid #ccc; outline: none; }
        .form-group input:focus { border-color: #a855f7; }
        .btn-save { background: #a855f7; color: white; border: none; padding: 15px; border-radius: 8px; font-size: 16px; font-weight: bold; width: 100%; cursor: pointer; margin-top: 15px; }
        .btn-save:hover { background: #9333ea; }
    </style>
</head>
<body>
    <div class="form-container">
        <h2 class="mb-4" style="color: #a855f7;"><i class="fas fa-plus-circle"></i> إضافة طلب جديد</h2>
        <form method="POST">
            <div class="form-group"><label>اسم العميل</label><input type="text" name="customer" required></div>
            <div class="form-group"><label>رقم الهاتف</label><input type="text" name="phone" required placeholder="مثال: 0550123456"></div>
            <div class="form-group"><label>العنوان</label><input type="text" name="address" required></div>
            <div class="form-group"><label>المنتج</label><input type="text" name="product" placeholder="مثال: ساعة يد"></div>
            <div class="form-group"><label>SKU (رمز المنتج)</label><input type="text" name="sku" placeholder="اختياري"></div>
            <div class="form-group"><label>المبلغ (د.ج)</label><input type="number" name="amount" required></div>
            <button type="submit" class="btn-save">حفظ الطلب</button>
            <a href="/" class="d-block text-center mt-3 text-decoration-none" style="color: #666;">العودة للوحة التحكم</a>
        </form>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    orders = Order.query.order_by(Order.id.desc()).all()
    return render_template_string(HTML, orders=orders)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        new_order = Order(
            customer=request.form['customer'], 
            phone=request.form['phone'], 
            address=request.form['address'], 
            product=request.form.get('product'),
            sku=request.form.get('sku'),
            amount=float(request.form['amount'])
        )
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

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
