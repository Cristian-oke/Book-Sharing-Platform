from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app import db
from app.models import Book, User
from app.schemas import book_schema, books_schema
from marshmallow import ValidationError

books_bp = Blueprint('books', __name__, url_prefix='/Book_Sharing/books')

@books_bp.route('/add', methods=['POST'])
@jwt_required()
def add_book():
    try:
        data = book_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
        
    new_book = Book(
        title=data['title'],
        author=data['author'],
        isbn=data.get('isbn'),
        description=data.get('description'),
        status=data.get('status', 'Noua'),
        availability=data.get('availability', 'Disponibila'),
        user_id=int(get_jwt_identity()) #legarea cartii de userul logat
    )
    
    db.session.add(new_book)
    db.session.commit()
    
    return jsonify({
        "message": "Cartea a fost adăugată cu succes în biblioteca ta",
        "book": book_schema.dump(new_book)
    }), 201

#afisarea tuturor cartilor
@books_bp.route('/view-books', methods=['GET'])
def get_all_books():
   
    title_query = request.args.get('title')
    author_query = request.args.get('author')
    city_query = request.args.get('city')

    query = Book.query.join(User)
    
    #aplicare dinamic filtre introduse de utilizator
    if title_query:
        query = query.filter(Book.title.ilike(f"%{title_query}%"))
        
    if author_query:
        query = query.filter(Book.author.ilike(f"%{author_query}%"))
        
    if city_query:
        query = query.filter(User.city.ilike(f"%{city_query}%"))
        
    books = query.all()
    return jsonify(books_schema.dump(books)), 200

#stege cartea -doar proprietarul sau admin
@books_bp.route('/delete/<int:book_id>', methods=['DELETE'])
@jwt_required()
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    current_user_id = int(get_jwt_identity())
    claims = get_jwt()
    
    if book.user_id != current_user_id and claims.get("role") != "admin":
        return jsonify({"error": "Nu ai permisiunea să ștergi această carte"}), 403
        
    db.session.delete(book)
    db.session.commit()
    return jsonify({"message": "Cartea a fost ștearsă cu succes"}), 200

#editare carte
@books_bp.route('/edit/<int:book_id>', methods=['PUT'])
@jwt_required()
def update_book(book_id):
    current_user_id = int(get_jwt_identity())
    
    book = Book.query.get_or_404(book_id)
    if book.user_id != current_user_id:
        return jsonify({"error": "Poți edita doar cartea care îți aparține"}), 403
        
    try:
        #valideaza doar campurile trmise nu pe toate
        validated_data = book_schema.load(request.get_json(), partial=True)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    
    #campurile care au trecut cu succes de validarea marshmallow 
    if 'title' in validated_data:
        book.title = validated_data['title']
    if 'author' in validated_data:
        book.author = validated_data['author']
    if 'isbn' in validated_data:
        book.isbn = validated_data['isbn']
    if 'description' in validated_data:
        book.description = validated_data['description']
    if 'status' in validated_data:
        book.status = validated_data['status']
    if 'availability' in validated_data:
        book.availability = validated_data['availability']
        
    db.session.commit()
    
    return jsonify({
        "message": "Cartea a fost actualizată cu succes!",
        "book": book_schema.dump(book)
    }), 200

@books_bp.route('/view-books/<int:user_id>', methods=['GET'])
def view_user_books(user_id):
    user = User.query.get_or_404(user_id)
    books = Book.query.filter_by(user_id=user.id).all()
    
    return jsonify({
        "user": {
            "name": user.name,
            "city": user.city
        },
        "books": books_schema.dump(books)
    }), 200