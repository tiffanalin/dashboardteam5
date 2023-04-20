from libs import *

def get_choice(cases_or_deaths, cases_or_deaths_choices):
    if cases_or_deaths == cases_or_deaths_choices[0]:
        choice = 'cases'
    elif cases_or_deaths == cases_or_deaths_choices[1]:
        choice = 'deaths'
    return choice


# getting special name of column in df
def get_choice_and_column(cases_or_deaths, cases_or_deaths_choices, data_type, data_type_choices):
    choice = get_choice(cases_or_deaths, cases_or_deaths_choices)
    
    column = ''
    if data_type == data_type_choices[0]: #'raw number':
        column = 'new_'+ choice +'_per_million'
    elif data_type == data_type_choices[1]: #'cumulative number':
        column = 'cumulative_' + choice
    elif data_type == data_type_choices[2]: #'average - 7 days':
        column = 'average_' + choice

    return (choice, column)


def get_peak(df, calc_base_on_column, choice):
    column_name = '1_derivative_' + calc_base_on_column + choice
    
    df[column_name] = df[calc_base_on_column + choice].diff()
    zoom = max(df[column_name]) - min(df[column_name])
    zoom = zoom / 100 * 15
    df[column_name] = df[column_name] * zoom
    
    # fix first value
    df.loc[0, '1_derivative_' + calc_base_on_column + choice] = 0
    
    # calculate peaks
    peaks = np.where(np.diff(np.sign(df['1_derivative_'+ calc_base_on_column + choice])) == -2)[0]
    df['peak_' + choice] = np.nan
    df.iloc[peaks, df.columns.get_loc('peak_' + choice)] = df.iloc[peaks, df.columns.get_loc(calc_base_on_column + choice)].values
    
    return df


def calc_peaks(df):
    calc_base_on_column = 'cumulative_'
    
    choice = 'cases'
    df = get_peak(df, calc_base_on_column, choice)
    
    choice = 'deaths'
    df = get_peak(df, calc_base_on_column, choice)
    return df
