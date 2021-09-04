# 1. import Dependencies
import numpy as np
import datetime as dt
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
Base.prepare(engine, reflect=True)

# Save reference to the table
M = Base.classes.measurement
S = Base.classes.station
session = Session(engine)

# 2. Create an app and provide data
app = Flask(__name__)


# 3. Define what to do when a user hits the index route
@app.route("/")
def home():                                
    return (
    "Available Routes:<br/><br/>"
    "/api/v1.0/precipitation<br/>"
    "/api/v1.0/stations<br/>"
    "/api/v1.0/tobs<br/>"
    "/api/v1.0/'yyyy-mm-dd'-------------------------- Enter 'Start Date'<br/>"
    "/api/v1.0/'yyyy-mm-dd'/'yyyy-mm-dd'-------- Enter 'Start Date'/'End Date'")

# 4. Define what to do when a user hits the other routes
@app.route("/api/v1.0/precipitation")
def precipitation():
    last_date = session.query(M.date).order_by(M.date.desc()).first()

    # Calculate the date one year from the last date in data set.
    # Capture last date as list of integers in variable "date"
    time_data = last_date[0]
    format_data = "%Y-%m-%d"
    date = dt.datetime.strptime(time_data, format_data)

    year_ago = date-dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    last_year = session.query(M.date,M.prcp).filter(M.date > year_ago).statement
    
    prcp_df = pd.read_sql(last_year, session.bind).set_index('date')

    # Sort the dataframe by date, convert to dictionary
    prcp_df2 = prcp_df.sort_index()
    prcp_df2 = prcp_df.dropna()
    precip_dict = prcp_df2.to_dict()

    session.close()
    return jsonify(precip_dict)

@app.route("/api/v1.0/stations")
def stations():
    stations = session.query(S.station).all()
    stations_list = [x[0] for x in stations]
    stations_list

    session.close()
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # Confirming last date for this station
    last_date2 = session.query(func.max(M.date)).filter(M.station == "USC00519281").all()

    # And calculating one year ago
    time_data = last_date2[0][0]
    format_data = "%Y-%m-%d"
    date = dt.datetime.strptime(time_data, format_data)
    year_ago = date-dt.timedelta(days=365)

    results = session.query(M.tobs).filter(M.date > year_ago).filter(M.station == "USC00519281").all()
    temps = [result[0] for result in results]

    session.close()
    return jsonify(temps)

@app.route("/api/v1.0/<start>")
def date_start(start):

    lo_temp = session.query(M.tobs).filter(M.date >= start).order_by(M.tobs).first()
    hi_temp = session.query(func.max(M.tobs)).filter(M.date >= start).all()
    avg_temp = session.query(func.avg(M.tobs)).filter(M.date >= start).all()
    dict = {'TMIN':lo_temp[0], 'TMAX':hi_temp[0][0], 'TAVG':avg_temp[0][0]}

    session.close()
    return jsonify(dict) 

@app.route("/api/v1.0/<start>/<end>")
def date_range(start, end):

    lo_temp = session.query(M.tobs).filter(M.date >= start).filter(M.date <= end).order_by(M.tobs).first()
    hi_temp = session.query(func.max(M.tobs)).filter(M.date >= start).filter(M.date <= end).all()
    avg_temp = session.query(func.avg(M.tobs)).filter(M.date >= start).filter(M.date <= end).all()
    dict = {'TMIN':lo_temp[0], 'TMAX':hi_temp[0][0], 'TAVG':avg_temp[0][0]}

    session.close()
    return jsonify(dict)

if __name__ == "__main__":
    app.run(debug=True)
