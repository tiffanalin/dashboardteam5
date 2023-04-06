import streamlit as st
import pandas as pd
import plotly.express as px


dataset_url ="https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv"

# read csv from a URL
@st.experimental_memo
def get_data() -> pd.DataFrame:
    return pd.read_csv(dataset_url)

data = get_data()

data["year"]=data["date"].str[0:4]

#data
st.header("Covid-19 Data")
# -- Get the user input
year_col, continent_col,= st.columns([5, 5])
with year_col:
    year_choice = st.selectbox(
        "What year would you like to look at?",
        ("2020","2021","2022","2023"),
    )
with continent_col:
    continent_choice = st.selectbox(
        "What continent would you like to look at?",
        ("All", "Asia", "Europe", "Africa", "Americas", "Oceania"),
    )


# -- Apply the year filter given by the user
filtered_df = data[(data.year == year_choice)]
# -- Apply the continent filter
if continent_choice != "All":
    filtered_df = filtered_df[filtered_df.continent == continent_choice]


# -- Create the figure in Plotly
fig = px.scatter(
    filtered_df,
    x="total_cases",
    y="total_deaths",
   # size="new_deaths",
    color="continent",
    hover_name="iso_code",
    
    size_max=60,
)
fig.update_layout(title="total cases vs. total deaths")
# -- Input the Plotly chart to the Streamlit interface
st.plotly_chart(fig, use_container_width=True)

filtered_df = data[(data.year == year_choice)]
# -- Apply the continent filter
if continent_choice != "All":
    filtered_df = filtered_df[filtered_df.continent == continent_choice]

# -- Create the figure in Plotly
fig = px.scatter(
    filtered_df,
    x="new_cases",
    y="new_deaths",
   # size="new_deaths",
    color="continent",
    hover_name="iso_code",
    
    size_max=60,
)
fig.update_layout(title="new cases vs. new deaths")
# -- Input the Plotly chart to the Streamlit interface
st.plotly_chart(fig, use_container_width=True)


df=filtered_df[["total_deaths","total_deaths","new_cases","new_deaths"]].apply(lambda x: (x-x.mean())/ x.std(), axis=0)
st.line_chart(df)
fig.update_layout(title="total cases vs. total deaths vs ")