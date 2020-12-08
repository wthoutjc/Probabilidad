from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file

from flask_wtf import FlaskForm
from wtforms import IntegerField, DecimalField
from wtforms.validators import InputRequired, NumberRange
from flask_bootstrap import Bootstrap

import math

from flask_mysqldb import MySQL

app = Flask(__name__)
Bootstrap(app)

app.config['SECRET_KEY'] = "#pass"

# MySQL CONFIG
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'adminProbabilida'
app.config['MYSQL_PASSWORD'] = '9498fF'
app.config['MYSQL_DB'] = 'Probabilidad'
mysql = MySQL(app)

class op():
    def insertarData(self, p, q):
        self.ncursor = mysql.connection.cursor()
        self.ncursor.execute("SET SQL_SAFE_UPDATES = 0")
        self.command = "UPDATE data SET P = %s, Q = %s WHERE k_data = 1"
        self.ncursor.execute(self.command, (p,q))
        mysql.connection.commit()
    
    def consultarData(self):
        self.ncursor = mysql.connection.cursor()
        self.command = "SELECT P, Q FROM data WHERE k_data = 1"
        self.ncursor.execute(self.command)
        self.data = self.ncursor.fetchone()
        return self.data

operationsSQL = op()

def binomial(y, n, p):
    factoriales = math.factorial(n)/(math.factorial(y)*math.factorial(n-y))
    probabilidades = p**y * (1-p)**(n-y)
    return factoriales*probabilidades

def bnegativa(y, r, p):
    factoriales=math.factorial(y-1)/(math.factorial(r-1)*math.factorial((y-1)-(r-1)))
    probabilidades = (p**r)*(1-p)**(y-r)
    return factoriales*probabilidades

def geometrica(y, p):
    return p*(1-p)**(y-1)

def hipergeometrica(r,y,N,n):
    fact1 = math.factorial(r)/(math.factorial(y)*math.factorial(r-y))
    fact2 = math.factorial(N-r)/(math.factorial(n-y)*math.factorial((N-r)-(n-y)))
    fact3 = math.factorial(N)/(math.factorial(n)*math.factorial(N-n))
    return (fact1*fact2)/fact3

def poisson(r, u):
    numerador=(u**r)*(math.e**(-1*u))
    denominador=math.factorial(r)
    return numerador/denominador

def poissonacumulada(r, u):
    suma = 0
    for i in range(r):
        suma = suma + (u**i)/math.factorial(i)
    return float(suma*(math.e**(-u)))

class binomialInputs(FlaskForm):
    y = IntegerField('Digite Y: ', validators=[InputRequired(), NumberRange(min=0, max=1000, message="Rango: 0-1000")])
    n = IntegerField('Digite n: ', validators=[InputRequired(), NumberRange(min=0, max=1000, message="Rango: 0-1000")])
    p = DecimalField('Digite p: ', validators=[InputRequired(), NumberRange(min=0, max=1, message="Rango: 0-1")])

class bnegativaInputs(FlaskForm):
    y = IntegerField('Digite Y: ', validators=[InputRequired(), NumberRange(min=0, max=1000, message="Rango: 0-1000")])
    r = IntegerField('Digite r: ', validators=[InputRequired(), NumberRange(min=0, max=1000, message="Rango: 0-1000")])
    p = DecimalField('Digite p: ', validators=[InputRequired(), NumberRange(min=0, max=1, message="Rango: 0-1")])

class geometricaInputs(FlaskForm):
    y = IntegerField('Digite Y: ', validators=[InputRequired(), NumberRange(min=1, max=1000, message="Rango: 1-1000")])
    p = DecimalField('Digite p: ', validators=[InputRequired(), NumberRange(min=0, max=1, message="Rango: 0-1")])

class hipergeometricaInputs(FlaskForm):
    r = IntegerField('Digite r: ', validators=[InputRequired(), NumberRange(min=0, max=1000, message="Rango: 0-1000")])
    y = IntegerField('Digite y: ', validators=[InputRequired(), NumberRange(min=0, max=1000, message="Rango: 0-1000")])
    N = IntegerField('Digite N: ', validators=[InputRequired(), NumberRange(min=0, max=1000, message="Rango: 0-1000")])
    n = IntegerField('Digite n: ', validators=[InputRequired(), NumberRange(min=0, max=1000, message="Rango: 0-1000")])

class poissonInputs(FlaskForm):
    r = IntegerField('Digite y: ', validators=[InputRequired(), NumberRange(min=0, max=1000, message="Rango: 0-1000")])
    u = DecimalField('Digite λ: ', validators=[InputRequired(), NumberRange(min=0, max=1000, message="Rango: 0-1000")])

