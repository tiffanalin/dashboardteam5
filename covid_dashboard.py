# from libs import *
from functions import *

#streamlit
import streamlit as st

#data dependencies 
import pandas as pd
import plotly.express as px
import warnings
warnings.filterwarnings("ignore")
from datetime import date

# OWID Covid-19 Data
dataset_url='https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv'

# read csv from a URL
@st.cache_data
def get_data() -> pd.DataFrame:
    return pd.read_csv(dataset_url)
df = get_data()


def get_indexes(x):
    index_fill_1 = [i for i in range(x.index[0], x.dropna().index[0])]    
    index_interpolate = [i for i in range(x.dropna().index[0], x.index[-1])]
    return index_fill_1, index_interpolate


def update_series(x):
    # if there are all nulls in series replace with 1 
    if len(x.dropna()) == 0:
        x = x.fillna(1)
        return x
    else:
        index_fill_1, index_interpolate = get_indexes(x)
        x_fill_1 = x[x.index.isin(index_fill_1)]
        x_interpolate = x[x.index.isin(index_interpolate)]
        x_fill_1 = x_fill_1.fillna(1)
        x_interpolate = x_interpolate.interpolate()
        return pd.concat([x_fill_1, x_interpolate])


# these are the columns that we want to work with
transform_cols = ['total_cases',
                  'total_deaths',
                  'total_deaths_per_million',
                  'total_cases_per_million'
                  ]

@st.cache_data
def get_Final_df(df,transform_cols) -> pd.DataFrame:
    df["year"] = df["date"].str[0:4]
    
    #remove non-country data from 'location'
    filter_out = ['Asia','Europe','High income','Western Sahara','Upper middle income','Oceania','North America','Low income', 'Lower middle income','European Union','South America','Africa']
    df = df[~df['location'].isin(filter_out)]

    # loop through and subset each country to a list
    country_dfs = []

    # loop through each country
    for country in df.location.unique():
        df_country = df[df.location == country]
        df_country.date = pd.to_datetime(df_country.date)  # convert string date to datetime
        df_country = df_country.sort_values(by='date')  # sort by date

        # apply transformation
        for col in transform_cols:
            df_country[col] = update_series(df_country[col]).astype(int)

        country_dfs.append(df_country)  # append unique country dataframe to list
        
    df_final = pd.concat(country_dfs)

    df_final = df_final.reset_index().sort_values(by=['location', 'date'])
    df_final = df_final.fillna(0)
    
    # return to string
    df_final.date = df_final.date.astype(str)

    # remove duplicated columns
    df_final = df_final.loc[:, ~df_final.columns.duplicated()]

    #normalize data to population (1,000,000 people)
    df_final[['total_cases',	'new_cases',	'total_deaths',	'new_deaths',	'total_cases_per_million']]=df_final[['total_cases',	'new_cases',	'total_deaths',	'new_deaths',	'total_cases_per_million']].apply(lambda x: (x/(df["population"])*1000000),axis=0)

    # Raw data - total_cases/total_deaths
    # Cumulative data 
    df_final['cumulative_cases'] = df_final['new_cases_smoothed'].cumsum()
    df_final['cumulative_deaths'] = df_final['new_deaths_smoothed'].cumsum()
    
    # Average - for N days
    days = 7
    df_final['average_cases'] = df_final['cumulative_cases'].rolling(window = days).mean()
    df_final['average_deaths'] = df_final['cumulative_deaths'].rolling(window = days).mean()

    return df_final


data_load_state = st.text('Loading data...')
df_final = get_Final_df(df, transform_cols)
data_load_state.text("Done with loading!)")
countries = sorted(df_final['location'].unique())

# SIDEBAR
# select box for cases vs. deaths
st.sidebar.title(":mag_right: View Options:")
cases_or_deaths = st.sidebar.selectbox("View cases or deaths", ['Cases', 'Deaths'])

# select data type
data_type = st.sidebar.selectbox("View Data type", ['Raw number', 'Cumulative number', 'Average - 7 days'])

# selected countries
selected_countries = st.sidebar.multiselect("Select countries", countries, default=['France','World'], key='w1')

# MAIN PAGE 
st.header(":mask: Covid-19 Data")

# select timeframe
select_date = st.date_input('Choose a date range:', value=(date(2023,4,7),date(2023,4,7)), min_value=date(2019,12,1),max_value=date(2023,4,30))

filtered_df = df_final[(df_final['location'].isin(selected_countries))] 
# filtered_df = filtered_df[(filtered_df.date == select_date)]
# updates graph based on selected countries

# General (common) data preparation - for all app
# cases, data type
choice, column = get_choice(cases_or_deaths, data_type)
y_data = filtered_df[column]

fig = px.line(filtered_df, x = 'date', y = y_data, color = 'location')
st.plotly_chart(fig)

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
filtered_df1 = df_final[(df_final.year == year_choice)&(df_final['location'].isin(selected_countries))]
# -- Apply the continent filter
if continent_choice != "All":
    filtered_df1 = filtered_df1[filtered_df1.continent == continent_choice]

# -- Create the figure in Plotly
fig = px.scatter(
    filtered_df1,
    x="total_cases",
    y="total_deaths",
    size="new_deaths",
    color="location",
    hover_name="iso_code",
    
    size_max=60,
)
fig.update_layout(title="total cases vs. total deaths")
# -- Input the Plotly chart to the Streamlit interface
st.plotly_chart(fig, use_container_width=True)

filtered_df = df_final[(df_final.year == year_choice)]
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


df = filtered_df[["total_deaths","total_deaths","new_cases","new_deaths"]].apply(lambda x: (x-x.mean())/ x.std(), axis=0)
st.line_chart(df)
fig.update_layout(title = "total cases vs. total deaths vs ")