from flask import  Flask,render_template,session,request,flash,url_for,redirect
from wtforms import Form,StringField,TextAreaField,PasswordField,validators,EmailField
import json
from functools import wraps
import os
import time
import threading
import sqlite3
import datetime
import sys
from pygame import mixer

sys.setrecursionlimit(4000)
mixer.init()


#Vestel_Venus_Simon_Zil_Sesi.mp3
app = Flask(__name__)
app.secret_key = "zilprogrami"

with open('config.json') as f:
  config = json.load(f)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("Bu sayfayı görüntülemek için giriş yapın","danger")
            return redirect(url_for("login"))
    return decorated_function

class login_form(Form):
    password = PasswordField("Şifre: ",validators=[validators.DataRequired(message="Lütfen Şifreyi Girin")])
ses = mixer
@app.route("/durdur")
@login_required
def durdur():
    try:
        os.system("taskkill /im wmplayer.exe")
        return redirect(url_for("dashboard"))
    except:
        return "zil Zaten Durmuş"

def zilcal(dosya_adi,süresi):
    os.system("{}".format(dosya_adi))
    time.sleep(süresi)
    try:
        os.system("taskkill /im wmplayer.exe")
    except:
        print("zil zaten durdu...")

@app.route("/")
def index():
    return render_template("index.html")
@app.route("/lock")
def lock():
    session.clear()
    flash("Kontrol Paneli Kilitlendi","success")
    return redirect(url_for("index"))
@app.route("/login",methods = ["POST","GET"])
def login():
    form = login_form(request.form)
    if request.method == "POST":
        gelensifre = form.password.data
        if gelensifre == config["sifre"]:
            session["logged_in"] = True
            flash("Giriş başarılı Kontrol Paneline Yönlendirildiniz....","success")
            return redirect(url_for("dashboard"))
        else:
            flash("Şifre Yanlış ", "warning")
            return redirect(url_for("login"))

    else:
        return render_template("login.html",form = form)


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

@app.route("/zil_cal_ogrenci_giris")
@login_required
def ogrenciziligiris():
    zilcal(config["zil_ogrenci_giris_adi"],int(config["zil_ogrenci_giris_toplam_uzunluk"]))
    flash("Öğrenci Giriş Zili Çaldı","success")
    return redirect(url_for("dashboard"))

@app.route("/zil_cal_ogrenci_cikis")
@login_required
def ogrencizilicikis():
    zilcal(config["zil_ogrenci_cikis_adi"],int(config["zil_ogrenci_cikis_adi_toplam_uzunluk"]))
    flash("Öğrenci Çıkış Zili Çaldı","success")
    return redirect(url_for("dashboard"))

@app.route("/zil_cal_ogretmen_giris")
@login_required
def ogretmenzil():
    zilcal(config["zil_ogretmen_giris_adi"],int(config["zil_ogretmen_giris_toplam_uzunluk"]))
    flash("Öğretmen Giriş Zili Çaldı","success")
    return  redirect(url_for("dashboard"))
#haftanın gününü bulma
def haftanin_gunu():
    gun_no  = datetime.datetime.now().weekday()
    if gun_no == 0:
        return "Pazartesi"
    elif gun_no == 1:
        return "Sali"
    elif gun_no == 2:
        return "Carsamba"
    elif gun_no == 3:
        return "Persembe"
    elif gun_no == 4:
        return "Cuma"
    elif gun_no == 5:
        return "Cumartesi"
    elif gun_no == 6:
        return "Pazar"
#veritabanına bağlanma
database_connect = sqlite3.connect("{}".format(config["sqlite_veritabani_adi"]),check_same_thread=False)
cursor = database_connect.cursor()
#veritabani ile sürekli çalma
def loop():
    """
    zil türleri
    1-Öğrenci Giriş
    2-Öğretmen Giriş
    3-Öğrenci Çıkış
    """
    if config["mod"] == "normal":
        gun = haftanin_gunu()
    elif config["mod"] == "kamp":
        gun = "Kamp"
    elif config["mod"] == "serbest":
        """
        buraya veritabanı olmadan zil çalma kodları yazılacak
        """
        return
    while True:
        cursor.execute("Select * From '{}' Where calma_saat = '{}' ".format(gun, datetime.datetime.now().hour))
        gelen_veri = cursor.fetchall()
        for veri in gelen_veri:
            if (str(veri[2]) == str(datetime.datetime.now().hour)) and (str(veri[3]) == str(datetime.datetime.now().minute)) and ( str(datetime.datetime.now().second) == str(00)):
                print("vakit geldi")
                if str(veri[1]) == str(1):
                    zilcal(config["zil_ogrenci_giris_adi"],int(config["zil_ogrenci_giris_toplam_uzunluk"]))
                elif str(veri[1]) == str(2):
                    zilcal(config["zil_ogretmen_giris_adi"],int(config["zil_ogretmen_giris_toplam_uzunluk"]))
                elif str(veri[1]) == str(3):
                    zilcal(config["zil_ogrenci_cikis_adi"],int(config["zil_ogrenci_cikis_adi_toplam_uzunluk"]))

if __name__ == "__main__":
    threading.Thread(target=loop).start()
    app.run(debug=True,host="0.0.0.0",port="{}".format(config["port"]))

