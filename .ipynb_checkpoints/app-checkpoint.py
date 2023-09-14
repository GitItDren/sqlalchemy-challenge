# Import the dependencies.



#################################################
# Database Setup
#################################################


# reflect an existing database into a new model

# reflect the tables


# Save references to each table


# Create our session (link) from Python to the DB


#################################################
# Flask Setup
#################################################
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from your_data_model_file import Base, Measurement
from datetime import datetime, timedelta

DATABASE_URI = "sqlite:///hawaii.sqlite"
engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)



app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    """List all available routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        # will add more if you need them
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Find the most recent date in the database
    with Session() as session:
    most_recent_date_result = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    most_recent_date = most_recent_date_result[0]

    # Calculate the date one year from the last date
    last_year_date = datetime.strptime(most_recent_date, "%Y-%m-%d") - timedelta(days=365)

    # Fetch precipitation data for the last 12 months
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= last_year_date).all()

    # Convert the results to a dictionary with date as the key and prcp as the value
    precipitation_data = {date: prcp for date, prcp in results}
    
    return jsonify(precipitation_data)
@app.route("/api/v1.0/stations")
def stations():
    with Session() as session:
    """Return a JSON list of stations from the dataset."""
    stations = session.query(Measurement.station).distinct().all()
    return jsonify([station[0] for station in stations])

@app.route("/api/v1.0/tobs")
def tobs():
    with Session() as session:
    """Query the dates and temperature observations of the most active station for the previous year."""
    most_active_station = session.query(Measurement.station, func.count(Measurement.station))\
                                 .group_by(Measurement.station)\
                                 .order_by(func.count(Measurement.station).desc())\
                                 .first()[0]
    
    most_recent_date = session.query(Measurement.date)\
                              .filter(Measurement.station == most_active_station)\
                              .order_by(Measurement.date.desc()).first()[0]

    last_year_date = datetime.strptime(most_recent_date, "%Y-%m-%d") - timedelta(days=365)

    results = session.query(Measurement.date, Measurement.tobs)\
                     .filter(Measurement.date >= last_year_date)\
                     .filter(Measurement.station == most_active_station).all()

    # Convert the results to a list of dictionaries
    tobs_data = [{"Date": date, "Temperature": tobs} for date, tobs in results]
    
    return jsonify(tobs_data)

@app.route("/api/v1.0/<start>")
def start_temp(start):
    with Session() as session:
    """Given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date."""
    result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
                    .filter(Measurement.date >= start).all()[0]
    
    return jsonify({"TMIN": result[0], "TAVG": result[1], "TMAX": result[2]})

@app.route("/api/v1.0/<start>/<end>")
def range_temp(start, end):
    with Session() as session:
    """Given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive."""
    result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
                    .filter(Measurement.date >= start)\
                    .filter(Measurement.date <= end).all()[0]
    
    return jsonify({"TMIN": result[0], "TAVG": result[1], "TMAX": result[2]})

if __name__ == '__main__':
    app.run(debug=True)
        