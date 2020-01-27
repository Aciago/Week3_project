"""
IronHack project 3
January 24th, 2020

Nick M.

Short description:
    Scrape Formula1.com website for historic Grand Prix data. Save raw data, find drivers with most wins overall.
    Return data as a visualization.
    Save everything.
"""

#import working libraries

import pandas as pd
from bs4 import BeautifulSoup as bs

import requests

import os
import time

import matplotlib.pyplot as plt

import pymysql
import csv
from sqlalchemy import create_engine, types

def scrape():
    """
    get tables from 1950 to 2019
    """
    gp=[]
    date=[]
    winner_full=[]
    winner=[]
    car=[]
    laps=[]
    total_time=[]
    
    overall_table = pd.DataFrame()
    
    for k in range(2015,2020):
        url = (f"https://www.formula1.com/en/results.html/{k}/races.html")
        html = requests.get(url).content
        soup = bs(html, 'lxml')
        print(f"Reading Formula 1 data for the year {k}.")
        time.sleep(1)
    
        gp = [i.text.strip() for i in soup.select('td.dark>a')]
    
        date = [i.text.strip() for i in soup.select('td.dark.hide-for-mobile')]
    
        winner_full = [i.text.strip() for i in soup.select('td.dark.bold span:nth-child(1), td.dark.bold span:nth-child(2)')]
    
        car = [i.text.strip() for i in soup.select('td.semi-bold.uppercase')]
    
        laps = [i.text.strip() for i in soup.select('td.bold.hide-for-mobile')]
    
        total_time = [i.text.strip() for i in soup.select('td.dark.bold.hide-for-tablet')]
    
        winner=[winner_full[i]+' '+winner_full[i+1] for i in range(0,int((len(winner_full))),2)]
    
        season_table = (pd.DataFrame([gp,date,winner,car,laps,total_time],index=['Grand Prix','Date','Driver','Car','Laps','Time']).T) #.shift()[1:]
    
        overall_table = overall_table.append(season_table, ignore_index=True) #.shift()[1:]
        
    return overall_table

def save_raw():
    """
    write scraped data into csv file
    """
    os.chdir("C:/Users/aciag/ih/Week3_project/data/")
    overall_table.to_csv("F1_raw_data.csv")
    print("File is ready!")
    
def get_raw(overall_table):
    """
    read from saved file, create initial dataframe
    """
    df=pd.read_csv("F1_raw_data.csv")
    df=df.drop('Unnamed: 0', axis=1) #weird column removal
    
    return df

def mysql_import(df):
    """
    MySQL settings and import
    """
    username='root'
    host='localhost'
    database_name='f1_results'
    password='Bat-chat25t'
    
    engine = create_engine(f"mysql+pymysql://{username}:{password}@localhost/f1_results")
    time.sleep(1)
    df.to_sql(name='gp_winners', con=engine, index=False, if_exists='replace')
    time.sleep(1)
    
    stats=pd.read_sql_query('select * from gp_winners', engine)
    return stats.head(10)

def drivers(df):
    """
    calc amount of wins per driver, sorting descending
    """
    gp_wins_table=['Date','Car','Laps','Time']
    
    gp_wins=(df.groupby('Driver').count()).drop(gp_wins_table, axis=1)
    gp_wins1=gp_wins.sort_values('Grand Prix',ascending=False)
    gp_wins1=gp_wins1.rename(columns={'Grand Prix':'Number of wins'})
    return gp_wins1

def report(gp_wins1):
    os.chdir("C:/Users/aciag/ih/Week3_project/output/")
    gp_wins1.to_csv("Top_F1_drivers.csv")
    gp_wins1.head(10).plot.barh(figsize=(10,10), title='Wins per driver', rot=0, width=0.5, fontsize=22, position=0).invert_yaxis()
    plt.savefig("Top_F1_drivers.png", dpi=200, quality=95, bbox_inches='tight')
    print("csv file and graph are saved!")
    
if __name__=='__main__':
    overall_table=scrape()
    save_raw()
    df=get_raw(overall_table)
    mysql_import(df)
    gp_wins1=drivers(df)
    report(gp_wins1)
    
# Each data pipeline stage should be covered: acquisition, wrangling, analysis, and reporting.