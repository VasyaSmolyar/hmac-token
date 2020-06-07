from flask import Flask, render_template, request, session, redirect, url_for, make_response
from HmacToken import HmacToken, TokenPeriod

app = Flask(__name__)
app.secret_key = 'some secret key'

users = [{
    'login' : 'admin',
    'pwd': 'admin_pass'
}, {
    'login': 'user',
    'pwd': 'user_pass'
}]

SALT = 'SAMPLE SALT'

htoken = HmacToken(SALT, TokenPeriod.minute * 2)

@app.route('/')
def index():
    if 'token' in request.cookies and 'login' in request.cookies and 'timing' in request.cookies:
        if htoken.checkToken(request.cookies['login'], request.cookies['timing'], request.cookies['token']):
            for user in users:
                if user['login'] == request.cookies['login']:
                    return render_template('profile.html', name=request.cookies['login'], token=request.cookies['token'])
            return render_template('index.html')
        return render_template('index.html')
    return render_template('index.html')

@app.route('/login')
def login():
    if 'token' in request.cookies and 'login' in request.cookies and 'timing' in request.cookies:
        if htoken.checkToken(request.cookies['login'], request.cookies['timing'], request.cookies['token']):
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/auth', methods=['POST'])
def auth():
    if 'login' in request.form and 'pwd' in request.form:
        for user in users:
            if user['login'] == request.form['login'] and user['pwd'] == request.form['pwd']:
                timing, token = htoken.getToken(user['login'])
                res = make_response(redirect(url_for('index')))
                res.set_cookie('login', user['login'], 60*60*60*24*15)
                res.set_cookie('timing', timing, 60*60*60*24*15)
                res.set_cookie('token', token, 60*60*60*24*15)
                return res
        return render_template('login.html', error='Wrong username or password')
    return render_template('login.html', error='400 Bad Request'), 400

@app.route('/logout')
def logout():
    res = make_response(redirect(url_for('index')))
    res.set_cookie('login', '', 0)
    res.set_cookie('timing', '', 0)
    res.set_cookie('token', '', 0)
    return res


if __name__ == "__main__":
    app.run(debug=True)