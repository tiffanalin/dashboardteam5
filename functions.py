from libs import *

# getting special name of column in df
def get_choice(cases_or_deaths, data_type, data_type_choices):
    st.write("get_choice")
    st.write("Cases or? - ",cases_or_deaths)
    st.write("Type - ",data_type)
    st.write()
    choice = ''

    if cases_or_deaths == 'cases':
        choice = 'cases'
    elif cases_or_deaths == 'deaths':
        choice = 'deaths'

    column = ''
    
    if data_type == data_type_choices[0]: #'raw number':
        column = 'new_'+ choice +'_per_million'
    elif data_type == data_type_choices[1]: #'cumulative number':
        column = 'cumulative_' + choice
    elif data_type == data_type_choices[2]: #'average - 7 days':
        column = 'average_' + choice

    st.write("choise! - ",choice)
    st.write("column - ",column)
    
    return (choice, column)


def get_peaks(filtered_df, column, cases_or_deaths):
    peaks, _ = find_peaks(filtered_df[column])
    peak_column = 'peak_' + cases_or_deaths
    filtered_df[peak_column] = np.nan
    filtered_df.loc[peaks, peak_column] = filtered_df.loc[peaks, column]
    return filtered_df