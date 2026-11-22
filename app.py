from flask import Flask, render_template_string

app = Flask(__name__)

# كود الواجهة (HTML) داخل المتغير
html_template = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <title>لوحة تحكم خالد ستور</title>
    <style>
        body { font-family: sans-serif; background-color: #f4f4f9; padding: 20px; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
        .card { background: white; padding: 20px; border-radius: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .card h3 { margin: 0; color: #888; }
        .card p { font-size: 24px; font-weight: bold; margin: 10px 0 0; }
        .orange { border-right: 5px solid orange; }
        .green { border-right: 5px solid green; }
    </style>
</head>
<body>
    <h1>لوحة التحكم</h1>
    <div class="grid">
        <div class="card orange">
            <h3>طلب مؤكد</h3>
            <p>3.2K</p>
        </div>
        <div class="card green">
            <h3>الطلبات المسلمة</h3>
            <p>1.7K</p>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(html_template)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
