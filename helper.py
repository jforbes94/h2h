# -*- coding: utf-8 -*-
"""
Created on Tue Dec 12 22:02:42 2023

@author: jeffr
"""
import espn_api
from espn_api.basketball import League



def get_weekly_scores(matchup):
    
    home_tuple = (matchup.home_team.team_name,matchup.home_stats)
    
    away_tuple = (matchup.away_team.team_name,matchup.away_stats)
    
    
    return home_tuple,away_tuple

def compare_stats(stats1,stats2):
    
    stats_ls = ['PTS','3PTM','AST','BLK','FG%','FT%','REB','STL','TO']
    stats_ls = [item + '.value' for item in stats_ls]
    
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