from app import ma
from app.models import User
from app.models import Book
from marshmallow import fields, validate
from app.models import LoanRequest, Loan
from app.models import Review


class UserRegisterSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User

    name = fields.String(required=True, validate=validate.Length(min=3, max=200, error="Numele trebuie să aibă între 3 și 200 de caractere.")
                         ,error_messages={"required": "Numele este necesar pentru înregistrare"})
    email = fields.Email(required=True, error_messages={"invalid": "Adresa de email nu este validă." , "required": "Adresa de email este necesară pentru înregistrare"})
    password = fields.String(required=True, 
                             validate=[
                             validate.Length(min=6, error="Parola trebuie să aibă cel puțin 6 caractere."),
                             validate.Regexp(r'.*\d.*', error="Parola trebuie să conțină cel puțin o cifră."),
                             validate.Regexp(r'.*[A-Z].*', error="Parola trebuie să conțină cel puțin o literă mare.")
                             ],error_messages={"required": "Parola este necesară pentru înregistrare"})
    city = fields.String(required=True, validate=validate.Length(min=2, max=100, error="Orașul introdus nu este valid.")
                         ,error_messages={"required": "Orașul este necesar pentru înregistrare"})

class UserLoginSchema(ma.Schema):
    email = fields.Email(required=True, error_messages={"invalid": "Adresa de email nu este validă." , "required": "Adresa de email este necesară pentru autentificare"})
    password = fields.String(required=True,error_messages={"required": "Parola este necesară pentru autentificare"})

#instante ale schemelor pentru a fi folosite in rute
user_register_schema = UserRegisterSchema()
user_login_schema = UserLoginSchema()

class BookSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Book
        include_fk = True #pentru maparea cheilor externe

    id = fields.Int(dump_only=True) #daor se trimite nu se cere la input
    title = fields.String(
        required=True, 
        validate=validate.Length(min=3, max=200, error="Titlul cărții trebuie să aibă între 3 și 200 de caractere."),
        error_messages={"required": "Titlul cărții este obligatoriu"}
    )
    author = fields.String(
        required=True, 
        validate=validate.Length(min=3, max=200, error="Numele autorului trebuie să aibă între 3 și 200 de caractere."),
        error_messages={"required": "Numele autorului este obligatoriu"}
    )
    isbn = fields.String(required=False, allow_none=True)
    description = fields.String(required=False, allow_none=True)
    status = fields.String(
        required=False, 
        validate=validate.OneOf(["Noua", "Buna", "Uzata"], error="Statusul poate fi doar: Noua, Buna sau Uzata.")
    )
    availability = fields.String(
        required=False, 
        validate=validate.OneOf(["Disponibila", "Imprumutata"], error="Disponibilitatea poate fi doar: Disponibila sau Imprumutata.")
    )

    image_url = fields.String(required=False, allow_none=True)
    user_id = fields.Int(dump_only=True)
    city = fields.Function(
    lambda obj: User.query.get(obj.user_id).city if obj.user_id else "Nespecificat", 
    dump_only=True
)

#instante ale schemelor pentru a fi folosite in rute
book_schema = BookSchema()
books_schema = BookSchema(many=True)


class LoanRequestSchema(ma.SQLAlchemySchema):
    class Meta:
        model = LoanRequest
        include_fk = True

    id = fields.Int(dump_only=True)
    book_id = fields.Int(dump_only=True)
    requester_id = fields.Int(dump_only=True)
    status = fields.String(dump_only=True) 
    created_at = fields.DateTime(dump_only=True)

class LoanResponseSchema(ma.Schema):

    status = fields.String(required=True,validate=validate.OneOf(["Aprobat", "Respins"], error="Statusul de răspuns poate fi doar 'Aprobat' sau 'Respins'."))

loan_request_schema = LoanRequestSchema()
loan_requests_schema = LoanRequestSchema(many=True)
loan_response_schema = LoanResponseSchema()

class ReviewSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Review

    id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)
    rating = fields.Int(
        required=True,
        validate=validate.Range(min=1, max=5, error="Rating-ul trebuie să fie o notă între 1 și 5"),
        error_messages={"required": "Rating-ul este obligatoriu"})
    comment = fields.String(required=False, allow_none=True)
    created_at = fields.DateTime(dump_only=True)

review_schema = ReviewSchema()
reviews_schema = ReviewSchema(many=True)