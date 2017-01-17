#!flask/bin/python
import json

import bcrypt
import re
from bson.int64 import long

from flask import make_response
from werkzeug.utils import redirect

from app import app, mongo
from app.forms import RegistrationForm, LoginForm, PatientForm, ContactForm
from config import config
from flask import url_for, session, render_template, request, flash, abort
from formbuilder import formLoader
from datetime import datetime
import json
from bson import ObjectId, json_util


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
                            if 'admin' in user:
                                session['global_admin'] = email
                                session['current_user_name'] = user['fullname']
                                return redirect(url_for('admin'))
                            session['global_user'] = email
                            session['current_user_name'] = user['fullname']
                            return redirect(url_for('index'))
                        else:
                            return render_template('landingPage.html', loginform=loginform,
                                                   error="Email ve ya Şifre Hatali")
                    else:
                        return render_template('landingPage.html', loginform=loginform,
                                               error="Email ve ya Şifre Hatali")
                else:
                    return render_template("landingPage.html", loginform=loginform,
                                           error="Lutfen Alanlara uygun parametreler girin")

        elif request.method == 'GET':
            if 'error_from_register' in session:
                error = session['error_from_register']
                clearTheSession()
                return render_template('landingPage.html', loginform=loginform, error=error)
            if 'error_from_logout' in session:
                error = session['error_from_logout']
                clearTheSession()
                return render_template('landingPage.html', loginform=loginform, error=error)
            return render_template('landingPage.html', loginform=loginform)

    elif 'global_admin' in session:
        return redirect(url_for('admin'))
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
                    {'TcKimlikNo': long(registerform.tckimlikno.data)})
                existing_user_with_tckimlik_doctors = mongo.db.doctors.find_one(
                    {'TcKimlikNo': long(registerform.tckimlikno.data)})
                if existing_user_with_email is None and existing_user_with_tckimlik is None and existing_user_with_email_doctors is None and existing_user_with_tckimlik_doctors is None:
                    hashpass = bcrypt.hashpw(registerform.password.data.encode('utf-8'), bcrypt.gensalt())
                    date = str(registerform.birthday.data)
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
                    session[
                        'error_from_register'] = "Kaydınız Bize ulaşmıştir Kaydınız Onaylandıktan sonra giriş yapabileceksiniz "
                    return redirect(url_for("landingPage")),
                else:
                    return render_template("register.html", registerform=registerform,
                                           error="Bu Tc kimlik numarasi ve ya email ile zaten kayıt olunmuş")
            else:
                return render_template("register.html", registerform=registerform,
                                       error="Bazı Alanlarda Hata bulunmaktadir")
        elif request.method == 'GET':
            return render_template('register.html', registerform=registerform)
    else:
        abort(403)


@app.route('/index', methods=['GET', 'POST'])
def index():
    if checkSession():
        if 'global_admin' in session:
            return redirect("admin")
        if 'global_user' in session:
            user = mongo.db.doctors.find_one({"email": session["global_user"]})
            doctorspatients = user["patients"]
            patients = []
            for p in doctorspatients:
                patients.append({"patient": mongo.db.patients.find_one({"_id": ObjectId(p)})})
            return render_template("index.html", user=user, patients=patients,
                                   currentUserName=session['current_user_name'])
    else:
        abort(403)


