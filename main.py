from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_bcrypt import Bcrypt
from flask_admin import Admin

app = Flask(__name__)
app.config['SECRET_KEY'] = "***code_academy_flask_exam***"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///my_database?check_same_thread=False'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# DB struktūra:

# Many-to-many pagalbinė lentelė
grupe_naudotojas = db.Table(
    'grupe_naudotojas', db.metadata,
    db.Column('naudotojo_id', db.Integer, db.ForeignKey('naudotojas.id')),
    db.Column('grupes_id', db.Integer, db.ForeignKey('grupe.id'))
)


class Grupe(db.Model):
    __tablename__ = 'grupe'
    id = db.Column(db.Integer, primary_key=True)
    grupes_pavadinimas = db.Column(db.String)
    naudotojai = db.relationship('Naudotojas', secondary=grupe_naudotojas, back_populates='grupes')


class Naudotojas(db.Model, UserMixin):
    __tablename__ = 'naudotojas'
    id = db.Column(db.Integer, primary_key=True)
    vardas_pavarde = db.Column(db.String, nullable=False)
    e_pastas = db.Column(db.String, unique=True, nullable=False)
    slaptazodis = db.Column(db.String, nullable=False)
    grupes = db.relationship('Grupe', secondary=grupe_naudotojas, back_populates='naudotojai')


class Saskaita(db.Model):
    __tablename__ = 'saskaita'
    id = db.Column(db.Integer, primary_key=True)
    aprasymas = db.Column(db.String, nullable=False)
    sask_suma = db.Column(db.Integer, unique=True, nullable=False)
    grupes_id = db.Column(db.String, db.ForeignKey('grupe.id'))
    grupe = db.relationship("Grupe", lazy=True)

# DB pabaiga

with app.app_context():

    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, port=5010)
