from flask_wtf import FlaskForm
from wtforms import  StringField, validators, PasswordField, BooleanField, SubmitField, IntegerField
from flask_admin.form import widgets
from wtforms.fields.html5 import DateField

class LoginForm(FlaskForm):
    email = StringField("Email Field", [validators.DataRequired(message="Email Alanını Boş Bırakamazsınız"),
                                        validators.Email(message="Geçerli Bir Email Adresi Giriniz")])
    password = PasswordField("Password Field", [validators.DataRequired(message="Şifre Alanını Boş Bırakamazsınız")])
    submit = SubmitField("Giriş Yap")


class RegistrationForm(FlaskForm):
    email = StringField('Email Adresi', [validators.Email(message="Geçerli Bir Email Adresi Giriniz")])
    fullname = StringField('Adınız ve Soyadınız', [validators.DataRequired(message="Bu alanı Boş bırakamazsiniz")])
    tckimlikno = IntegerField('Tc kimlik No', [
        validators.NumberRange(min=10000000000, max=1000000000000, message="Lutfen Tc kimlik No'nuzu giriniz")])
    hospital = StringField('Çaliştiğiniz Hastahane', [validators.DataRequired(message="Bu alanı Boş bırakamazsiniz")])
    city = StringField('Yaşadığınız Şehir', [validators.DataRequired(message="Bu alanı Boş bırakamazsiniz")])
    birthday = DateField('Doğum Tarihiniz', [validators.DataRequired('Lutfen Doğru formatta tarihi girin Ay/Gun/Yıl')])
    password = PasswordField('Şifreniz', [
        validators.Length(min=6, max=35, message="Şifrede En az 6 en Fazla 35 karakter kullanmalisiniz"),
        validators.EqualTo('confirm', message='Şifreler eşleşmeli')
    ])
    confirm = PasswordField('Şifre Tekrar')
    accept_tos = BooleanField('Sozleşmeyi Okudum ve Kabul ediyorum',
                              [validators.DataRequired(message="Kaydolmak istiyorsaniz Sozleşmeyi Kabul etmelisiniz")])
    submit = SubmitField("Giriş Yap")
