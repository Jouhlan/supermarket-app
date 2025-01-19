from flask_login import UserMixin
from . import db, fernet
from sqlalchemy.sql import func


def encrypt_data(value):
    """Encrypt the given value."""
    if value is None:
        return None
    return fernet.encrypt(value.encode()).decode()


def decrypt_data(value):
    """Decrypt the given value."""
    if value is None:
        return None
    return fernet.decrypt(value.encode()).decode()


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)


class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    asset_type = db.Column(db.String(100), nullable=False)
    loaned_by = db.Column(db.String(100), nullable=False)
    monthly_payment = db.Column(db.String(100), nullable=False)  # Encrypted float stored as string
    currency = db.Column(db.String(100), nullable=False)
    interest = db.Column(db.String(100), nullable=False)  # Encrypted float stored as string
    loan_amount = db.Column(db.String(100), nullable=False)  # Encrypted float stored as string
    investment_owner = db.Column(db.String(100), nullable=False)
    status_of_loan = db.Column(db.String(50), nullable=False)
    modified_reason = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())

    def __init__(self, **kwargs):
        """Encrypt fields during initialization."""
        self.asset_type = encrypt_data(kwargs.get('asset_type'))
        self.loaned_by = encrypt_data(kwargs.get('loaned_by'))
        self.monthly_payment = encrypt_data(str(kwargs.get('monthly_payment')))
        self.currency = encrypt_data(kwargs.get('currency'))
        self.interest = encrypt_data(str(kwargs.get('interest')))
        self.loan_amount = encrypt_data(str(kwargs.get('loan_amount')))
        self.investment_owner = encrypt_data(kwargs.get('investment_owner'))
        self.status_of_loan = encrypt_data(kwargs.get('status_of_loan'))
        self.modified_reason = encrypt_data(kwargs.get('modified_reason'))

    @staticmethod
    def decrypt_loan(loan):
        """Decrypt fields before usage."""
        loan.asset_type = decrypt_data(loan.asset_type)
        loan.loaned_by = decrypt_data(loan.loaned_by)
        loan.monthly_payment = float(decrypt_data(loan.monthly_payment))
        loan.currency = decrypt_data(loan.currency)
        loan.interest = float(decrypt_data(loan.interest))
        loan.loan_amount = float(decrypt_data(loan.loan_amount))
        loan.investment_owner = decrypt_data(loan.investment_owner)
        loan.status_of_loan = decrypt_data(loan.status_of_loan)
        loan.modified_reason = decrypt_data(loan.modified_reason)
        return loan


class LoanHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    loan_id = db.Column(db.Integer, db.ForeignKey('loan.id'), nullable=True)
    changed_by = db.Column(db.String(100), nullable=False)
    action = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), default=func.now())
    field = db.Column(db.String(100), nullable=True)
    old_value = db.Column(db.String(255), nullable=True)
    new_value = db.Column(db.String(255), nullable=True)
    modified_reason = db.Column(db.Text, nullable=True)

    loan = db.relationship('Loan', backref=db.backref('history', lazy=True))
