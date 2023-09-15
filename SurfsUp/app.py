# Import the dependencies.
import numpy as np
import os
import sqlalchemy
import datetime as dt
import pandas as pd
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify



#################################################
# Database Setup
#################################################
os.chdir(os.path.dirname(os.path.realpath(__file__)))
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def index():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        #f"/api/v1.0/tstats/&lt;start&gt;<br/>"
        #f"/api/v1.0/tstats/&lt;start&gt;/&lt;end&gt;<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start-end<br/>"
    )

#Convert the query results from your precipitation analysis to a dictionary
#using "date" as the key and "prcp" as the value. 

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    most_recent_date_str = session.query(Measurement.date)\
        .order_by(Measurement.date.desc())\
        .first()[0]
    most_recent_date = dt.date.fromisoformat(most_recent_date_str)
    year_ago = most_recent_date - dt.timedelta(days=365)
    precipitation=session.query(Measurement.date, func.avg(Measurement.prcp))\
        .filter(Measurement.date>=year_ago)\
        .group_by(Measurement.date)\
        .order_by(Measurement.date)\
        .all()
    
    session.close()

    precipitation_dict = {}
    for prec in precipitation:
        prec_date = prec[0]
        prec_value = prec[1]
        precipitation_dict[prec_date] = prec_value
    return jsonify(precipitation_dict)

#Return a JSON list of stations from teh dataset.

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    total_stations = session.query(Measurement.station)\
        .group_by(Measurement.station).all()
    
    session.close()

    all_stations = list(np.ravel(total_stations))

    return jsonify(all_stations)

#Query the dates and temprature observations of the most-active station
#for the previous year of data.
#Return a JSON list of temperature observatins for the previous year. 

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    most_recent_date_str = session.query(Measurement.date)\
        .order_by(Measurement.date.desc()).first()[0]
    most_recent_date = dt.date.fromisoformat(most_recent_date_str)
    year_ago = most_recent_date - dt.timedelta(days=365)
    
    temp_ob_data = session.query(Measurement.station, Measurement.tobs)\
        .filter(Measurement.station == 'USC00519281')\
        .filter(Measurement.date >= year_ago).all()
    
    session.close()
   
    ma_station_temps = list(np.ravel(temp_ob_data))

    return jsonify(ma_station_temps)

#Return a JSON list of the minimum temprature, 
#the average temprature and the maximum temperature for a specified 
#start or start-end range.
#For a specified start, calculate "TMIN", "TAVG" and "TMAX" for all the dates
#greater than or equal to the start date. 


#For a specified start date and end date, calculate "TMIN", "TAVG" and "TMAX"
#for the dates from the start date to the end date, inclusive. 



if __name__ == "__main__":
    app.run(debug=True)