from flask import Flask, render_template, request
from datetime import datetime
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'employee'

#home page
@app.route("/")
def home():
    return render_template('index.html')



#add employee page
@app.route("/addemp/", methods=['GET', 'POST'])
def about():
    return render_template('AddEmp.html')

#add emp functioon
@app.route("/addemp/function", methods=['GET', 'POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    emp_image_file = request.files['emp_image_file']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (emp_id, first_name, last_name, pri_skill, location))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('AddEmpOutput.html', name=emp_name)



#Get Employee 
@app.route("/getemp/")
def getEmp():
    return render_template('GetEmp.html',date=datetime.now())

#Get Employee Results
@app.route("/getemp/results",methods=['GET','POST'])
def Employee():
    
     #Get Employee
     emp_id = request.form['emp_id']
    # SELECT STATEMENT TO GET DATA FROM MYSQL
     select_stmt = "SELECT * FROM employee WHERE emp_id = %(emp_id)s"

     
     cursor = db_conn.cursor()
        
     try:
         cursor.execute(select_stmt, { 'emp_id': int(emp_id) })
         # #FETCH ONLY ONE ROWS OUTPUT
         for result in cursor:
            print(result)
        

     except Exception as e:
        return str(e)
        
     finally:
        cursor.close()

     return render_template("GetEmpOutput.html",result=result,date=datetime.now())



#attendance page
@app.route("/attendance/")
def attendance():
    return render_template('Attendance.html')

#check in button

#check out button



#apply leave page
@app.route("/leave/")
def leave():
    return render_template('ApplyLeave.html')

#apply leave function



#portfolio page
@app.route("/portfolio/")
def portfolio():
    return render_template('Portfolio.html')




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
