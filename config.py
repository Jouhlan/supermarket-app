import os

class Config:
    SECRET_KEY = 'your_secret_key_here'
    SQLALCHEMY_DATABASE_URI = f"sqlite:////data/Supermarket.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False