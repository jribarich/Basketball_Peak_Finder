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
import ast
from bs4 import BeautifulSoup
from bs4 import Comment
import pandas as pd
from rich import print  # easily read stuff on the command line


class Player():
    def __init__(self, name = None, ext = None, 
        nicknames = None, position = None, height = None, 
        hand = None, college = None, reg_season = None, 
        playoff = None):
        self.name = name
        self.ext = ext  
        self.nicknames = nicknames  # list
        self.position = position
        self.height = height
        self.hand = hand 
        self.college = college  
        self.reg_season = reg_season  # panda DataFrame
        self.playoff = playoff  # panda DataFrame

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
        filename = ext + '.jpg'
        os.remove(filename)

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
    ppg = reg['PTS'].astype(float).tolist()
    apg = reg['AST'].astype(float).tolist()
    rpg = reg['TRB'].astype(float).tolist()
    
    peak_data[0] = [peak_list, seasons, seas_sum, ppg, apg, rpg]

    if not plof.empty:  # playoffs
        plof['sum'] = peak_calculation(plof)
        idx = plof['sum'].idxmax()

        peak_list = [plof.loc[idx, 'Season'], plof.loc[idx, 'Tm'], plof.loc[idx, 'PER'], 
                    plof.loc[idx, 'WS'], plof.loc[idx, 'FG%'], plof.loc[idx, 'PTS'], 
                    plof.loc[idx, 'AST'], plof.loc[idx, 'TRB']]

        seasons = plof['Season'].tolist()
        seas_sum = plof['sum'].tolist()
        ppg = plof['PTS'].astype(float).tolist()
        apg = plof['AST'].astype(float).tolist()
        rpg = plof['TRB'].astype(float).tolist()

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


def player_info(soup):
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

    return nicknames, cleaned_pos, height, hand, college


def table_data(soup):
    rows = soup.find_all('tr')

    headers = [[th.text for th in rows[i].find_all('th')] for i in range(len(rows))]
    
    categories = headers[0]
    seasons = headers[1:]

    data = [[td.text for td in rows[i].find_all('td')] for i in range(len(rows)-1)][1:]
    
    i = 0
    while True:
        if len(seasons[i]) != 0:
            if seasons[i][0] != 'Career':
                data[i].insert(0, seasons[i][0])

            else:
                break

        i += 1

    # 2 variables used to track if player has been traded midseason
    traded = 0
    age = None

    clean_data = []
    for j in range(len(data)):
        if ((data[j][1]).isnumeric()) and not ('Did Not Play' in data[j][2]):
            if 'TOT' in data[j][2]:
                data[j][2] = ''
                age = data[j][1]

            elif age == data[j][1]:
                traded += 1

                # change team name to multiple teams
                if traded > 1:
                    data[j-traded][2] = data[j-traded][2] + ', ' + data[j][2] 

                else:
                    data[j-traded][2] = data[j-traded][2] + data[j][2]

            elif age != data[j][1] and traded != 0:
                # add previous data from traded season and current data
                clean_data.append(data[j-traded-1])
                clean_data.append(data[j])

                age = None
                traded = 0

            else:
                clean_data.append(data[j])

    stats = pd.DataFrame(clean_data, columns= categories)
    stats[stats.eq('')] = 0  # sets all empty columns to 0

    return stats


def special_data(soup, table_name):
    ''' 
        used for the JavaScript tables 
        (all tables besides reg.season per game)
    '''
    table = soup.find('div', {'id': table_name})

    if table == None:
        return None

    comments = table.find_all(string=lambda text: isinstance(text, Comment))

    new_soup = BeautifulSoup(str(comments), 'html.parser')

    return new_soup 


def player_stats(p):
    url = 'https://www.basketball-reference.com/players/'
    end = '.html'

    player_url = url + p.ext[0] + '/' + p.ext + end
    response = requests.get(player_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    p.nicknames, p.position, p.height, p.hand, p.college = player_info(soup)

    p.reg_season = table_data(soup)

    drop_list = ['Age', 'Tm' ,'Lg', 'Pos', 'G', 'MP']
    adv_soup = special_data(soup, 'all_advanced')
    adv_df = table_data(adv_soup).drop(drop_list, axis = 1)

    # merges advanced stats into stats
    p.reg_season = pd.merge(p.reg_season, adv_df, how='outer', on='Season')

    playoff_soup = special_data(soup, 'all_playoffs_per_game')
    adv_playoff_soup = special_data(soup, 'all_playoffs_advanced')

    if playoff_soup != None:  # check if player has made playoffs
        p.playoff = table_data(playoff_soup)
        adv_playoff_df = table_data(adv_playoff_soup).drop(drop_list, axis = 1)

         # merges advanced playoffs into playoffs into one
        p.playoff = pd.merge(p.playoff, adv_playoff_df, how='outer', on='Season')
    
    else:
        p.playoff = pd.DataFrame({'P' : []})  # empty dataframe

    get_pic(soup)

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


if __name__ == "__main__":
    retrieve('debug')