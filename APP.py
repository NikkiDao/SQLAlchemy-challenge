#!/usr/bin/env python
# coding: utf-8

# ### DESIGN CLIMATE APP

# In[1]:


# Python SQL toolkit and Object Relational Mapper
from flask import Flask, jsonify
import numpy as np
import sqlalchemy
import pandas as pd
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


# In[2]:


# Setup database and reflect the tables using sqlalchemy
engine = create_engine("sqlite:///Resources/hawaii.sqlite", echo=False)


# In[3]:


# Reflect Database into ORM class
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station


# In[4]:


#Create an app
app = Flask(__name__)


# In[5]:


#Define what to do when a user hits the index route
@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return (
        f"Welcome to the Hawaii Temps API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"

    )


# In[6]:


# Create precipitation route

@app.route("/api/v1.0/precipitation")
def precipitation():
    print("Server received request for '/api/v1.0/precipitation'.")
  
    session = Session(engine) 
    # Query date and prcp from database and then turn into a dictionary
    data_prcp = session.query(Measurement.date, Measurement.prcp)        .order_by(Measurement.date.desc())        .filter(Measurement.date >= '2016-08-23').all()
 
    session.close()

    #Create a dictionary from the row data and to append to a list 
    prcp_dict = {}
    for date, prcp in data_prcp:
        if date not in prcp_dict:
            prcp_dict[date] = []
            prcp_dict[date].append(prcp)
        else:
            prcp_dict[date].append(prcp)

    return jsonify(prcp_dict)


# In[7]:


# Create stations route

@app.route("/api/v1.0/stations")
def station():
    print("Server received request for '/api/v1.0/stations'.")
   
    session = Session(engine) 
    # Query date and prcp from database and then turn into a dictionary
    station_names = session.query(Station.name).all()
    
    session.close()
    # convert data to list format to be JSON serializable
    station_dict = list(np.ravel(station_names))

    return jsonify(station_dict)


# In[8]:


# Create tobs route

@app.route("/api/v1.0/tobs")
def tobs():
    print("Server received request for '/api/v1.0/tobs'.")
    
    session = Session(engine) 
    # Query date and prcp from database and then turn into a dictionary
    station_12months = session.query(Measurement.date, Measurement.tobs)        .filter(Measurement.station == 'USC00519281')        .filter(Measurement.date >= '2016-08-23').all()
  
    session.close()

    # Print the temp data from the most active station from the last year
    station_list = list(np.ravel(station_12months))

    return jsonify(station_list)


# In[9]:


# Create start route, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date

@app.route("/api/v1.0/<start>")
def date_starts(start):
    print("Server received request for '/api/v1.0/<start>'.")
    
    session = Session(engine) 
    # Query date and prcp from database and then turn into a dictionary
    # Lowest, avgerage, and highest temperature query
    station_results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))        .filter(Measurement.station == 'USC00519281')        .filter(Measurement.date >= start).first()

    session.close()

    # Create dictionary with the results
    temps_dict = {"Low Temp": station_results[0], "Average Temp": station_results[1], "Hi Temp": station_results[2]}

    return jsonify(temps_dict)


# In[10]:


# Create start/end route, calculate the TMIN, TAVG, and TMAX for dates from the start date through the end date (inclusive)

@app.route("/api/v1.0/<start>/<end>")
def date_start_end(start, end):
    print("Server received request for '/api/v1.0/<start>/<end>'.")
    
    session = Session(engine) 
    # Query start date, end date, and TOBS data from database and then turn into a dictionary
    station_results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))    .filter(Measurement.station== 'USC00519281')    .filter(Measurement.date <= end)    .filter(Measurement.date >= start).first()
    
    session.close()

    # Create dictionary to output
    temps_dict = {"Low Temp": station_results[0], "Average Temp": station_results[1], "Hi Temp": station_results[2]}

    return jsonify(temps_dict)


# In[ ]:


if __name__ == '__main__':
    app.run(debug=True)

