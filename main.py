import sys
import os
import csv
import requests
import pandas as pd
import re
from bs4 import BeautifulSoup
import datetime


# using python 2.7
# get the team names and urls from ESPN and save to .csv
def getTeams():
    print("Getting WNBA Teams...")
    url = "http://www.espn.com/wnba/teams"
    r = requests.get(url)

    soup = BeautifulSoup(r.text, "html.parser")
    tables = soup.find_all('ul', class_='medium-logos')

    # for each team, we need to get the team name (in english),
    # 3 letter name, link to team page, link to roster, link to schedule, link to stats
    # example: "Atlanta Dream", "atl", "atlanta-dream", link, link, link, link
    team_names = []
    letters_short = []
    letters_long = []
    team_page = []
    rosters = []
    schedules = []
    stats = []


    for table in tables:
        lis = table.find_all('li')
        for li in lis:
            # team name
            name = li.div.b.a
            team_names.append(name.text)

            #team page
            team_link = name['href']
            team_page.append(team_link)

            #team letters and letter_long
            short_letters = team_link.split('/')[-2]
            letters_short.append(short_letters)
            long_letters = team_link.split('/')[-1]
            letters_long.append(long_letters)

            # the other team URLs are formatted as follows
            stats_url = "http://www.espn.com/wnba/team/stats/_/name/" + short_letters + "/" + long_letters

            stats.append(stats_url)
            rosters.append(stats_url.replace('stats', 'roster'))
            schedules.append(stats_url.replace('stats', 'schedule'))

    dic = {'name': team_names,
           'letters_short': letters_short,
           'letters_long': letters_long,
           'team_page': team_page,
           'roster': rosters,
           'schedule': schedules,
           'stats': stats }

    teams = pd.DataFrame(dic, index=team_names)
    teams.index.name = 'team'
    print("Saving teams to CSV...")
    teams.to_csv("team_info.csv", encoding='utf-8')

# takes in a base URL and a datetime and returns the correct url
# date format for the ESPN WNBA schedule page
def datetimeToURL(url, date):
    # add a 0 before single digit months
    currMonth = str(date.month)
    if date.month < 10:
        currMonth = "0" + str(date.month)

    currDay = str(date.day)
    if date.day < 10:
        currDay = "0" + str(date.day)

    return url + str(date.year) + currMonth + currDay

# takes in the data-date from an HTML attribute and returns the
# matching date time in pacific time
# examples:
# 2017-08-06T19:00Z -> 12:00PM
# 2017-08-06T20:30Z -> 1:30PM
# edge cases after 5:00PM
# 2017-08-13T02:00Z -> 7:00PM
# 2017-08-13T00:00Z -> 5:00PM

def dataDateToDateTime(input):
    date = input.split('T')[0]
    time = input.split('T')[1]

    year = int(date.split('-')[0])
    month = int(date.split('-')[1])
    day = int(date.split('-')[2])

    time = time.split('Z')[0]
    hour = int(time.split(':')[0])
    minute = int(time.split(':')[1])

    hour -= 7
    if hour < 0 :
        hour += 24
        day -= 1
    return datetime.datetime(year, month, day, hour, minute)

# goes to ESPN to download schedule
def updateSchedule():
    print("Getting schedule...")

    # with 12 teams, the maximum amount of games on any given day is 6
    # regular season goes from april 13th to sept 3 for regular season

    # week of 7/16
    url = "http://www.espn.com/wnba/schedule/_/date/"
    dateString = url.split('/')[-1]
    currDate = datetime.datetime(2017, 8, 06)
    endDate = datetime.datetime(2017, 9, 03)
    print("Start date: " + str(currDate))
    print("End   date: " + str(endDate))
    print("Downloading weekly schedules...")
    # get each week to download

    datetimesToDownload = []
    urlsToDownload = []


    while currDate <= endDate:
        datetimesToDownload.append(currDate)
        urlsToDownload.append(datetimeToURL(url, currDate))
        delta = datetime.timedelta(days=7)
        newDate = currDate + delta
        currDate = newDate





    print("Getting individual games...")

    gameIDs = [] # a number that can be added on to "http://www.espn.com/wnba/game?gameId=" to get a game page
    homeTeam = [] # link to home team page
    awayTeam = [] # link to away team page
    gameTime = [] # datetime of the game time and date
    televised = [] # either "not-televised" if blank or lists the national tv network

    # delete next line
    # j = 0
    # for each day in each week, download all the games times and teams and save to a csv file
    for link in urlsToDownload:
        # delete these
        # if(j != 0) :
        #     break
        # j += 1
        # end delete
        # go link and grab the week's games, add them to games
        r = requests.get(link)
        soup = BeautifulSoup(r.text, "html.parser")
        tables = soup.find(id='sched-container')



        for table in tables:
            if table['class'][0] == 'responsive-table-wrap': # looking at one of the day divs
                if table.text != 'No games scheduled' :
                    for entry in table.table.tbody: # for each game in a day
                        # home team

                        # extract the home and away teams, the time, game page link, and TV channel
                        soupColumn = BeautifulSoup(str(entry), "html.parser")
                        #print(soupColumn.prettify())
                        columns = soupColumn.find_all('td')
                        
                        i = 0
                        for column in columns: # go through each td column

                            if i == 0: # HOME TEAM

                                homeTeam.append(column.a['href'])
                            elif i == 1 : # AWAY TEAM

                                awayTeam.append(column.a['href'])
                            elif i == 2: # TIME / GAME LINK

                                date = column['data-date']
                                # also add the current date/time to the game
                                gameTime.append(dataDateToDateTime(date))

                                link = column.a['href']
                                link = link.split('=')[-1]
                                gameIDs.append(link)
                            elif i == 3 and len(column.contents) != 0: # NATL TELEVISED NETWORK
                                televised.append(column.a['href'])
                            elif i == 3 and len(column.text) == 0:
                                televised.append('not-televised')
                            i += 1



                        # print("next game")

            #gameTable = soup.find_next(class_='responsive-table-wrap')



    dic = {'gameIDs': gameIDs,
           'homeTeam': homeTeam,
           'awayTeam': awayTeam,
           'gameTime': gameTime,
           'televised': televised}

    print("Saving games to CSV...")
    games = pd.DataFrame(dic, index=gameIDs)
    games.index.name = 'game'

    games.to_csv("schedule_info.csv", encoding='utf-8')


def getStats(gameID):
    print('getting stats')



def main():
    print('works')
    # WNBA

    # Run these functions once to populate the game_info and schedule_info csv's
    # getTeams()
    # updateSchedule() # does not work for games in the past


    getStats('what') # given a game id, take a snapshot of the stats


if __name__ == "__main__":
    main()

