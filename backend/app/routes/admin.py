from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from app import db
from app.models import LoanRequest, User, Book, Review, Loan

admin_bp = Blueprint('admin', __name__, url_prefix='/Book_Sharing/admin')

@admin_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_platform_stats():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Acces interzis"}), 403

    total_users = User.query.count()
    total_books = Book.query.count()
    total_reviews = Review.query.count()
    total_loans = Loan.query.count()
    total_loans_requests = LoanRequest.query.count()

    #cate cartii are un user in medie
    avg_books_per_user = round(total_books / total_users, 2) if total_users > 0 else 0

    #cate review-uri primeste un user in medie
    avg_reviews_received = round(total_reviews / total_users, 2) if total_users > 0 else 0

    #cate imprumuturi sunt active
    active_loans = Loan.query.filter_by(status="activ").count()

    return jsonify({
        "total": {
            "users": total_users,
            "books": total_books,
            "reviews": total_reviews,
            "loans_completed": total_loans - active_loans,
            "total_loans_requests": total_loans_requests
        },
        "averages": {
            "books_per_user": avg_books_per_user,
            "reviews_per_user": avg_reviews_received
        },
        "live_activity": {
            "current_active_loans": active_loans
        }
    }), 200

@admin_bp.route('/delete-user/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    claims = get_jwt()
    if claims.get("role") == "admin":
        user = User.query.get_or_404(user_id)
        user_book_ids = [b.id for b in Book.query.filter_by(user_id=user_id).all()]
        Review.query.filter_by(user_id=user_id).delete()
        Loan.query.filter(
        (Loan.borrower_id == user_id) | (Loan.book_id.in_(user_book_ids))).delete(synchronize_session=False)
        LoanRequest.query.filter(
        (LoanRequest.borrower_id == user_id) | (LoanRequest.book_id.in_(user_book_ids))).delete(synchronize_session=False)
        Book.query.filter_by(user_id=user_id).delete()

        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "Utilizatorul a fost șters cu succes"}), 200
    else:
        return jsonify({"error": "Acces interzis"}), 403