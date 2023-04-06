from libs import *

# getting special name of column in df
def get_choice(cases_or_deaths, data_type):
    choice = ''

    if cases_or_deaths == 'Cases':
        choice = 'cases'
    elif cases_or_deaths == 'Deaths':
        choice = 'deaths'

    if data_type == 'Raw number':
        column = 'new_'+ choice +'_smoothed'
    elif data_type == 'Cumulative number':
        column = 'cumulative_' + choice
    elif data_type == 'Average - 7 days':
        column = 'average_' + choice

    return (choice, column)