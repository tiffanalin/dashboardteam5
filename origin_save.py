# from libs import *
# from functions import *

#streamlit
import streamlit as st

#data dependencies 
import pandas as pd
import plotly.express as px
import warnings
warnings.filterwarnings("ignore")
from datetime import date

########## DATA ###########
#OWID Covid-19 Data
dataset_url='https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv'

# read csv from a URL
@st.cache_data
def get_data() -> pd.DataFrame:
    return pd.read_csv(dataset_url)

df = get_data()

df["year"]=df["date"].str[0:4]

print(df.shape)
print('Total unique continents:',len(df.continent.unique()))
print('Total unique countries:',len(df.location.unique()))
print('Date span:',df.date.min(),df.date.max())
print("Data intformation",df.info())
print('Data describtion',df.describe())

def get_indexes(x):
        
    index_fill_1 = [i for i in range(x.index[0], x.dropna().index[0])]    
    index_interpolate = [i for i in range(x.dropna().index[0], x.index[-1])]
    return index_fill_1, index_interpolate

def update_series(x):
    
    # if there are all nulls in series replace with 1 
    if len(x.dropna()) == 0:
        x = x.fillna(0)
        return x
    
    else:
        index_fill_1, index_interpolate = get_indexes(x)
        x_fill_1 = x[x.index.isin(index_fill_1)]
        x_interpolate = x[x.index.isin(index_interpolate)]
        x_fill_1 = x_fill_1.fillna(0)
        x_interpolate = x_interpolate.interpolate()
        return pd.concat([x_fill_1, x_interpolate])


# these are the columns that we want to work with
transform_cols = ['total_cases',
                  'total_deaths',
                  'total_deaths_per_million',
                  'total_cases_per_million'
                  ]
@st.cache_data
def get_Final_df(df,transform_cols):
    #remove non-country data from 'location'
    filter_out=['Asia','Europe','High income','Western Sahara','Upper middle income','Oceania','North America','Low income', 'Lower middle income','European Union','South America','Africa']
    df_final = df[~df['location'].isin(filter_out)]

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

    return df_final

df_final=get_Final_df(df,transform_cols)
countries_list=df_final.location.unique()

########## SIDEBAR ########### 
st.sidebar.title(":mag_right: View Options:")

# select box for cases vs. deaths
cases_or_deaths = st.sidebar.selectbox("View cases or deaths", ['Cases', 'Deaths'])

# multiselect countries after filtering non-country locations
filter_out=['Asia','Europe','High income','Western Sahara','Upper middle income','Oceania','North America','Low income', 'Lower middle income','European Union','South America','Africa']
df = df[~df['location'].isin(filter_out)]
countries = sorted(df['location'].unique())
selected_countries = st.sidebar.multiselect("Select countries", countries, default=['France','World'], key='w1')

# date range selector
select_date = st.sidebar.date_input('Choose a date range:', value=(date(2020,1,1),date(2020,1,31)), min_value=date(2019,12,1),max_value=date(2023,4,30), key='w2')
#"the date selected:", select_date

#if 'dummy_data' not in st.session_state.keys():
#    dummy_data = countries_list
#    st.session_state['dummy_data'] = dummy_data
#else:
#    dummy_data = st.session_state['dummy_data']

#def checkbox_container(data):
#    st.sidebar.header('Select Countries: ')
   
#    cols = st.sidebar.columns(2)
   
#    if cols[0].button('Select All'):
#        for i in data:
#            st.session_state['dynamic_checkbox_' + i] = True
#        st.experimental_rerun()
#    if cols[1].button('UnSelect All'):
#        for i in data:
#            st.session_state['dynamic_checkbox_' + i] = False
#        st.experimental_rerun()
#    for i in data:
#        st.sidebar.checkbox(i, key='dynamic_checkbox_' + i)

#def get_selected_checkboxes():
#    return [i.replace('dynamic_checkbox_','') for i in st.session_state.keys() if i.startswith('dynamic_checkbox_') and st.session_state[i]]


#checkbox_container(dummy_data)
#st.sidebar.write('You selected:')
#st.sidebar.write(get_selected_checkboxes())


########## MAIN PAGE ########### 
st.header(":mask: Covid-19 Dashboard")

# updates graph based on selected countries
def update_graph(selected_countries, start_date, end_date):
    filtered_df=df_final[(df_final['location'].isin(selected_countries)) & (df_final['date'] >= start_date) & (df_final['date'] <= end_date)]
    fig = px.line(filtered_df, x='date', y='new_cases_smoothed', color='location')
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='New cases (smoothed)',
        legend_title='Location'
    )
    st.plotly_chart(fig)


# calls the update function initially and whenever selected options change 
update_graph(selected_countries, select_date[0].strftime('%Y-%m-%d'), select_date[1].strftime('%Y-%m-%d'))
#st.multiselect("Select countries:",countries, default = selected_countries, on_change=update_graph)

#filter data
filtered_df = df_final[(df_final.date == select_date)]
filtered_df = df_final[(df_final['location'].isin(selected_countries))] 


# -- Get the user input
year_col, continent_col,= st.columns([5,5])

with year_col:
    year_choice = st.selectbox(
       "Choose a year",
        ("2020","2021","2022","2023"),
    )
with continent_col:
    continent_choice = st.selectbox(
        "Chooose Continent",
        ("All", "Asia", "Europe", "Africa", "Americas", "Oceania"),
    )

# -- Apply the year filter given by the user
filtered_df = df_final[(df_final.year == year_choice)]
# -- Apply the continent filter
#if continent_choice != "All":
#    filtered_df = filtered_df[filtered_df.continent == continent_choice]

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


df=filtered_df[["total_deaths","total_deaths","new_cases","new_deaths"]].apply(lambda x: (x-x.mean())/ x.std(), axis=0)
st.line_chart(df)
fig.update_layout(title="total cases vs. total deaths vs ")
