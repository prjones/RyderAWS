from flask import Flask, render_template, request, redirect
import markdown as md
import csv, os
import sqlite3
from datetime import datetime
from datetime import timedelta
import psycopg2
import uuid
import matplotlib.pyplot as plt
import pandas as pd
from pandas import DataFrame, Series 


app = Flask(__name__)
conn = psycopg2.connect(host="ec2-174-129-214-193.compute-1.amazonaws.com",database="d245l8lq8fvt3k", user="jptsqrcgcolpzw", password="68ba5ad64cadf6d0b7f387da474436dfbd3dca326fd914db29d2b35a59690ef9", port="5432")
c = conn.cursor()


#Pandas Functions

history = pd.read_sql_query("SELECT * FROM scooterhistory", conn)
df = DataFrame(history)

def lists(value):
    print(df.head(5))
    print(df[value].value_counts().head(50))
def bar(value):
    fig = plt.figure(figsize = (8,12))
    x =df[value].value_counts().head(50)
    x.transpose()
    x.plot.bar()
    plt.savefig("bar.png")
def scatter(value, value2):
    fig = plt.figure(figsize = (12,8))
    plt.scatter(df[value],df[value2])
    plt.savefig("scatter.png")






#Ride Functions
def checkAvailability(startLocation): #returns selectedScooterID as str

    global selectedScooterID
    c.execute("SELECT scooterid FROM scooters WHERE startlocation='{}' AND startcharge>33 AND status='open'".format(startLocation))
    #selectedScooterID = c.fetchone()
    selectedScooterID = str(c.fetchone()[0])
    
    return selectedScooterID
def undockScooter(selectedScooterID):

    c.execute("UPDATE scooters SET status='travel' WHERE scooterid='{}'".format(selectedScooterID))
    #print(c.execute("SELECT * FROM scooters WHERE scooterid='{}'".format(selectedScooterID))) 
def getTime(startLocation, endLocation):
    c.execute("SELECT time FROM distances WHERE startlocation='{}' AND endlocation='{}'".format(startLocation, endLocation))
    time = float(c.fetchone()[0])
    seconds = time * 60
    return seconds
def dockScooter(selectedScooterID, endLocation, decreaseCharge):

    c.execute("UPDATE scooters SET startlocation='{}', status='open', startcharge=startcharge-{} WHERE scooterid='{}'".format(endLocation, decreaseCharge, selectedScooterID))
def updateScooterHistory(selectedScooterID, startTime, endTime, username, startCharge, endCharge, startLocation, endLocation, distance, time, cost, wasreservation, rideid):
    query = "INSERT INTO scooterhistory (scooterid, starttime, endtime, username, startcharge, endcharge, startlocation, endlocation, distance, time, cost, wasreservation, rideid) \
        VALUES ('{}', '{}', '{}', '{}', {}, {}, '{}', '{}', {}, {}, {}, {}, '{}' \
        )".format(selectedScooterID, str(startTime), str(endTime), username, startCharge, endCharge, startLocation, endLocation, distance, time, cost, False, rideid)
    c.execute(query)
def updateUserHistory(username, distance, cost, time):
    
    c.execute("UPDATE userhistory SET totaldistance=totaldistance+'{}', totalcost=totalcost+{}, totaltime=totaltime+{}, tripnum=tripnum+1 WHERE username='{}'".format(distance, cost, time, username))
def chargeScooters(scooterID):
    c.execute("UPDATE scooters SET startcharge=startcharge+1 WHERE NOT scooterid='{}' OR startcharge=100".format(scooterID))
def getDistance(startLocation, endLocation):
    c.execute("SELECT distance FROM distances WHERE startlocation='{}' AND endlocation='{}'".format(startLocation, endLocation))
    distance = float(c.fetchone()[0])
    return distance
def getCharge(time):
    charge = (time / 60)
    return charge
