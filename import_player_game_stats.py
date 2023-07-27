#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 10 17:21:07 2023

@author: caseyh
"""

import os
import pandas as pd
import numpy as np

os.getcwd()

teams_str = ['adelaide', 'brisbanel', 'carlton', 'collingwood', 'essendon',
             'fremantle', 'geelong', 'goldcoast', 'gws', 'hawthorn', 'melbourne',
             'kangaroos', 'padelaide', 'richmond', 'stkilda', 'swans', 'westcoast',
             'bullldogs']

statistics = ['Disposals',
              'Kicks',
              'Marks',
              'Handballs',
              'Goals',
              'Behinds',
              'Hit Outs',
              'Tackles',
              'Rebounds',
              'Inside 50s',
              'Clearances',
              'Clangers',
              'Frees',
              'Frees Against',
              'Contested Possessions',
              'Uncontested Possessions',
              'Contested Marks',
              'Marks Inside 50',
              'One Percenters',
              'Bounces',
              'Goal Assists',
              '% Played',
              'Subs']

opponent_mapping = {'RI': 'RCH', 'GE': 'GEE', 'NM': 'NTH', 'PA': 'POR', 'GC': 'GCS', 'ME': 'MEL', 'GW': 'GWS',
                    'HW': 'HAW', 'CA': 'CAR', 'BL': 'BRL', 'CW': 'COL', 'AD': 'ADE', 'FR': 'FRE', 'WB': 'WBD',
                    'FO': 'WBD', 'SY': 'SYD', 'WC': 'WCE', 'SK': 'STK', 'ES': 'ESS'}
team_mapping = {'richmond': 'RCH', 'geelong': 'GEE', 'kangaroos': 'NTH', 'padelaide': 'POR', 'goldcoast': 'GCS',
                'melbourne': 'MEL', 'gws': 'GWS', 'hawthorn': 'HAW', 'carlton': 'CAR', 'brisbanel': 'BRL',
                'collingwood': 'COL', 'adelaide': 'ADE', 'fremantle': 'FRE', 'bullldogs': 'WBD', 'swans': 'SYD',
                'westcoast': 'WCE', 'stkilda': 'STK', 'essendon': 'ESS'}


def rearrange(value):
    return ' '.join(' '.join(value.lower().split(', ')[::-1]).split('-'))


def clean(value):
    if value == '-':
        return 0
    elif type(value) == float:
        return np.nan
    elif type(int(value)) == int:
        return int(value)


def get_data(year, team):
    url = f'https://afltables.com/afl/stats/teams/{team}/{year}_gbg.html'
    stat_tables = pd.read_html(url, attrs={'class': 'sortable'}, flavor='bs4')
    try:
        output = pd.DataFrame({})
        
        for table in stat_tables:
            desc = table.columns[0][0]
            df = table[desc]
            
            # get stats from tables
            player_stats = df[(df['Player'] != 'Totals') & (df['Player'] != 'Opponent')].drop(columns='Tot')
            
            # flatten dataset into stat columns
            player_stats = pd.melt(player_stats, id_vars=['Player']).rename(columns={
                'variable': 'round', 'value': desc})
            
            # if empty then concat else merge with table
            if output.shape[0] == 0:
                output = pd.concat([output, player_stats])
            else:
                output = output.merge(player_stats, how='left', on=['Player', 'round'])
        
        # get opponent team has played
        opp_played = df[df['Player'] == 'Opponent'].melt(id_vars='Player').drop(columns='Player').rename(columns={
            'variable': 'round', 'value': 'opponent'})
        output = output.merge(opp_played, how='left', on=['round'])
        
        # add team and year to table
        output['team'] = team
        output['year'] = year
        
        output = output.fillna(np.nan)
        
        for col in output.columns:
            try:
                output[col] = output[col].apply(lambda x: clean(x))
            except:
                continue
        
        print(f'data collected: {year} {team}')
        return output
        
    except:
        print(f'no data: {year} {team}')
        

main = pd.DataFrame({})
for team in teams_str:
    for year in range(2023,2024):
        
        df = get_data(year, team)  
        main = pd.concat([main, df])
        
        # change team names to 3 letter code
        for key in opponent_mapping.keys():
                main.loc[main['opponent'] == key, 'opponent'] = opponent_mapping[key]
        for key in team_mapping.keys():
            main.loc[main['team'] == key, 'team'] = team_mapping[key]
        main['Player'] = main['Player'].apply(lambda x: rearrange(x))

        directory = os.getcwd()
        main.to_csv(f'{directory}/player_stats/{year}_player_stats.csv', index=False)

