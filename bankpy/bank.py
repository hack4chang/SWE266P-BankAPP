from flask import Flask, request, render_template, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from database import AccountBalance, db

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

    @app.route('/dashboard', methods=["POST"])
    def dashboard():
        username = request.args.get('username')
        balance = request.args.get('balance')
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
                return redirect(url_for('dashboard', username=username, balance=user.balance), code=307) 
            else:
                return '<h3>User Not Found or Password Incorrect! Please Login Again!</h3>'

    @app.route('/register_verify', methods=["POST"])
    def register_verify():
        username = request.form.get("username")
        password = request.form.get("password")
        password2 = request.form.get("password2")
        if not username or not password or not password2 or password != password2:
            return '<h3>Invalid Input or Invalid Account ID or Invalid Password!</h3>'
        try:
            print(f"[Register Request] Username - {username}; Password - {password}")
            new_account = AccountBalance(username=username, password=password, balance=19.99)
            db.session.add(new_account)
            db.session.commit()
            print(f"[Request Success]")
            return redirect(url_for('login', message="Register Success!"))

        except Exception as e:
            db.session.rollback()
            print(f"Error occurred: {e}")
            if str(e).find("UNIQUE constraint failed"):
                return '<h3>Username Exist! Please login or register with another name!</h3>', 400
            else:
                return '<h3>Invalid Input or Invalid Account ID or Invalid Password!</h3>', 400

    @app.route('/register', methods=["GET", "POST"])
    def register():
        # if session.get('id') != None:
        #     return redirect(url_for('dashboard', username=session.get('id')))
        return render_template('register.html')

    @app.route('/dashboard/<username>/deposit', methods=["GET", "POST"])
    def deposit(username, balance):
        return render_template('deposit.html', user=username, balance=balance) 

    """
    @app.route('/dashboard/<username>/withdraw', methods=["GET", "POST"])
    def withdraw(username, balance):
        return render_template('withdraw.html', user=username, balance=balance) 
    """

    @app.route('/logout', methods=["GET", "POST"])
    def logout():
        # session.pop('id', None)
        return redirect(url_for('home'))

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
