""" 
Basketball Peak Finder:
Finds an individual player's peak in their career

Command line example:
"python3 peakfinder.py"

Created by Jack Ribarich
August 4th, 2020

"""

import sys
import os
import requests
from threading import Thread
import ast
from bs4 import BeautifulSoup
import pandas as pd
import sheets
from rich import print  # easily read stuff on the command line


class Player():
    def __init__(self, name = None, ext = None, 
        nicknames = None, position = None, height = None, 
        hand = None, college = None, reg_season = None, 
        playoff = None, adv_data = None):
        self.name = name
        self.ext = ext  
        self.nicknames = nicknames  # list
        self.position = position
        self.height = height
        self.hand = hand 
        self.college = college  
        self.reg_season = reg_season  # panda DataFrame
        self.playoff = playoff  # panda DataFrame
        self.adv_data = adv_data # panda Dataframe of Advanced Stats

    def __repr__(self):
        return(f"""Nicknames: {self.nicknames}\nPosition: {self.position}
Height: {self.height}\nShoots: {self.hand}\nCollege: {self.college}\n
Regular Season Stats:\n{self.reg_season}\n
Playoff Stats:\n{self.playoff}\n""")


def usage():
    print("""
        To run this application:\n
        - make sure all libraries are installed\n
        - use command "python3 peakfinder.py"
        """)

    exit()

def get_pic(soup):
    link = soup.select("img[src^=http]")
    lnk = link[1]["src"]
    
    if '.svg' in lnk:
        return  # player has no pic

    with open(os.path.basename(lnk),"wb") as f:
        f.write(requests.get(lnk).content)


def remove_pic(ext):
    try: 
        os.remove(f'{ext}.jpg')

    except:
        return  # do nothing if player picture doesn't exist


def peak_calculation(df):
    scalar = 2.5
    flt = lambda x: x.astype(float)  # changes data into floats

    PER = scalar*flt(df['PER'])/flt(df['PER']).max()
    WS = scalar*flt(df['WS'])/flt(df['WS']).max()

    calc = PER + WS

    return calc


def determine_peak_season(p): 
    peak_data = [None, None]
    peak_list = None
    seasons = None
    seas_sum = None
    ppg = None 
    apg = None
    rpg  = None
    reg = p.reg_season 
    plof = p.playoff

    reg['sum'] = peak_calculation(reg)
    idx = reg['sum'].idxmax()  # max season index

    peak_list = [reg.loc[idx, 'Season'], reg.loc[idx, 'Tm'], reg.loc[idx, 'PER'], 
                reg.loc[idx, 'WS'], reg.loc[idx, 'FG%'], reg.loc[idx, 'PTS'], 
                reg.loc[idx, 'AST'], reg.loc[idx, 'TRB']]
    
    seasons = reg['Season'].tolist()
    seas_sum = reg['sum'].tolist()

    ppg = [float(i) for i in reg['PTS'].tolist()]
    apg = [float(i) for i in reg['AST'].tolist()]
    rpg = [float(i) for i in reg['TRB'].tolist()]
    
    peak_data[0] = [peak_list, seasons, seas_sum, ppg, apg, rpg]

    if not plof.empty:  # playoffs
        plof['sum'] = peak_calculation(plof)
        idx = plof['sum'].idxmax()

        peak_list = [plof.loc[idx, 'Season'], plof.loc[idx, 'Tm'], plof.loc[idx, 'PER'], 
                    plof.loc[idx, 'WS'], plof.loc[idx, 'FG%'], plof.loc[idx, 'PTS'], 
                    plof.loc[idx, 'AST'], plof.loc[idx, 'TRB']]

        seasons = plof['Season'].tolist()
        seas_sum = plof['sum'].tolist()
        ppg = [float(i) for i in plof['PTS'].tolist()]
        apg = [float(i) for i in plof['AST'].tolist()]
        rpg = [float(i) for i in plof['TRB'].tolist()]

        peak_data[1] = [peak_list, seasons, seas_sum, ppg, apg, rpg]

    return peak_data


def get_player(p, name):
    question = "Which NBA player's peak would you like to find: "

    if name == 'debug':
        player_input = input(question)
        p.name = player_input.strip().lower()

    else:
        p.name = name.strip().lower()
    
    with open('player_database.txt') as f:
        player_dict = ast.literal_eval(f.read())
    
    try:
        p.ext = player_dict[p.name]  # search player.py dict

    except: 
            return


