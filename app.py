import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px
import pymongo

# Initialize connection.
# Uses st.experimental_singleton to only run once.
# @st.experimental_singleton(suppress_st_warning=True)
# def init_connection():
#     return pymongo.MongoClient(**st.secrets["mongo"], connect=False)

# client = init_connection()

# Pull data from the collection.
# Uses st.experimental_memo to only rerun when the query changes or after 10 min.
# @st.experimental_memo(ttl=600)
# def get_data():
#     db = client.mydb
#     items = db.mycollection.find()
#     items = list(items)  # make hashable for st.experimental_memo
#     return items
#
# items = get_data()

#DATA_URL = "G:/WORK/GRAY_SOLUTIONS_PROJECTS/Sreamlit_Project/Motor_Vehicle_Collisions_Crashes.csv"
#DATA_URL = "https://github.com/thehamzza/Streamlit-Web-App-Motor-Vehicle-Collisions-in-New-York-City/blob/main/Motor_Vehicle_Collisions_Crashes.csv"
DATA_URL = ("https://github.com/thehamzza/Streamlit-Web-App-Motor-Vehicle-Collisions-in-New-York-City/blob/77f82403f9a58fc252a984cc8272730dcdc46af8/Motor_Vehicle_Collisions_Crashes.csv")


st.title("Motor Vehicle Collisions in New York City")
st.markdown("This application is a Streamlit dashboard that can be used to analyze motor vehicle collisions in NYC 🗽🚕💥")

# Pull data from the collection.
# Uses st.experimental_memo to only rerun when the query changes or after 10 min.
# @st.experimental_memo(ttl=600)
##@st.cache(persist=True)
# def load_data(nrows):
#     db = client.mydb
#     items = db.mycollection.find()
#     items = list(items)  # make hashable for st.experimental_memo

#     #data = pd.read_csv(DATA_URL, nrows=nrows, parse_dates=[['CRASH_DATE', 'CRASH_TIME']])
#     data = pd.DataFrame(items, nrows=nrows, parse_dates=[['CRASH_DATE', 'CRASH_TIME']])
#     data.dropna(subset=['LATITUDE', 'LONGITUDE'], inplace=True)
#     lowercase= lambda x: str(x).lower()
#     data.rename(lowercase, axis='columns', inplace=True)
#     data.rename(columns={'crash_date_crash_time':'date/time'}, inplace=True)
#     return data

def get_database():
    from pymongo import MongoClient
    import pymongo

    # Provide the mongodb atlas url to connect python to mongodb using pymongo
    CONNECTION_STRING = "mongodb://<username>:<password>@<cluster0>.mongodb.net/motor_vehicle_crash_nyc.motor_vehicle_crash_data"

    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    client = MongoClient(CONNECTION_STRING)

    # Create the database for our example (we will use the same database throughout the tutorial
    return client

data = get_database()

#data = load_data(100000)
#data = get_data
data = pd.DataFrame(data, nrows=100000, parse_dates=[['CRASH_DATE', 'CRASH_TIME']])
data.dropna(subset=['LATITUDE', 'LONGITUDE'], inplace=True)
lowercase= lambda x: str(x).lower()
data.rename(lowercase, axis='columns', inplace=True)
data.rename(columns={'crash_date_crash_time':'date/time'}, inplace=True)
#return data

st.header("Where are the most people injured in NYC")
injured_people = st.slider("Number of persons injured in vehicle collision", 0, 19)
st.map(data.query("injured_persons >= @injured_people")[["latitude", "longitude"]].dropna(how="any"))


st.header("How many collisions occur during a given time of the day?")
hour = st.slider("Hours to look at", 0, 23)
data = data[data['date/time'].dt.hour == hour]

st.markdown("Vehicle Collisions between %i:00 and %i:00" % (hour, (hour + 1) % 24))
midpoint = (np.average(data['latitude']), np.average(data['longitude']))

st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state={
        "latitude": midpoint[0],
        "longitude": midpoint[1],
        "zoom": 11,
        "pitch":50,
    },

    layers=[
        pdk.Layer(
            "HexagonLayer",
            data=data[['date/time', 'latitude', 'longitude']],
            get_position = ['longitude', 'latitude'],
            radius = 100,
            extruded =True,
            pickable = True,
            elevation_scale=4,
            elevation_range=[0, 1000],
        ),

    ],

))

st.subheader("Breakdown by minute between %i:00 and %i:00" % (hour, (hour + 1) % 24))
filtered = data[
    (data['date/time'].dt.hour >= hour) & (data['date/time'].dt.hour < (hour + 1))
]
hist = np.histogram(filtered['date/time'].dt.minute, bins=60, range=(0, 60))[0]
chart_data = pd.DataFrame({'minute': range(60), 'crashes':hist})
fig= px.bar(chart_data, x='minute', y='crashes', hover_data=['minute', 'crashes'], height=400)
st.write(fig)

st.header("Top 5 dangerous streets by affected type")
select = st.selectbox('Affected type of people', ['Pedestrians', 'Cyclists', 'Motorists'])

if select == 'Pedestrians':
    st.write(data.query("injured_pedestrians >= 1")[["on_street_name", "injured_pedestrians"]].sort_values(by=['injured_pedestrians'], ascending=False).dropna(how="any")[:5])

elif select == 'Cyclists':
    st.write(data.query("injured_cyclists >= 1")[["on_street_name", "injured_cyclists"]].sort_values(by=['injured_cyclists'], ascending=False).dropna(how="any")[:5])

elif select == 'Motorists':
    st.write(data.query("injured_motorists >= 1")[["on_street_name", "injured_motorists"]].sort_values(by=['injured_motorists'], ascending=False).dropna(how="any")[:5])



if st.checkbox("Show Raw Data", False):
    st.subheader("Raw Data")
    st.write(data)

