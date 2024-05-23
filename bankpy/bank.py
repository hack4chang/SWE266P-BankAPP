from flask import Flask, request, render_template, redirect, url_for, flash, session, send_file
from flask_sqlalchemy import SQLAlchemy
from database import AccountBalance, ZelleHistory, db, AccountBalanceSnapshot, BankService
import re, os, csv

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = '123'
    db.init_app(app)
    os.makedirs("trans_history", exist_ok=True)

    with app.app_context():
        db.create_all()

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.route('/')
    def home():
        return render_template('home.html')

    @app.route('/login', methods=["GET", "POST"])
    def login():
        message = request.args.get('message')
        print(message)
        return render_template('login.html', message=message)
 

    @app.route('/<username>/dashboard', methods=["GET", "POST"])
    def dashboard(username):
        print("In the dashboard - username: " + username)
        user = AccountBalance.query.filter_by(username=username).first()
        if not user:
            flash("Warning: User does not exist.", "warning")
            return redirect(url_for("login"))
        balance = "%.2f" % user.balance
        print("In the dashboard - balance: " + str(balance))
        return render_template('dashboard.html', username=username, balance=balance) 

    @app.route('/login_verify', methods=["GET", "POST"])
    def login_verify():
        print("check")
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")
            action = request.form.get('action')
            print("Username - " + username + "; Password - " + password)

            user = AccountBalance.query.filter_by(username=username).first()
            if user and user.check_password(password):
                return redirect(url_for('dashboard', username=username)) 
            elif user and action == 'forgot_password':
                username = request.form.get('username')
                account = AccountBalance.query.filter_by(username=username).first()
                password = account.password
                meesage = 'The password for ' + username + ' is: ' + password
                flash(meesage, "warning")
                return redirect(request.url)
            else:
                meesage = "User not found or password incorrect! Please login again!"
                flash(meesage, 'warning')
                return redirect(request.url)
        return render_template('login.html')

    @app.route('/register_verify', methods=["GET", "POST"])
    def register_verify():

        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")
            password2 = request.form.get("password2")
            initial_balance = request.form.get("initial_balance")
            if(initial_balance == ""):
                initial_balance = 0
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
        return render_template('register.html')

    @app.route('/<username>/dashboard/deposit', methods=["GET", "POST"])
    def deposit(username):
        user = AccountBalance.query.filter_by(username=username).first()
        if not user:
            flash("user does not exist", "warning")
            return redirect(url_for("login"))
        balance = user.balance
        return render_template('deposit.html', username=username, balance=balance) 

    @app.route('/<username>/dashboard/withdraw', methods=["GET", "POST"])
    def withdraw(username):
        user = AccountBalance.query.filter_by(username=username).first()
        if not user:
            flash("user does not exist", "warning")
            return redirect(url_for("login"))
        balance = user.balance
        return render_template('withdraw.html', username=username, balance=balance) 
    
    @app.route("/withdraw_verify/<username>", methods=["GET", "POST"])
    def withdraw_verify(username):
        entered_amount = request.form.get("withdraw_amount")
        if not entered_amount:
            flash("Please enter amount to withdraw", "warning")
            return redirect(url_for("withdraw", username=username))
        withdraw_amount = float(entered_amount)
        user = AccountBalance.query.filter_by(username=username).first()
        snapshot = AccountBalanceSnapshot(user)
        service = BankService()
        service.withdraw(snapshot, withdraw_amount)
        db.session.commit()
        print("Updated Balance: ", str(AccountBalance.query.filter_by(username=username).first().balance))
        return redirect(url_for('dashboard', username=username)) 


    @app.route("/deposit_verify/<username>", methods=["GET", "POST"])
    def deposit_verify(username):
        entered_amount = request.form.get("deposit_amount")
        if not entered_amount:
            flash("Please enter amount to deposit", "warning")
            return redirect(url_for("deposit", username=username))
        deposit_amount = float(entered_amount)
        user = AccountBalance.query.filter_by(username=username).first()
        if user:
            user.update_balance(+deposit_amount)
            db.session.commit()
        print("Updated Balance: ", str(AccountBalance.query.filter_by(username=username).first().balance))
        return redirect(url_for('dashboard', username=username)) 

    @app.route('/<username>/dashboard/zelle', methods=["POST"])
    def zelle(username):
        user = AccountBalance.query.filter_by(username=username).first()
        if not user:
            flash("user does not exist", "warning")
            return redirect(url_for("login"))
        balance = user.balance
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

    @app.route('/<username>/zelle/download_zelle_history', methods=["GET"])
    def download_zelle_history(username):
        file = request.args.get('file')
        try:
            return send_file(file)
        except Exception as e:
            return render_template('404.html', username=username)
        
    @app.route('/logout', methods=["GET", "POST"])
    def logout():
        return redirect(url_for('home'))

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
