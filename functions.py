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
    zoom = (df[column_name].max() - df[column_name].min()) / 100
    df[column_name] *= zoom / 5

    # fix first value
    df.loc[df.index[0], column_name] = 0
    
    # calculate peaks
    derivative_col = '1_derivative_'+ calc_base_on_column + choice
    
    # Find the index of peaks in the first derivative column
    # A peak is identified as a point where the derivative changes from negative to positive
    # peaks = df[derivative_col][((df[derivative_col].shift() < 0) & (df[derivative_col] > 0))].index
    positive_values = df[derivative_col] > 0
    shifted_values = df[derivative_col].shift() < 0
    peaks = df[derivative_col][(shifted_values & positive_values)].index

    df['peak_' + choice] = np.nan
    df.loc[peaks, 'peak_' + choice] = df.loc[peaks, calc_base_on_column + choice].values

    return df


def calc_peaks(df):
    calc_base_on_column = 'cumulative_'
    
    choice = 'cases'
    df_cases = get_peak(df, calc_base_on_column, choice)
    
    choice = 'deaths'
    df_deaths = get_peak(df_cases, calc_base_on_column, choice)
    return df_deaths
