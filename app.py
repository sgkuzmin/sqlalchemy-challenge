from flask import Flask, jsonify
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

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
def welcome():
    return (
        f"Welcome to weather API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs"
        f"/api/v1.0/start_date, where start_date is in the format YYYY-MO-DATE<br>"
        f"/api/v1.0/start_date/end_date"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # calculate precipitation for the most recent year
    mostRecentDate=max(session.query(Measurement.date))[0]
    yearBackFromRecent=dt.datetime.strptime(mostRecentDate,"%Y-%m-%d")-dt.timedelta(days=365)
    prcp_scores=session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date > yearBackFromRecent).order_by(Measurement.date).all()
    #Convert the query results to a dictionary using date as the key and prcp as the value.
    prcp_dict=dict(prcp_scores)
    

    session.close()

    return jsonify(prcp_dict)

@app.route("/api/v1.0/stations")
def stations():
    #Return a JSON list of stations from the dataset.
    session = Session(engine)
    stations_results=session.query(Station.id, Station.station).all()
    stations_list=dict(stations_results)
    session.close()
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    #Query the dates and temperature observations of the most active station 
    # for the last year of data.
    session = Session(engine)
    mostRecentDate=max(session.query(Measurement.date))[0]
    yearBackFromRecent=dt.datetime.strptime(mostRecentDate,"%Y-%m-%d")-dt.timedelta(days=365)
    tobs_USC00519281=session.query(Measurement.date,Measurement.tobs).\
    filter(Measurement.date > yearBackFromRecent).\
    filter(Measurement.station == 'USC00519281').\
        order_by(Measurement.date).all()
    tobs_dict=dict(tobs_USC00519281)
    session.close()
    #Return a JSON list of temperature observations (TOBS) for the previous year.
    return jsonify(tobs_dict)

@app.route("/api/v1.0/<start_date>")
def stat_start_only(start_date):
#When given the start only, calculate TMIN, TAVG, 
# and TMAX for all dates greater than and equal to the start date for all Hawaii stations.
    session = Session(engine)
    tobs_stats=session.query(func.min(Measurement.tobs),\
            func.max(Measurement.tobs),\
                func.avg(Measurement.tobs)).\
                        filter(Measurement.date >= start_date).all()
    
    tobs_stats_dict={'Tmin':tobs_stats[0][0], 'Tmax':tobs_stats[0][1],'Tavg':tobs_stats[0][2]}
    session.close()
    return jsonify(tobs_stats_dict)

@app.route("/api/v1.0/<start_date>/<end_date>")
def stat_start_and_end(start_date, end_date):
#When given the start and the end date, calculate the TMIN, TAVG, and TMAX for 
# dates between the start and end date inclusive for all Hawaii stations.
    session = Session(engine)
    tobs_stats=session.query(func.min(Measurement.tobs),\
            func.max(Measurement.tobs),\
                func.avg(Measurement.tobs)).\
                        filter(Measurement.date >= start_date).\
                            filter(Measurement.date <= end_date).all()
    
    tobs_stats_dict={'Tmin':tobs_stats[0][0], 'Tmax':tobs_stats[0][1],'Tavg':tobs_stats[0][2]}
    session.close()
    return jsonify(tobs_stats_dict)

if __name__ == "__main__":
    app.run(debug=True)