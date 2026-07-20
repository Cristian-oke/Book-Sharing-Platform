from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, get_jwt, jwt_required
from app import db
from app.schemas import user_register_schema, user_login_schema
from app.models import Book, Review, User,LoanRequest, Loan
from datetime import timedelta


#blueprint pentru autentificare
auth_bp = Blueprint('auth', __name__, url_prefix='/Book_Sharing/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    
    try:
        data = user_register_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Acest email este deja înregistrat"}), 400

    #cripatare parola
    hashed_password = generate_password_hash(data['password'])
    
    # creare utilizator nou
    new_user = User(
        name=data['name'],
        email=data['email'],
        password_hash=hashed_password,
        city=data['city']
    )
    
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "Înregistrare reușita"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():

    try:
        data = user_login_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
        
    user = User.query.filter_by(email=data['email']).first()
    
    # verificare utilizator si parola
    if not user:
        return jsonify({"error": "Această adresă de email nu este înregistrată"}), 400
    if not check_password_hash(user.password_hash, data['password']):
        return jsonify({"error": "Date de autentificare invalide"}), 401
        
    #generare token JWT folosind id utilizatorului drept identitate cu expirare la 2 ore
    additional_claims = {"role": user.role}
    access_token = create_access_token(identity=str(user.id),additional_claims=additional_claims,expires_delta=timedelta(hours=2))
    
    return jsonify({
        "message": "Autentificare reușita",
        "access_token": access_token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "city": user.city,
            "role": user.role
        }
    }), 200


@auth_bp.route('/admin-test', methods=['GET'])
@jwt_required()
def admin_test():
    claims = get_jwt()
    
    if claims.get("role") == "admin":
        return jsonify({"message": "Sunt admin"}), 200
    else:
        return jsonify({"message": "Acces interzis"}), 403