@app.route('/inbox', methods=['GET', 'POST'])
def inbox():
    if checkSession():
        if 'global_admin' in session:
            messages = mongo.db.messages.find()
            return render_template("inbox.html", messages=messages, admin='admin',
                                   currentUserName=session['current_user_name'])
        else:
            return redirect(url_for('index'))
    else:
        abort(403)


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if checkSession():
        if 'global_admin' in session:
            user = mongo.db.doctors.find_one({"email": session['global_admin']})
            return render_template("profile.html", pagename="Profil", admin="admin",
                                   currentUserName=session['current_user_name'], doctor=user)
        user = mongo.db.doctors.find_one({"email": session['global_user']})
        return render_template("profile.html", pagename="Profil", currentUserName=session['current_user_name'],
                               doctor=user)
    else:
        abort(403)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if checkSession():
        if 'global_admin' in session:
            return redirect(url_for("admin"))
        form = ContactForm(request.form)
        if request.method == 'POST':
            if form.validate():
                konu = form.konu.data
                mesaj = form.message.data
                mongo.db.messages.insert_one({"senderemail": session['global_user'],
                                              "konu": konu,
                                              "message": mesaj})
                return render_template("contact.html", form=form, currentUserName=session['current_user_name'],
                                       admin="admin", error="Mesaj Başari ile gonderildi")
            else:
                return render_template("contact.html", form=form, currentUserName=session['current_user_name'],
                                       admin="admin", error="Lutfen Tum Alanları Doldurun")
        return render_template("contact.html", form=form, currentUserName=session['current_user_name'])
    else:
        abort(403)


@app.route("/admin", methods=['GET', 'POST'])
def admin():
    if 'global_admin' in session:
        allDoctors = mongo.db.doctors.find()
        user = mongo.db.doctors.find_one({"email": session['global_admin']})
        allpatients = mongo.db.patients.find()
        return render_template("admin.html", doctors=allDoctors, patients=allpatients, user=user,
                               currentUserName=session['current_user_name'], pagename="Anasayfa")
    else:
        abort(403)


@app.route('/createform', methods=['POST', 'GET'])
def createform():
    if checkSession():
        session["create_form_purpose"] = "createform"
        if 'global_admin' in session:
            return render_template('createform.html', base_url=config['base_url'], admin='admin',
                                   currentUserName=session['current_user_name'], pagename="Form Şablonu Yarat")
        return render_template('createform.html', base_url=config['base_url'],
                               currentUserName=session['current_user_name'], pagename="Form Şablonu Yarat")
    else:
        abort(403)


@app.route('/createpatient', methods=['GET', 'POST'])
def createpatient():
    if checkSession():
        patientform = PatientForm(request.form)
        if request.method == 'POST':
            if request.form['submit'] == 'Hasta Kaydet':
                if patientform.validate():
                    tckno = patientform.tckimlikno.data
                    tckno = long(tckno)
                    existingPatient = mongo.db.patients.find_one({'tckimlikno': tckno})
                    if existingPatient is None:
                        date = str(patientform.birthday.data)
                        year, month, day = date.split('-')
                        mongo.db.patients.insert_one({"email": patientform.email.data,
                                                      "fullname": patientform.fullname.data,
                                                      "tckimlikno": patientform.tckimlikno.data,
                                                      "birthday": datetime(int(year), int(month), int(day)),
                                                      "registerDate": datetime.now(),
                                                      "phone": patientform.phone.data})
                        if 'global_admin' in session:
                            return render_template("createpatient.html", error="Hasta başarıyla kaydedildi",
                                                   form=patientform, admin='admin',
                                                   currentUserName=session['current_user_name'],
                                                   pagename="Yeni Hasta Yarat", )
                        return render_template("createpatient.html", error="Hasta başarıyla kaydedildi",
                                               pagename="Yeni Hasta Yarat",
                                               form=patientform, currentUserName=session['current_user_name'])
                    elif 'global_admin' in session:
                        return render_template("createpatient.html", error="Aynı TC Kimlik no ile hasta kayıtlı",
                                               form=patientform, admin='admin', pagename="Yeni Hasta Yarat",
                                               currentUserName=session['current_user_name'])
                    return render_template("createpatient.html", error="Aynı TC Kimlik no ile hasta kayıtlı",
                                           pagename="Yeni Hasta Yarat",
                                           form=patientform, currentUserName=session['current_user_name'])

                elif 'global_admin' in session:
                    return render_template("createpatient.html", error="Lütfen alanları doğru şekilde doldurun",
                                           pagename="Yeni Hasta Yarat",
                                           form=patientform, admin='admin',
                                           currentUserName=session['current_user_name'])
                return render_template("createpatient.html", error="Lütfen alanları doğru şekilde doldurun",
                                       pagename="Yeni Hasta Yarat",
                                       form=patientform, currentUserName=session['current_user_name'])
        elif 'global_admin' in session:
            return render_template("createpatient.html", form=patientform, admin='admin', pagename="Yeni Hasta Yarat",
                                   currentUserName=session['current_user_name'])
        return render_template("createpatient.html", form=patientform, currentUserName=session['current_user_name'],
                               pagename="Yeni Hasta Yarat")
    return redirect(url_for("landingPage"))


