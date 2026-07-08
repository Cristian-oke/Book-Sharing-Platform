from datetime import datetime, timezone
from sqlalchemy import Index
from app import db

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    city = db.Column(db.String(100), nullable=False) 

    role = db.Column(db.String(50), default="user", nullable=False) #normal sau admin

    #un utilizator poate avea mai multe carti pe care le poate imprumuta 
    books = db.relationship('Book', backref='owner', lazy=True)
    #un utilizator poate avea mai multe recenzii
    reviews = db.relationship('Review', backref='reviewer', lazy=True)

class Book(db.Model):
    __tablename__ = 'books'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(200), nullable=False)
    isbn = db.Column(db.String(20), nullable=True)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default="Noua")       # noua, buna, uzata
    availability = db.Column(db.String(50), default="Disponibila") # disponibila, imprumutata
    
    # foreign key care leaga cartea de utilizatorul care o detine
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # o carte poate avea mai multe cereri de imprumut pentru o carte
    loan_requests = db.relationship('LoanRequest', backref='book', lazy=True)
    #o carte poate avea mai multe imprumuturi dar nu in acelasi timp doar unul activ
    loans = db.relationship('Loan', backref='book', lazy=True)


class LoanRequest(db.Model):
    __tablename__ = 'loan_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    borrower_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(50), default="in_asteptare") # in_asteptare, aprobata, respinsa
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))  #lambda pentru a genera la fiecare inserare noua nu doar o data

class Loan(db.Model):
    __tablename__ = 'loans'
    
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    borrower_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    loan_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    return_date = db.Column(db.DateTime, nullable=True) # daca e null imprumutul este activ
    status = db.Column(db.String(50), default="activ") # activ, returnat

    # constrangere- cel mult un imprumut activ per carte la un moment dat
    # creeaza un index unic pe book_id doar unde statusul este activ
    __table_args__ = (
        Index('un_active_loan_per_book','book_id',unique=True,postgresql_where=(status == 'activ')),
    )

class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False) # 1-5 stele
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))