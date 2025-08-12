import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
from dateutil.relativedelta import relativedelta


# TODO: stats for gas: MPG for last fill up, overall MPG, ability to look at by car, by grade, by fillup station

def get_grade(days):
    """Determine the maintenance grade based on the number of days until the next maintenance.

    Parameters
    ----------
    days : int
        number of days until the next maintenance
    
    Returns
    -------
    grade : str
        maintenance grade
    """
    if days > 90:
        return "Good"
    elif days < -50:
        return "Not Recorded"
    else:
        return "Due"


def get_color(grade):
    """Get the color for the maintenance grade.

    Parameters
    ----------
    grade : str
        maintenance grade
    
    Returns
    -------
    color : str
        color for the maintenance grade
    """
    if grade == "Good":
        return "normal"
    elif grade == "Due":
        return "inverse"
    else:
        return "off"

# setpage config
st.set_page_config(page_title="Dashboard", layout="wide")

conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(
        spreadsheet="https://docs.google.com/spreadsheets/d/1k26SF5V4aEH8NH4_XH7kSDn1wPg0iqEjkGmdM8scTac/edit?gid=0#gid=0",
        ttl="10m")


maintenances = [
            "Head gasket inspection",
            "Head gasket replacement",
            "Timing belt inspection",
            "Timing belt replacement",
            "Tire rotation and balancing",
            "Engine oil inspection",
            "Engine oil and filter replacement",
            "Engine air filter inspection",
            "Engine air filter replancement",
            "Spark plugs replacement",
            "Differential fluid (front) inspection",
            "Differential fluid (front) replacement",
            "Differential fluid (rear) inspection",
            "Differential fluid (rear) replacement",
            "Brake fluid inspection",
            "Brake fluid replacement",
            "Power steering fluid inspection",
            "Power steering fluid replacement",
            "Automatic transmission fluid inspection",
            "Automatic transmission fluid replacement",
            "Engine coolant inspection",
            "Engine coolant replacement",
            "Engine coolant (high milage) replacement",
            "Cabin air filter inspection",
            "Cabin air filter replacement",
            "Wheel alignment",
            "Brake pad (front) inspection",
            "Brake pad (front) replacement",
            "Brake pad (rear) inspection",
            "Brake pad (rear) replacement",
            "Brake rotor (front) inspection",
            "Brake rotor (front) replacement",
            "Brake rotor (rear) inspection",
            "Brake rotor (rear) replacement",
            "Brake caliper (front) inspection",
            "Brake caliper (front) replacement",
            "Brake caliper (rear) inspection",
            "Brake caliper (rear) replacement",
            "Brake pin lubricated (front)",
            "Brake pin lubricated (rear)",
            "Drive belt inspection",
            "Drive belt replacement",
            "Ball joint, suspension components, and dust covers inspection",
            "Ball joint, suspension components, and dust covers replacement",
            "Steering linkage and boots inspection",
            "Steering linkage and boots replacement",
            "Engine inverter coolant inspection",
            "Engine inverter coolant replacement",
            "Exhaust pipes and mounting inspection",
            "Exhaust pipes and mounting replacement",
            "Windshield wiper blades inspection",
            "Windshield wiper blades replacement",
            "Tire air pressure check",
            "Tire air pressure adjustment",
            "Check for leaks poor connections",
            "Fuel tank cap gasket inspection",
            "Fuel tank cap gasket replacement",
            "Tire inspection",
            "Tire replacement",
            "Battery inspection",
            "Battery replacement",
]