@app.route("/insertrecord", methods=['GET', 'POST'])
def insertrecord():
    if checkSession():
        forms = mongo.db.form_templates.find()
        if 'onayla' in request.form:
            title = request.form["onayla"]
            tckimlik = request.form["tckimlik"]
            patient = mongo.db.patients.find_one({"tckimlikno": long(tckimlik)})
            if patient is None:
                if 'global_admin' in session:
                    return render_template("insertrecord.html", forms=forms, admin='admin',
                                           error="Boyle biri yok uydurma", currentUserName=session['current_user_name'])
                return render_template("insertrecord.html", forms=forms, error="Boyle biri yok uydurma",
                                       currentUserName=session['current_user_name'])
            else:
                session["purpose_from_insert"] = "insertrecord"
                session["patient_from_insert"] = tckimlik
                session["form_template_from_insert"] = title
                return redirect(url_for('render'))
        if 'global_admin' in session:
            return render_template("insertrecord.html", forms=forms, admin='admin',
                                   currentUserName=session['current_user_name'])
        return render_template("insertrecord.html", forms=forms, currentUserName=session['current_user_name'])
    else:
        abort(403)


@app.route("/detailedsearch", methods=['GET', 'POST'])
def detailedsearch():
    if checkSession():
        patients = mongo.db.patients.find()
        if 'detay' in request.form:
            session["patient_details_from_detailed_search"] = request.form["detay"]
            return redirect(url_for("patientdetails"))
        if 'global_admin' in session:
            return render_template("detailedsearch.html", patients=patients, admin="admin",
                                   pagename="Hastalarda Arama Yapın",
                                   currentUserName=session['current_user_name'])
        return render_template("detailedsearch.html", patients=patients, pagename="Hastalarda Arama yapın",
                               currentUserName=session['current_user_name'])
    else:
        abort(403)


@app.route("/patientdetails", methods=['POST', 'GET'])
def patientdetails():
    if checkSession():
        if 'patient_details_from_detailed_search' in session:
            tckimlik = session['patient_details_from_detailed_search']
            patient = mongo.db.patients.find_one({"tckimlikno": long(tckimlik)})
            patientforms = []
            patientsdata = []
            if 'forms' in patient:
                forms = patient['forms']
                for data in forms:
                    patientforms.append(mongo.db.forms.find_one({"_id": ObjectId(data)}))
                for data in patientforms:
                    formdata = correctFormData(json.loads(data['formdata']))
                    patientsdata.append(
                        {"form_template": mongo.db.form_templates.find_one({"_id": ObjectId(data["form_template"])}),
                         "doctor": mongo.db.doctors.find_one({"_id": ObjectId(data['doctor'])}),
                         "form_data": formdata,
                         "id": str(data["_id"])})
            if 'Detay' in request.form:
                session["see_patient_details_from_patient_details_patient_id"] = request.form['Detay']
                return redirect(url_for('result'))
            if 'global_admin' in session:
                return render_template("patientdetails.html", patient=patient, patientsdata=patientsdata, admin="admin",
                                       pagename="Hasta Detayları", currentUserName=session['current_user_name'])
            return render_template("patientdetails.html", patient=patient, patientsdata=patientsdata,
                                   pagename="Hasta Detayları", currentUserName=session['current_user_name'])
    else:
        abort(403)


