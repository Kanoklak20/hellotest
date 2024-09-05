from flask.cli import FlaskGroup
from werkzeug.security import generate_password_hash
from app import app, db
from app.models.authuser import UserInfo, Tables

cli = FlaskGroup(app)

@cli.command("create_db")
def create_db():
    db.drop_all()
    db.create_all()
    db.session.commit()

@cli.command("seed_db")
def seed_db():
    db.session.add(UserInfo(email="bar@gmail.com", firstname='somchaiii',lastname='songbad',phone_no='9999999999',birth='12-12-2525',
                            password=generate_password_hash('1234',method='sha256'),
                            username='somchai',role='customer'))
    
    db.session.add(UserInfo(email="bour@gmail.com", firstname='สมธร',lastname='ทรงแบด',phone_no='9999999999',birth='12-12-2525',
                            password=generate_password_hash('1111',
                                                 method='sha256'),username='somtorn',role='customer'))
    db.session.add(UserInfo(email="admin@admin.com", firstname='admin',lastname='admin',phone_no='9999999999',birth='12-12-2525',
                            password=generate_password_hash('admin',method='sha256'),
                            username='somchai',role='admin'))
    db.session.add(Tables(no='C4',date='2024-03-02',status=False))
    db.session.commit()  


if __name__ == "__main__":
    cli()