m_cycles_miles = [
    30000,  # Head gasket inspection
    90000,  # Head gasket replacement
    30000,  # Timing belt inspection
    90000,  # Timing belt replacement
    7500,  # Tire rotation and balancing
    1000,  # Engine oil inspection
    5000,  # Engine oil and filter replacement
    5000,  # Engine air filter inspection
    15000,  # Engine air filter replacement
    60000,  # Spark plugs replacement
    10000,  # Differential fluid (front) inspection
    30000,  # Differential fluid (front) replacement
    10000,  # Differential fluid (rear) inspection
    30000,  # Differential fluid (rear) replacement
    1000,  # Brake fluid inspection
    12000,  # Brake fluid replacement
    10000,  # Power steering fluid inspection
    30000,  # Power steering fluid replacement
    10000,  # Automatic transmission fluid inspection
    24000,  # Automatic transmission fluid replacement
    10000,  # Engine coolant inspection
    30000,  # Engine coolant replacement
    90000,  # Engine coolant (high milage) replacement
    7500,  # Cabin air filter inspection
    15000,  # Cabin air filter replacement
    30000,  # Wheel alignment
    6000,  # Brake pad (front) inspection
    15000,  # Brake pad (front) replacement
    6000,  # Brake pad (rear) inspection
    15000,  # Brake pad (rear) replacement
    6000,  # Brake rotor (front) inspection
    30000,  # Brake rotor (front) replacement
    6000,  # Brake rotor (rear) inspection
    30000,  # Brake rotor (rear) replacement
    6000,  # Brake caliper (front) inspection
    45000,  # Brake caliper (front) replacement
    6000,  # Brake caliper (rear) inspection
    45000,  # Brake caliper (rear) replacement
    15000,  # Brake pin lubricated (front)
    15000,  # Brake pin lubricated (rear)
    20000,  # Drive belt inspection
    90000,  # Drive belt replacement
    15000,  # Ball joint, suspension components, and dust covers inspection
    30000,  # Ball joint, suspension components, and dust covers replacement
    15000,  # Steering linkage and boots inspection
    30000,  # Steering linkage and boots replacement
    15000,  # Engine inverter coolant inspection
    30000,  # Engine inverter coolant replacement
    15000,  # Exhaust pipes and mounting inspection
    500000,  # Exhaust pipes and mounting replacement
    7500,  # Windshield wiper blades inspection
    15000,  # Windshield wiper blades replacement
    500,  # Tire air pressure check
    500,  # Tire air pressure adjustment
    5000,  # Check for leaks poor connections
    5000,  # Fuel tank cap gasket inspection
    100000,  # Fuel tank cap gasket replacement
    7500,  # Tire inspection
    50000,  # Tire replacement
    7500,  # Battery inspection
    48000,  # Battery replacement
]


# how often does each maintenance occur
m_cycles_months = [i / 1000 for i in m_cycles_miles]

dfm = pd.DataFrame({
    "maintenance": maintenances,
    "milage": m_cycles_miles,
    "months": m_cycles_months
    })

def get_car_maintenance_health(car):
    car_mask = df["Car"] == car  # select the car from the dataframe
    m_mask = df["What type of record is this?"] == "Car maintenance"  # select only car maintenance records
    last_m = df[m_mask][car_mask][["Odometer", "Car", "Date", "What type of maintenance?"]]  # create a dataframe with the last maintenance records

    if last_m.empty:
        last_m["grade"] = ["Not Recorded" for _ in range(len(maintenances))]
        return last_m  # if there are no maintenance records, return False

    # tidy up the last maintenance records
    last_m = last_m.assign(maintenance=last_m["What type of maintenance?"].str.split(", ")).explode("maintenance").reset_index(drop=True)[["Car", "Date", "maintenance", "Odometer"]]
    last_m["Date"] = last_m["Date"].apply(lambda x: datetime.strptime(x, "%Y-%m-%d"))
    last_m = last_m.sort_values(by=["maintenance","Date"], ascending=[True, False]).groupby("maintenance").first().reset_index()

    # merge the last maintenance records with the maintenance cycles
    merged = pd.merge(
        last_m,
        dfm,
        how="right",
        left_on="maintenance",
        right_on="maintenance"
    )

    # calculate the next maintenance data/milage
    max_odometer = df[car_mask]["Odometer reading"].max()

    # handle nones in the data columns
    merged["Date"] = merged["Date"].fillna(datetime(1800,1,1))
    merged["next_maintenance_months"] = merged["Date"] + merged["months"].apply(lambda x: relativedelta(months=np.floor(x)))  # non-integer months is amniguous, so we use floor
    # TODO: handle the next maintenance based on the car's odometer reading

    merged["next_maintenance_miles"] = merged["Odometer"] + merged["milage"]

    # prepare for some date calculations
    merged["next_maintenance_months"] = merged["next_maintenance_months"].apply(lambda x: datetime.strptime(x.strftime("%Y-%m-01"), "%Y-%m-%d"))
    merged["today"] = datetime.now()

    # calculate the difference in days and assign a grade
    merged["difference_days"] = (merged["next_maintenance_months"] - merged["today"]).dt.days
    merged["grade"] = merged["difference_days"].apply(lambda x: get_grade(x))
    merged = merged.sort_values(by=["grade", "difference_days"], ascending=[True, True]).reset_index(drop=True)

    return merged


