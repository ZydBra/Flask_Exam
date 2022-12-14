from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField
from wtforms.validators import DataRequired, EqualTo, ValidationError
from wtforms_sqlalchemy.fields import QuerySelectField
import main


class RegistravimosiForma(FlaskForm):
    vardas_pavarde = StringField('Full Name', validators=[DataRequired()])
    e_pastas = EmailField('Email', validators=[DataRequired()])
    slaptazodis_1 = PasswordField('Password', validators=[DataRequired()])
    slaptazodis_2 = PasswordField('Reapeat Password', validators=[DataRequired(), EqualTo('slaptazodis_1',
                                                                                          message='Passwords must be the same!')])
    def tikrinti_pasta(self, e_pastas):
        naudotojas = main.Naudotojas.query.filter_by(e_pastas=e_pastas.data).first()
        if naudotojas:
            raise ValidationError('This Email already registered!')


class PrisijungimoForma(FlaskForm):
    e_pastas = StringField('Email', validators=[DataRequired()])
    slaptazodis = PasswordField('Password', validators=[DataRequired()])


class SaskaitosIvedimoForma(FlaskForm):
    sask_suma = StringField('Amount, €', validators=[DataRequired()])
    aprasymas = StringField('Description', validators=[DataRequired()])


class GrupesPasirinkimoForma(FlaskForm):
    pasirinkta_grupe = QuerySelectField('Group Name', query_factory=main.Grupe.query.all,
                                        get_label='grupes_pavadinimas',
                                        get_pk=lambda obj: str(obj))
