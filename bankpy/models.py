from flask import Flask, request, render_template, redirect, url_for
from flask_login import LoginManager, UserMixin, login_required, login_user, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class AccountBalance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    account_balance = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'
