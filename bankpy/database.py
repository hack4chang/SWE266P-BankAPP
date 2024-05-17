from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from decimal import Decimal, getcontext
getcontext().prec = 10

db = SQLAlchemy()

class AccountBalance(db.Model):
    __tablename__ = 'account_balance'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    balance = db.Column(db.Float, nullable=False)

    def __init__(self, username, password, balance=19.99):
        self.username = username
        self.password = password # vulnerable: not hashed
        self.balance = balance

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        """
        for user reset password
        """
        # self.password_hash = generate_password_hash(password)
        self.password = password # generate_password_hash(password)

    def check_password(self, password):
        """
        for user login password check
        """
        # return check_password_hash(self.password, password)
        return password == self.password

    def update_balance(self, difference):
        result = Decimal(str(self.balance)) + Decimal(str(difference))
        self.balance = float(result)

#make snapshot class that is created with values called from database