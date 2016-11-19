import requests
from bs4 import BeautifulSoup
from requests.exceptions import Timeout, ConnectionError
import sys
import time


def fetch_afisha_page():
    url = 'http://www.afisha.ru/msk/schedule_cinema/'
    return requests.get(url).content


def parse_afisha_list(raw_html):
    soup = BeautifulSoup(raw_html, 'lxml')
    raw_divs = soup.find('div', id='schedule').find_all('div', class_='object')
    for div in raw_divs:
        movie_title = div.find('h3', {'class': 'usetags'}).a.text
        cinemas_num = len(div.find('table').find_all('tr'))
        yield {'title': movie_title, 'cinemas': cinemas_num}


def get_rate_votes(movie):
    s = requests.Session()
    url = 'http://kinopoisk.ru/index.php'
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'}
    params = {'first': 'yes', 'kp_query': movie}
    time.sleep(10)
    try:
        page = s.get(url, params=params,
                     headers=headers, timeout=10).content
    except (Timeout, ConnectionError):
        sys.exit('Maybe we\'re banned, try later')
    soup = BeautifulSoup(page, 'lxml')
    rate = soup.find('span', class_='rating_ball')
    rate = float(rate.text) if rate else 0
    votes = soup.find('span', class_='ratingCount')
    votes_num = int(votes.text.replace('\xa0', '')) if votes else 0
    return {'rate': rate, 'votes': votes_num}


def collect_info(raw_html):
    movies_list = []
    for movie in parse_afisha_list(raw_html):
        movie_rate = get_rate_votes(movie['title'])
        movies_list.append({'title': movie['title'],
                            'cinemas': movie['cinemas'],
                            'rate': movie_rate['rate'],
                            'votes': movie_rate['votes']
                            })
    return movies_list


def output_to_console(movies_list, amount):
    best_movies = sorted(movies_list, key=lambda x: x['rate'])[-amount:]
    for line, movie in enumerate(reversed(best_movies), 1):
        print('{}. {}\t{}\t{}\t{}'.format(
            line, movie['title'], movie['rate'],
            movie['cinemas'], movie['votes']))


if __name__ == '__main__':
    raw_html = fetch_afisha_page()
    movies_list = collect_info(raw_html)
    output_to_console(movies_list, 10)
