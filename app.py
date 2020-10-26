from __future__ import unicode_literals
from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_pymongo import PyMongo, pymongo
import hashlib
import datetime
from PIL import Image
from pytesseract import image_to_string
import os
from werkzeug import secure_filename
import sys

app = Flask(__name__)

ALLOWED_EXTENSIONS = set([ 'png', 'jpg', 'jpeg'])
app.config['MONGO_DBNAME'] = 'wkeeper'
app.config['MONGO_URI'] = 'mongodb://wkeeper:wkeeper10@ds123624.mlab.com:23624/wkeeper'
mongo = PyMongo(app)

users = mongo.db.users
transactions = mongo.db.transactions

@app.route('/')
def dashboard():
	if 'username' in session:
		login_user = users.find_one({'username' : session['username']})

		now = datetime.datetime.now()
		today_transactions = transactions.find({'transaction' : "subtract", 'username' : session['username'], 'day' : now.day, 'month' : now.month, 'year' : now.year})
		month_transactions = transactions.find({'transaction' : "subtract", 'username' : session['username'], 'month' : now.month, 'year' : now.year})

		transactions_today_nr = 0
		transactions_today_total = 0
		for transaction in today_transactions:
			transactions_today_total = transactions_today_total + float(transaction['balance'])
			transactions_today_nr = transactions_today_nr + 1

		transactions_month_nr = 0
		transactions_month_total = 0
		for transaction in month_transactions:
			transactions_month_total = transactions_month_total + float(transaction['balance'])
			transactions_month_nr = transactions_month_nr + 1

		today_percentage = None
		month_percentage = None

		if transactions_today_nr:
			today_percentage = (transactions_today_total*100)/(login_user['balance']+transactions_today_total)
			today_percentage = int(today_percentage)

		if transactions_month_nr:
			month_percentage = (transactions_month_total*100)/(login_user['balance']+transactions_month_total)
			month_percentage = int(month_percentage)


		transactions_list = transactions.find({'username' : session['username']})
		food_count = 0
		clothing_count = 0
		groceries_count = 0
		electronics_count = 0
		other_count = 0


		for transaction in transactions_list:
			if transaction['type'] == 'food':
				food_count = food_count + 1
			elif transaction['type'] == "clothing":
				clothing_count += 1
			elif transaction['type'] == "groceries":
				groceries_count += 1
			elif transaction['type'] == "electronics":
				electronics_count += 1
			elif transaction['type'] == "other":
				other_count += 1

		type_count = food_count + clothing_count + groceries_count + electronics_count + other_count

		if type_count:
			food_count = round((100*food_count)/type_count, 2)
			clothing_count = round((100*clothing_count)/type_count, 2)
			groceries_count = round((100*groceries_count)/type_count, 2)
			electronics_count = round((100*electronics_count)/type_count, 2)
			other_count = round((100*other_count)/type_count, 2)

		if today_percentage and month_percentage:
			return render_template('dashboard.html', username=session['username'], balance=login_user['balance'], total_today=transactions_today_total, percentage_today=today_percentage, total_month=transactions_month_total, percentage_month=month_percentage, food_percentage=food_count, clothing_percentage=clothing_count, groceries_percentage=groceries_count, electronics_percentage=electronics_count, other_percentage=other_count)
		elif today_percentage:
			return render_template('dashboard.html', username=session['username'], balance=login_user['balance'], total_today=transactions_today_total, percentage_today=today_percentage, total_month=0, percentage_month=0, food_percentage=food_count, clothing_percentage=clothing_count, groceries_percentage=groceries_count, electronics_percentage=electronics_count, other_percentage=other_count)
		elif month_percentage:
			return render_template('dashboard.html', username=session['username'], balance=login_user['balance'], total_today=0, percentage_today=0, total_month=transactions_month_total, percentage_month=month_percentage, food_percentage=food_count, clothing_percentage=clothing_count, groceries_percentage=groceries_count, electronics_percentage=electronics_count, other_percentage=other_count)
		else:
			return render_template('dashboard.html', username=session['username'], balance=login_user['balance'], total_today=0, percentage_today=0, total_month=0, percentage_month=0, food_percentage=food_count, clothing_percentage=clothing_count, groceries_percentage=groceries_count, electronics_percentage=electronics_count, other_percentage=other_count)
	else:
		flash('You must be logged in to access dashboard')
		return redirect(url_for('about'))


