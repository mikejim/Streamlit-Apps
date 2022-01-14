# The following example follows a tutorial from FreeCodeCamp, available at:
# https://www.youtube.com/watch?v=JwSS70SZdyM

import streamlit as st
import pandas as pd
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

st.title('NBA Player Stats Explorer')

st.markdown("""
This app performs simple webscrapping of NBA player stats data! Python libraries
used: base64, pandas, streamlit.
Datasource: [Basketball-reference.com](https://www.basketball-reference)
""")
# Sidebar is the bar on the left of the page
st.sidebar.header('User Input Features')
# The first argument is the label of the selectbox.
# The second argument is a reversed list using years 1950 to 2021 (2021 first)
selected_year = st.sidebar.selectbox('Year', list(reversed(range(1950, 2022))))

# Web scraping of NBA player stats
@st.cache
def load_data(year):
    url = "https://www.basketball-reference.com/leagues/NBA_" + str(year) + "_per_game.html"
    html = pd.read_html(url, header=0)
    df = html[0]
    # Drop some redundant layer
    raw = df.drop(df[df.Age == 'Age'].index)
    raw = raw.fillna(0)
    # Delete some redundant index Rk
    playerstats = raw.drop(['Rk'], axis=1)
    return playerstats
playerstats = load_data(selected_year)

# Sidebar - Team selection to choose the team to be displayed on the table
# Uses the playerstats dataframe, from which it will use the unique values
# from the TM column
sorted_unique_team = sorted(playerstats.Tm.unique())
# Multiselect function that will get the sorted teams and list them in the
# sidebar. 3rd and 2nd argument are the same for position and value of the multis
selected_team = st.sidebar.multiselect('Team', sorted_unique_team, sorted_unique_team)

# Sidebar - Position selection, these are NBA position names
unique_pos = ['C', 'PF', 'SF', 'PG', 'SG']
selected_pos = st.sidebar.multiselect('Position', unique_pos, unique_pos)

# Filtering data using the TM column asking if it is within the selected teams
df_selected_team = playerstats[(playerstats.Tm.isin(selected_team)) & (playerstats.Pos.isin(selected_pos))]

# Display the labels using the dimensions of the dataframe
st.header('Display Player Stats of Selected Team(s)')
st.write('Data Dimension ' + str(df_selected_team.shape[0]) + ' rows and ' + str(df_selected_team.shape[1]) + ' columns')

test = df_selected_team.astype(str)
st.dataframe(test)

#st.dataframe(df_selected_team)

# Download NBA players stats data
# https://discuss.streamlit.io/t/how-to-download-file-in-streamli/1806
def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{64}" download="">Download CSV File</a>'
    return href

st.markdown(filedownload(df_selected_team), unsafe_allow_html=True)

# Heatmap that will show a button to load the heat map
if st.button('Intercorrelation Heatmap'):
    st.header('Intercorrelation Matrix Heatmap')
    # Use the selected team to export it to a csv and load it from there
    df_selected_team.to_csv('output.csv', index=False)
    df = pd.read_csv('output.csv')

    # Intercorrelation calculation
    corr = df.corr()
    mask = np.zeros_like(corr)
    mask[np.triu_indices_from(mask)] = True
    with sns.axes_style("white"):
        f, ax = plt.subplots(figsize=(7, 5))
        ax = sns.heatmap(corr, mask=mask, vmax=1, square=True)
    st.pyplot(f)
