from bs4 import BeautifulSoup
import requests
import csv

# Open csv file
f = open('kolympic_data.csv', 'w', encoding='utf-8', newline='')
wr = csv.writer(f)

# Column name
wr.writerow(['name', 'sex', 'born', 'height', 'weight', 'team', 'noc', 'games', 'year', 'season', 'city', 'sport', 'event', 'medal', 'athlete_id'])

# 1. Get country list
# [[country_noc, country_url], ... ]
base_url = 'http://www.olympedia.org'
countries_page = requests.get(base_url + '/countries')
countries_soup = BeautifulSoup(countries_page.content, 'html.parser')
countries_table = countries_soup.select_one('body > div.container > table:nth-child(5)')
country_nocs = [item.get_text() for item in countries_table.select('tbody > tr > td:nth-child(1) > a')]
country_urls = [base_url + item['href'] for item in countries_table.select('tbody > tr > td:nth-child(2) > a')]
isCompeted = [item['class'] for item in countries_table.select('tbody > tr > td:nth-child(3) > span')]
countries = []
for i in range(len(country_urls)):
    if isCompeted[i][1] == 'glyphicon-ok':
        countries.append([country_nocs[i], country_urls[i]])

# 2. Creating a dictionary to know the host city for the Olympics
# {(year + season): City}
games_page = requests.get(base_url + '/editions')
games_soup = BeautifulSoup(games_page.content, 'html.parser')
summer_table = games_soup.select_one('body > div.container > table:nth-child(5)')
winter_table = games_soup.select_one('body > div.container > table:nth-child(7)')
summer_year_items = summer_table.select('tr > td:nth-child(2)')
summer_city_items = summer_table.select('tr > td:nth-child(3)')
summer_years = [item.get_text() + 'Summer' for item in summer_year_items]
summer_cities = [item.get_text() for item in summer_city_items]
winter_year_items = winter_table.select('tr > td:nth-child(2)')
winter_city_items = winter_table.select('tr > td:nth-child(3)')
winter_years = [item.get_text() + 'Winter' for item in winter_year_items]
winter_cities = [item.get_text() for item in winter_city_items]
years = summer_years + winter_years
cities = summer_cities + winter_cities
year_season__city = {years[i]: cities[i] for i in range(len(years))}

# for testing
# countries = countries[:2]

# 3. Tour by country
for idx, country in enumerate(countries):
    # 1. Enter the country
    country_page = requests.get(country[1])

    # 2. Get the participation list from 'Participations by edition'
    country_soup = BeautifulSoup(country_page.content, 'html.parser')
    olympic_table = country_soup.select_one('body > div.container > table:nth-child(11)')
    if olympic_table is None:
        continue
    result_urls = [base_url + olympic['href'] for olympic in olympic_table.select('tbody > tr > td:nth-child(6) > a')]

    # 3. Finding all 'athlete_id's in the country while traversing the participation list
    # Each player must be approached after scraping all players from the country without duplication.
    # This is because the athlete information contains all the athletes' records in the Olympics.
    athlete_ids = {}
    for result_url in result_urls:
        # 1. Into the result page
        result_page = requests.get(result_url)

        # 2. Get 'athlete_id' without duplicates from the result page
        result_soup = BeautifulSoup(result_page.content, 'html.parser')
        result_table = result_soup.select_one('table')
        local_athlete_ids = [int(athlete['href'][10:]) for athlete in result_table.select('tbody > tr > td:nth-child(2) > a')]
        for id in local_athlete_ids:
            if athlete_ids.get(id) is None:
                athlete_ids[id] = 1

    # 4. Create 'athlete_url' from 'athlete_id'
    athlete_urls = [base_url + '/athletes/' + str(id) for id in athlete_ids.keys()]

    # 5. Get athlete info
    # Value to get 'athlete_id' from 'athelte_url' again using slicing
    athlete_id_slice_start = len(base_url + '/athletes/')
    for athlete_url in athlete_urls:
        # 1. Into athlete page
        athlete_page = requests.get(athlete_url)
        athlete_soup = BeautifulSoup(athlete_page.content, 'html.parser')

        # 2. Creating a dictionary of athlete bio info
        # {'NOC': 'Republic of Korea', 'Sex': 'Female', ... }
        key_items = athlete_soup.select('body > div.container > table.biodata > tr > th')
        keys = [item.get_text() for item in key_items]
        value_items = athlete_soup.select('body > div.container > table.biodata > tr > td')
        values = [item.get_text() for item in value_items]
        athlete_bio_info = {keys[i]: values[i] for i in range(len(keys))}

        # 3. Get games and disciplines info
        # games = ['2018 Winter Olympics', ... ]
        # disciplines = ['Short Track Speed Skating', '500 metres, Women', ... ]
        # In the disciplines array, some values ​​are disciplines like 'Short Track Speed ​​Skating', and some values ​​are events like '500 meters, Women'.
        games_items = athlete_soup.select('body > div.container > table.table > tbody > tr > td:nth-child(1)')
        games_s = [item.get_text() for item in games_items]
        discipline_items = athlete_soup.select('body > div.container > table.table > tbody > tr > td:nth-child(2) > a:nth-child(1)')
        disciplines = [item.get_text() for item in discipline_items]

        # Get medal Info
        medal_items = athlete_soup.select('body > div.container > table.table > tbody > tr > td:nth-child(5)')
        medals = [item.get_text() for item in medal_items]

        # Create & insert athlete info
        cur_games = ''
        cur_sport = ''
        for i in range(len(games_s)):
            if games_s[i].strip() != '':
                cur_games = games_s[i].strip()
                cur_sport = disciplines[i]
                continue

            if games_s[i] == '\n':
                cur_sport = disciplines[i]
                continue

            # Create athlete info
            # Initial value
            name = None
            sex = None
            born = None
            height = None
            weight = None
            team = None
            noc = None
            games = None
            year = None
            season = None
            city = None
            sport = None
            event = None
            medal = None
            athlete_id = None

            # Actual value
            name = athlete_soup.select_one('body > div.container > h1').get_text().replace('\n', '')
            sex_temp = athlete_bio_info.get('Sex')
            sex = 'M' if sex_temp == 'Male' else 'F' if sex_temp == 'Female' else None
            born = athlete_bio_info.get('Born')
            body = athlete_bio_info.get('Measurements')
            if body is not None:
                if len(body.split(' / ')) > 1:
                    body = body.split(' / ')
                    height = body[0][:-3]
                    weight = body[1][:-3]
                else:
                    if body[-2:] == 'cm':
                        height = body[:-3]
                    else:
                        weight = body[:-3]
            team = athlete_bio_info.get('NOC').strip()
            noc = country[0]
            games = cur_games
            games_tokens = games.split(' ')
            year = games_tokens[0]
            season = games_tokens[1]
            year_season = games_tokens[0] + games_tokens[1]
            if year_season__city.get(year_season) is None:
                continue
            city = year_season__city[year_season]
            sport = cur_sport
            event = disciplines[i]
            medal = None if medals[i] == '' else medals[i]
            athlete_id = athlete_url[athlete_id_slice_start:]

            # Insert athlete info
            row = [name, sex, born, height, weight, team, noc, games, year, season, city, sport, event, medal, athlete_id]
            wr.writerow(row)

# Close csv file
f.close()

# End!
print('End!')