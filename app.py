import numpy as np
import datetime as dt
import pandas as pd
import sqlalchemy

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#------------------------------------------------
# Database Setup
#------------------------------------------------
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#------------------------------------------------
# Flask Setup
#------------------------------------------------
app = Flask(__name__)


#-------------------------------------------------
# Flask Routes
#-------------------------------------------------
# Home page
# List all routes that are available

#-------------------------------------------------
#variables
one_yrDt = dt.date(2017, 8, 23) - dt.timedelta(days=366) 

@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

#------------------------------------------------
#Query Time!
#------------------------------------------------

#/api/v1.0/precipitation
#Convert the query results to a dictionary using date as the key and prcp as the value.
#Return the JSON representation of your dictionary.

@app.route('/api/v1.0/precipitation')
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of precipitation query results"""
    # Query one year dt for prcp
    pq_results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_yrDt).\
                order_by(Measurement.date).all()

    session.close()

    # Create a dictionary and append for precipitation data
    precip = []
    for date, prcp in pq_results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        precip.append(prcp_dict)

    return jsonify(prcp_dict)

#----------------------------------------------------------------------------------------------------
#/api/v1.0/stations
#Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    stat_results = session.query(Station.name, Station.station).all()
    st_data = list(np.ravel(stat_results))
    session.close()

    return jsonify(st_data)

#------------------------------------------------------------------------------------------------------
#/api/v1.0/tobs
#Query the dates and temperature observations of the most active station for the last year of data.
#Return a JSON list of temperature observations (TOBS) for the previous year.
@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)
    #most_act = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).all()

    temp = session.query(Measurement.tobs).filter(Measurement.station == 'USC00519281').filter(Measurement.date >= one_yrDt).all()
    #create a json list of TOBS for previous year
    temp_obvs = list(np.ravel(temp))
    session.close()
    return jsonify(temp_obvs)
#-------------------------------------------------------------------------------------------------------------------------
#/api/v1.0/<start> and /api/v1.0/<start>/<end>
#Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
#When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
#When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
@app.route("/api/v1.0/<start>") #start is the parameter for user to provide dt
def start_range(start):
    session = Session(engine)
    t_results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start).all()
    begin = list(np.ravel(t_results))
    session.close()
    return jsonify(begin)

@app.route("/api/v1.0/<start>/<end>") #start/end is the parameter for user to provide
def start_end_range(start, end):
    session = Session(engine)
    e_results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    last = list(np.ravel(e_results))
    session.close()
    return jsonify(last)



if __name__ == "__main__":
    app.run(debug=True)