#Reserve Functions
def reserveScooter(selectedScooterID, username):

    c.execute("UPDATE scooters SET status='{}' WHERE scooterid='{}'".format(username, selectedScooterID))  
def markUser(selectedScooterID, username):
    c.execute("UPDATE users SET reservation='{}' WHERE username='{}'".format(selectedScooterID, username))
#Pickup Functions
def getStartLocation(selectedScooterID):
    c.execute("SELECT startlocation FROM scooters WHERE scooterid='{}'".format(selectedScooterID))
    startLocation = str(c.fetchone()[0])
    return startLocation
def getReservation(username): #returns selectedScooterID as str

    c.execute("SELECT reservation FROM users WHERE username='{}'".format(username))
    selectedScooterID = str(c.fetchone()[0])
    
    return selectedScooterID
def pickupDockScooter(selectedScooterID, endLocation, decreaseCharge, username):

    c.execute("UPDATE scooters SET startlocation='{}', status='open', startcharge=startcharge-{} WHERE scooterid='{}'".format(endLocation, decreaseCharge, selectedScooterID))
    c.execute("UPDATE users SET reservation='xxxxxxxxxx' WHERE username='{}'".format(username))
def pickupUpdateScooterHistory(selectedScooterID, startTime, endTime, username, startCharge, endCharge, startLocation, endLocation, distance, time, cost, wasreservation, rideid):
    query = "INSERT INTO scooterhistory (scooterid, starttime, endtime, username, startcharge, endcharge, startlocation, endlocation, distance, time, cost, wasreservation, rideid) \
        VALUES ('{}', '{}', '{}', '{}', {}, {}, '{}', '{}', {}, {}, {}, {}, '{}' \
        )".format(selectedScooterID, str(startTime), str(endTime), username, startCharge, endCharge, startLocation, endLocation, distance, time, cost, True, rideid)
    c.execute(query)
def pickupUpdateUserHistory(username, distance, cost, time):
    
    c.execute("UPDATE userhistory SET totaldistance='{}', totalcost=totalcost+{}, totaltime=totaltime+{}, tripnum=tripnum+1 WHERE username='{}'".format(distance, cost, time, username))


WEB_APP_NAME = "Ryder Scooters"
global user
user = 'username'
'''
    Main NavBar Methods
'''

@app.route('/')
@app.route('/home')
@app.route('/home/<name>')
def home(name=WEB_APP_NAME):
    return render_template("practicewindow.html", content=name)

@app.route('/about/')
@app.route('/about/<name>')  # be sure to include both forward slashes
def about(name=WEB_APP_NAME):
    return render_template("about.html", content=name)

@app.route('/contact/')
@app.route('/contact/<name>')  # be sure to include both forward slashes
def contact(name=WEB_APP_NAME):
    return render_template("contact.html", content=name)




'''
    Login Methods
'''


@app.route('/login', methods=['POST'])
def userLogin():
    global username 
    username = request.form['user']
    password = request.form['password']


    c.execute("SELECT password FROM users WHERE username='{}'".format(username))
    string = str(c.fetchone())
    string = string[2:-3]
    
    #print(string)
    if password == string:
        print("YUH")
        c.execute("UPDATE login SET username = '{}'".format(username))
        conn.commit()
        print("username: " +username)
        
        return render_template("user_login_ok.html", user=user)

    elif c.fetchone() == None:
        print("Real bad @ 136")
        return render_template("user_login_form.html", content="Login Failed")
    else:
        print("real bad @ 139")
        return render_template("user_login_form.html", content="Login Failed")


@app.route('/login', methods=['GET'])
def login_page():
    return render_template("user_login_form.html")

