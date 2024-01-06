# -*- coding: utf-8 -*-
"""
Created on Tue Dec 12 22:02:42 2023

@author: jeffr
"""
import espn_api
from espn_api.basketball import League
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


def get_weekly_scores(matchup):
    
    home_tuple = (matchup.home_team.team_name,matchup.home_stats)
    
    away_tuple = (matchup.away_team.team_name,matchup.away_stats)
    
    
    return home_tuple,away_tuple

def compare_stats(stats_ls,stats1,stats2):
    
    
    cnt1 = 0
    cnt2 = 0
    cntT = 0
    
    for i in stats_ls:
        
        st1 = stats1.loc[0, i]
        st2 = stats2.loc[0, i]
        if(i == 'TO.value'):
            if(st1 > st2):
                cnt2 +=1
            elif(st1 < st2):
                cnt1 += 1
                
            else: 
                cntT+=1
        else:
            if(st1 > st2):
                cnt1 +=1
            elif(st1 < st2):
                cnt2 += 1
                
            else: 
                cntT+=1
    
    return cnt1,cnt2,cntT


def calculate_matchup(h2h,stats_ls):
    
    num_cats = float(len(stats_ls))
    
    team1_conditions = [
        (h2h['Team1Cat'] > num_cats / 2),  # Team 1 wins
        (h2h['Team2Cat'] >= num_cats / 2),  # Team 1 loses
        (h2h['Team1Cat'] == h2h['Team2Cat'])  # Tie
    ]
    
    team1_results = [1, 0, 0.5]

    # Apply the conditions and store the numerical result in a new column 'Team1Result'
    h2h['Team1Result'] = np.select(team1_conditions, team1_results, default=0)
    
    team2_conditions = [
        (h2h['Team2Cat'] > num_cats / 2),  # Team 2 wins
        (h2h['Team1Cat'] > num_cats / 2),  # Team 2 loses
        (h2h['Team2Cat'] == h2h['Team1Cat'])  # Tie
    ]

    team2_results = [1, 0, 0.5]

    # Apply the conditions and store the numerical result in a new column 'Team2Result'
    h2h['Team2Result'] = np.select(team2_conditions, team2_results, default=0)
    
    return h2h


def calculate_h2h(df,team_combinations,stats_ls,starting_week =1,ending_week=8):
    
    h2h= pd.DataFrame(columns=['Team1', 'Team2','Week','Team1Cat','Team2Cat','TieCat'])
    
    
    for team1, team2 in team_combinations:
        
        for w in range(starting_week,ending_week+1):
            
            temp = df[df['week'] ==w]
            stats1 = temp[temp['Team'] == team1][stats_ls].reset_index(drop=True)
            stats2 = temp[temp['Team'] == team2][stats_ls].reset_index(drop=True)
           
            cnt1,cnt2,cnt3 = helper.compare_stats(stats_ls,stats1, stats2)
            h2h.loc[len(h2h)] = [team1,team2,w,cnt1,cnt2,cnt3]
            
    h2h = calculate_matchup(h2h, stats_ls)
    


    h2h_agg = h2h.groupby(['Team1', 'Team2'])[['Team1Result', 'Team2Result']].sum().reset_index()        
    h2h_agg['Result'] = h2h_agg.apply(lambda row: f"{row['Team1Result']}-{row['Team2Result']}", axis=1)
    h2h_agg['win%'] = h2h_agg['Team1Result'] / (h2h_agg['Team1Result'] + h2h_agg['Team2Result'])
    
    h2h_agg['win%'] = h2h_agg['win%'].round(3)


    def style_grid(val):
        return 'text-align: center; font-size: 12px;'



    teamlevel = h2h_agg[(h2h_agg['Team1'] != h2h_agg['Team2'])]
    teamlevel = teamlevel .groupby(['Team1'])[['Team1Result', 'Team2Result']].sum().reset_index()
    teamlevel['win%'] = teamlevel['Team1Result'] / (teamlevel['Team1Result'] + teamlevel['Team2Result'])
    
    teamlevel['win%'] = teamlevel['win%'].round(3)

    teamlevel = teamlevel.rename(columns={'Team1Result':'Wins','Team2Result':'Losses:'})

    teamlevel = teamlevel.sort_values(by='win%', ascending=False)

    teamlevel = teamlevel.reset_index(drop = True)
    
    return h2h_agg,teamlevel



