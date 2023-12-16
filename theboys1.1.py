# -*- coding: utf-8 -*-
"""
Spyder Editor


This is a temporary script file.
"""

import pandas as pd
import helper
import espn_api
from espn_api.basketball import League
import itertools
from collections import OrderedDict
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os


espn_s2 = os.environ.get('ESPN_S2')
swid = os.environ.get('SWID')

# Use the values in your code
print(f"ESPN_S2: {espn_s2}")
print(f"SWID: {swid}")


league = League(league_id=1950930852, year=2024,
                espn_s2=espn_s2,
                swid=swid)
 


ls = list(range(13))
teams=[]
for i in ls:
    if i != 5:
        x= league.get_team_data(i+1)
        teams.append(x)

total_tups = []

for i in teams:
    item_tuple = (i.team_name,i.stats)
    total_tups.append(item_tuple)
    

Total = pd.DataFrame([(string, d) for string, d in total_tups], columns=['String', 'Dictionary'])
Total = pd.concat([Total['String'], pd.json_normalize(Total['Dictionary'])], axis=1)

stats_ls = ['PTS','3PTM','AST','BLK','FG%','FT%','REB','STL','TO'] 


for stat in stats_ls:
    if(stat == 'T0'):
        Total['Rank_' + stat] = Total[stat].rank(ascending=False)
    else:
        Total['Rank_' + stat] = Total[stat].rank(ascending=True)
    

df = pd.DataFrame()

r= range(1,league.currentMatchupPeriod,1)
for i in r:
        
    x = league.box_scores(i)
    week= []
    
    for j in x:
        a,b = helper.get_weekly_scores(j)
        week.append(a)
        week.append(b)
        
     
    df1 = pd.DataFrame([(string, d) for string, d in week], columns=['String', 'Dictionary'])
    df1 = pd.concat([df1['String'], pd.json_normalize(df1['Dictionary'])], axis=1)
    df1 = df1.loc[:, ~df1.columns.str.contains('result')]
    df1['week'] = i
    df = pd.concat([df,df1])

df = df.rename(columns={'String':'Team'})


team_combinations = list(itertools.combinations(df['Team'], 2))
team_combinations= list(OrderedDict.fromkeys(team_combinations))

val = '.value'
stats_ls = [item + val for item in stats_ls]


h2h= pd.DataFrame(columns=['Team1', 'Team2','Week','Team1Cat','Team2Cat','TieCat'])



for team1, team2 in team_combinations:
    
    for w in r:
        temp = df[df['week'] ==w]
        i = 'PTS.value'
        stats1 = temp[temp['Team'] == team1][stats_ls].reset_index(drop=True)
        stats2 = temp[temp['Team'] == team2][stats_ls].reset_index(drop=True)
       
        cnt1,cnt2,cnt3 = helper.compare_stats(stats1, stats2)
        h2h.loc[len(h2h)] = [team1,team2,w,cnt1,cnt2,cnt3]
        
        
# Define conditions and corresponding numerical values for Team 1
team1_conditions = [
    (h2h['Team1Cat'] >= 5),  # Team 1 wins
    (h2h['Team1Cat'] < 5) & (h2h['Team2Cat'] >= 5),  # Team 1 loses
    (h2h['Team1Cat'] == h2h['Team2Cat'])  # Tie
]

team1_results = [1, 0, 0.5]

# Apply the conditions and store the numerical result in a new column 'Team1Result'
h2h['Team1Result'] = np.select(team1_conditions, team1_results, default=0)

# Define conditions and corresponding numerical values for Team 2 (reversed logic)
team2_conditions = [
    (h2h['Team2Cat'] >= 5),  # Team 2 wins
    (h2h['Team2Cat'] < 5) & (h2h['Team1Cat'] >= 5),  # Team 2 loses
    (h2h['Team2Cat'] == h2h['Team1Cat'])  # Tie
]

team2_results = [1, 0, 0.5]

# Apply the conditions and store the numerical result in a new column 'Team2Result'
h2h['Team2Result'] = np.select(team2_conditions, team2_results, default=0)


h2h_agg = h2h.groupby(['Team1', 'Team2'])[['Team1Result', 'Team2Result']].sum().reset_index()        
h2h_agg['Result'] = h2h_agg.apply(lambda row: f"{row['Team1Result']}-{row['Team2Result']}", axis=1)
h2h_agg['win%'] = h2h_agg['Team1Result'] / (h2h_agg['Team1Result'] + h2h_agg['Team2Result'])


def style_grid(val):
    return 'text-align: center; font-size: 12px;'



teamlevel = h2h_agg[(h2h_agg['Team1'] != h2h_agg['Team2'])]
teamlevel = teamlevel .groupby(['Team1'])[['Team1Result', 'Team2Result']].sum().reset_index()
teamlevel['win%'] = teamlevel['Team1Result'] / (teamlevel['Team1Result'] + teamlevel['Team2Result'])

teamlevel = teamlevel.rename(columns={'Team1Result':'Wins','Team2Result':'Losses:'})

teamlevel = teamlevel.sort_values(by='win%', ascending=False)

teamlevel = teamlevel.reset_index(drop = True)

    



teamlevel.to_html('styled_h2h_agg.html', classes='table table-striped', escape=False, render_links=True)

pivot_df = h2h_agg.pivot(index='Team1', columns='Team2', values='Result')

pivot_df.to_html('styled_h2h_pivot.html',classes='table table-striped', escape=False, render_links=True)
