from flask import Flask, request, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from database import AccountBalance, db

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    with app.app_context():
        db.create_all()

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500

    @app.route('/')
    @app.route('/index.html')
    def home():
        return render_template('home.html')

    @app.route('/login.html', methods=["GET", "POST"])
    def login():
        return render_template('login.html')

    @app.route('/<username>/dashboard.html', methods=["GET", "POST"])
    def dashboard(username):
        return render_template('dashboard.html')

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
                return redirect(url_for('dashboard', username=username)) # redirect(url_for('dashboard'))
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
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            print(f"Error occurred: {e}")
            if str(e).find("UNIQUE constraint failed"):
                return '<h3>Username Exist! Please login or register with another name!</h3>'
            else:
                return '<h3>Invalid Input or Invalid Account ID or Invalid Password!</h3>'

    @app.route('/register.html', methods=["GET", "POST"])
    def register():
        return render_template('register.html')

    @app.route('/logout', methods=["GET", "POST"])
    def logout():
        # session.pop('user', None)
        return redirect(url_for('home'))

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=30678)
