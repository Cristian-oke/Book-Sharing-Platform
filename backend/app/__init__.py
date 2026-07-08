import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow


# initializare extensii ca si obiecte
db = SQLAlchemy()
migrate = Migrate()
ma = Marshmallow()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)

    # configurare baza de date si JWT
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/booksharing_db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'secret-default-key')

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    ma.init_app(app)
    
    from app.models import User, Book, LoanRequest, Loan, Review

    # inregistrare blueprint pentru autentificare
    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    # inregistrare blueprint pentru carti
    from app.routes.books import books_bp
    app.register_blueprint(books_bp)


    from app.routes.loans import loans_bp
    app.register_blueprint(loans_bp)

    from app.routes.reviews import reviews_bp
    app.register_blueprint(reviews_bp)

    from app.routes.admin import admin_bp
    app.register_blueprint(admin_bp)


    @app.route('/')
    def index():
        return {"message": "API ruleaza"}

    return app