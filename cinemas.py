import requests
from bs4 import BeautifulSoup


def fetch_afisha_page():
    url = 'http://www.afisha.ru/msk/schedule_cinema/'
    return requests.get(url).content


def parse_afisha_list(raw_html):
    movies = []
    soup = BeautifulSoup(raw_html, 'lxml')
    raw_divs = soup.find('div', id='schedule').find_all('div', class_='object')
    for div in raw_divs:
        movie_title = div.find('h3', {'class': 'usetags'}).a.text
        cinemas = len(div.find('table').find_all('tr'))
        movies.append([movie_title, cinemas])
    return movies


def get_rate_votes(movie):
    url = 'http://kinopoisk.ru/index.php'
    params = {'first': 'yes', 'kp_query': movie}
    page = requests.get(url, params=params).content
    soup = BeautifulSoup(page, 'lxml')
    rate = soup.find('span', class_='rating_ball')
    rate = float(rate.text) if rate else 0
    votes = soup.find('span', class_='ratingCount')
    votes = int(votes.text.replace('\xa0', '')) if votes else 0
    return rate, votes


def collect_info(movies):
    movies_info = []
    for movie, cinemas in movies:
        rate, votes = get_rate_votes(movie)
        movies_info.append({'title': movie,
                            'rate': rate,
                            'cinemas': cinemas,
                            'votes': votes})
    return movies_info


def sort_movies(movies):
    return sorted(movies, key=lambda x: (x['rate'], x['cinemas']),
                  reverse=True)[:10]


if __name__ == '__main__':
    raw_html = fetch_afisha_page()
    movies = parse_afisha_list(raw_html)
    movies_info = collect_info(movies)
    for line, movie in enumerate(sort_movies(movies_info), 1):
        print('{}. {}\t{}\t{}\t{}'.format(
            line, movie['title'], movie['rate'],
            movie['cinemas'], movie['votes']))
