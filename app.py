from sqlite3 import Cursor
from unicodedata import name
from flask import Flask, redirect, render_template, request, send_file, url_for, session, jsonify, flash
from flask_mysqldb import MySQL, MySQLdb
from flask_login import UserMixin
from functools import wraps
from io import BytesIO

app = Flask(__name__)
app.secret_key="mnms"

app.config['MYSQL_HOST'] ="localhost"
app.config['MYSQL_USER'] ="root"
app.config['MYSQL_PASSWORD'] ="Mahbk221"
app.config['MYSQL_DB'] ="proj"

mysql = MySQL(app)
#cursor = mysql.connection.cursor()
#

trimester1Tests=['Physcial Test', 'Ultrasound for Fetal Nuchal Translucency', 'Pelvic Test', 'Pap Smear', 'Ultrasound for Fetal Nasal Bone Determination', 'Maternal Serum (Blood) Test', 'Test for Hepatitis B, Syphilis and HIV']
trimester2Tests=['AFP Screening', 'Glucose Tolerance Test', 'Examine the Fetal Anatomy for Abnormalities', 'Check the Amount of Amniotic Fluid', 'Measure the Length of The Cervix']
trimester3Tests=['Check the Amount of Amniotic Fluid', 'Biophysical Profile Test', 'Determine the Position of the Fetus', 'Assess the Placenta', 'The Nonstress Test (NST)', 'Depression screening']

def addTests(trimTests, email, trimNo, cursor):
    for trimTest in trimTests:
        print (email, trimTest, trimNo, 0)
        #cursor = mysql.connection.cursor()
        cursor.execute("Insert into TrimesterTests values (%s,%s,%s,%s)",(email, trimTest, trimNo, 0))
        # mysql.connection.commit()
        # cursor.close()

def getTests(email, trimNo, cursor):
    print(email,trimNo)
    test = cursor.execute("Select * from TrimesterTests where email= %s and Trimester= %s", (email, trimNo))
    print('test:', test)
    testInfo = cursor.fetchall()
    return testInfo

def updateTests(trimTests, email, trimNo, cursor, checkedTests):
    #print(checkedTests)
    #print(trimTests)
    matching=[]

    for check in checkedTests:
        temp = [s for s in trimTests if check in s]
        print("temp:", temp)
        matching = matching + temp
    print(matching)
    # NOW YOU HAVE MATCHED TESTS in an ARRAY
    for match in matching:
        cursor.execute("Update TrimesterTests set isDone=1 where email=%s and trimester=%s and testname like %s",(email, trimNo, match))

    notChecked = [x for x in trimTests if not x in matching or matching.remove(x)]
    
    print(notChecked)

    for notC in notChecked:
        cursor.execute("Update TrimesterTests set isDone=0 where email=%s and trimester=%s and testname like %s",(email, trimNo, notC))



def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return wrap

@app.route('/')
#@login_required
def index():
    if "logged_in" in session:
        isLogged = True
    else:
        isLogged =False

    return render_template('Homepage.html', logged_in = isLogged)

@app.route('/n')
#@login_required
def indexNurse():
    if "logged_in" in session:
        isLogged = True
    else:
        isLogged =False

    return render_template('NurseHomePage.html', logged_in = isLogged)




@app.route('/test')
@login_required
def test():
    cursor = mysql.connection.cursor()
    mothers = cursor.execute ("Select * from mothers")
    #mothers = cursor.fetchall()
    if mothers > 0:
        #mothersInfo = Cursor.fetchall  DOES NOT WORK
        mothersInfo = cursor.fetchall()
        print(mothersInfo)
        return render_template('test.html', mothers=mothersInfo)

    else:
        return ('empty')



@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        print(request.form)
        email = request.form.get('email',None)
        print("emaildada")
        password = request.form.get('password',None)

        if (email == None or password == None):
            return "error 404 hehehe"
        else:

            #print("before cur")
            cursor = mysql.connection.cursor()
            #print("after cur")
            user = cursor.execute("Select * from mothers where email= %s and password= %s", (email, password))
            nurse = cursor.execute("Select email from nurses where email= %s", [email])
            #print(user)
            cursor.close()

            if user >0 or nurse>0:
                #print("user > 0")
                session['userEmail'] = email
                session['logged_in'] = True

                if user>0:
                    session['user']='mother'
                    return redirect(url_for('index'))
                
                else:
                    session['user']='nurse'
                    return redirect(url_for('indexNurse'))

                #return redirect(url_for('index'))
                #return "<p> {{email}} </p>"
            
            else:
                print("dhadhda")
                return redirect(url_for('login'))
    
    elif request.method == "GET":
        return render_template('Login.html')
        

@app.route('/logout')
def logout():
    session.pop('userEmail')
    session.pop('logged_in')
    session.pop('user')
    #session['logged_in'] = False
    return redirect(url_for('login'))

@app.route('/signup')
def signup():
    return render_template('SignUp.html')

