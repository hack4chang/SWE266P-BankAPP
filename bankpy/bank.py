from flask import Flask, request, render_template, redirect, url_for, flash, session, send_file
from uuid import uuid4
from database import AccountBalance, ZelleHistory, db, AccountBalanceSnapshot, BankService
from datetime import timedelta
import re, os, csv

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # stronger secret key
    app.secret_key = str(uuid4())
    # add salt to make hash more robust
    SALT = ">@a3s$^*@(!f1i+C&0#sA8_023rL"
    db.init_app(app)
    os.makedirs("trans_history", exist_ok=True)
    # session id timeout
    app.permanent_session_lifetime = timedelta(minutes=10)

    with app.app_context():
        db.create_all()

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404


    @app.route('/')
    def home():
        ### [VULFIX] CWE-639: Authorization Bypass Through User-Controlled Key 
        if session.get('user') != None:
           return redirect(url_for('dashboard', username=session.get('user')))
        return render_template('home.html')


    @app.route('/login', methods=["GET", "POST"])
    def login():
        ### [VULFIX] CWE-639: Authorization Bypass Through User-Controlled Key 
        if session.get('user') != None:
            return redirect(url_for('dashboard', username=session.get('user')))
        message = request.args.get('message')
        print(message)
        return render_template('login.html', message=message, secret=SALT)
 

    @app.route('/<username>/dashboard', methods=["GET", "POST"])
    def dashboard(username):
        ### [VULFIX] CWE-639: Authorization Bypass Through User-Controlled Key 
        if not session.get('user'):
            return redirect(url_for('login'))
        if username != session.get('user'):
            return redirect(url_for('dashboard', username=session.get('user'))) 
        print("In the dashboard - username: " + username)
        user = AccountBalance.query.filter_by(username=username).first()
        # if not user:
        #     flash("Warning: User does not exist.", "warning")
        #     return redirect(url_for("login"))
        balance = "%.2f" % user.balance
        print("In the dashboard - balance: " + str(balance))
        return render_template('dashboard.html', username=username, balance=balance) 


    @app.route('/login_verify', methods=["GET", "POST"])
    def login_verify():
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")
            action = request.form.get('action')
            print("Username - " + username + "; Password - " + password)

            user = AccountBalance.query.filter_by(username=username).first()
            if user and user.check_password(password):
                session['user'] = username
                session.permanent = True
                session.modified = True
                return redirect(url_for('dashboard', username=username)) 
            # elif user and action == 'forgot_password':
            #     username = request.form.get('username')
            #     account = AccountBalance.query.filter_by(username=username).first()
            #     password = account.password
            #     message = 'The password for ' + username + ' is: ' + password
            #     flash(message, "warning")
            #     return redirect(request.url)
            else:
                message = "User not found or password incorrect! Please login again!"
                flash(message, 'warning')
                return redirect(url_for("login"))
        return render_template('login.html')


    @app.route('/register_verify', methods=["GET", "POST"])
    def register_verify():
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")
            password2 = request.form.get("password2")
            initial_balance = request.form.get("initial_balance")
            ### [VULFIX] CWE-20 Improper Input Validation 
            if (initial_balance == "") or (float(initial_balance) < 0.0):
                initial_balance = 0.0
            if not username or not password or not password2 or password != password2:
                flash('Invalid Input or Invalid Account ID or Invalid Password!', "warning")
                return redirect(url_for("register"))
        
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
                return redirect(url_for("register"))
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
        return render_template('register.html', secret=SALT)


    @app.route('/<username>/dashboard/deposit', methods=["GET", "POST"])
    def deposit(username):
        ### [VULFIX] CWE-639: Authorization Bypass Through User-Controlled Key 
        if not session.get('user'):
            return redirect(url_for('login'))
        if username != session.get('user'):
            return redirect(url_for('deposit', username=session.get('user'))) 
        user = AccountBalance.query.filter_by(username=username).first()
        # if not user:
        #     flash("user does not exist", "warning")
        #     return redirect(url_for("login"))
        balance = user.balance
        return render_template('deposit.html', username=username, balance=balance) 


    @app.route('/<username>/dashboard/withdraw', methods=["GET", "POST"])
    def withdraw(username):
        ### [VULFIX] CWE-639: Authorization Bypass Through User-Controlled Key 
        if not session.get('user'):
            return redirect(url_for('login'))
        if username != session.get('user'):
            return redirect(url_for('withdraw', username=session.get('user'))) 
        user = AccountBalance.query.filter_by(username=username).first()
        # if not user:
        #     flash("user does not exist", "warning")
        #     return redirect(url_for("login"))
        balance = user.balance
        return render_template('withdraw.html', username=username, balance=balance) 
    

    @app.route("/withdraw_verify/<username>", methods=["GET", "POST"])
    def withdraw_verify(username):
        ### [VULFIX] CWE-639: Authorization Bypass Through User-Controlled Key 
        if username != session.get('user'):
            return redirect(url_for('withdraw_verify', username=session.get('user'))) 
        entered_amount = request.form.get("withdraw_amount")
        if not entered_amount:
            flash("Please enter amount to withdraw", "warning")
            return redirect(url_for("withdraw", username=username))
        withdraw_amount = float(entered_amount)
        
        ### [VULFIX] CWE-20 Improper Input Validation 
        if withdraw_amount <= 0.0:
            flash("Please enter amount greater than zero", "warning")
            return redirect(url_for("withdraw", username=username))
        
        user = AccountBalance.query.filter_by(username=username).first()
        balance = float(user.balance)
        
        ### [VULFIX] CWE-20 Improper Input Validation 
        if balance < withdraw_amount:
            flash("Please enter amount greater than your current balance!", "warning")
            return redirect(url_for("withdraw", username=username))

        snapshot = AccountBalanceSnapshot(user)
        service = BankService()
        service.withdraw(snapshot, withdraw_amount)
        db.session.commit()
        print("Updated Balance: ", str(AccountBalance.query.filter_by(username=username).first().balance))
        return redirect(url_for('dashboard', username=username)) 


    @app.route("/deposit_verify/<username>", methods=["GET", "POST"])
    def deposit_verify(username):
        ### [VULFIX] CWE-639: Authorization Bypass Through User-Controlled Key 
        if username != session.get('user'):
            return redirect(url_for('deposit_verify', username=session.get('user'))) 
        entered_amount = request.form.get("deposit_amount")
        if not entered_amount:
            flash("Please enter amount to deposit", "warning")
            return redirect(url_for("deposit", username=username))
        deposit_amount = float(entered_amount)
        
        ### [VULFIX] CWE-20 Improper Input Validation 
        if deposit_amount <= 0.0:
            flash("Please enter amount greater than zero", "warning")
            return redirect(url_for("deposit", username=username))
        
        user = AccountBalance.query.filter_by(username=username).first()
        if user:
            user.update_balance(+deposit_amount)
            db.session.commit()
        print("Updated Balance: ", str(AccountBalance.query.filter_by(username=username).first().balance))
        return redirect(url_for('dashboard', username=username)) 

        
    @app.route('/<username>/dashboard/zelle', methods=["POST", "GET"])
    def zelle(username):
        ### [VULFIX] CWE-639: Authorization Bypass Through User-Controlled Key 
        if not session.get('user'):
            return redirect(url_for('login'))
        if username != session.get('user'):
            return redirect(url_for('zelle', username=session.get('user'))) 
        user = AccountBalance.query.filter_by(username=username).first()
        # if not user:
        #     flash("user does not exist", "warning")
        #     return redirect(url_for("login"))
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
        
        
    @app.route('/zelle_verify/<username>/', methods=["POST", "GET"])
    def zelle_verify(username):
        ### [VULFIX] CWE-639: Authorization Bypass Through User-Controlled Key 
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


    @app.route('/<username>/zelle/download_zelle_history', methods=["GET"])
    ### [VULFIX] CWE-22: Improper Limitation of a Pathname to a Restricted Directory (Path Traversal)
    def download_zelle_history(username):
        if username != session.get('user'):
            return redirect(url_for('zelle', username=session.get('user')))
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
