# dashboardteam5
Open source dashboarding project

Team: Mari, Hala, Tiffany

## Setup instructions:

1. Clone the repository
2. Open terminal and go to the directory of the project repository.
3. Inside your project repository, create a virtual environment with the Python venv module:

`python -m venv env`

4. Now activate your virtual environment:

`source env/bin/activate`

5. Install dependencies in your virtual environment (activated) with the command:

`python -m pip install -r requirements.txt`

## Data Source
We will use Our World in Data Covid-19 data for all countries in the world: https://github.com/owid/covid-19-data

CSV file here: https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv

## Streamlit
<b>Link to Streamlit Cloud: 
https://docs.streamlit.io/streamlit-community-cloud </b>

<b>Link to Streamlit App: 

https://tiffanalin-dashboardteam5-covid-app-8i33k2.streamlit.app/ </b>

## How to run the dashboard locally
Use this commands to install Streamlit: `pip install streamlit`

You should be able to run: `streamlit hello`

Run project with this command:
`streamlit run covid_dashboard.py`

