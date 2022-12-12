from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask_bcrypt import Bcrypt
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

app = Flask(__name__)
app.config['SECRET_KEY'] = "***code_academy_flask_exam***"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///my_database?check_same_thread=False'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

bcrypt = Bcrypt(app)
admin = Admin(app, name='Flask Admin')

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
# Admin puslapis
admin.add_view(ModelView(Saskaita, db.session))
admin.add_view(ModelView(Grupe, db.session))
admin.add_view(ModelView(Naudotojas, db.session))


@login_manager.user_loader
def uzkrauti_naudotoja(e_pastas):
    return Naudotojas.query.get(e_pastas)


with app.app_context():
    db.create_all()


# Programos maršrutai:
@app.route('/')
def index():
    return redirect(url_for('prisijungti'))


@app.route('/register', methods=['GET', 'POST'])
def registruotis():
    forma = forms.RegistravimosiForma()
    if forma.validate_on_submit():
        koduotas_slaptazodis = bcrypt.generate_password_hash(forma.slaptazodis_1.data).decode('utf-8')
        naudotojas = Naudotojas(
            vardas_pavarde=forma.vardas_pavarde.data,
            e_pastas=forma.e_pastas.data,
            slaptazodis=koduotas_slaptazodis
        )
        db.session.add(naudotojas)
        db.session.commit()
        flash(f'Registration succeeded, {naudotojas.vardas_pavarde}, now you can sign in.', 'success')
        return redirect(url_for('index'))
    return render_template('register.html', form=forma)


@app.route('/login', methods=['GET', 'POST'])
def prisijungti():
    forma = forms.PrisijungimoForma()
    if forma.validate_on_submit():
        naudotojas = Naudotojas.query.filter_by(e_pastas=forma.e_pastas.data).first()
        if not naudotojas:
            flash(f'User with email {forma.e_pastas.data} does not exist!', 'danger')
            return redirect(url_for('prisijungti'))
        if not bcrypt.check_password_hash(naudotojas.slaptazodis, forma.slaptazodis.data):
            flash(f'User with email {forma.e_pastas.data} password do not match!', 'danger')
            return redirect(url_for('prisijungti'))
        login_user(naudotojas)
        flash(f'Welcome, {naudotojas.vardas_pavarde}!', 'success')
        return redirect(request.args.get('next') or url_for('atvaizduoti_grupes'))
    return render_template('login.html', form=forma)


@app.route('/logout')
def atsijungti():
    flash(f'See you next time, {current_user.vardas_pavarde}!', 'success')
    logout_user()
    return redirect(url_for('prisijungti'))


@app.route('/groups')
@login_required
def atvaizduoti_grupes():
    try:
        visos_grupes = Grupe.query.filter(Grupe.naudotojai.any(Naudotojas.id == current_user.id)).all()
    except:
        visos_grupes = []
    print(visos_grupes)
    return render_template('groups.html', visos_grupes=visos_grupes)


@app.route('/bills/<grupes_id>', methods=['GET', 'POST'])
@login_required
def ivesti_saskaita(grupes_id):
    forma = forms.SaskaitosIvedimoForma()
    # forma.query = Grupe.query.filter_by(id=current_user.id)
    if forma.validate_on_submit():
        saskaita = Saskaita(sask_suma=forma.sask_suma.data, aprasymas=forma.aprasymas.data, grupes_id=grupes_id)
        db.session.add(saskaita)
        db.session.commit()
        flash(f'Invoice ID: {saskaita.id} added.', 'success')
        return redirect(url_for('ivesti_saskaita', grupes_id=grupes_id))
    return render_template('bills.html', form=forma)


@app.route('/show_bills/<grupes_id>', methods=['GET', 'POST'])
@login_required
def rodyti_grupes_saskaitas(grupes_id):
    try:
        grupes_saskaitos = Saskaita.query.filter_by(grupes_id=grupes_id).all()
    except:
        grupes_saskaitos = []
    print(grupes_saskaitos)
    return render_template("show_bills.html", grupes_saskaitos=grupes_saskaitos, grupes_id=grupes_id)


if __name__ == '__main__':
    app.run(debug=True, port=5010)