@app.route("/approvedoctor", methods=['GET', 'POST'])
def approvedoctor():
    if 'global_admin' in session:
        unapporevedDoctors = mongo.db.unauthorizedDoctors.find()
        if 'onayla' in request.form:
            email = request.form["onayla"]
            doctor = mongo.db.unauthorizedDoctors.find_one({'email': email})
            mongo.db.doctors.insert(doctor)
            mongo.db.unauthorizedDoctors.remove({'email': email})
        elif 'reddet' in request.form:
            email = request.form["reddet"]
            mongo.db.unauthorizedDoctors.remove({'email': email})
        return render_template("approvedoctor.html", undoctor=unapporevedDoctors,
                               pagename="Kaydolmak İsteyen Doktorlar",
                               currentUserName=session['current_user_name'])
    else:
        abort(403)


@app.route("/approveform", methods=['GET', 'POST'])
def approveform():
    if 'global_admin' in session:
        unapporevedForms = mongo.db.unauthorizedFormTemplates.find()
        if 'onizleme' in request.form:
            title = request.form["onizleme"]
            session["onizleme_form_approve_form"] = "onizleme"
            session['onizleme_form_template_title'] = title
            return redirect(url_for("render"))
        if 'onayla' in request.form:
            title = request.form["onayla"]
            form = mongo.db.unauthorizedFormTemplates.find_one({'title': title})
            mongo.db.form_templates.insert(form)
            mongo.db.unauthorizedFormTemplates.remove({'title': title})
        elif 'reddet' in request.form:
            title = request.form["reddet"]
            mongo.db.unauthorizedFormTemplates.remove({'title': title})
        return render_template("approveform.html", pagename="Onay Bekleyen Form Şablonları", forms=unapporevedForms,
                               currentUserName=session['current_user_name'])
    else:
        abort(403)


@app.route('/result', methods=['GET'])
def result():
    if 'inserted_form_id_from_submit' in session:
        form_template = mongo.db.form_templates.find_one({"title": session["form_template_from_insert"]})
        patient = mongo.db.patients.find_one({"tckimlikno": long(session["patient_from_insert"])})
        if 'global_user' in session:
            user = mongo.db.doctors.find_one({"email": session["global_user"]})
        if 'global_admin' in session:
            user = mongo.db.doctors.find_one({"email": session["global_admin"]})
        form = mongo.db.forms.find_one({'_id': ObjectId(session['inserted_form_id_from_submit'])})
        form_data = form['formdata']
        formDict = correctFormData(json.loads(form_data))
        clearTheSession()
        if 'global_admin' in session:
            return render_template("result.html", form_template=form_template, patient=patient, doctor=user,
                                   pagename="Hasta Kayıt Formu",
                                   form_data=formDict, admin='admin', currentUserName=session['current_user_name'])
        return render_template("result.html", form_template=form_template, patient=patient, doctor=user,
                               pagename="Hasta Kayıt Formu",
                               form_data=formDict, currentUserName=session['current_user_name'])
    if 'see_patient_details_from_render_form_id' in session:
        requestedform = mongo.db.forms.find_one({"_id": ObjectId(session["see_patient_details_from_render_form_id"])})
        form_template = mongo.db.form_templates.find_one({"_id": ObjectId(requestedform["form_template"])})
        patient = mongo.db.patients.find_one({"_id": ObjectId(requestedform["patient"])})
        user = mongo.db.doctors.find_one({"_id": ObjectId(requestedform["doctor"])})
        form_data = requestedform['formdata']
        form_dict = correctFormData(json.loads(form_data))
        clearTheSession()
        if 'global_admin' in session:
            return render_template("result.html", form_template=form_template, patient=patient, doctor=user,
                                   pagename="Hasta Kayıt Formu",
                                   form_data=form_dict, admin='admin', currentUserName=session['current_user_name'])
        return render_template("result.html", form_template=form_template, patient=patient, doctor=user,
                               pagename="Hasta Kayıt Formu",
                               form_data=form_dict, currentUserName=session['current_user_name'])
    if 'see_patient_details_from_patient_details_patient_id' in session:
        requestedform = mongo.db.forms.find_one(
            {"_id": ObjectId(session["see_patient_details_from_patient_details_patient_id"])})
        form_template = mongo.db.form_templates.find_one({"_id": ObjectId(requestedform["form_template"])})
        patient = mongo.db.patients.find_one({"_id": ObjectId(requestedform["patient"])})
        user = mongo.db.doctors.find_one({"_id": ObjectId(requestedform["doctor"])})
        form_data = requestedform['formdata']
        form_dict = correctFormData(json.loads(form_data))
        clearTheSession()
        session['patient_details_from_detailed_search'] = patient['tckimlikno']
        if 'global_admin' in session:
            return render_template("result.html", form_template=form_template, patient=patient, doctor=user,
                                   pagename="Hasta Kayıt Formu",
                                   form_data=form_dict, admin='admin', currentUserName=session['current_user_name'])
        return render_template("result.html", form_template=form_template, patient=patient, doctor=user,
                               pagename="Hasta Kayıt Formu",
                               form_data=form_dict, currentUserName=session['current_user_name'])


