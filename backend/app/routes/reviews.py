from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt, jwt_required, get_jwt_identity
from app import db
from app.models import Review, Loan, Book
from app.schemas import review_schema, reviews_schema
from marshmallow import ValidationError

reviews_bp = Blueprint('reviews', __name__, url_prefix='/Book_Sharing/reviews')

#adaugare recenzie
@reviews_bp.route('/add-review/<int:user_id>', methods=['POST'])
@jwt_required()
def add_review(user_id):
    try:
        data = review_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
        
    reviewer_id = int(get_jwt_identity()) 
    reviewed_id = user_id                
    
    if reviewer_id == reviewed_id:
        return jsonify({"error": "Nu îți poți acordan o recenzie proprie"}), 400
        

    has_history = Loan.query.join(Book).filter(
        Loan.status == "Completed",
        (
            ((Loan.borrower_id == reviewer_id) & (Book.user_id == reviewed_id)) | ((Loan.borrower_id == reviewed_id) & (Book.user_id == reviewer_id))
        )
    ).first()
    
    if not has_history:
        return jsonify({"error": "Poți lăsa o recenzie doar utilizatorilor cu care ai finalizat cel puțin un împrumut"}), 403

    new_review = Review(
        user_id=reviewed_id,
        rating=data['rating'],
        comment=data.get('comment')
    )
    
    db.session.add(new_review)
    db.session.commit()
    
    return jsonify({
        "message": "Recenzia a fost adăugată cu succes",
        "review": review_schema.dump(new_review)
    }), 201


@reviews_bp.route('/view-reviews/<int:user_id>', methods=['GET'])
def get_user_reviews(user_id):
    reviews = Review.query.filter_by(user_id=user_id).all()
    
    if reviews:
        media = sum([r.rating for r in reviews]) / len(reviews)
    else:
        media = 0.0
        
    return jsonify({
        "average_rating": round(media, 2),
        "total_reviews": len(reviews),
        "reviews": reviews_schema.dump(reviews)
    }), 200

@reviews_bp.route('/delete-review/<int:review_id>', methods=['DELETE'])
@jwt_required()
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)
    claims = get_jwt()  
    if claims.get("role") != "admin":
        return jsonify({"error": "Nu ai permisiunea să ștergi această recenzie"}), 403
    
    db.session.delete(review)
    db.session.commit()
    return jsonify({"message": "Recenzia a fost ștearsă cu succes"}), 200

@reviews_bp.route('/all-reviews', methods=['GET'])
@jwt_required()
def get_all_reviews_admin():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Acces interzis"}), 403
        
    all_reviews = Review.query.all()
    return jsonify(reviews_schema.dump(all_reviews)), 200