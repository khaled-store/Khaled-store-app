from flask import Flask, redirect, url_for, session, request
import requests

app = Flask(__name__)
# ضع مفتاحاً سرياً خاصاً بك هنا
app.secret_key = 'my_secret_key_123'

# ضع هنا بياناتك الحقيقية
CLIENT_ID = 'YOUR_CLIENT_ID_HERE'
CLIENT_SECRET = 'YOUR_CLIENT_SECRET_HERE'
REDIRECT_URI = 'http://localhost:5000/callback'

@app.route('/')
def home():
    if 'user_email' in session:
        return f"أهلاً بك يا {session['user_email']}! أنت الآن مسجل دخول."
    return '<a href="/login">اضغط هنا لتسجيل الدخول عبر Google</a>'

@app.route('/login')
def login():
    # رابط جوجل لطلب الدخول
    google_auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&"
        f"response_type=code&scope=email profile"
    )
    return redirect(google_auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    # تبديل الكود بـ Token
    token_response = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            'code': code,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'redirect_uri': REDIRECT_URI,
            'grant_type': 'authorization_code'
        }
    ).json()

    access_token = token_response.get('access_token')
    
    # جلب معلومات المستخدم
    user_info = requests.get(
        "https://www.googleapis.com/oauth2/v1/userinfo",
        headers={'Authorization': f'Bearer {access_token}'}
    ).json()

    session['user_email'] = user_info['email']
    return redirect(url_for('home'))

if __name__ == '__main__':
    # تأكد أن المنصة التي تستخدمها تسمح بفتح البورت 5000
    app.run(debug=True, port=5000)
