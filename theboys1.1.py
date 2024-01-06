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

r= range(1,league.currentMatchupPeriod+1,1)
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

Season_gran,Season_agg = helper.calculate_h2h(df,team_combinations,stats_ls,1,league.currentMatchupPeriod-1)
Season_gran = Season_gran.pivot(index='Team1', columns='Team2', values='Result')
Season_gran.to_html('Season_granular_.html', classes='table table-striped', escape=False, render_links=True)
Season_agg.to_html('Season_agg.html',classes='table table-striped', escape=False, render_links=True)


prev_week_gran,prev_week_agg = helper.calculate_h2h(df,team_combinations,stats_ls,league.currentMatchupPeriod-1,league.currentMatchupPeriod-1)
prev_week_gran = prev_week_gran.pivot(index='Team1', columns='Team2', values='Result')
prev_week_gran.to_html('prev_week_granular_.html', classes='table table-striped', escape=False, render_links=True)
prev_week_agg.to_html('prev_week_agg.html',classes='table table-striped', escape=False, render_links=True)


curr_week_gran,curr_week_agg = helper.calculate_h2h(df,team_combinations,stats_ls,league.currentMatchupPeriod,league.currentMatchupPeriod)
curr_week_gran = curr_week_gran.pivot(index='Team1', columns='Team2', values='Result')
curr_week_gran.to_html('curr_week_granular.html', classes='table table-striped', escape=False, render_links=True)
curr_week_agg.to_html('curr_week_agg.html',classes='table table-striped', escape=False, render_links=True)





print(league.currentMatchupPeriod)

