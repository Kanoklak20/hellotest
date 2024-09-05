from flask_login import UserMixin
from app import db
from datetime import date
from sqlalchemy_serializer import SerializerMixin


class UserInfo(db.Model,UserMixin):
    __tablename__ = "userinfo"
    # primary keys are required by SQLAlchemy
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    firstname = db.Column(db.String(100))
    lastname = db.Column(db.String(100))
    phone_no = db.Column(db.String(10))
    birth = db.Column(db.Date)
    password = db.Column(db.String(100))
    username = db.Column(db.String(50))
    role=db.Column(db.String(10))

    def __init__(self, email, firstname, lastname, phone_no,birth, password,username,role):
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.phone_no = phone_no
        self.birth = birth
        self.password = password
        self.username = username
        self.role=role
    
    def update(self, email, firstname,lastname,phone_no,password):
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.phone_no = phone_no
        self.password = password
        
class Reservations(db.Model,SerializerMixin):
    __tablename__ = "reservation"
    
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('userinfo.id')) 
    table_id = db.Column(db.Integer,db.ForeignKey('tables.id'))
    date  = db.Column(db.Date)
    table = db.relationship("Tables",  backref="reservations")
    cus = db.relationship("UserInfo",  backref="reservations")
    def __init__(self,date,table_id,owner_id):
        self.table_id=table_id
        self.date = date
        self.owner_id=owner_id
    def to_dict(self, depth=1):
        reservation_dict = {
            'id': self.id,
            'date': self.date,
            'table_id': self.table.no,
            'firstname': self.cus.firstname,
            'lastname':self.cus.lastname,
            'phone':self.cus.phone_no
        }
        return reservation_dict

class Tables(db.Model, SerializerMixin):
    __tablename__ = "tables"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    no = db.Column(db.String(10))
    status = db.Column(db.Boolean)
    
    def __init__(self,no,date,status):
        self.no=no
        self.status=status
        self.date=date
