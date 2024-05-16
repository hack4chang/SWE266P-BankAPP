from flask import Flask, request, render_template, redirect, url_for

app = Flask(__name__)

bank_accounts = {}
login_records = {}
current_account = None

class Balance: #balance class to make balance immutable
    balance = 0
    def __init__(self, amount):
        self.balance = amount
    def __str__(self) -> str:
        return str(self.balance)

class Account: #user bank account#
    username = ""
    password = ""
    balance = None
    def __init__(self, username, password, balance):
        self.username = username
        self.password = password
        self.balance = balance

class BankService: #Bank Service class to do actions of bank
    def __init__(self) -> None:
        pass
    
    def deposit(bal_to_dep: Balance, dep_amt: int) -> Balance:
        curr_amt = bal_to_dep.balance
        new_bal = Balance(curr_amt + dep_amt)
        return new_bal

    def withdraw(bal_to_wit: Balance, with_amt: int) -> Balance:
        curr_amt = bal_to_wit.balance
        new_bal = Balance(curr_amt - with_amt)
        return new_bal

def write_account_to_file(account):
    with open('bank_info.txt', 'a') as f:
        f.write("-ACCOUNT-\n")
        f.write("username:" + account.username + "," + "password:" + account.password + "," + str(account.balance) + "\n")
        
def overrite_balance(account):
    with open('bank_info.txt', 'w') as f:
        for line in f.readlines():
            print(line)


@app.route('/') #this is the url that takes you to the returned page
def home():
    return render_template('home.html')


@app.route('/register.html', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get('register_username')
        password = request.form.get('register_password')
        initial_balance = request.form.get('register_balance')
        print("USERNAME IS", username)
        print("PASSWORD IS", password)
        print("INITIAL BALANCE IS", initial_balance)
        if username in bank_accounts.keys():
            return render_template('register_taken_username.html')
        if not username or not password:
            return redirect(url_for('invalid_input'))
        else:
            balance = Balance(int(initial_balance))
            new_account = Account(username, password, balance)
            bank_accounts[username] = new_account
            login_records[username] = password
            write_account_to_file(new_account)
        return redirect(url_for('home')) #takes you back to the home page after registering
    return render_template('register.html')


@app.route('/invalid_input.html', methods=["GET", "POST"])
def invalid_input():
    return render_template('invalid_input.html')


@app.route('/register.html', methods=["GET", "POST"])
def registered():
    if request.method == "POST":
        username = request.form.get('register_username')
        password = request.form.get('register_password')
        initial_balance = request.form.get('register_balance')
        print("REGISTERED BALANCE IS", initial_balance)
        if username in bank_accounts.keys():
            return render_template('register_taken_username.html')
        balance = Balance(int(initial_balance))
        new_account = Account(username, password)
        new_account.balance = balance
        bank_accounts[username] = new_account
        login_records[username] = password
        write_account_to_file(new_account)
        return render_template('home.html')


@app.route('/forgot_password.html', methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        username = request.form.get('username')
        print("USERNAME IS", username)
        if username in login_records.keys():
            print("RETURNING PASSWORD")
            return render_template('forgot_password.html', data=login_records[username])
        else:
            print("NO PASSWORD")
            return redirect(url_for('no_password'))


@app.route('/no_password.html', methods=["GET", "POST"])
def no_password():
    return render_template('no_password.html')


@app.route('/account.html', methods=["GET", "POST"])
def account():
    action = request.form.get('login') #THIS USES BUTTON NAME ATTRIBUTE 
    if action == 'forgot_password':
        username = request.form.get('username') 
        if username in login_records:
            return render_template('forgot_password.html', data=login_records[username])
        else:
            return redirect(url_for('no_password'))
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        if login_records.get(username, "aa") == password:
            balance = bank_accounts[username].balance
            current_account = bank_accounts[username]
            return render_template('account.html', username=username, balance=balance)
        else:
            return render_template('no_account.html')
        

@app.route('/deposit.html', methods=["GET", "POST"])
def deposit():
    return render_template(url_for('deposit'))


@app.route('/deposit_success.html', methods=["GET", "POST"])
def deposit_success():
    if request.method == "POST":
        deposit_amount = request.form.get('deposit_amount') #RETURNS STRING
        username = request.form.get('username')
        current_account = bank_accounts[username]
        new_balance = Balance(int(deposit_amount) + current_account.balance.balance)
        current_account.balance = new_balance
        print("NEW BANK ACCOUNT BALANCE IS", str(bank_accounts[username].balance))
        return render_template('deposit_success.html', username=username, balance=new_balance)


if __name__ == '__main__':
    current_account = None
    app.run(debug=True, host='0.0.0.0', port=5000)