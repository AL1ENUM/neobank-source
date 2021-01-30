from flask import Flask, render_template, request
from passlib.hash import sha256_crypt
import mysql.connector as mariadb
app = Flask(__name__)
connection = mariadb.connect(user='banker',password='neobank1',database='bank')
@app.route('/')
def ins():
  return render_template('index.html')
@app.route('/insert',methods=['POST','GET'])
def index():
    if request.method=='POST':
     email = request.form['email']
     pin = sha256_crypt.encrypt(request.form['pin'])
     balance = request.form['balance']
     cur = connection.cursor()
     cur.execute('insert into account (email,pin,balance) values (%s,%s,%s)',(email,pin,balance))
     connection.commit()
     cur.close()
     return "User added"
if __name__ == '__main__':
   app.run(debug=True, host='0.0.0.0',port='5007')