@app.route('/managerlogin', methods=['POST'])
def managerLogin():
    global username 
    username = request.form['user']
    password = request.form['password']


    c.execute("SELECT password FROM managers WHERE username='{}'".format(username))
    string = str(c.fetchone())
    string = string[2:-3]
    
    if password == string:
        print("YUH")
        c.execute("UPDATE login SET username = '{}'".format(username))
        print("manager username: "+username)
        conn.commit()
        return render_template("manager_login_ok.html", user=username)

    elif c.fetchone() == None:
        return render_template("manager_login_form.html", content="Login Failed")
    else:
        return render_template("manager_login_form.html", content="Login Failed")
    

@app.route('/managerlogin', methods=['GET'])
def manager_login_page():
    return render_template("manager_login_form.html")
'''
    User Function Methods
'''
@app.route('/ride', methods=['POST'])
def runRide():
    c.execute("SELECT username FROM login")
    username = str(c.fetchone())
    username = username[2:-3]
    print("ride: "+username)
    startTime = datetime.now()
    startLocation = request.form['startlocation']
    endLocation = request.form['endlocation']
    rideID = uuid.uuid4()

    checkAvailability(startLocation)
    print(selectedScooterID)
    c.execute("SELECT startcharge FROM scooters WHERE scooterid='{}'".format(selectedScooterID))
    startCharge = int(c.fetchone()[0])

    distance = getDistance(startLocation, endLocation)
    undockScooter(selectedScooterID)
    time = getTime(startLocation, endLocation)  

    decreaseCharge = getCharge(time)
    endTime = startTime + timedelta(seconds=time)
    cost = 1 + (getTime(startLocation, endLocation)*.0025)
    endCharge = startCharge - decreaseCharge

    dockScooter(selectedScooterID, endLocation, decreaseCharge)
    updateScooterHistory(selectedScooterID, startTime, endTime, username, startCharge, endCharge, startLocation, endLocation, distance, time, cost, False, rideID)
    updateUserHistory(username, distance, cost, time) #time im seconds
    chargeScooters(selectedScooterID)
    conn.commit()
    return render_template("practicewindow.html", content=user)

@app.route('/ride', methods=['GET'])
def ridePage():
    return render_template("rideNow.html")





@app.route('/reserve', methods=['POST'])
def runReservation():
    c.execute("SELECT username FROM login")
    username = str(c.fetchone())
    username = username[2:-3]
    print("reserve: "+username)
    startLocation = request.form['reservationlocation']
    selectedScooterID = checkAvailability(startLocation)
    reserveScooter(selectedScooterID, username)
    markUser(selectedScooterID, username)
    print(selectedScooterID)
    conn.commit()
    return render_template("practicewindow.html", content=user)

@app.route('/reserve', methods=['GET'])
def reservePage():
    return render_template("reserve.html", content=user)







@app.route('/pickup', methods=['POST'])
def runPickup():
    c.execute("SELECT username FROM login")
    username = str(c.fetchone())
    username = username[2:-3]
    print("pickup: "+username)
    startTime = datetime.now()
    endLocation = request.form['endlocation']
    rideID = uuid.uuid4()
    selectedScooterID = getReservation(username)
    print(selectedScooterID)
    startLocation = getStartLocation(selectedScooterID)
    c.execute("SELECT startcharge FROM scooters WHERE status='{}'".format(username))
    
    if float(c.fetchone()[0]) == None:
        return render_template("practicewindow.html", content=user) #make a "No reservation found" page
    
    else:
        c.execute("SELECT startcharge FROM scooters WHERE status='{}'".format(username))
        startCharge = float(c.fetchone()[0])
        print("YEET")
    
    distance = getDistance(startLocation, endLocation)
    undockScooter(selectedScooterID)
    time = getTime(startLocation, endLocation)  

    decreaseCharge = getCharge(time)
    endTime = startTime + timedelta(seconds=time)
    cost = 1 + (getTime(startLocation, endLocation)*.0025)
    endCharge = startCharge - decreaseCharge

    pickupDockScooter(selectedScooterID, endLocation, decreaseCharge, username)
    pickupUpdateScooterHistory(selectedScooterID, startTime, endTime, username, startCharge, endCharge, startLocation, endLocation, distance, time, cost, True, rideID)
    pickupUpdateUserHistory(username, distance, cost, time) #time im seconds
    conn.commit()
    
    return render_template("practicewindow.html", content=user)

