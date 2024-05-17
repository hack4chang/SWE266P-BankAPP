from flask import Flask, request, render_template, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from database import BankAccount, db
import re

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = '123'
    db.init_app(app)

    with app.app_context():
        db.create_all()

    @app.route('/')
    def home():
        # print(session.get('id'))
        # if session.get('id') != None:
        #    return redirect(url_for('dashboard', username=session.get('id')))
        return render_template('home.html')

    @app.route('/login', methods=["GET", "POST"])
    def login():
        # if session.get('id') != None:
        #     return redirect(url_for('dashboard', username=session.get('id')))
        message = request.args.get('message')
        print(message)
        return render_template('login.html', message=message)

    @app.route('/<username>/dashboard', methods=["GET", "POST"])
    def dashboard(username):
        print("In the dashboard - username: " + username)
        balance = BankAccount.query.filter_by(username=username).first().balance
        print("In the dashboard - balance: " + str(balance))
        return render_template('dashboard.html', username=username, balance=balance) 

    @app.route('/login_verify', methods=["POST"])
    def login_verify():
        username = request.form.get("username")
        password = request.form.get("password")
        print("Username - " + username + "; Password - " + password)
        if not username or not password:
            return '<h3>Invalid Input or Invalid Password!</h3>'
        else:
            user = BankAccount.query.filter_by(username=username).first()
            if user and user.check_password(password):
                return redirect(url_for('dashboard', username=username)) 
            else:
                return '<h3>User Not Found or Password Incorrect! Please Login Again!</h3>'

    @app.route('/register_verify', methods=["POST"])
    def register_verify():
        username = request.form.get("username")
        password = request.form.get("password")
        password2 = request.form.get("password2")

        command_pattern = r'[^a-zA-Z0-9_.-]'  
        ip_pattern = r'(\d{1,3}\.){3}\d{1,3}'

        if re.search(command_pattern, username) or re.fullmatch(ip_pattern, username) or \
           not username or not password or not password2 or password != password2:
            return '<h3>Invalid Input or Invalid Account ID or Invalid Password!</h3>'
        if db.session.query(BankAccount.username).first():
            print("USERNAME TAKEN")
        try:
            print(f"[Register Request] Username - {username}; Password - {password}")
            new_account = BankAccount(username=username, password=password, balance=19.99)
            db.session.add(new_account)
            db.session.commit()
            print(f"[Request Success]")
            return redirect(url_for('login', message="Register Success!"))

        except Exception as e:
            db.session.rollback()
            print(f"Error occurred: {e}")
            if str(e).find("UNIQUE constraint failed"):
                return '<h3>Username Taken! Please login or register with a different username!</h3>', 400
            else:
                return '<h3>Invalid Input or Invalid Account ID or Invalid Password!</h3>', 400

    @app.route('/register', methods=["GET", "POST"])
    def register():
        # if session.get('id') != None:
        #     return redirect(url_for('dashboard', username=session.get('id')))
        return render_template('register.html')

    @app.route('/<username>/dashboard/deposit', methods=["GET", "POST"])
    def deposit(username):
        balance = BankAccount.query.filter_by(username=username).first().balance
        return render_template('deposit.html', username=username, balance=balance) 

    @app.route('/<username>/dashboard/withdraw', methods=["GET", "POST"])
    def withdraw(username):
        balance = BankAccount.query.filter_by(username=username).first().balance
        return render_template('withdraw.html', username=username, balance=balance) 
    
    @app.route("/withdraw_verify/<username>", methods=["GET", "POST"])
    def withdraw_verify(username):
        withdraw_amount = int(request.form.get("withdraw_amount"))
        user = BankAccount.query.filter_by(username=username).first()
        if user:
            if withdraw_amount > user.balance:
                return '<h3>The input amount is greater than your balance!</h3>', 400
            user.update_balance(-withdraw_amount)
            db.session.commit()
        print("Updated Balance: ", str(BankAccount.query.filter_by(username=username).first().balance))
        return redirect(url_for('dashboard', username=username)) 


    @app.route("/deposit_verify/<username>", methods=["GET", "POST"])
    def deposit_verify(username):
        deposit_amount = int(request.form.get("deposit_amount"))
        user = BankAccount.query.filter_by(username=username).first()
        if user:
            user.update_balance(+deposit_amount)
            db.session.commit()
        print("Updated Balance: ", str(BankAccount.query.filter_by(username=username).first().balance))
        return redirect(url_for('dashboard', username=username)) 


    @app.route('/logout', methods=["GET", "POST"])
    def logout():
        # session.pop('id', None)
        return redirect(url_for('home'))

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