# setup basic page
st.title("CarLog Dashboard")
st.write("Sometimes the data doesn't update immediately, so you can clear the cache to force a refresh.")
if st.button("Fetch Data"):
    st.cache_data.clear()
    st.cache_resource.clear()
    # st.experimental_rerun()  # Reruns the script to reflect changes
    st.success("Cache cleared successfully!")

st.subheader("Maintenance and Gas Overview")
main_tab, gas_tab = st.tabs(["Maintenance", "Gas"])
main_tab.subheader("Car Health Overview")

cars_unique = np.unique(df["Car"])  # get the unique cars from the dataframe
grades = [get_car_maintenance_health(car)['grade'] for car in cars_unique]


car_health_df = pd.DataFrame(np.array(grades).T, columns=cars_unique)  # create a dataframe with the car health
car_health_df = car_health_df.melt(var_name = "car", value_name = "grade")  # reshape the dataframe to have one column for each car

car_health_df.sort_values(by=["grade"], ascending=[True], inplace=True)  # sort the dataframe by grade and car



car_health_fig = px.bar(
    car_health_df,
    y="car",
    color="grade",
    color_discrete_map={
        "Good": "green",
        "Due": "red",
        "Not Recorded": "grey"
    },
    labels={"car": "Car", "grade": "Maintenance Grade/Status"},
    orientation="h",
)
car_health_fig.update_xaxes(showticklabels=False, ticks="", showline=False)  # hide the x-axis tick labels

main_tab.plotly_chart(car_health_fig, use_container_width=True)  # show the car health bar chart
main_tab.write("This chart shows the maintenance grade for each car. Green is good (not due for > 90 days), red is due (due in <= 90 days or overdue for < 50 days), and grey is not recorded (overdue for >= 50 days).")
# st.write(df)
# horizontal line
main_tab.markdown("---")

main_tab.subheader("More Maintenance Details")

small_col, _ = main_tab.columns([1,3])
car = small_col.radio("Select Car to View More Details", options=cars_unique, key="car_select", horizontal=True)  # select what car to view


merged = get_car_maintenance_health(car)

# st.write(merged)

if np.unique(merged["grade"]).any() == "Not Recorded":
    main_tab.write(f"No maintenance records found for {car}. Please add more records via the form on your phone.")
    main_tab.stop()


milage, months = main_tab.tabs(["Milage", "Months"])
# create a number of columns and rows for the metrics

with months:
    col1, col2, col3 = st.columns(3)

    for i in range(len(merged)):
        if i % 3 == 0:
            col = col1
        elif i % 3 == 1:
            col = col2
        else:
            col = col3

        if merged["grade"][i] == "Not Recorded":
            col.metric(
                label=f"{merged['maintenance'][i]}",
                value=f"NA",
                delta=merged["grade"][i],
                delta_color=get_color(merged["grade"][i]),
                border=True,
                help=f"Don't forget to record the next maintenance for {merged['maintenance'][i]} (Not Recorded)"
            )
        else:
            col.metric(
                label=f"{merged['maintenance'][i]}",
                value=f"{merged['difference_days'][i]} days",
                delta=merged["grade"][i],
                delta_color=get_color(merged["grade"][i]),
                border=True,
                help=f"Next maintenance due on {merged['next_maintenance_months'][i].strftime('%Y-%m-%d')} ({merged["grade"][i]})"
            )