@app.route('/pickup', methods=['GET'])
def pickupPage():
    return render_template("pickup.html", content=user)





@app.route('/account')
def getAccountInfo():
    c.execute("SELECT username FROM login")
    username = str(c.fetchone())
    print("pre cut username: "+username)
    username = username[2:-3]
    print('username' + username)
    c.execute("SELECT starttime, startlocation, endlocation, distance, time FROM scooterhistory WHERE username='{}'".format(username))
    data = []
    headers = ['Start Time', 'Start Location', 'End Location', 'Distance', 'Time']
    data.append(headers)
    while True:
        row = c.fetchone()
        if row == None:
            break
        data.append(row)
    return render_template("account.html", content=data)


@app.route('/account', methods=['GET'])
def accountPage():
    return render_template("account.html", content=user)



'''
    Manager Function Methods
'''
#Graph Selection
@app.route('/analysis/', methods=['POST'])
def getAnalyticsType():
    decision = request.form['graphtype']
    if str(decision) == 'Bar': #bar chart
        return redirect("/barchart/")
        
    if str(decision) == 'Scatter': #scatter chart
        return redirect("/scatterchart/")

    return render_template("analysis.html")

@app.route('/analysis/', methods=['GET'])
def analysis():
    return render_template("scatter.html")

#Bar Chart
@app.route('/analytic-bar/', methods=['POST'])
def getBarAnalytics():
    want = request.form['xaxis']
    bar(str(want))

    return render_template("barchart.html")

@app.route('/analytic-bar/', methods=['GET'])
def barLoad():
    return render_template("analysisBar.html")


#Scatter Chart
@app.route('/analytic-scatter/', methods=['POST'])
def getScatterAnalytics():
    want = request.form['xaxis']
    want2 = request.form['yaxis']
    scatter(str(want),str(want2))

    return render_template("scatter.html")

@app.route('/analytic-scatter/', methods=['GET'])
def scatterLoad():
    return render_template("analysisScatter.html")


#Show Scatter Chart
@app.route('/scatterchart/', methods=['GET'])
def scatterchartLoad():
    return render_template("scatter.html")

#Show Bar Chart
@app.route('/barchart/', methods=['GET'])
def barchartLoad():
    return render_template("barchart.html")








@app.route('/map', methods=['GET'])
def map():
    return render_template("marker.html")

@app.route('/ridehistory', methods=['GET'])
def getRideHistory():
    c.execute("SELECT starttime, username, startlocation, endlocation, distance, time, cost FROM scooterhistory")
    data = []
    headers = ['Start Time', 'Username', 'Start Location', 'End Location', 'Distance', 'Time', 'Cost']
    data.append(headers)
    while True:
        row = c.fetchone()
        if row == None:
            break
        data.append(row)
    return render_template("ridehistory.html", content=data)

def rideHistory():
    return render_template('ridehistory.html')

@app.route('/userhistory', methods=['GET'])
def getUserHistory():
    c.execute("SELECT username, totaldistance, totaltime, tripnum FROM userhistory WHERE NOT tripnum=0")
    data = []
    headers = ['Username', 'Distance', 'Time', 'Trips']
    data.append(headers)
    while True:
        row = c.fetchone()
        if row == None:
            break
        data.append(row)
    return render_template("userhistory.html", content=data)

def userHistory():
    return render_template('userhistory.html')

@app.route('/logout', methods=['POST'])
def logoutUser():
    c.execute("UPDATE login SET username='none'")
    conn.commit()
    return render_template('logout.html')

@app.route('/logout', methods=['GET'])
def logoutPage():
    return render_template('logout.html')

# run the Flask app (which will launch a local webserver)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)



 
conn.commit()
