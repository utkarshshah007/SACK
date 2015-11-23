from flask import Flask
from flask import render_template
import cx_Oracle
import csv

app = Flask(__name__)


@app.route("/")
def hello():
    query = """SELECT * FROM GENRES"""
    result = cursor.execute(query)
    print result.fetchall()
    return render_template("index.html")


def connectToDB():
    ip = 'cis550.cfserwqjknt5.us-east-1.rds.amazonaws.com'
    port = 1521
    SID = 'ORCL'

    dsn_tns = cx_Oracle.makedsn(ip, port, SID)
    global connection 
    connection = cx_Oracle.connect('groupsack', 'sackgroup', dsn_tns)

    print "connection successful"
    global cursor 
    cursor = connection.cursor()
    

def closeConnection():
    cursor.close()
    connection.close()
    print "connection closed"

if __name__ == "__main__":
    connectToDB()
    app.run()
    closeConnection()