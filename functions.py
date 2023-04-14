from libs import *

# getting special name of column in df
def get_choice(cases_or_deaths, cases_or_deaths_choices, data_type, data_type_choices):
    choice = ''
    if cases_or_deaths == cases_or_deaths_choices[0]:
        choice = 'cases'
    elif cases_or_deaths == cases_or_deaths_choices[1]:
        choice = 'deaths'

    column = ''
    if data_type == data_type_choices[0]: #'raw number':
        column = 'new_'+ choice +'_per_million'
    elif data_type == data_type_choices[1]: #'cumulative number':
        column = 'cumulative_' + choice
    elif data_type == data_type_choices[2]: #'average - 7 days':
        column = 'average_' + choice

    return (choice, column)


def get_peaks(filtered_df, column, cases_or_deaths):
    peaks, _ = find_peaks(filtered_df[column])
    peak_column = 'peak_' + cases_or_deaths
    filtered_df[peak_column] = np.nan
    filtered_df.loc[peaks, peak_column] = filtered_df.loc[peaks, column]
    return filtered_df