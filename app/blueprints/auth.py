from flask import Blueprint, render_template, request, redirect, url_for

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		# Add your authentication logic here
		if username == 'admin' and password == 'password':  # Example check
			return redirect(url_for('main.index'))
		else:
			return 'Invalid credentials', 401
	return render_template('login.html')

@auth_bp.route('/logout')
def logout():
	return "You have been logged out"