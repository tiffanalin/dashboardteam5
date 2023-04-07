from libs import *

# getting special name of column in df
def get_choice(cases_or_deaths, data_type):
    choice = ''

    if cases_or_deaths == 'cases':
        choice = 'cases'
    elif cases_or_deaths == 'deaths':
        choice = 'deaths'

    if data_type == 'raw number':
        column = 'new_'+ choice +'_smoothed'
    elif data_type == 'cumulative number':
        column = 'cumulative_' + choice
    elif data_type == 'average - 7 days':
        column = 'average_' + choice

    return (choice, column)

def get_peaks(filtered_df, column, cases_or_deaths):
    peaks, _ = find_peaks(filtered_df[column])
    peak_column = 'peak_' + cases_or_deaths
    filtered_df[peak_column] = np.nan
    filtered_df.loc[peaks, peak_column] = filtered_df.loc[peaks, column]
    return filtered_df