@app.route('/save', methods=['POST'])
def save():
    if checkSession():
        if request.method == 'POST':
            formData = request.form.get('formData')

            if formData == 'None':
                return 'Error processing request'
            jsonString = json.loads(formData)
            existingFormTemplate = mongo.db.form_templates.find_one({'title': jsonString['title']})
            unAuothorizedexistingFormTemplate = mongo.db.unauthorizedFormTemplates.find_one(
                {'title': jsonString['title']})
            if existingFormTemplate is None and unAuothorizedexistingFormTemplate is None:
                mongo.db.unauthorizedFormTemplates.insert_one(jsonString)
                session['form_data'] = formData
            else:
                return redirect(url_for('createform'))
            return 'tes'
    else:
        abort(403)


@app.route('/render', methods=['POST', 'GET'])
def render():
    if checkSession():
        if 'purpose_from_insert' in session:
            form = mongo.db.form_templates.find_one({'title': session['form_template_from_insert']})
            patient = mongo.db.patients.find_one({"tckimlikno": long(session["patient_from_insert"])})
            form_loader = formLoader(json_util.dumps(form, ensure_ascii=False),
                                     '{0}/submit'.format(config['base_url']))
            render_form = form_loader.render_form()
            patientforms = []
            patientsdata = []
            if 'forms' in patient:
                for pforms in patient['forms']:
                    patientforms.append(mongo.db.forms.find_one({"_id": ObjectId(pforms)}))
            for tmp in patientforms:
                patientsdata.append({"doctor": mongo.db.doctors.find_one({"_id": ObjectId(tmp["doctor"])}),
                                     "form_template": mongo.db.form_templates.find_one(
                                         {"_id": ObjectId(tmp["form_template"])}),
                                     "id": tmp["_id"]})
            if 'detayligor' in request.form:
                session["see_patient_details_from_render_form_id"] = request.form['detayligor']
                return redirect(url_for('result'))
            if 'global_admin' in session:
                return render_template("render.html", pagename="Yeni Kayıt Ekle", admin='admin',
                                       patientsdata=patientsdata, patient=patient,
                                       render_form=render_form, currentUserName=session['current_user_name'])
            return render_template("render.html", pagename="Yeni Kayıt Ekle", patientsdata=patientsdata,
                                   patient=patient, render_form=render_form,
                                   currentUserName=session['current_user_name'])
        if 'onizleme_form_approve_form' in session:
            title = session['onizleme_form_template_title']
            form = mongo.db.unauthorizedFormTemplates.find_one({'title': title})
            form_loader = formLoader(json_util.dumps(form, ensure_ascii=False),
                                     '{0}/submit'.format(config['base_url']))
            render_form = form_loader.render_form()
            if 'global_admin' in session:
                return render_template('render.html', admin="admin", pagename="Onizleme", render_form=render_form,
                                       currentUserName=session['current_user_name'])
            return render_template('render.html', pagename="Onizleme", render_form=render_form,
                                   currentUserName=session['current_user_name'])
        if 'form_data' not in session:
            return redirect(url_for('createform'))
        form_data = session['form_data']
        form_loader = formLoader(form_data, '{0}/submit'.format(config['base_url']))
        render_form = form_loader.render_form()
        if 'global_admin' in session:
            return render_template('render.html', admin="admin", pagename="Onizleme", render_form=render_form,
                                   currentUserName=session['current_user_name'])
        return render_template('render.html', pagename="Onizleme", render_form=render_form,
                               currentUserName=session['current_user_name'])
    else:
        abort(403)