def player_info(soup, p):
    position_dict = {'Point Guard': 'PG', 'Shooting Guard': 'SG', 
                    'Small Forward': 'SF', 'Power Forward': 'PF',
                    'Center': 'C'}
    nicknames = 'None'
    nick_flag = 0
    pos_flag = 0
    coll_flag = 0
    college = 'None'  # implement later where it says hs or if foreign
    
    height_item = soup.find('span', {'itemprop': 'height'})
    height = height_item.text.strip()

    info = soup.find('div', {'id' : 'info'})

    for x in info.find_all('p'):
        word = x.text.strip()

        if nick_flag == 0 and len(word) != 0:  # nickname
            if ('(' in word and 
                'born' not in word and
                 'formerly' not in word):  # the b for born for players who've legally changed names
                nicknames = word[1:-1]  # takes off parenthesis
                nicknames = ','.join(list(nicknames.split(','))[:1]) # take first 2 if multiple
                nick_flag = 1

        for i in x.find_all('strong'):
            if 'Position' in i.text:  # position and shooting
                pos_flag = 1
                nick_flag = 1  # no nickname

            if 'College' in i.text:  # College
                coll_flag = 1

        if pos_flag == 1: 
            position = word.replace('\n', '')

            sep1 = ':'
            first = position.split(sep1, 1)[1]

            sep2 = '▪'
            position = first.split(sep2, 1)[0].strip()

            # the shooting hand is in the second part of the line
            hand = first.split(sep2, 1)[1].split(sep1, 1)[1].strip()

            pos_flag = 0

        if coll_flag == 1:
            college = word.replace('\n', '')

            sep = ':'
            college = college.split(sep, 1)[1].strip()

            coll_flag = 0

    cleaned_pos = [val for key,val in position_dict.items() if key in position]
    cleaned_pos = '/'.join(cleaned_pos)

    p.nicknames = nicknames
    p.position = cleaned_pos
    p.height = height
    p.hand = hand
    p.college = college


def player_data(p, player_url):
    response = requests.get(player_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Create threads
    t3 = Thread(target=get_pic, args=(soup, ))
    t4 = Thread(target=player_info, args=(soup, p))
    
    t3.start()
    t4.start()

    # Block until both Threads are done
    t3.join()
    t4.join()

def player_tables(p, player_url):
    made_playoffs = {'Regular': 1, 'Playoffs': 2, 'Regular Advanced': 5, 'Playoffs Advanced': 6}
    no_playoffs = {'Regular': 1, 'Regular Advanced': 3}
    drop_list = ['Age', 'Tm' ,'Lg', 'Pos', 'G', 'MP']
    REG_RANGE = 'Regular!A1:AD'
    PLOFADV_RANGE = 'Playoffs_Adv!A1:AC'
    REGADV_RANGE = 'RegAdv!A1:AC'
    PLAYOFF_RANGE = 'Playoffs!A1:AD'

    adv_playoff_df = sheets.getDF(player_url, None, 0, made_playoffs['Playoffs Advanced'], PLOFADV_RANGE)

    if not adv_playoff_df.empty:
        # Create threads
        t5 = Thread(target=sheets.getDF, args=(player_url, p, 1, made_playoffs['Regular'], REG_RANGE))
        t6 = Thread(target=sheets.getDF, args=(player_url, p, 2, made_playoffs['Regular Advanced'], REGADV_RANGE))
        t7 = Thread(target=sheets.getDF, args=(player_url, p, 3, made_playoffs['Playoffs'], PLAYOFF_RANGE))

        t5.start()
        t6.start()
        t7.start()

        # Block until all threads are done
        t5.join()
        t6.join()
        t7.join()

        # Drop unneccesary columns to make JOIN smoother
        p.reg_season.drop(drop_list, axis=1, inplace=True)
        p.playoff.drop(drop_list, axis=1, inplace=True)

        # merges advanced stats into stats
        p.reg_season = pd.merge(p.reg_season, p.adv_data, how='outer', on='Season')
        p.playoff = pd.merge(p.playoff, adv_playoff_df, how='outer', on='Season')
        
        # Drop rows that don't match 'YEAR-YEAR' format such as 'Career'
        p.reg_season = p.reg_season[p.reg_season['Season'].str.contains('-', na=False)]
        p.playoff = p.playoff[p.playoff['Season'].str.contains('-', na=False)]
    
    else:
        # Create threads
        t5 = Thread(target=sheets.getDF, args=(player_url, p, 1, no_playoffs['Regular'], REG_RANGE))
        t6 = Thread(target=sheets.getDF, args=(player_url, p, 2, no_playoffs['Regular Advanced'], REGADV_RANGE))
        
        t5.start()
        t6.start()

        # Block until both threads are done
        t5.join()
        t6.join()

        p.reg_season.drop(drop_list, axis=1, inplace=True)
        p.playoff = pd.DataFrame({'P' : []})  # empty dataframe

        # merges advanced stats into stat
        p.reg_season = pd.merge(p.reg_season, adv_df, how='outer', on='Season')

        # Drop rows that don't match 'YEAR-YEAR' format such as 'Career'
        p.reg_season = p.reg_season[p.reg_season['Season'].str.contains('-')].dropna()


def player_stats(p):
    url = 'https://www.basketball-reference.com/players/'
    end = '.html'

    thread_list = []

    player_url = url + p.ext[0] + '/' + p.ext + end

    # Create threads
    t1 = Thread(target=player_data, args=(p, player_url))
    t2 = Thread(target=player_tables, args=(p, player_url))
    
    t1.start()
    t2.start()

    # Block until both threads are done
    t1.join()
    t2.join()

    peak_data = determine_peak_season(p)

    return peak_data
 

def retrieve(name):
    debug = 0
    if len(sys.argv) > 1:
        if sys.argv[1] == 'help':
            usage()
        elif sys.argv[1] == 'debug':
            debug = 1

    player = Player()  #  creates player class

    get_player(player, name)  # retrieves player url extension

    if player.ext == None:
        return None, None

    peak_data = player_stats(player)  # retrieves, stores, and formats data

    if debug == 1:
        print(repr(player))

    return player, peak_data