with milage:
    col1, col2, col3 = st.columns(3)

    for i in range(len(merged)):
        if i % 3 == 0:
            col = col1
        elif i % 3 == 1:
            col = col2
        else:
            col = col3

        if merged["grade"][i] == "Not Recorded":
            col.metric(
                label=f"{merged['maintenance'][i]}",
                value=f"NA",
                delta=merged["grade"][i],
                delta_color=get_color(merged["grade"][i]),
                border=True,
                help=f"Don't forget to record the next maintenance for {merged['maintenance'][i]} (Not Recorded)"
            )
        else:
            col.metric(
                label=f"{merged['maintenance'][i]}",
                value=f"ODO: {merged['next_maintenance_miles'][i]}",
                delta=merged["grade"][i],
                delta_color=get_color(merged["grade"][i]),
                border=True,
                help=f"Next maintenance due on {merged['next_maintenance_months'][i].strftime('%Y-%m-%d')} ({merged["grade"][i]})"
            )



# Gas Stats Section
gas_tab.subheader("Gas Overview")
gas_tab.write("This section is still under construction. Please check back later.")


car_choice = gas_tab.multiselect("Select a car to view", options=cars_unique, default=cars_unique[0], key="gas_car_select")
mask = (df["Car"].isin(car_choice)) & (df["What type of record is this?"] == "Gas record")
gasdf = df[mask][["Car", "Date", "Odometer reading", "Address:", "Brand of Fuel", "Octane", "Total Price in Cents", "Number of Gallons", "Does this match your recipt?", "Price per gallon"]].sort_values(by=["Date", "Odometer reading"], ascending=True).reset_index(drop=True)

gasdf["mpg"] = gasdf["Odometer reading"].diff() / gasdf["Number of Gallons"] * 1000 # calculate mpg
# gas_tab.write(gasdf)

mpg_plot = px.line(gasdf, x="Date", y="mpg", color="Car", title=f"MPG Over Time for {car_choice}", hover_data=["Address:", "Brand of Fuel", "Octane", "Total Price in Cents", "Number of Gallons", "Does this match your recipt?"])
# gas_tab.plotly_chart(mpg_plot, use_container_width=True)


milage_plot = px.line(gasdf, x="Date", y="Odometer reading", color="Car", title=f"Gas Mileage Over Time for {car_choice}", hover_data=["Address:", "Brand of Fuel", "Octane", "Total Price in Cents", "Number of Gallons", "Does this match your recipt?"])
# gas_tab.plotly_chart(milage_plot, use_container_width=True)


ppg_plot = px.line(gasdf, x="Date", y="Price per gallon", color="Car", title=f"Gas Price Over Time for {car_choice}", hover_data=["Address:", "Brand of Fuel", "Octane", "Total Price in Cents", "Number of Gallons", "Does this match your recipt?"])
# gas_tab.plotly_chart(ppg_plot, use_container_width=True)


gascol1, gascol2, gascol3 = gas_tab.columns(3)

gascol1.plotly_chart(mpg_plot, use_container_width=True)
gascol2.plotly_chart(milage_plot, use_container_width=True)
gascol3.plotly_chart(ppg_plot, use_container_width=True)

gascol1.metric(label="Total Fill Ups", value=len(gasdf))
gascol2.metric(label="Total Gallons", value=f"{gasdf['Number of Gallons'].sum():.2f} gal")


delta = gasdf["Price per gallon"].median() - gasdf["Price per gallon"].iloc[:-1].median()
delta_color = "normal" if delta > 0 else "inverse"
gascol3.metric(label="Average Price per Gallon", value=f"${gasdf['Price per gallon'].median():.2f}/gal", delta=f"{delta:.2f}/gal", delta_color=delta_color)

