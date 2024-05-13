from flask import Flask, request, render_template, redirect, url_for

app = Flask(__name__)

bank_accounts = {}
login_records = {}

class Balance:
    balance = 0
    def __init__(self, amount):
        self.balance = amount
    def __str__(self) -> str:
        return str(self.balance)

class Account:
    username = ""
    password = ""
    balance = None
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.balance = Balance(10000)

def write_account_to_file(account):
    with open('bank_info.txt', 'a') as f:
        f.write("-ACCOUNT-\n")
        f.write("username: " + account.username + "\n")
        f.write("password: " + account.password + "\n")
        f.write("balance: " + str(account.balance) + "\n")



@app.route('/') #this is the url that takes you to the returned page
def home():
    return render_template('home.html')

@app.route('/register.html', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get('register_username')
        password = request.form.get('register_password')
        print("USERNAME IS", username)
        print("PASSWORD IS", password)
        if username in bank_accounts.keys():
            return render_template('register_taken_username.html')
        if not username or not password:
            return redirect(url_for('invalid_input'))
        else:
            new_account = Account(username, password)
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
        if username in bank_accounts.keys():
            return render_template('register_taken_username.html')
        new_account = Account(username, password)
        bank_accounts[username] = new_account
        login_records[username] = password
        write_account_to_file(new_account)
        return render_template('home.html')

@app.route('/forgot_password.html', methods=["GET", "POST"])
def forgot_password():
    print(request.method)
    if request.method == "GET":
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
    action = request.form.get('action')
    if action == 'forgot_password':
        username = request.form.get('username')
        if username in login_records:
            return render_template('forgot_password.html', data=login_records[username])
        else:
            return redirect(url_for('no_password'))
    else:
        pass

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)