"""
    Google Sheets API
    Updated: 8/5/2021
    
    This file contains functions related to creating
    and accessing sheets using Google's Sheets API

"""
import pygsheets
import pandas as pd

def authorizeSheet():
    return pygsheets.authorize(client_secret='credentials.json')

def createSheet(client, title):
    return client.create(title) # creates sheet

def getAccess(client, title):
    sheet = client.open(title) # opens sheet
    ws = sheet.sheet1 # opens up first sheet

    return ws

def fillSheet(ws, player_link, tableNum):
    pre = '=ARRAYFORMULA(SUBSTITUTE(IMPORTHTML("'
    after = '", "table",'
    end = '),"*",""))'
    text = pre + player_link + after + str(tableNum) + end

    ws.update_value('A1', text)

def getDF(player_link, tableNum):
    title = 'BballTest'
    client = authorizeSheet()
    ws = getAccess(client, title)
    fillSheet(ws, player_link, tableNum)

    df = ws.get_as_df(has_header=True)

    return df