from flask import Flask, render_template,session, abort
from werkzeug.utils import secure_filename


from flask import Flask, redirect, url_for, render_template,request
from flask_wtf import FlaskForm
from wtforms.fields import DateField, TimeField
from wtforms import validators, SubmitField
from datetime import datetime

from Nacteni_dat import *




class InfoForm(FlaskForm):
    startdate = DateField('Zadáno dne:', format='%Y-%m-%d', validators=(validators.DataRequired(),))
    enddate = DateField('Odevzdání dne:', format='%Y-%m-%d', validators=(validators.DataRequired(),))
    submit = SubmitField('Submit')


Filename='Ukoly'

headings=('Zadáno dne','Zadáno kde','Odevzdání dne','Odevzdání kde','Předmět','Název','Popis','Povinnost','Zbývajících dní')

def Homeworks():
    if not os.path.exists(Filename):
        open(Filename,'x')
    with open(Filename, 'rb') as inp:
        try:
            List = pickle.load(inp)
            List2 = []
            for ukol in List:
                List3=ukol.__dict__.values()
                List3=list(List3)
                date=datetime.datetime.strptime(List3[2], '%d.%m.%Y')
                Status=(date.date()-datetime.date.today()).days
                if Status<-3:
                    List3[-1]=False
                else:
                    List3[-1]=Status
                    List2.append(List3)
            return tuple(List2)
        except:
            return None




app = Flask(__name__, template_folder="templates", static_folder="static")

app.config['SECRET_KEY'] = '#$%^&*'
app.config['UPLOAD_PATH'] = 'Data'

@app.route('/add', methods=['GET','POST'])
def add_to_table():
    form = InfoForm()
    Subj = ['AuR', 'EnM', 'Čj', 'M', 'Aj', 'CAu', 'EM', 'SE', 'TV', 'PA', 'AM']
    HW=Ukol()

    if request.method == "POST":
        HW.Start_Place= request.form["splace"]
        HW.End_Place = request.form["eplace"]
        HW.Title = request.form["title"]
        HW.Description = request.form["description"]
        HW.Optianoly = request.form['optianoly']
        date1 = str(str(form.startdate.data.day)+'.'+str(form.startdate.data.month)+'.'+str(form.startdate.data.year))
        date2 = str(str(form.enddate.data.day) + '.' + str(form.enddate.data.month) + '.' + str(form.enddate.data.year))
        HW.Start_date = date1
        HW.End_date = date2
        HW.Subject = request.form['subject']


        List=LoadData()
        if not List:
            List=[]
        List.append(HW)
        CreateFile(List)
        return redirect(url_for('homeworks'))

    if form.validate_on_submit():
        pass

    return render_template('Add_Homework.html',subjects=Get_Subjects('Urcity rozvrh hodin.html'), form=form)


@app.route('/homeworks')
def homeworks():
    data = Homeworks()
    return render_template('Homeworks.html',headings=headings, data=data)


@app.route('/')
def home():
    return redirect(url_for('homeworks'))



@app.route('/timetable', methods = ['GET', 'POST'])
def timetable():
    headings_timetable=('','1','2','3','4','5','6','7','8','9')
    days=('Po','Út','St','Čt','Pa')
    if request.method == 'POST':
        try:
            f = request.files['file']
            f.save(os.path.join(app.config['UPLOAD_PATH'], 'Urcity rozvrh hodin.html'))
        except:
            pass

        try:
            f = request.files['file2']
            f.save(os.path.join(app.config['UPLOAD_PATH'], 'Suplování.xlsx'))
        except:
            pass

    return render_template('Timetable.html',day=days ,headings=headings_timetable, data=Actual_Timetable())



@app.route('/timetable/<name>')
def timetables(name):
    headings_timetable=('','1','2','3','4','5','6','7','8','9')
    days=('Po','Út','St','Čt','Pá')
    return render_template('Timetable.html',day=days ,headings=headings_timetable, data=LoadTable(name))


app.run(host='0.0.0.0', port=80, debug=True)