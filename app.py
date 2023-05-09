# Import the dependencies.

import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
#################################################
# Database Setup
#################################################

#create the engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
Base.prepare(autoload_with=engine, reflect=True)
# reflect the tables
Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# Set the welcome page,and list all routes that are available. 

@app.route("/")
def welcome():
    ##List all available api routes.
    return (
        f"<h1>Welcome to the Climate App API!</h1>"
        f"<h2>Available API Routes:<h2>"
        f"Precipitation:/api/v1.0/precipitation<br/>"
        f"Active stations:/api/v1.0/stations<br/>"
        f"Temperature of one year: /api/v1.0/tobs<br/>"
        f"Temperature stat from the start date(yyyy-mm-dd): /api/v1.0/start<br/>"
        f"Temperature stat from start to end date(yyyy-mm-dd): /api/v1.0/start/stop<br/>"
    )
#Returns the precipitation data measured in Hawaii
@app.route('/api/v1.0/precipitation')
def precipitation():
    session = Session(engine)
    sel_data = [Measurement.date,Measurement.prcp]
    sel_query = session.query(*sel_data).all()
    session.close()

    precipitation = []
    for date, prcp in sel_query:
        prcp_dict = {}
        prcp_dict["Date"] = date
        prcp_dict["Precipitation"] = prcp
        precipitation.append(prcp_dict)

    return jsonify(precipitation)
#List the active stations
@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)
    sel_data = [Station.station,Station.name,Station.latitude,Station.longitude,Station.elevation]
    sel_query = session.query(*sel_data).all()
    session.close()

    stations = []
    for station,name,lat,lon,el in sel_query:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        station_dict["Lat"] = lat
        station_dict["Lon"] = lon
        station_dict["Elevation"] = el
        stations.append(station_dict)

    return jsonify(stations)
#Display the 12 month temperate data
@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)
    latestdate = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    latest_date = dt.datetime.strptime(latestdate, '%Y-%m-%d')
    date_1y_ago = dt.date(latest_date.year -1, latest_date.month, latest_date.day)
    sel_data = [Measurement.date,Measurement.tobs]
    sel_query = session.query(*sel_data).filter(Measurement.date >= date_1y_ago).all()
    session.close()

    tobsall = []
    for date, tobs in sel_query:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Tobs"] = tobs
        tobsall.append(tobs_dict)

    return jsonify(tobsall)    

#Calculate the min, max, and average temperatures from given date
@app.route('/api/v1.0/<start>')
def tobs_start(start):
    session = Session(engine)
    sel_query = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    session.close()

    tobsall_1 = []
    for min,avg,max in sel_query:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        tobsall_1.append(tobs_dict)

    return jsonify(tobsall_1)

#Calculate the min, max, and average temperatures from the given start date to the given end date
@app.route('/api/v1.0/<start>/<stop>')
def tobs_start_stop(start,stop):
    session = Session(engine)
    sel_query = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= stop).all()
    session.close()

    tobsall_2 = []
    for min,avg,max in sel_query:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        tobsall_2.append(tobs_dict)

    return jsonify(tobsall_2)


  
if __name__ == "__main__":
    app.run(debug=True)