@app.route('/submit', methods=['POST'])
def submit():
    if checkSession():
        if request.method == 'POST':
            form = json_util.dumps(request.form, ensure_ascii=False)
            if 'purpose_from_insert' in session:
                form_template = mongo.db.form_templates.find_one({"title": session["form_template_from_insert"]})
                patient = mongo.db.patients.find_one({"tckimlikno": long(session["patient_from_insert"])})
                if 'global_user' in session:
                    user = mongo.db.doctors.find_one({"email": session["global_user"]})
                if 'global_admin' in session:
                    user = mongo.db.doctors.find_one({"email": session["global_admin"]})
                insertedformid = mongo.db.forms.insert_one(
                    {"form_template": form_template['_id'], "formdata": form, "patient": patient['_id'],
                     "doctor": user["_id"], "registertime": datetime.now()}).inserted_id
                session['inserted_form_id_from_submit'] = str(insertedformid)
                if "patients" in user:
                    doctorsPatients = user['patients']
                    if patient["_id"] not in doctorsPatients:
                        mongo.db.doctors.update({"email": user["email"]}, {"$push": {"patients": patient["_id"]}},
                                                upsert=False)
                else:
                    mongo.db.doctors.update({"email": user["email"]}, {"$set": {"patients": [patient["_id"]]}},
                                            upsert=False)
                if "forms" in patient:
                    mongo.db.patients.update({"tckimlikno": long(patient["tckimlikno"])},
                                             {"$push": {"forms": insertedformid}})
                else:
                    mongo.db.patients.update({"tckimlikno": long(patient["tckimlikno"])},
                                             {"$set": {"forms": [insertedformid]}})
                return redirect(url_for("result"))
            elif 'onizleme_form_approve_form' in session:
                clearTheSession()
                if 'global_admin' in session:
                    return redirect(url_for("approveform"))
                return redirect(url_for("index"))
            elif "create_form_purpose" in session:
                clearTheSession()
                return redirect(url_for('createform'))
            else:
                if 'global_admin' in session:
                    return redirect('admin')
                return render_template('index.html')
    else:
        abort(403)


def checkSession():
    if 'global_user' in session or 'global_admin' in session:
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


@app.route("/logout")
def logout():
    if checkSession():
        session.clear()
        session["error_from_logout"] = "Basari ile Çıkış Yaptınız"
        return redirect('landingPage')
    else:
        abort(403)


def correctFormData(form_data):
    correctForm = []
    for k in form_data:
        correctForm.append({'title': k, 'value': form_data[k]})

    return correctForm


def clearTheSession():
    if 'global_admin' in session:
        tmpemail = session['global_admin']
        tmpname = session['current_user_name']
        session.clear()
        session['global_admin'] = tmpemail
        session['current_user_name'] = tmpname
    elif 'global_user' in session:
        tmpemail = session['global_user']
        tmpname = session['current_user_name']
        session.clear()
        session['global_user'] = tmpemail
        session['current_user_name'] = tmpusername
