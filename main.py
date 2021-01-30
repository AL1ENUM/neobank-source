from flask import jsonify
from flask import Flask,flash,redirect,render_template,request,session,abort
from passlib.hash import sha256_crypt
import mysql.connector as mariadb
import os
import operator
import pyotp
import pyqrcode
from io import BytesIO
app = Flask(__name__)
con = mariadb.connect(user='db_user',password='db_password',database='db_name')
secret = pyotp.random_base32()
@app.route('/')
def home():
  if not session.get('logged_in'):
    return render_template('login.html')
  else:
    return render_template('index.html')

@app.route('/login',methods=['POST'])
def do_admin_login():
  login = request.form
  email = login['email']
  pin = login['pin']
  cur = con.cursor(buffered=True)
  sql = "SELECT pin FROM account WHERE email = %s"
  e = (email,)
  data = cur.execute(sql,e)
  data = cur.fetchone()
  if not data:
    flash('Wrong email or pin!') 
  elif sha256_crypt.verify(pin,data[0]):
    account = True
    if account:
      session['logged_in'] = True
      session['email'] = email
      flash('Success!')
    else:
      flash('Wrong email or pin!')
  return home()
@app.route('/qr',methods=['GET'])
def qrcode():
  if session.get('logged_in'):
   uri = pyotp.totp.TOTP(secret).provisioning_uri(session['email'],issuer_name="neobank.vln")
   totp =  pyotp.TOTP(secret)
   url = pyqrcode.create(uri)
   stream = BytesIO()
   url.svg(stream,scale=5)
   return stream.getvalue(),200,{
     'Content-Type': 'image/svg+xml',
     'Cache-Control': 'no-cache, no-store, must-revalidate',
     'Pragma': 'no-cache',
     'Expires': '0'
     }
  else:
   return render_template('login.html')
@app.route('/otp',methods=['POST','GET'])
def otp():
  if session.get('logged_in') and request.method == 'POST':
   login = request.form
   code = login['otp']
   totp =  pyotp.TOTP(secret)
   if totp.verify(code):
     cur = con.cursor(buffered=True)
     q = "SELECT email,balance FROM account WHERE email = %s"
     e = (session['email'],)
     data = cur.execute(q,e)
     data = cur.fetchone()
     if not data:
      return render_template('index.html')
     else:
      session['data'] = data
      return render_template('bank.html',data=data)
   else:
     return render_template('index.html')
  else:
    return home()
@app.route('/email_list',methods=['GET'])
def getEmails():
  cursor = con.cursor()
  cursor.execute("SELECT email FROM account")
  emails = cursor.fetchall()
  return jsonify(emails)
@app.route('/withdraw', methods=['POST'])
def withdraw():
  if session['logged_in']:
    amount = request.form['withdraw']
    data = session['data']
    balance =  eval(amount+"-"+data[1])
    data = [session['email'],balance]
    return render_template('bank.html',data=data)
  else:
    return home()
@app.route('/logout')
def logout():
  session['logged_in'] = False
  session['email'] =  None
  session['data'] = None
  return home()

if __name__ == "__main__":
   app.secret_key = os.urandom(12)
   app.run(debug=False,host='0.0.0.0',port=5000)
