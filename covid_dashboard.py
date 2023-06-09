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
    df=pd.read_csv(data_file)
    df=df[['iso_code','date','continent','location','total_cases',
                  'total_deaths',
                  'total_deaths_per_million',
                  'total_cases_per_million',
                  'new_cases_per_million',
                  'new_deaths_per_million',
                  'new_cases_smoothed_per_million',
                  'new_deaths_smoothed_per_million'
                  ]]
    return df
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
                  'total_cases_per_million',
                  'new_cases_per_million',
                  'new_deaths_per_million',
                  'new_cases_smoothed_per_million',
                  'new_deaths_smoothed_per_million'
                  ]
#Clean and fill missing data
@st.cache_data
def get_final_df(df,transform_cols) -> pd.DataFrame:
    
    df["year"] = df["date"].str[0:4] #add year column
    df.date = pd.to_datetime(df.date)  # convert string date to datetime
    df['day']=[i.date() for i in df['date']]    #add day column

    #remove non-country data from 'location'
    filter_out = ['World','Asia','Europe','High income','Western Sahara','Upper middle income','Oceania','North America','Low income', 'Lower middle income','European Union','South America','Africa']
    df = df[~df['location'].isin(filter_out)]

    # raw data - used new_cases_per_million

   # cumulative data - total
    df['cumulative_cases'] = df['total_cases_per_million']
    df['cumulative_deaths'] = df['total_deaths_per_million']
    
    # average - for N days - smooth
    df['average_cases'] = df['new_cases_smoothed_per_million']
    df['average_deaths'] = df['new_deaths_smoothed_per_million']

    # loop through and subset each country to a list
    country_dfs = []

    # loop through each country
    for country in df.location.unique():
        df_country = df[df.location == country]        
        df_country = df_country.sort_values(by='date')  # sort by date
        
        # apply transformation
        for col in transform_cols:
            df_country[col] = update_series(df_country[col]).astype(int)

        df_country = calc_peaks(df_country)
        
        country_dfs.append(df_country)  # append unique country dataframe to list
        
    df_final = pd.concat(country_dfs)
    df_final = df_final.reset_index().sort_values(by=['location', 'date'])
    df_final = df_final.fillna(0)
   
    # remove duplicated columns
    df_final = df_final.loc[:, ~df_final.columns.duplicated()]

    # peak detection
    return df_final


data_load_state = st.text('Loading data...')

#get final df
df_final = get_final_df(df, transform_cols)
data_load_state.text("Done with loading!")

countries = sorted(df_final['location'].unique())
continent= sorted(df_final['continent'].unique())
#get contries and continent
min_date=df_final['day'].min()
max_date=df_final['day'].max()

# SIDEBAR
st.sidebar.title(":mag_right: View Options:")

#show df
if st.sidebar.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(df_final)

#select continent
show_by=st.sidebar.radio(
        "Show by Countries or Continent👉",
        key="visibility",
        options=["Countries", "Continent"],)

if show_by=="Countries":
    point_color="location" 
    selected_countries = st.sidebar.multiselect("Select countries", countries,default=["France"])
    filtered_place_graph1 = df_final[(df_final['location'].isin(selected_countries))]
    filtered_place_graph2 = df_final[(df_final['location'].isin(selected_countries))] 
    filtered_place_graph2 = filtered_place_graph2.groupby(["location","year"]).max().reset_index()
elif show_by=="Continent":
    point_color="continent" 
    all_continent=st.sidebar.checkbox("Select all continent")
    if all_continent:
        selected_continent = st.sidebar.multiselect("Select countinent", continent,continent)
    else:
        selected_continent = st.sidebar.multiselect("Select countinent", continent,default=["Europe"])
    
    filtered_place_graph1 = df_final[(df_final['continent'].isin(selected_continent))]
    filtered_place_graph1 = filtered_place_graph1.groupby(["continent","day"]).sum().reset_index()
    filtered_place_graph2 = df_final[(df_final['continent'].isin(selected_continent))]
    filtered_place_graph2 = filtered_place_graph2.groupby(["continent","year"]).max().reset_index()  



# MAIN PAGE 
st.header(":mask: Covid-19 Data")

