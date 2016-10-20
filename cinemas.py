import re
import requests
from bs4 import BeautifulSoup


def fetch_afisha_page():
    url = 'http://www.afisha.ru/msk/schedule_cinema/'
    return requests.get(url).content


def parse_afisha_list(raw_html):
    movie_names = {}
    soup = BeautifulSoup(raw_html, 'lxml')
    raw_divs = soup.find('div', id='schedule').find_all('div', class_='object')
    for div in raw_divs:
        movie_name = div.find('h3', {'class': 'usetags'}).a.text
        cinemas = len(div.find('table').find_all('tr'))
        movie_names[movie_name] = cinemas
    return movie_names


def fetch_movie_info(movie_name):
    url = 'http://api.kinopoisk.cf/searchFilms?keyword={}'.format(movie_name)
    movie_list = requests.get(url).json()
    year_rate = []
    for movie in movie_list['searchFilms']:
        year = movie.get('year', '')
        if len(year) == 4:
            year_rate.append([year, movie.get('rating', '')])
    rating = max(year_rate, key=lambda x: x[0])[1]
    rate_votes = re.findall(r'(\d\.\d)\s\(([ 0-9]+)\)', rating)
    if not rate_votes:
        return '0', '0'
    else:
        return rate_votes[0]


def collect_info(movies):
    all_movie_info_list = []
    for movie, cinemas in movies.items():
        rate, votes = fetch_movie_info(movie)
        all_movie_info_list.append([movie, rate, cinemas, votes])
    return all_movie_info_list


def output_movies_to_console(movies):
    return sorted(movies, key=lambda x: (x[1], x[2]), reverse=True)[:10]


if __name__ == '__main__':
    raw_html = fetch_afisha_page()
    movie_names = parse_afisha_list(raw_html)
    all_movies = collect_info(movie_names)
    for line, movie in enumerate(output_movies_to_console(all_movies), 1):
        print('{}. {}\t{}\t{}\t{}'.format(
            line, movie[0], movie[1], movie[2], movie[3]))
