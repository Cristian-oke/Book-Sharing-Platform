from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Book, LoanRequest, Loan,User
from app.schemas import loan_request_schema, loan_requests_schema, loan_response_schema
from marshmallow import ValidationError
import datetime

loans_bp = Blueprint('loans', __name__, url_prefix='/Book_Sharing/loans')

#trimite cerere de imprumut
@loans_bp.route('/request/<int:book_id>', methods=['POST'])
@jwt_required()
def request_book(book_id):
    current_user_id = int(get_jwt_identity())
    
    #verificare existenta carte
    book = Book.query.get_or_404(book_id)
    
    if book.user_id == current_user_id:
        return jsonify({"error": "Nu poți trimite o cerere de împrumut pentru propria ta carte"}), 400
    if book.availability != "Disponibila":
        return jsonify({"error": "Această carte nu este disponibilă în acest moment-este deja împrumutată sau indisponibilă"}), 400
        
    existing_request = LoanRequest.query.filter_by(book_id=book_id, borrower_id=current_user_id, status="In asteptare").first()
    
    if existing_request:
        return jsonify({"error": "Ai trimis deja o cerere pentru această carte, cererea se află în așteptare."}), 400

    new_request = LoanRequest(
        book_id=book_id,
        borrower_id=current_user_id,
        status="In asteptare")
    
    db.session.add(new_request)
    db.session.commit()
    
    return jsonify({
        "message": "Cererea de împrumut a fost trimisă cu succes către proprietar",
        "request": loan_request_schema.dump(new_request)
    }), 201


#afisare cereri pentru propriile carti
@loans_bp.route('/my-incoming-requests', methods=['GET'])
@jwt_required()
def get_incoming_requests():
    current_user_id = int(get_jwt_identity())
    incoming_requests = LoanRequest.query.join(Book).filter(Book.user_id == current_user_id).all()
    
    result = []
    for request_item in incoming_requests:
        book = request_item.book
        applicant = User.query.get(request_item.borrower_id) 
        
        result.append({
            "request_id": request_item.id,
            "status": request_item.status,
            "created_at": request_item.created_at,
            "book": {
                "id": book.id if book else None,
                "title": book.title if book else "Carte Ștearsă",
                "author": book.author if book else None
            },
            "requested_by": {
                "id": request_item.borrower_id,
                "name": applicant.name if applicant else "Utilizator Anonim",
                "city": applicant.city if applicant else "Nespecificat"
            }
        })
        
    return jsonify({
        "total_incoming_requests": len(result),
        "incoming_requests": result
    }), 200

#afisare cereri trimise
@loans_bp.route('/my-outgoing-requests', methods=['GET'])
@jwt_required()
def get_outgoing_requests():
    current_user_id = int(get_jwt_identity())
    outgoing = LoanRequest.query.filter(LoanRequest.borrower_id == current_user_id).all()
    result = []
    for request_item in outgoing:
        
        book = request_item.book
        owner = User.query.get(request_item.book.user_id) if book else None
        
        result.append({
            "request_id": request_item.id,
            "status": request_item.status,
            "created_at": request_item.created_at, 
            "book": {
                "id": book.id if book else None,
                "title": book.title if book else "Carte Ștearsă",
                "author": book.author if book else None,
                "owner": {
                    "name": owner.name if owner else "Anonim",
                    "city": owner.city if owner else "Nespecificat"
                }
            }
        })
        
    return jsonify({
        "total_requests": len(result),
        "outgoing_requests": result
    }), 200


# raspundere la o cerere-aprobat/respins
@loans_bp.route('/request/<int:request_id>/respond', methods=['PUT'])
@jwt_required()
def respond_to_request(request_id):
    try:
        data = loan_response_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
        
    current_user_id = int(get_jwt_identity())
    loan_request = LoanRequest.query.get_or_404(request_id)
    
    if loan_request.book.user_id != current_user_id:
        return jsonify({"error": "Nu ai permisiunea de a aproba/respinge cereri pentru această carte"}), 403    
    if loan_request.status != "In asteptare":
        return jsonify({"error": "S-a răspuns deja la această cerere de împrumut."}), 400

    decision = data['status']
    loan_request.status = decision
    
    if decision == "Aprobat":
        loan_request.book.availability = "Imprumutata"
        
        new_loan = Loan(
            book_id=loan_request.book_id,        
            borrower_id=loan_request.borrower_id,  
            status="activ"                       
        )
        db.session.add(new_loan)
        db.session.add(new_loan)
        
        #respingere automata a altor cereri pentru aceeasi carte daca a fost aprobat una
        other_requests = LoanRequest.query.filter(
            LoanRequest.book_id == loan_request.book_id,
            LoanRequest.id != request_id,
            LoanRequest.status == "In asteptare" ).all()
        for req in other_requests:
            req.status = "Respins"

    db.session.commit()
    
    return jsonify({
        "message": f"Cererea a fost {decision} cu succes",
        "request": loan_request_schema.dump(loan_request)
    }), 200

#finalizarea unui imprimut-cartea a fost returnata
@loans_bp.route('/return/<int:loan_id>', methods=['POST'])
@jwt_required()
def return_book(loan_id):
    current_user_id = int(get_jwt_identity())
    loan = Loan.query.get_or_404(loan_id)
    book = Book.query.get(loan.book_id)
    
    
    if loan.borrower_id != current_user_id:
        return jsonify({"error": "Doar persoana care a împrumutat cartea o poate returna."}), 403
        
    if loan.status != "activ":
        return jsonify({"error": "Acest împrumut este deja finalizat sau inactiv."}), 400
        
    loan.status = "Completed"
    loan.return_date = datetime.datetime.utcnow()
    if book:
        book.availability = "Disponibila" 
    
    db.session.commit()
    
    return jsonify({
        "message": "Cartea a fost returnată cu succes proprietarului!",
        "loan_status": loan.status,
        "book_availability": book.availability if book else "Disponibila"
    }), 200


#afisare toate imprumuturile proprii
@loans_bp.route('/my-loans', methods=['GET'])
@jwt_required()
def get_my_loans():
    current_user_id = int(get_jwt_identity())
    loans = Loan.query.filter(Loan.borrower_id == current_user_id).all()
    
    result = []
    for loan in loans:
        book = Book.query.get(loan.book_id)
        owner = User.query.get(book.user_id) if book else None
        
        result.append({
            "id": loan.id,
            "book_title": book.title if book else "Carte Ștearsă",
            "book_author": book.author if book else "Necunoscut",
            "owner_id": book.user_id if book else None,
            "owner_name": owner.name if owner else "Anonim",
            "start_date": loan.loan_date,
            "end_date": loan.return_date,
            "status": loan.status 
        })
        
    return jsonify({"loans": result}), 200