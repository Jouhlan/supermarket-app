from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.exceptions import BadRequest
from . import app, db, bcrypt
from .models import User, Loan, LoanHistory
from sqlalchemy import func
from pytz import timezone, utc
from .models import Loan, LoanHistory

from datetime import datetime


# Pre-generated bcrypt hashes for hardcoded users
users = {
    'Bindu': {'password': '$2b$12$QLItOomfGWh7FglEFex.fOiCb.yPQFFFXRWHDsQjSb7NVs6QhR/2S'},  # Hash for 'Bindu_123'
    'Eswar': {'password': '$2b$12$SOIbNSqmuGDdVo02ScbqV.2BKIBf/0iw2v6RZG8TAdR07uRXtyw6u'},  # Hash for 'Eswar_123'
    'Siva': {'password': '$2b$12$YW87ECVnWwQKtKMVfIc9yO8ZFyCp5GC.zJLp3v3HYfYDw2UU8yGcu'}   # Hash for 'Siva_123'
}

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users:
            stored_hash = users[username]['password']
            if bcrypt.check_password_hash(stored_hash, password):
                user = User.query.filter_by(username=username).first()
                if user is None:
                    user = User(username=username, password=stored_hash)
                    db.session.add(user)
                    db.session.commit()

                login_user(user)
                return redirect(url_for('index'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists.')
        else:
            new_user = User(username=username, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('dashboard.html')

@app.route('/upload_pdf', methods=['GET', 'POST'])
@login_required
def upload_pdf():
    flash('PDF upload is not enabled yet!')
    return redirect(url_for('index'))

@app.route('/loans_and_investments')
@login_required
def loans_and_investments():
    loans = Loan.query.all()
    # Decrypt each loan before passing it to the template
    decrypted_loans = [Loan.decrypt_loan(loan) for loan in loans]
    return render_template('loans_and_investments.html', loans=decrypted_loans)

@app.route('/loans/add', methods=['GET', 'POST'])
@login_required
def add_loan():
    if request.method == 'POST':
        new_loan = Loan(
            asset_type=request.form['asset_type'],
            loaned_by=request.form['loaned_by'],
            monthly_payment=request.form['monthly_payment'],
            currency=request.form['currency'],
            interest=request.form['interest'],
            loan_amount=request.form['loan_amount'],
            investment_owner=request.form['investment_owner'],
            status_of_loan=request.form['status_of_loan'],
            modified_reason=request.form['modified_reason']
        )
        db.session.add(new_loan)
        db.session.commit()

        loan_history = LoanHistory(
            loan_id=new_loan.id,
            changed_by=current_user.username,
            action='Added',
            modified_reason=request.form['modified_reason']
        )
        db.session.add(loan_history)
        db.session.commit()

        flash('Loan successfully added!')
        return redirect(url_for('loans_and_investments'))
    return render_template('add_loan.html')

@app.route('/loans/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_loan(id):
    loan = Loan.query.get_or_404(id)
    decrypted_data = loan.decrypt_fields()

    if request.method == 'POST':
        loan.asset_type = request.form['asset_type']
        loan.loaned_by = request.form['loaned_by']
        loan.monthly_payment = request.form['monthly_payment']
        loan.currency = request.form['currency']
        loan.interest = request.form['interest']
        loan.loan_amount = request.form['loan_amount']
        loan.investment_owner = request.form['investment_owner']
        loan.status_of_loan = request.form['status_of_loan']
        loan.modified_reason = request.form['modified_reason']

        db.session.commit()
        flash('Loan updated successfully!')
        return redirect(url_for('loans_and_investments'))

    return render_template('edit_loan.html', loan=decrypted_data)

@app.route('/loans/delete/<int:id>', methods=['POST'])
@login_required
def delete_loan(id):
    loan = Loan.query.get_or_404(id)
    loan_history = LoanHistory(
        loan_id=loan.id,
        changed_by=current_user.username,
        action='Deleted'
    )
    db.session.add(loan_history)
    db.session.delete(loan)
    db.session.commit()

    flash('Loan deleted successfully.')
    return redirect(url_for('loans_and_investments'))

@app.route('/view_history')
@login_required
def view_history():
    user_timezone = timezone('America/New_York')  # Replace with your timezone
    history = LoanHistory.query.order_by(LoanHistory.timestamp.desc()).all()
    for entry in history:
        if entry.timestamp:
            utc_time = entry.timestamp.replace(tzinfo=utc)
            local_time = utc_time.astimezone(user_timezone)
            entry.timestamp = local_time.strftime('%Y-%m-%d %H:%M:%S %Z')
    return render_template('history.html', history=history)

@app.errorhandler(BadRequest)
def handle_bad_request(e):
    return jsonify({'error': 'Bad request', 'message': str(e)}), 400

@app.before_request
def validate_json():
    exempt_routes = ['login', 'logout', 'register', 'index', 'loans_and_investments', 'add_loan', 'static', 'edit_loan', 'delete_loan']
    if request.endpoint not in exempt_routes:
        if request.method in ['POST', 'PUT'] and not request.is_json:
            raise BadRequest('Missing JSON in request')
