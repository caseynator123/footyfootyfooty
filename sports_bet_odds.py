#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 15 15:54:43 2023

@author: caseyh
"""
import os

import pandas as pd
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
from bs4 import BeautifulSoup
import requests
from datetime import datetime

disposals = ['To Get 15 or More Disposals',
            'To Get 20 or More Disposals',
            'To Get 25 or More Disposals',
            'To Get 30 or More Disposals']
team_mapping = {'richmond':'RCH','geelong':'GEE',
                'north-melbourne':'NTH','port-adelaide':'POR',
                'gold-coast':'GCS','melbourne':'MEL',
                'greater-western-sydney':'GWS','hawthorn':'HAW',
                'carlton':'CAR','brisbane':'BRL',
                'collingwood':'COL','adelaide':'ADE',
                'fremantle':'FRE','western-bulldogs':'WBD',
                'sydney':'SYD','west-coast':'WCE',
                'st-kilda':'STK','essendon':'ESS'}

def get_odds(r):
    url = f'https://www.sportsbet.com.au/betting/australian-rules/afl/round-{r}'
    
    day = datetime.now().strftime("%A").lower()
    
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    tmp = soup.find_all('script')
    
    game_urls = []
    for i in tmp[:9]:
        try:
            url_find = re.compile(r'https://www.sportsbet.com.au/betting/australian-rules/afl/(.*?)\-\d{7}')
            game_url = url_find.search(i.text)
            game_urls.append(game_url.group())
        except:
            continue
    
    r_search = re.compile(r'\/(\w*\-?\w*\-?\w*)\-v\-(\w*\-?\w*\-?\w*)\-')
    game_list = []
    for game in game_urls:
        game_list.append(r_search.findall(game))
        
    driver = webdriver.Chrome()
    driver.set_window_size(700,800)
    
    output = pd.DataFrame({},columns = ['teams','round','Player', 'disposals', 'odds'])
    
    for game, game_url in zip(game_list, game_urls):
        driver.get(game_url)
        try:
            first_click = driver.find_element_by_xpath('(//*[@class="size14_f7opyze medium_f1wf24vo"])')
            first_click.click()
            
            for i in range(1,7):
                if driver.find_element_by_xpath(f'(//*[@class="size14_f7opyze medium_f1wf24vo"])[{i}]').text == 'Disposal Markets':
                    disposal_market = driver.find_element_by_xpath(f'(//*[@class="size14_f7opyze medium_f1wf24vo"])[{i}]')
            
            
            disposal_market.click()
            time.sleep(3)
            
            for i in range(5,50):
                try:
                    tmp = driver.find_element_by_xpath(f'(//*[@class="size14_f7opyze bold_f1au7gae"])[{i}]').text
                except:
                    continue
                if tmp in disposals:
    
                    dis = driver.find_element_by_xpath(f'(//*[@class="size14_f7opyze bold_f1au7gae"])[{i}]')
    
                    dis.click()
    
                    player = driver.find_element_by_xpath('(//*[@class="outcomeContainer_f1wc7xgg outcomeDetailsFirst_f162fqwy"])').text.split('\n')
                    
                    new_row = {'Player': player[0].lower(), 'teams': f'{game[0][0]} v {game[0][1]}', 'round':f'R{r}', 'disposals':tmp,'odds':player[-1]}
                    output.loc[len(output)] = new_row
    
                    for j in range(1,50):
                        try:
    
                            tmp1 = driver.find_element_by_xpath(f'(//*[@class="outcomeContainer_f1wc7xgg"])[{j}]').text.split('\n')
                            
                            new_row = {'Player': tmp1[0].lower(), 'teams': f'{game[0][0]} v {game[0][1]}', 'round':f'R{r}', 'disposals':tmp,'odds':tmp1[-1]}
                            output.loc[len(output)] = new_row
                        except:
                            continue
                    
                    dis.click()
                    time.sleep(2)
                
        except:
            continue
    
    output['home'] = output['teams'].apply(lambda x: x.split(' v ')[0])
    output['away'] = output['teams'].apply(lambda x: x.split(' v ')[1])
    
    for key in team_mapping.keys():
         output.loc[output['home']==key, 'home'] = team_mapping[key]
    for key in team_mapping.keys():
        output.loc[output['away']==key, 'away'] = team_mapping[key]     

    directory = os.getcwd()
    output.to_csv(f'{directory}/sportsbet_odds/r{r}/disposal_markets_{day}.csv', index = False)

get_odds(r='19')

