@app.route('/about')
def about():
	return render_template('about.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
	if request.method == 'POST':

		if request.form['username'] == "" or request.form['email'] == "" or request.form['password'] == "" or request.form['username'] == " " or request.form['email'] == " " or request.form['password'] == " ":
			return render_template('register.html', error='Fields cannot be blank')

		existing_user = users.find_one({'username' : request.form['username']})
		if existing_user is None:
			if request.form['password'] == request.form['password2']:
				hashpass = hashlib.sha256((request.form['password']).encode('utf-8')).hexdigest()
				users.insert({'username' : request.form['username'], 'email' : request.form['email'], 'password' : hashpass, 'balance' : 0})
				session['username'] = request.form['username']
				return redirect(url_for('dashboard'))
			else:
				return render_template('register.html', error='Passwords don\'t match')
		else:
			return render_template('register.html', error='This username already exists')
	else:
		return render_template("register.html")



@app.route('/login', methods=['POST', 'GET'])
def login():
	if request.method == 'POST':
		if request.method == 'POST':

			login_user = users.find_one({'username' : request.form['username']})

			if login_user:
				hashpass = hashlib.sha256((request.form['password']).encode('utf-8')).hexdigest()
				if hashpass == login_user['password']:
					session['username'] = login_user['username']
					return redirect(url_for('dashboard'))
			return render_template('login.html', error="Username or password is incorrect")
	else:
		return render_template("login.html")



@app.route('/logout')
def logout():
	session.pop('username', None)
	return redirect(url_for('about'))

@app.route('/profile')
def profile():
	if 'username' in session:
		login_user = users.find_one({'username' : session['username']})
		return render_template('profile.html', username=session['username'], email=login_user['email'], balance=login_user['balance'])
	else:
		flash('You must be logged in to access profile')
		return redirect(url_for('about'))

@app.route('/history')
def history():
	if 'username' in session:
		user_transactions = transactions.find({'username' : session['username']})
		return render_template('history.html', transaction_list=user_transactions)
	else:
		flash('You must be logged in to access history')
		return redirect(url_for('about'))


@app.route('/topup', methods=['POST', 'GET'])
def topup():
	if 'username' in session:
		now = datetime.datetime.now()
		if request.method == 'POST':
			login_user = users.find_one({'username' : session['username']})
			login_user['balance'] = login_user['balance'] + int(request.form['total'])
			users.save(login_user)

			transactions.insert({'username': session['username'], 'balance' : request.form['total'], 'type' : 'topup', 'store' : 'Topup', 'time' : now.strftime("%H:%M"), 'year' : now.year, 'month' : now.month, 'day' : now.day, 'transaction' : 'topup'})

			flash('Funds Added')
			return redirect(url_for('dashboard'))
		else:
			return render_template('topup.html', time=now.strftime("%H:%M"), date=now.strftime("%d/%m/%Y"))
	else:
		flash('You must be logged in to access topup')
		return redirect(url_for('about'))



@app.route('/subtract', methods=['POST', 'GET'])
def subtract():
	if 'username' in session:
		now = datetime.datetime.now()
		if request.method == 'POST':
			login_user = users.find_one({'username' : session['username']})
			if float(request.form['total']) > login_user['balance']:
				flash('You do not have enough funds in your balace')
				return redirect(url_for('dashboard'))

			login_user['balance'] = login_user['balance'] - float(request.form['total'])
			users.save(login_user)

			transactions.insert({'username': session['username'], 'balance' : request.form['total'], 'type' : request.form['type'], 'store' : request.form['store'], 'time' : now.strftime("%H:%M"), 'year' : now.year, 'month' : now.month, 'day' : now.day, 'transaction' : 'subtract'})

			flash('Funds subtracted')
			return redirect(url_for('dashboard'))
		else:
			return render_template('subtract.html', time=now.strftime("%H:%M"), date=now.strftime("%d/%m/%Y"), total=None, company=None)
	else:
		flash('You must be logged in to access subtract')
		return redirect(url_for('about'))

keywords = ["total", "otal", "tota", "numerar", "umerar", "numera", "nunerar", "$", "lei", "euro", "pay", "amount", "suma", "plata"]
companyKeywords = ["s.r.l", u"§.r.l", "$.r.l", "s.a", "firma", "company"]

def isNumber(c):
	try:
		int(c)
		return True
	except ValueError:
		return False

def hasText(index, text):
	if index < 0 or text[index] == '\n':
		return False
	return True

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/uploadreceipt', methods=['POST', 'GET'])
def uploadreceipt():
	if request.method == 'POST':

		wd = os.getcwd()
		file = request.files['receipt-photo']

		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file.save(wd+"/static/uploads/"+filename)
			

			aham = wd+"/static/uploads/"+filename

			text = image_to_string(Image.open(aham))
			text = text.rstrip().lower()
			i = -1
			totalPay = 0
			paymentString = ""
			kwfound = ""
			company = ""

			for kwd in companyKeywords:
				i = text.find(kwd)
				if i != 0 and i != -1:
					i = i - 1
					while hasText(i, text):
						company += text[i]
						i = i - 1
					company = company[::-1]

			i = -1

			for kwd in keywords:
				i = text.find(kwd)
				if i != 0 and i != -1:
					while isNumber(text[i]) == False:
						i = i + 1
					while isNumber(text[i]) or text[i] == '.' or text[i] == ',':
						paymentString += text[i]
						i = i + 1
					if text[i] == '%' or text[i + 1] == '%':
						paymentString = ""
						continue
					kwfound = kwd
					break

			if paymentString == "":
				flash('No TOTAL found')
				return redirect(url_for('dashboard'))

			paymentString = paymentString.replace(',', '.')

			now = datetime.datetime.now()
			return render_template('subtract.html', time=now.strftime("%H:%M"), date=now.strftime("%d/%m/%Y"), total=float(paymentString), company=company)
		else:
			flash('You must choose a photo')
			return redirect(url_for('dashboard'))
	else:
		return redirect(url_for('dashboard'))


@app.route('/sitemap')
def sitemap():
	return render_template('sitemap.html')

@app.route('/changemail', methods=['GET', 'POST'])
def changemail():
	login_user = users.find_one({'username' : session['username']})

	if request.method == 'POST':
		login_user['email'] = request.form['email']
		users.save(login_user)

		flash('Email was updated')
		return redirect(url_for('dashboard'))
	else:
		if 'username' in session:
			return render_template('changemail.html', email=login_user['email'])
		else:
			flash('You must be logged into your account to access changemail')
			return redirect(url_for('dashboard'))

app.config['SECRET_KEY'] = "hello"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
