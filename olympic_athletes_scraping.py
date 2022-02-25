from bs4 import BeautifulSoup
import requests
import csv

# csv파일 열기
f = open('kolympic_data.csv', 'w', encoding='utf-8', newline='')
wr = csv.writer(f)

# 컬럼명
wr.writerow(['name', 'sex', 'born', 'height', 'weight', 'team', 'noc', 'games', 'year', 'season', 'city', 'sport', 'event', 'medal', 'athlete_id'])

# 1. 나라 목록 가져오기
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

# 0. (year + season) <-> City 딕셔너리 만들기
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

# 테스트용
# countries = countries[:2]

# 2. 나라별로 순회
for idx, country in enumerate(countries):
    # 1. 나라 안에 들어간다.
    country_page = requests.get(country[1])

    # 2. 'Participations by edition'에서 참가 목록 가져온다.
    country_soup = BeautifulSoup(country_page.content, 'html.parser')
    olympic_table = country_soup.select_one('body > div.container > table:nth-child(11)')
    if olympic_table is None:
        continue
    result_urls = [base_url + olympic['href'] for olympic in olympic_table.select('tbody > tr > td:nth-child(6) > a')]

    # 3. 참가 목록 순회하면서 해당 국가의 모든 athlete_id 구하기
    # 중복 없이 해당 나라의 모든 선수들을 긁어온 후 각 선수에 접근해야 한다.
    # 선수 정보에는 그 선수가 올림픽에 출전했던 모든 기록이 있기 때문이다.
    athlete_ids = {}
    for result_url in result_urls:
        # 1. 참가 안에 들어간다.
        result_page = requests.get(result_url)

        # 2. 선수 키값을 가져온다.
        result_soup = BeautifulSoup(result_page.content, 'html.parser')
        result_table = result_soup.select_one('table')
        local_athlete_ids = [int(athlete['href'][10:]) for athlete in result_table.select('tbody > tr > td:nth-child(2) > a')]
        for id in local_athlete_ids:
            if athlete_ids.get(id) is None:
                athlete_ids[id] = 1

    # 4. athlete id로부터 athlete url 만들기
    athlete_urls = [base_url + '/athletes/' + str(id) for id in athlete_ids.keys()]

    # 5. 선수 정보 가져오기
    athlete_slice_start = len(base_url + '/athletes/')
    for athlete_url in athlete_urls:
        # 1. 선수 안에 들어간다.
        athlete_page = requests.get(athlete_url)
        athlete_soup = BeautifulSoup(athlete_page.content, 'html.parser')

        # 2. 선수 관련 정보 가져온다.
        # 선수 정보 키-밸류 딕셔너리 만들기
        key_items = athlete_soup.select('body > div.container > table.biodata > tr > th')
        keys = [item.get_text() for item in key_items]
        value_items = athlete_soup.select('body > div.container > table.biodata > tr > td')
        values = [item.get_text() for item in value_items]
        athlete_bio_info = {keys[i]: values[i] for i in range(len(keys))}

        # 종목 정보 가져오기
        games_items = athlete_soup.select('body > div.container > table.table > tbody > tr > td:nth-child(1)')
        games_s = [item.get_text() for item in games_items]
        discipline_items = athlete_soup.select('body > div.container > table.table > tbody > tr > td:nth-child(2) > a:nth-child(1)')
        disciplines = [item.get_text() for item in discipline_items]

        # 메달 정보 가져오기
        medal_items = athlete_soup.select('body > div.container > table.table > tbody > tr > td:nth-child(5)')
        medals = [item.get_text() for item in medal_items]

        # 선수정보 생성 & 삽입하기
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

            # 선수 정보 생성하기
            # 초기값
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

            # 실제값
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
            athlete_id = athlete_url[athlete_slice_start:]

            # 선수 정보 삽입하기
            row = [name, sex, born, height, weight, team, noc, games, year, season, city, sport, event, medal, athlete_id]
            wr.writerow(row)

# csv파일 닫기
f.close()

# 끝!
print('끝!')