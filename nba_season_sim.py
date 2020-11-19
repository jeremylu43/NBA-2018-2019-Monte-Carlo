import pandas as pd
import numpy as np
import glob
import matplotlib.pyplot as plt
import random

# Creates dataframe with each team and its appropriate statistics
adv_stats = pd.read_csv("team_adv_stats.csv")
adv_stats = adv_stats.filter(['Team', 'W', 'L','Pace'])
i=0
for name in adv_stats['Team']:
    if ('*' in name):
        adv_stats.loc[i, 'Team'] = name[:-1]
    i+=1
team_names = adv_stats['Team'].to_list()
dicts = {}
keys = range(len(adv_stats))
values = team_names
for i in keys:
    dicts[i] = values[i]
adv_stats=adv_stats.rename(index=dicts)

adv_stats["Home For"] = [[] for _ in range(30)]
adv_stats["Away For"] = [[] for _ in range(30)]
adv_stats["Home Against"] = [[] for _ in range(30)]
adv_stats["Away Against"] = [[] for _ in range(30)]
adv_stats["Home ORtg"] = [None]*30
adv_stats["Home DRtg"] = [None]*30
adv_stats["Away ORtg"] = [None]*30
adv_stats["Away DRtg"] = [None]*30

adv_stats = adv_stats.drop('Team', axis=1)

# Creates Dataframe detailing entire regular season matchups and scores
path = 'reg season games/'
all_files = glob.glob(path + "/*.csv")

li = []

for filename in all_files:
    df = pd.read_csv(filename, index_col=None, header=0)
    li.append(df)

all_games = pd.concat(li, axis=0, ignore_index=True)
all_games=all_games.drop(['Date','Start (ET)', 'Attend.', 'Notes'],axis=1)

# Calculates a team's Home/Away ORtg and DRtg
for row in all_games.iterrows():
    #print(adv_stats.loc[adv_stats['Team'] == (row[1][0])]["Home Scores"])
    adv_stats.loc[row[1][2]]["Home For"].append(row[1][3])
    adv_stats.loc[row[1][0]]["Away For"].append(row[1][1])
    adv_stats.loc[row[1][2]]["Home Against"].append(row[1][1])
    adv_stats.loc[row[1][0]]["Away Against"].append(row[1][3])

for row in adv_stats.iterrows():
    adv_stats.loc[row[0], "Home ORtg"]=np.mean(adv_stats.loc[row[0]]["Home For"])/adv_stats.loc[row[0]]["Pace"]*100
    adv_stats.loc[row[0], "Home DRtg"]=np.mean(adv_stats.loc[row[0]]["Home Against"])/adv_stats.loc[row[0]]["Pace"]*100
    adv_stats.loc[row[0], "Away ORtg"]=np.mean(adv_stats.loc[row[0]]["Away For"])/adv_stats.loc[row[0]]["Pace"]*100
    adv_stats.loc[row[0], "Away DRtg"]=np.mean(adv_stats.loc[row[0]]["Away Against"])/adv_stats.loc[row[0]]["Pace"]*100
    
# Calculates Home/Away Pythagorean Win Percentages for each team
c = 14
adv_stats['hPythag'] = [None]*30
adv_stats['aPythag'] = [None]*30

for row in adv_stats.iterrows():
    adv_stats.loc[row[0], "hPythag"] = adv_stats.loc[row[0],'Home ORtg']**c/(adv_stats.loc[row[0],'Home ORtg']**c + adv_stats.loc[row[0],'Home DRtg']**c)
    adv_stats.loc[row[0], "aPythag"] = adv_stats.loc[row[0],'Away ORtg']**c/(adv_stats.loc[row[0],'Away ORtg']**c + adv_stats.loc[row[0],'Away DRtg']**c)
    
# Simulates season 10000 times
adv_stats["Sim Ws"] = [[] for _ in range(30)]
adv_stats["Sim Ls"] = [[] for _ in range(30)]
for i in range(10000):
    adv_stats["Sim W"] = 0
    adv_stats["Sim L"] = 0
    for row in all_games.iterrows():
        h_team = row[1][2]
        a_team = row[1][0]
        
        win_prob = adv_stats.loc[h_team, "hPythag"]/(adv_stats.loc[h_team, "hPythag"] + adv_stats.loc[a_team, "aPythag"])
        r = random.uniform(0, 1)
        if (r <= win_prob):
            adv_stats.loc[h_team, "Sim W"] +=1
            adv_stats.loc[a_team, "Sim L"] +=1
        else: 
            adv_stats.loc[a_team, "Sim W"] +=1
            adv_stats.loc[h_team, "Sim L"] +=1
            
    for row in adv_stats.iterrows():
        adv_stats.loc[row[0], "Sim Ws"].append(adv_stats.loc[row[0], 'Sim W'])