@app.route('/signup/mother', methods=["POST", "GET"])
def signUpMother():
    if request.method == "POST":
        name = request.form.get('name',None)
        email = request.form.get('email',None)
        password = request.form.get('password',None)
        phoneno = request.form.get('phoneno',None)
        emergencyno = request.form.get('emergencyno',None)
        hospital = request.form.get('hospital')
        dob = request.form.get('dob',None)
        duedate = request.form.get('duedate',None)
        gender = request.form.get('gender',None)

        print("hospital:" ,hospital)

        if (email == None or password == None):
            return "error 404 hehehe"
        else:

            cursor = mysql.connection.cursor()
            user = cursor.execute("Select email from mothers where email= %s", [email])
            nurse = cursor.execute("Select email from nurses where email= %s", [email])
            

            if user > 0 or nurse>0:
                #there is already a user with this email, signup again
                cursor.close()
                return redirect(url_for('signUpMother'))

            else:
                cursor.execute("Insert into mothers (name, email, password, phoneno, emergencycontact, hospital, dob, duedate, Babygender) values (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (name, email, password, phoneno, emergencyno, hospital,
                dob, duedate, gender))
                
                # mysql.connection.commit()
                # cursor.close()

                # Add all trim tests to DB for this new user
                addTests(trimester1Tests,email,1, cursor)
                addTests(trimester2Tests,email,2, cursor)
                addTests(trimester3Tests,email,3, cursor)

                mysql.connection.commit()
                cursor.close()

                return redirect(url_for('login'))
        

    elif request.method == "GET":
        cursor = mysql.connection.cursor()
        hospitals = cursor.execute("Select * from hospitals")
        hospitalInfo = cursor.fetchall()
        return render_template('SignUp(Mothers).html', hospitalInfo = hospitalInfo)


@app.route('/signup/nurses', methods=["POST", "GET"])
def signUpNurses():
    if request.method == "POST":
        name = request.form.get('name',None)
        email = request.form.get('email',None)
        password = request.form.get('password',None)
        hospital = request.form.get('hospital',None)

        if (email == None or password == None):
            return "error 404 hehehe"
        else:

            cursor = mysql.connection.cursor()
            user = cursor.execute("Select email from mothers where email= %s", [email])
            nurse = cursor.execute("Select email from nurses where email= %s", [email])
            

            if user > 0 or nurse > 0:
                #there is already a user with this email, signup again
                cursor.close()
                return redirect(url_for('signUpNurses'))

            else:
                cursor.execute("Insert into nurses (name, email, password, hospital) values (%s,%s,%s,%s)",
                (name, email, password, hospital))
                
                mysql.connection.commit()
                cursor.close()

                return redirect(url_for('login'))
        

    elif request.method == "GET":
        cursor = mysql.connection.cursor()
        hospitals = cursor.execute("Select * from hospitals")
        hospitalInfo = cursor.fetchall()
        return render_template('SignUp(Nurses).html', hospitalInfo = hospitalInfo)


@app.route('/TestReminder', methods=["POST", "GET"])
@login_required
def TestReminder():
    if request.method == "POST":
        checkedTest1 = request.form.getlist('trim1')
        checkedTest2 = request.form.getlist('trim2')
        checkedTest3 = request.form.getlist('trim3')

        cursor = mysql.connection.cursor()

        email = session['userEmail']
        updateTests(trimester1Tests,email,1, cursor, checkedTest1)
        updateTests(trimester2Tests,email,2, cursor, checkedTest2)
        updateTests(trimester3Tests,email,3, cursor, checkedTest3)

        mysql.connection.commit()
        cursor.close()
        flash(f"Changes Saved!!")
        #return "done"
        return redirect(url_for('TestReminder'))


    elif request.method =="GET":
        cursor = mysql.connection.cursor()
        email = session['userEmail']
        trim1 = getTests(email,1,cursor)
        trim2 = getTests(email,2,cursor)
        trim3 = getTests(email,3,cursor)
        #print(trim1)
        cursor.close()
        return render_template('TestReminder.html', trim1=trim1, trim2=trim2, trim3=trim3)


@app.route('/talk')
@login_required
def Talk():

    email = session["userEmail"]
    cursor = mysql.connection.cursor()

    type= session['user']

    if session['user'] == 'mother':
        print("mother is talking")
        user = cursor.execute("Select id,name,email, hospital from mothers where email = %s", [email])
        #user = cursor.execute("Select * from mothers where email = 'mu@gmail.com' and id=2")
        userInfo = cursor.fetchone()

        #actualUser = userInfo[0]
        
        print(userInfo)
        print(userInfo[0])
        #print(actualUser[0])

        other = cursor.execute("Select id,name,email, hospital from nurses where hospital = %s", [userInfo[3]])
        otherInfo = cursor.fetchone()
        userType = "Mother"

    else:
        print("nurse is talking")
        user = cursor.execute("Select id,name,email, hospital from nurses where email = %s", [email])
        userInfo = cursor.fetchone()

        other = cursor.execute("Select id,name,email, hospital from mothers where email = 'iu@gmail.com' and id=1")
        otherInfo = cursor.fetchone()
        userType = "Nurse"

        



    cursor.close()
    return render_template('talkJSTest.html', user=userInfo, other=otherInfo, type = type, userType = userType)


