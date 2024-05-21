from flask import Flask, request, render_template, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from database import AccountBalance, db
import re

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = '123'
    db.init_app(app)

    with app.app_context():
        db.create_all()

    """
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500
    """

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
        balance = AccountBalance.query.filter_by(username=username).first().balance
        print("In the dashboard - balance: " + str(balance))
        return render_template('dashboard.html', username=username, balance=balance) 

    @app.route('/login_verify', methods=["POST"])
    def login_verify():
        username = request.form.get("username")
        password = request.form.get("password")
        print("Username - " + username + "; Password - " + password)
        if not username or not password:
            return render_template('invalid_input.html')
        else:
            user = AccountBalance.query.filter_by(username=username).first()
            if user and user.check_password(password):
                return redirect(url_for('dashboard', username=username)) 
            else:
                return '<h3>User Not Found or Password Incorrect! Please Login Again!</h3>'

    @app.route('/register_verify', methods=["GET", "POST"])
    def register_verify():

        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")
            password2 = request.form.get("password2")
            initial_balance = request.form.get("initial_balance")
            if not username or not password or not password2 or password != password2:
                flash('Invalid Input or Invalid Account ID or Invalid Password!', "warning")
                return redirect(request.url)
        
            try:
                print(f"[Register Request] Username - {username}; Password - {password}")
                # password check would be around here (throws exception if issue found)
                PasswordUsernameRequirements(password, username)

                new_account = AccountBalance(username=username, password=password, balance=float(initial_balance))
                db.session.add(new_account)
                db.session.commit()
                print(f"[Request Success]")
                return redirect(url_for('login', message="Register Success!"))

            except Exception as e:
                db.session.rollback()
                print(f"Error occurred: {e}")
                if "UNIQUE constraint failed" in str(e):
                    flash("Username Exist! Please login or register with another name!", "warning")
                elif "Improper Password characters detected." in str(e):
                    flash("Invalid Password! Improper Characters.", "warning")
                elif "Improper Password length detected." in str(e):
                    flash("Improper Password length detected. Must be greater than 0 characters and less than 127 characters.", "warning")
                elif "Invalid username detected." in str(e):
                    flash("Invalid username detected.", "warning")
                else:
                    flash("Invalid Input or Invalid Account ID or Invalid Password!", "warning")
                return redirect(request.url)
        return render_template('register.html')


    #check password requirements based on regex and length
    # throws exception 
    def PasswordUsernameRequirements(password, username):
        command_pattern = r'[^a-zA-Z0-9_.-]'  
        ip_pattern = r'(\d{1,3}\.){3}\d{1,3}'

        # restricted to underscores, hyphens, dots, digits, and lowercase alphabetical characters
        command_pattern2 = r'[a-z0-9_.-]' 
        
        if (re.search(command_pattern, username) or re.fullmatch(ip_pattern, username)):
            raise Exception("Invalid username detected.")
        elif(not re.search(command_pattern2, password)):
           raise Exception("Improper Password characters detected.")
        elif(len(password) == 0 or len(password) > 127):
           raise Exception("Improper Password length detected.")
        else:
            print("Password successful")

       
        
    @app.route('/register', methods=["GET", "POST"])
    def register():
        # if session.get('id') != None:
        #     return redirect(url_for('dashboard', username=session.get('id')))
        return render_template('register.html')

    @app.route('/<username>/dashboard/deposit', methods=["GET", "POST"])
    def deposit(username):
        balance = AccountBalance.query.filter_by(username=username).first().balance
        return render_template('deposit.html', username=username, balance=balance) 

    @app.route('/<username>/dashboard/withdraw', methods=["GET", "POST"])
    def withdraw(username):
        balance = AccountBalance.query.filter_by(username=username).first().balance
        return render_template('withdraw.html', username=username, balance=balance) 
    
    @app.route("/withdraw_verify/<username>", methods=["GET", "POST"])
    def withdraw_verify(username):
        withdraw_amount = int(request.form.get("withdraw_amount"))
        user = AccountBalance.query.filter_by(username=username).first()
        if user:
            if withdraw_amount > user.balance:
                return '<h3>The input amount is greater than your balance!</h3>', 400
            user.update_balance(-withdraw_amount)
            db.session.commit()
        print("Updated Balance: ", str(AccountBalance.query.filter_by(username=username).first().balance))
        return redirect(url_for('dashboard', username=username)) 


    @app.route("/deposit_verify/<username>", methods=["GET", "POST"])
    def deposit_verify(username):
        deposit_amount = int(request.form.get("deposit_amount"))
        user = AccountBalance.query.filter_by(username=username).first()
        if user:
            user.update_balance(+deposit_amount)
            db.session.commit()
        print("Updated Balance: ", str(AccountBalance.query.filter_by(username=username).first().balance))
        return redirect(url_for('dashboard', username=username)) 


    @app.route('/logout', methods=["GET", "POST"])
    def logout():
        # session.pop('id', None)
        return redirect(url_for('home'))

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