#add time double_ended_slider
#values = st.slider(
#    'Select a date range: ',
#    min_value=min_date,max_value=max_date, value=(date(2021,5,7),date(2022,4,7)),step=timedelta(days=1))

#filtered_graph1=filtered_place_graph1[(filtered_place_graph1['day'] >= values[0]) & (filtered_place_graph1['day']<= values[1])]

# select cases or deaths and data type (raw number, cumulative, average 7 days)
cases_or_deaths, data_type,= st.columns([5, 5])

with cases_or_deaths:
    cases_or_deaths_choices = ['Cases', 'Deaths']
    cases_or_deaths = st.selectbox("View cases or deaths",cases_or_deaths_choices)
    
with data_type:
    data_type_choices = ['Raw number', 'Cumulative number', 'Average - 7 days']
    data_type = st.selectbox("View Data type", data_type_choices)

show_peaks = None
if (data_type == data_type_choices[1] and show_by=='Countries'): #'cumulative number'
    # select to show peaks
    show_peaks = st.checkbox("Show peaks")


#add time double_ended_slider
values = st.slider('Select a date range: ',min_value=min_date,max_value=max_date, value=(date(2021,5,7),date(2022,4,7)),step=timedelta(days=1))

filtered_graph1 = filtered_place_graph1[(filtered_place_graph1['day'] >= values[0]) & (filtered_place_graph1['day']<= values[1])]

# General data preparation - for all app
# get cases, data type
cases_or_deaths_choice, column = get_choice_and_column(cases_or_deaths, cases_or_deaths_choices, data_type, data_type_choices)

#draw line chart
fig = px.line(filtered_graph1, x = 'day', y = column, color = 'location' if show_by=="Countries" else 'continent',labels={
                     "day": "Date (day)",
                     column: data_type+" Of Cases Per Million" if cases_or_deaths_choice == 'cases' else data_type+" Of Deaths Per Million" 
                 })

# Show peaks
if show_peaks == True:
    st.header("Showing peaks")
    # peak_column = 'peak_' + cases_or_deaths_choice
    
    calc_base_on_column = 'cumulative_'
    peak_column = '1_derivative_' + calc_base_on_column + cases_or_deaths_choice
    figs = []
    # if show_by == 'Continent':
    #     for continent in selected_continent:
    #         peak_label = '1 Derivative of ' + continent

    #         fig.add_scatter(x=filtered_graph1[filtered_graph1['continent']==continent]['date'], 
    #                         y=filtered_graph1[filtered_graph1['continent']==continent][peak_column], 
    #                         mode='markers', 
    #                         name=peak_label)
    # else:
    for country in selected_countries:
        peak_label = '1 Derivative of ' + country

        fig.add_scatter(x=filtered_graph1[filtered_graph1['location']==country]['date'], 
                        y=filtered_graph1[filtered_graph1['location']==country][peak_column], 
                        mode='markers', 
                        name=peak_label)

fig.update_layout(title = cases_or_deaths + " Vs. Time")
st.plotly_chart(fig)

CHOICES = {"total_cases_per_million":"Total Cases Per Million","total_deaths_per_million":"Total Deaths Per Million"}

def format_func(option):
    return CHOICES[option]

y_col, size_choice,= st.columns([5, 5])
with y_col:
    y_choice = st.selectbox(
        "Choose Y axis:",
        options=list(CHOICES.keys()), format_func=format_func)
    
with size_choice:
    size_choice = st.selectbox(
        "Size of each point?",
        options=list(CHOICES.keys()), format_func=format_func)
    

# -- Create the figure in Plotly

fig = px.scatter(filtered_place_graph2,
    x='year',
    y=y_choice,
    size=size_choice,
    color=point_color,
    hover_name="iso_code",    
    size_max=30,labels={
                     "year": "Year",
                     y_choice: "Total Cases Per Million" if y_choice== "total_cases_per_million" else "Total Deaths Per Million"
                 })

fig.update_layout(title="Total Cases vs. Total Deaths")
# -- Input the Plotly chart to the Streamlit interface
st.plotly_chart(fig, use_container_width=True)