@app.route('/upload', methods=["POST", "GET"])
@login_required
def upload():
    if request.method == "POST":
        email = session["userEmail"]
        file = request.files['file']

        cursor = mysql.connection.cursor()
        cursor.execute("Insert into upload (email, filename, data) values (%s,%s,%s)",(email, file.filename, file.read()))
        mysql.connection.commit()
        cursor.close()


        return redirect(url_for('view'))


    elif request.method =="GET":
        return render_template('upload.html')


@app.route('/download/<upload_id>')
def download (upload_id):
    cursor = mysql.connection.cursor()

    upload = cursor.execute("Select * from upload where id = %s", [upload_id])
    uploadInfo = cursor.fetchone()
    return send_file(BytesIO(uploadInfo[3]), attachment_filename=uploadInfo[2], as_attachment=True)



@app.route('/Medication')
@login_required
def Medication():
    cursor = mysql.connection.cursor()
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cur.execute("SELECT * FROM events ORDER BY id")
    calendar = cur.fetchall()  
    return render_template('Medication.html', calendar = calendar)

@app.route("/addmedication",methods=["POST","GET"])
def addmedication():
    cursor = mysql.connection.cursor()
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        title = request.form['title']
        start = request.form['start']
        end = request.form['end']
        print(title)     
        print(start)  
        cur.execute("INSERT INTO events (title,start_event,end_event) VALUES (%s,%s,%s)",[title,start,end])
        mysql.connection.commit()       
        cur.close()
        msg = 'success'  
    return jsonify(msg)
 
@app.route("/editmedication",methods=["POST","GET"])
def update():
    cursor = mysql.connection.cursor()
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        title = request.form['title']
        start = request.form['start']
        end = request.form['end']
        id = request.form['id']
        print(title)     
        print(start)  
        cur.execute("UPDATE events SET title = %s, start_event = %s, end_event = %s WHERE id = %s ", [title, start, end, id])
        mysql.connection.commit()       
        cur.close()
        msg = 'success'  
    return jsonify(msg)    

 
@app.route("/deletemedication",methods=["POST","GET"])
def ajax_delete():
    cursor = mysql.connection.cursor()
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        getid = request.form['id']
        print(getid)
        cur.execute('DELETE FROM events WHERE id = {0}'.format(getid))
        mysql.connection.commit()       
        cur.close()
        msg = 'Record deleted successfully'  
    return jsonify(msg)


@app.route('/view', methods=["POST", "GET"])
@login_required
def view():
    if request.method == "POST":
        email = session["userEmail"]

        cursor = mysql.connection.cursor()
        userFiles = cursor.execute("Select id,email, filename from upload where email = %s", [email])
        userFilesInfo = cursor.fetchall()
        print(userFilesInfo)
        return f'files info: {userFilesInfo}'

        cursor.close()


        


    elif request.method =="GET":
        path = "Mother"
        email = session["userEmail"]

        cursor = mysql.connection.cursor()
        userFiles = cursor.execute("Select id,email, filename from upload where email = %s", [email])
        userFilesInfo = cursor.fetchall()
        print(userFilesInfo)
        return render_template('View.html', userFilesInfo = userFilesInfo, path = path)


@app.route('/view/<user_email>', methods=["POST", "GET"])
@login_required
def viewD(user_email):
    if request.method == "POST":
        email = session["userEmail"]

        cursor = mysql.connection.cursor()
        userFiles = cursor.execute("Select id,email, filename from upload where email = %s", [email])
        userFilesInfo = cursor.fetchall()
        print(userFilesInfo)
        return f'files info: {userFilesInfo}'

        cursor.close()


        


    elif request.method =="GET":
        path = "Nurse"
        print(user_email)
        cursor = mysql.connection.cursor()
        user = cursor.execute("Select email from mothers where id = %s", [user_email])
        userInfo = cursor.fetchone()

        userFiles = cursor.execute("Select id,email, filename from upload where email = %s", [userInfo])
        userFilesInfo = cursor.fetchall()
        print(userFilesInfo)
        return render_template('View.html', userFilesInfo = userFilesInfo, path = path)


@app.route('/viewPatient', methods=["POST", "GET"])
@login_required
def viewPatient():
    if request.method == "POST":
        email = session["userEmail"]

        cursor = mysql.connection.cursor()
        userFiles = cursor.execute("Select id,email, filename from upload where email = %s", [email])
        userFilesInfo = cursor.fetchall()
        print(userFilesInfo)
        return f'files info: {userFilesInfo}'

        cursor.close()


        


    elif request.method =="GET":
        email = session["userEmail"]

        cursor = mysql.connection.cursor()
        nurse = cursor.execute("Select * from nurses where email = %s", [email])
        nurseInfo = cursor.fetchone()
        print(nurseInfo[4])
        hosp = nurseInfo[4]

        usersInHospital = cursor.execute("Select * from mothers where hospital = %s", [hosp])
        userInHospitalInfo = cursor.fetchall()
        
        #return "hehe"
        return render_template('ViewPatient.html', userInHospitalInfo = userInHospitalInfo)


if __name__ == '__main__':
    app.run(debug = True, threaded=True)