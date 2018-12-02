# getting all the required modules
from flask import Flask, render_template, request, url_for, flash, session, logging, redirect
from flask_mysqldb import MySQL
from passlib.hash import sha256_crypt
from functools import wraps


app = Flask(__name__)

# Secret key
app.secret_key = "secret123"


# Connecting the database using
# Configuring Mysql
app.config['MYSQL_HOST'] = "localhost" # The connection Host
app.config['MYSQL_USER'] = "root" # The current effective user
app.config['MYSQL_PASSWORD'] = "sadattmagara254" # Mysql authentication passord
app.config['MYSQL_DB'] = "pos" # Mysql database to use
app.config['MYSQL_CURSORCLASS'] = "DictCursor" # Mysql hundler

# Initialize Mysql
mysql = MySQL(app)

# the Index page
@app.route("/")
def index():
	return render_template('index.html')

# The lodin route
@app.route("/login", methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
			username = request.form['pos-login-uoe']
			pwd = request.form['pos-login-pwd']

			# Create the login cursor
			cur = mysql.connection.cursor()

			# Query execution
			# Getting all the username from the database 
			result = cur.execute("SELECT * FROM users WHERE username=%s", [username])
			# No need to commit anything to the database

			# Checking if the data exists
			if result > 0:
				data = cur.fetchone()
				password = data['password']

				if sha256_crypt.verify(pwd, password):
					session['logged_in'] = True
					session['username'] = username

					flash("Welcome " + username , 'success')
					return redirect(url_for('dashboard'))
				else:
					error = "invalid Login credentials"
					return render_template('signin.html', error=error)
				# Close the connection
				cur.close()
			else: #if the data return null or None
				error = "Username and password did not match"
				return render_template('signin.html', error=error)


	# Rendering the login form to the browser
	return render_template('signin.html')	

# The signup route
@app.route('/register', methods=['GET', 'POST'])
def register():
	if request.method == 'POST':
		name = request.form['pos-signup-name']
		email = request.form['pos-signup-email']
		username = request.form['pos-signup-username']
		password = sha256_crypt.encrypt(str(request.form['pos-signup-pwd']))
		confirmpassword = sha256_crypt.encrypt(str(request.form['pos-signup-cpwd']))

		if password == confirmpassword:
			flash("The password did not matach", 'danger')
			return redirect(url_for('register'))

		# Create cursor
		cur = mysql.connection.cursor()

		# Insert the form values to the database
		cur.execute("INSERT INTO users(fname, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))

		# Commit the data to the database		
		mysql.connection.commit()

		# Close the cursor
		cur.close()

		flash('Registration successful you can now login', 'success');


		return redirect(url_for('dashboard'))
	# Rendering the signin page to the browser
	return render_template('signup.html')
	
# check if the the user is logged in
def is_logged_in(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return f(*args, **kwargs)
		else:
			flash('unauthorized, please login', 'danger')
			return redirect(url_for('login'))	
	return wrap
# Logout
@app.route('/logout')
def logout():
	session.clear();
	flash("you are now logged out", "success")
	return redirect(url_for("login"))

# Rendering the stores dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
	return render_template('dashboard.html')

if __name__ == "__main__":
    app.run(debug=True, port=3000)  	