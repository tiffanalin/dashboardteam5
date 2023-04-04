import streamlit as st
import pandas as pd
import plotly.express as px
import warnings
warnings.filterwarnings("ignore")

dataset_url='https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv'

# read csv from a URL
@st.cache_data
def get_data() -> pd.DataFrame:
    return pd.read_csv(dataset_url)


df = get_data()

df["year"]=df["date"].str[0:4]

#print(df.shape)
#print('Total unique continents:',len(df.continent.unique()))
#print('Total unique countries:',len(df.location.unique()))
#print('Date span:',df.date.min(),df.date.max())
#print("Data intformation",df.info())
#print('Data describtion',df.describe())

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
def get_Final_df(df,transform_cols):

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


    #remove non-country data from 'location'
    filter_out=['Asia','Europe','High income','Western Sahara','Upper middle income','Oceania','North America','Low income', 'Lower middle income','European Union','South America','Africa']
    df_final = df[~df['location'].isin(filter_out)]

    #normalize data to population (1,000,000 people)
    df[['total_cases',	'new_cases',	'total_deaths',	'new_deaths',	'total_cases_per_million']]=df[['total_cases',	'new_cases',	'total_deaths',	'new_deaths',	'total_cases_per_million']].apply(lambda x: (x/(df["population"])*1000000),axis=0)

    return df_final

df_final=get_Final_df(df,transform_cols)
countries_list=df_final.location.unique()

#data
st.header("Covid-19 Data")
# -- Get the user input

if 'dummy_data' not in st.session_state.keys():
    dummy_data = countries_list
    st.session_state['dummy_data'] = dummy_data
else:
    dummy_data = st.session_state['dummy_data']

def checkbox_container(data):
    st.sidebar.header('Select Countries: ')
   
    cols = st.sidebar.columns(2)
   
    if cols[0].button('Select All'):
        for i in data:
            st.session_state['dynamic_checkbox_' + i] = True
        st.experimental_rerun()
    if cols[1].button('UnSelect All'):
        for i in data:
            st.session_state['dynamic_checkbox_' + i] = False
        st.experimental_rerun()
    for i in data:
        st.sidebar.checkbox(i, key='dynamic_checkbox_' + i)

def get_selected_checkboxes():
    return [i.replace('dynamic_checkbox_','') for i in st.session_state.keys() if i.startswith('dynamic_checkbox_') and st.session_state[i]]


checkbox_container(dummy_data)
st.sidebar.write('You selected:')
st.sidebar.write(get_selected_checkboxes())

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
