from flask import Flask, request, render_template, redirect, url_for, flash, session, send_file
from flask_sqlalchemy import SQLAlchemy
from database import AccountBalance, ZelleHistory, db
from uuid import uuid4
from datetime import timedelta
import re, os, csv

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = "secret_key_00000"
    db.init_app(app)
    os.makedirs("trans_history", exist_ok=True)
    app.permanent_session_lifetime = timedelta(minutes=10)
    

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
        if session.get('user') != None:
           return redirect(url_for('dashboard', username=session.get('user')))
        return render_template('home.html')

    @app.route('/login', methods=["GET", "POST"])
    def login():
        if session.get('user') != None:
            return redirect(url_for('dashboard', username=session.get('user')))
        message = request.args.get('message')
        print(message)
        return render_template('login.html', message=message)

    @app.route('/<username>/dashboard', methods=["GET", "POST"])
    def dashboard(username):
        if not session.get('user'):
            return redirect(url_for('login'))
        if username != session.get('user'):
            return redirect(url_for('dashboard', username=session.get('user'))) 
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
            return '<h3>Invalid Input or Invalid Account ID or Invalid Password!</h3>'
        else:
            user = AccountBalance.query.filter_by(username=username).first()
            if user and user.check_password(password):
                session['user'] = username
                session.permanent = True
                session.modified = True
                return redirect(url_for('dashboard', username=username)) 
            else:
                return '<h3>User Not Found or Password Incorrect! Please Login Again!</h3>'

    @app.route('/register_verify', methods=["GET", "POST"])
    def register_verify():

        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")
            password2 = request.form.get("password2")
            if not username or not password or not password2 or password != password2:
                flash('Invalid Input or Invalid Account ID or Invalid Password!', "warning")
                return redirect(request.url)
        
            try:
                print(f"[Register Request] Username - {username}; Password - {password}")
                # password check would be around here (throws exception if issue found)
                PasswordUsernameRequirements(password, username)

                new_account = AccountBalance(username=username, password=password, balance=19.99)
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
        if not session.get('user'):
            return redirect(url_for('login'))
        if username != session.get('user'):
            return redirect(url_for('deposit', username=session.get('user'))) 
        balance = AccountBalance.query.filter_by(username=username).first().balance
        return render_template('deposit.html', username=username, balance=balance) 

    @app.route('/<username>/dashboard/withdraw', methods=["GET", "POST"])
    def withdraw(username):
        if not session.get('user'):
            return redirect(url_for('login'))
        if username != session.get('user'):
            return redirect(url_for('withdraw', username=session.get('user'))) 
        balance = AccountBalance.query.filter_by(username=username).first().balance
        return render_template('withdraw.html', username=username, balance=balance) 
    
    @app.route("/withdraw_verify/<username>", methods=["GET", "POST"])
    def withdraw_verify(username):
        if username != session.get('user'):
            return redirect(url_for('withdraw_verify', username=session.get('user'))) 
        withdraw_amount = int(request.form.get("withdraw_amount"))
        input_username = str(request.form.get("username")) # for verification
        print(withdraw_amount, input_username)

        if input_username != username:
            return '<h3>Invalid Input: Username Verification Failed!</h3>', 400
        if withdraw_amount <= 0.0:
            return '<h3>Invalid Input: Withdraw Amount Error!</h3>', 400
        
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
        if username != session.get('user'):
            return redirect(url_for('deposit_verify', username=session.get('user'))) 
        deposit_amount = int(request.form.get("deposit_amount"))
        input_username = str(request.form.get("username")) # for verification
        print(deposit_amount, input_username)
        if input_username != username:
            return '<h3>Invalid Input: Username Verification Failed!</h3>', 400
        if deposit_amount <= 0.0:
            return '<h3>Invalid Input: Deposit Amount Error!</h3>', 400
        user = AccountBalance.query.filter_by(username=username).first()
        if user:
            user.update_balance(+deposit_amount)
            db.session.commit()
        print("Updated Balance: ", str(AccountBalance.query.filter_by(username=username).first().balance))
        return redirect(url_for('dashboard', username=username)) 

    @app.route('/<username>/dashboard/zelle', methods=["POST"])
    def zelle(username):
        if not session.get('user'):
            return redirect(url_for('login'))
        if username != session.get('user'):
            return redirect(url_for('zelle', username=session.get('user'))) 
        balance = AccountBalance.query.filter_by(username=username).first().balance
        history = []
        try:
            history = ZelleHistory.query.filter_by(receiver=username).all()
            file_path = os.path.join("trans_history", f'{username}.csv')
            file_content = [['Sender', 'Amount', 'Memo']]
            
            if history:
                for trans in history:
                    file_content.append([trans.sender, trans.amount, trans.memo])
            
            with open(file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(file_content)

        except Exception as e:
            print(e)

        return render_template('zelle_transfer.html', username=username, balance=balance, history=history) 
        
    @app.route('/zelle_verify/<username>/', methods=["POST"])
    def zelle_verify(username):
        if username != session.get('user'):
            return redirect(url_for('zelle_verify', username=session.get('user'))) 
        receiver = request.form.get('receiver')
        amount = round(float(request.form.get('amount')), 2)
        memo = request.form.get('memo')
        balance = AccountBalance.query.filter_by(username=username).first().balance
        receiver_acc = AccountBalance.query.filter_by(username=receiver).first()
        
        user_acc = AccountBalance.query.filter_by(username=username).first()

        if receiver == username or not receiver_acc:
            return '<h3>Invalid Input: Invalid Receiver!</h3>', 400
        elif amount > balance or amount <= 0.0:
            return '<h3>Invalid Input: Invalid Amount!</h3>', 400
        elif len(memo) > 200:
            return '<h3>Invalid Input: Memo characters exceed 200!</h3>', 400

        receiver_acc.update_balance(amount)
        user_acc.update_balance(-amount)

        new_record = ZelleHistory(username, receiver, amount, memo)
        db.session.add(new_record)
        db.session.commit()
        
        return redirect(url_for('dashboard', username=username))

    @app.route('/<username>/zelle/download_zelle_history', methods=["POST"])
    def download_zelle_history(username):
        try:
            return send_file(f"trans_history/{username}.csv")
        except Exception as e:
            return render_template('404.html', username=username)
        
    @app.route('/logout', methods=["GET", "POST"])
    def logout():
        session.pop('user', None)
        return redirect(url_for('home'))

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)