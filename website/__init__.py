# file __init__.py giúp tổ chức mã nguồn theo cách có cấu trúc hơn,
# cho phép chia nhỏ ứng dụng thành các module và package dễ quản lý.
from flask import Flask, render_template
from flask_login import current_user, LoginManager
from sqlalchemy.testing.pickleable import User
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
DB_NAME = "database.sqlite3"

def create_database():
    db.create_all()
    print('Database created.')
# initialize application
def create_app():
    app = Flask(__name__)
    # secret key
    app.config['SECRET_KEY'] = 'icl ts pmo sybau'
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'

    db.init_app(app)

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('404.html')

    @login_manager.user_loader
    def load_user(id):
        return Customer.query.get(int(id))

    @login_manager.request_loader
    def load_user_from_request(request):
        api_key = request.args.get('api_key')
        return User.query.filter_by(api_key=api_key).first() if api_key else None

    from .views import views
    from .auth import auth
    from .admin import admin
    from .models import Customer, Cart, Product, Order

    # dang ky blueprint vao ung dung flask
    # localhost:5000/about-us
    app.register_blueprint(views, url_prefix='/')
    # localhost:5000/auth/change-password
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(admin, url_prefix='/')
    # return flask application

    # with app.app_context():
    #     create_database()
    return app