#SOFTWARE

@app.route("/data")
def data():
    results = operationsSQL.consultarData()

    array = []

    for result in results:
        array.append(float(result))

    return jsonify({"results" : array})

@app.route("/", methods=["GET","POST"])
def binomialflask():
    form = binomialInputs()
    if request.method == 'POST':
        if form.validate_on_submit():
            result = binomial(int(form.y.data), int(form.n.data), float(form.p.data))
            operationsSQL.insertarData(result, 1-result)
            array = [float(round(result,5)), float(round(result*100,2))]
            return render_template("appbinomialr.html", result = array)
        else:
            flash('Datos incorrectos')
    return render_template("appbinomial.html", form=form)

@app.route("/bnegativa", methods=["GET","POST"])
def bnegativaflask():
    form = bnegativaInputs()
    if request.method == 'POST':
        if form.validate_on_submit():
            if int(form.y.data) >= int(form.r.data):
                result = bnegativa(int(form.y.data), int(form.r.data), float(form.p.data))
                operationsSQL.insertarData(result, 1-result)
                array = [float(round(result,5)), float(round(result*100,2))]
                return render_template("appbnegativar.html", result = array)
            else:
                flash('Recuerde que y>=r !!!')
        else:
            flash('Datos incorrectos')
    return render_template("appbnegativa.html", form=form)

@app.route("/geometrica", methods=["GET","POST"])
def geometricaflask():
    form = geometricaInputs()
    if request.method == 'POST':
        if form.validate_on_submit():
            result = geometrica(int(form.y.data), float(form.p.data))
            media = 1/float(form.p.data)
            variacion = (1-float(form.p.data))/(float(form.p.data)**2)
            destandar = math.sqrt(variacion)
            operationsSQL.insertarData(result, 1-result)
            array = [float(round(result,5)), float(round(result*100,2)), media, destandar]
            return render_template("appgeometricar.html", result = array)
        else:
            flash('Datos incorrectos')
    return render_template("appgeometrica.html", form=form)

@app.route("/hipergeometrica", methods=["GET","POST"])
def hipergeometricaflask():
    form = hipergeometricaInputs()
    if request.method == 'POST':
        if form.validate_on_submit():
            if (int(form.y.data) <= int(form.r.data)) and (int(form.n.data)-int(form.y.data))<=(int(form.N.data)-int(form.r.data)):
                result = hipergeometrica(int(form.r.data), int(form.y.data), int(form.N.data), int(form.n.data))
                operationsSQL.insertarData(result, 1-result)
                array = [float(round(result,5)), float(round(result*100,2))]
                return render_template("apphipergeometricar.html", result = array)
            else:
                flash('Recuerde las restricciones!!')
        else:
            flash('Datos incorrectos')
    return render_template("apphipergeometrica.html", form=form)

@app.route("/poisson", methods=["GET","POST"])
def poissonflask():
    form = poissonInputs()
    if request.method == 'POST':
        if form.validate_on_submit():
            result = poisson(int(form.r.data), int(form.u.data))
            result2 = poissonacumulada(int(form.r.data), int(form.u.data))
            operationsSQL.insertarData(result, 1-result)
            array = [float(round(result,5)), float(round(result*100,2)), float(round(result2,5)), float(round(result2*100,2)) ]
            return render_template("apppoissonr.html", result = array)
        else:
            flash('Datos incorrectos')
    return render_template("apppoisson.html", form=form)

#END SOFTWARE
#TEORIA

@app.route("/teobinomial")
def teobinomial():
    return render_template("teobinomial.html")

@app.route("/teobnegativa")
def teobnegativa():
    return render_template("teobnegativa.html")

@app.route("/teogeometrica")
def teogeometrica():
    return render_template("teogeometrica.html")

@app.route("/teohipergeometrica")
def teohipergeometrica():
    return render_template("teohipergeometrica.html")

@app.route("/teopoisson")
def teopoisson():
    return render_template("teopoisson.html")

#END TEORIA
#BIBLIOGRAFIA

@app.route("/biobinomial")
def biobinomial():
    return render_template("biobinomial.html")

@app.route("/biobnegativa")
def biobnegativa():
    return render_template("biobnegativa.html")

@app.route("/biogeometrica")
def biogeometrica():
    return render_template("biogeometrica.html")

@app.route("/biohipergeometrica")
def biohipergeometrica():
    return render_template("biohipergeometrica.html")

@app.route("/biopoisson")
def biopoisson():
    return render_template("biopoisson.html")
    
if __name__ =='__main__':
    app.run()