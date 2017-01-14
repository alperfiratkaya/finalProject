#!flask/bin/python
import json

import bcrypt
from werkzeug.utils import redirect

from app import app, mongo
from app.forms import RegistrationForm, LoginForm
from config import config
from flask import url_for, session, render_template, request, flash, abort
from formbuilder import formLoader
from datetime import datetime


@app.route('/index', methods=['GET', 'POST'])
def index():
    if 'username' in session:
        user = mongo.db.doctors.find_one({"email": session["username"]})
        session["user"] = user
        forms = mongo.db.form_templates.find()
        return render_template("index.html", user=user, forms=forms)
    abort(403)


@app.route('/', methods=['GET', 'POST'])
@app.route('/landingPage', methods=['GET', 'POST'])
def landingPage():
    if not checkSession():
        loginform = LoginForm(request.form)
        if request.method == 'POST':
            if request.form['submit'] == 'Giriş Yap':
                if loginform.validate():
                    email = loginform.email.data
                    password = loginform.password.data
                    user = mongo.db.doctors.find_one({"email": email})
                    if user is not None:
                        if bcrypt.hashpw(password.encode('utf-8'), user['password']) == user['password']:
                            session['username'] = email
                            if user['admin'] is not None:
                                session['admin'] = email
                                return render_template("admin.html")
                            return redirect(url_for('index'))
                        else:
                            return render_template('landingPage.html', loginform=loginform,
                                                   error="Email ve ya Şifre Hatali")
                else:
                    return render_template("landingPage.html", loginform=loginform, error="Email ve ya Şifre Hatalı")

        elif request.method == 'GET':
            return render_template('landingPage.html', loginform=loginform)
    return redirect(url_for('index'))


@app.route("/register", methods=["GET", "POST"])
def register():
    registerform = RegistrationForm(request.form)
    if not checkSession():
        if request.method == "POST":
            if registerform.validate():
                existing_user_with_email = mongo.db.unauthorizedDoctors.find_one({'email': registerform.email.data})
                existing_user_with_email_doctors = mongo.db.doctors.find_one({'email': registerform.email.data})
                existing_user_with_tckimlik = mongo.db.unauthorizedDoctors.find_one(
                    {'TcKimlikNo': registerform.tckimlikno.data})
                existing_user_with_tckimlik_doctors = mongo.db.doctors.find_one(
                    {'TcKimlikNo': registerform.tckimlikno.data})
                if existing_user_with_email is None and existing_user_with_tckimlik is None and existing_user_with_email_doctors is None and existing_user_with_tckimlik_doctors is None:
                    hashpass = bcrypt.hashpw(registerform.password.data.encode('utf-8'), bcrypt.gensalt())
                    date = str(registerform.birthday.data)
                    print(date)
                    year, month, day = date.split('-')
                    mongo.db.unauthorizedDoctors.insert_one({"email": registerform.email.data,
                                                             "password": hashpass,
                                                             "fullname": registerform.fullname.data,
                                                             "tckimlikno": registerform.tckimlikno.data,
                                                             "birthday": datetime(int(year), int(month), int(day)),
                                                             "hospital": registerform.hospital.data,
                                                             "city": registerform.city.data,
                                                             "registerDate": datetime.now()}
                                                            )

                    return render_template("landingPage.html", loginform=LoginForm(request.form),
                                           kayit="Kayıt oldugunuz için teşekkürler kaydiniz onaylanınca sisteme giriş yapabileceksiniz")
                else:
                    return render_template("register.html", registerform=registerform,
                                           error="Bu Tc kimlik numarasi ve ya email ile zaten kayıt olunmuş")
            else:
                return render_template("register.html", registerform=registerform,
                                       error="Bazı Alanlarda Hata bulunmaktadir")
        return render_template('register.html', registerform=registerform)
    else:
        abort(403)


@app.route("/admin", methods=['GET', 'POST'])
def admin():
    if 'admin' in session:
        return render_template("admin.html")
    else:
        abort(403)


@app.route("/logout")
def logout():
    if checkSession():
        session.clear()
        return render_template('landingPage.html', loginform=LoginForm(request.form), error="Başari ile Çıkış Yaptınız")
    else:
        abort(403)

@app.route('/createform', methods=['POST'])
def createform():
    if checkSession():
        return render_template('createform.html', base_url=config['base_url'])
    else:
        abort(403)

@app.route('/save', methods=['POST'])
def save():
    if checkSession():
        if request.method == 'POST':
            formData = request.form.get('formData')

            if formData == 'None':
                return 'Error processing request'
            jsonString = json.loads(formData)
            print(jsonString)
            existingFormTemplate = mongo.db.form_templates.find_one({'title': jsonString['title']})
            if existingFormTemplate is None:
                mongo.db.form_templates.insert_one(jsonString)
                session['form_data'] = formData
            else:
                session.pop('form_data', None)
                return redirect(url_for('createform'))
            return 'tes'
    else:
        abort(403)

@app.route('/render')
def render():
    if checkSession():
        if 'form_data' not in session:
            return redirect(url_for('createform'))

        form_data = session['form_data']
        session['form_data'] = None

        form_loader = formLoader(form_data, '{0}/submit'.format(config['base_url']))
        render_form = form_loader.render_form()
        return render_template('render.html', render_form=render_form)
    else:
        abort(403)

@app.route('/submit', methods=['POST'])
def submit():
    if checkSession():
        if request.method == 'POST':
            form = json.dumps(request.form)

            return form
    else:
        abort(403)

def checkSession():
    if 'username' in session:
        return True
    else:
        return False


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template("internal_server_error.html"), 500


@app.errorhandler(405)
def method_not_allowed_error(e):
    return render_template("method_not_allowed_error.html"), 405


@app.errorhandler(403)
def forbidden(e):
    return render_template("forbidden.html"), 403
