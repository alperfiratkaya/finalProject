from flask_wtf import FlaskForm
from wtforms import StringField, validators, PasswordField, BooleanField, SubmitField, IntegerField,TextField
from flask_admin.form import widgets
from wtforms.fields.html5 import DateField
from wtforms import ValidationError
import phonenumbers
from wtforms.widgets import TextArea


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
    submit = SubmitField("Kayıt Ol")


class PatientForm(FlaskForm):
    fullname = StringField('Hasta Adı Soyadı', [validators.DataRequired(message='Bu alanı Boş bırakamazsiniz')])
    tckimlikno = IntegerField('Tc kimlik No', [
        validators.NumberRange(min=10000000000, max=1000000000000, message="Lutfen Tc kimlik No'nuzu giriniz")])
    email = StringField('Email Adresi')
    phone = StringField('Phone', [validators.DataRequired()])
    birthday = DateField('Doğum Tarihiniz', [validators.DataRequired('Lutfen Doğru formatta tarihi girin Ay/Gun/Yıl')])
    submit = SubmitField("Hasta Kaydet")

    def validate_phone(form, field):
        if len(field.data) > 16:
            raise ValidationError('Geçersiz telefon numarası.')
        try:
            input_number = phonenumbers.parse(field.data)
            if not (phonenumbers.is_valid_number(input_number)):
                raise ValidationError('Geçersiz telefon numarası.')
        except:
            input_number = phonenumbers.parse("+90" + field.data)
            if not (phonenumbers.is_valid_number(input_number)):
                raise ValidationError('Geçersiz telefon numarası.')

class ContactForm(FlaskForm):
    konu = StringField('Mesajın Konusu', [validators.DataRequired(message='Bu alanı Boş bırakamazsiniz')])
    message = StringField(u'Mesajınızı Buraya Yazın', [validators.DataRequired(message='Bu alanı Boş bırakamazsiniz')],widget=TextArea())
    submit = SubmitField("Gonder")