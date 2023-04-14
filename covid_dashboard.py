from libs import *
from functions import *

from datetime import date, timedelta

# OWID Covid-19 Data
# dataset_url='https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv'
path = 'data/'
file_name = 'owid-covid-data.csv'
data_file = path + file_name

# read csv from a URL
@st.cache_data
def get_data() -> pd.DataFrame:
    return pd.read_csv(data_file)
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
def get_final_df(df,transform_cols) -> pd.DataFrame:
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
    # df_final[['total_cases',	'new_cases',	'total_deaths',	'new_deaths',	'total_cases_per_million']]=df_final[['total_cases',	'new_cases',	'total_deaths',	'new_deaths',	'total_cases_per_million']].apply(lambda x: (x/(df["population"])*1000000),axis=0)

    # raw data
    # new_cases_per_million

    # cumulative data 
    # total
    df_final['cumulative_cases'] = df_final['total_cases_per_million']
    df_final['cumulative_deaths'] = df_final['total_deaths_per_million']
    
    # average - for N days
    # smoth
    df_final['average_cases'] = df_final['new_cases_smoothed_per_million']
    df_final['average_deaths'] = df_final['new_deaths_smoothed_per_million']

    # peak detection
    return df_final


data_load_state = st.text('Loading data...')
df_final = get_final_df(df, transform_cols)
data_load_state.text("Done with loading!)")
countries = sorted(df_final['location'].unique())

if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(df_final)

continent=['Asia', 'Europe', 'Africa' ,'Oceania', 'North America' ,'South America']

# SIDEBAR
# select cases or deaths
st.sidebar.title(":mag_right: View Options:")
cases_or_deaths_choices = ['Cases', 'Deaths']
cases_or_deaths = st.sidebar.selectbox("View cases or deaths",cases_or_deaths_choices)

# select data type
data_type_choices = ['Raw number', 'Cumulative number', 'Average - 7 days']
data_type = st.sidebar.selectbox("View Data type", data_type_choices)

if data_type == data_type_choices[1]: #'cumulative number'
    # select to show peaks
    show_peaks = st.sidebar.checkbox("Show peaks")

show_by=st.sidebar.radio(
        "Show by Countries or Continent👉",
        key="visibility",
        options=["Countries", "Continent"],
    )
if show_by=="Countries":
    all_countries = st.sidebar.checkbox("Select all countries")
    if all_countries:
        selected_countries = st.sidebar.multiselect("Select countries", countries,countries)
    else:
        selected_countries = st.sidebar.multiselect("Select countries", countries,default=["France"])
    filtered_place = df_final[(df_final['location'].isin(selected_countries))] 
    
elif show_by=="Continent":
    all_continent=st.sidebar.checkbox("Select all continent")
    if all_continent:
        selected_continent = st.sidebar.multiselect("Select countries", continent,continent)
    else:
        selected_continent = st.sidebar.multiselect("Select countries", continent,default=["Europe"])
    filtered_place = df_final[(df_final['continent'].isin(selected_continent))] 


# MAIN PAGE 
st.header(":mask: Covid-19 Data")



filtered_place['date'] = pd.to_datetime(filtered_place['date'])
filtered_place['d']=[i.date() for i in filtered_place['date']]
min_date=filtered_place['d'].min()
max_date=filtered_place['d'].max()


values = st.slider(
    'Select a date range: ',
    min_value=min_date,max_value=max_date, value=(date(2021,5,7),date(2022,4,7)),step=timedelta(days=1))


filtered_df = filtered_place[(filtered_place['d'] >= values[0]) & (filtered_place['d']<= values[1])]

# General data preparation - for all app
# get cases, data type
choice, column = get_choice(cases_or_deaths, cases_or_deaths_choices, data_type, data_type_choices)


fig = px.line(filtered_df, x = 'date', y = column, color = 'location',labels={
                     "date": "Date (day)",
                     column: data_type+" Of Cases Per Million" if choice == 'cases' else data_type+" Of Deaths Per Million" 
                 })
fig.update_layout(title = cases_or_deaths + " Vs. Time")
st.plotly_chart(fig)

y_col, size_choice,= st.columns([5, 5])
with y_col:
    y_choice = st.selectbox(
        "Choose Y axis:",
        ("total_cases_per_million","2022","total_deaths_per_million"),
    )
with size_choice:
    size_choice = st.selectbox(
        "Size of each point?",
        ("total_deaths_per_million","total_cases_per_million"),
    )

# -- Apply the year filter given by the user
#graph2_data = filtered_place[(df_final.year == year_choice)]
# -- Apply the continent filter

# -- Create the figure in Plotly
fig = px.scatter(filtered_place.groupby(['location',"year"])[['iso_code',"total_cases_per_million",'population',"total_deaths_per_million"]].max().reset_index(),
    x="year",
    y=y_choice,
    size=size_choice,
    color="location",
    hover_name="iso_code",
    
    size_max=30,labels={
                     "year": "Year",
                     y_choice: "Total Cases Per Million" if y_choice== "total_cases_per_million" else "Total Deaths Per Million"
                 }
)
fig.update_layout(title=" ")
# -- Input the Plotly chart to the Streamlit interface
st.plotly_chart(fig, use_container_width=True)
