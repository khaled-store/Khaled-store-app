from flask import Flask, redirect, url_for, session, request
import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key_here' # غيرها لشيء عشوائي

# ضع هنا البيانات التي حصلت عليها من Google Cloud
CLIENT_ID = 'YOUR_CLIENT_ID'
CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
REDIRECT_URI = 'http://localhost:5000/callback'

@app.route('/login')
def login():
    # توجيه المستخدم لصفحة تسجيل دخول جوجل
    google_url = f"https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope=email profile"
    return redirect(google_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    # تبادل الكود ببيانات المستخدم
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        'code': code,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI,
        'grant_type': 'authorization_code'
    }
    response = requests.post(token_url, data=data).json()
    
    # هنا تحصل على بيانات المستخدم
    access_token = response.get('access_token')
    user_info = requests.get(f"https://www.googleapis.com/oauth2/v1/userinfo?access_token={access_token}").json()
    
    session['user'] = user_info['email']
    return f"مرحباً {user_info['name']}، تم تسجيل دخولك بنجاح!"

@app.route('/')
def index():
    if 'user' in session:
        return "أنت مسجل دخول بالفعل، أهلاً بك في المتجر."
    return 'يرجى تسجيل الدخول: <a href="/login">تسجيل دخول جوجل</a>'

if __name__ == '__main__':
    app.run(debug=True)
