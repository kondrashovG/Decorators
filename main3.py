from pprint import pprint
import requests
from bs4 import BeautifulSoup
import json
import datetime
import lxml


def logger(path):
    def __logger(old_function):
        def new_function(*args, **kwargs):
            with open(path, 'a+') as f:
                dt_now = str(datetime.datetime.now())
                f.write(f'{dt_now} {old_function.__name__} {args} {kwargs} {old_function(*args, **kwargs)}')
                return old_function(*args, **kwargs)

        return new_function

    return __logger


# s1, s2 , s3 - слова для поиска, start_page - стартовая страница для поиска вакансий на hh.ru


@logger('vak.log')
def get_vakansions(s1, s2, s3, start_page=0):
    vacantions, n_page = [], start_page

    url = 'https://spb.hh.ru/search/vacancy?text=' + s1 + '&area=1&area=2&page='
    fake_ua = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/107.0.0.0 Safari/537.36'}
    while True:
        print('Страница', n_page)
        res = requests.get(url=url + str(n_page), headers=fake_ua)
        if not res:
            break
        headers = BeautifulSoup(res.text, 'lxml').find_all(class_='serp-item__title')
        for h in headers:
            content = requests.get(url=h.attrs['href'], headers=fake_ua)._content.decode('utf-8')
            content = content[:content.find("Задайте вопрос работодателю")]
            if s2 in content and s3 in content:
                print(h.text)
                print(h.attrs['href'])
                sal = ''.join(str(BeautifulSoup(content, 'lxml').
                                  find(class_='bloko-header-section-2 bloko-header-section-2_lite')).split('\xa0'))
                place = str(BeautifulSoup(content, 'lxml').find(class_='vacancy-company-redesigned')). \
                    split('<p data-qa="vacancy-view-location">')[-1]. \
                    split('<span data-qa="vacancy-view-raw-address">')[-1].split('<')[0]
                company = ' '.join(str(BeautifulSoup(content, 'lxml').
                                       find(class_="bloko-link bloko-link_kind-tertiary")).
                                   split('data-qa="bloko-header-2">')[-1].split(' <!-- -->')).split('<')[0]
                print(company)
                print(place)
                salary = ['', '', '', '']
                if 'undefined' not in sal:
                    if 'от' in sal:
                        salary[0] = sal.split('>от <!-- -->')[-1].split('<!-- -->')[0]
                    if 'до <' in sal:
                        salary[1] = sal.split('до <!-- -->')[-1].split('<!-- -->')[0]
                    salary[2:] = sal.split('<!-- --> <!-- -->')[-1]. \
                        split('<span class="vacancy-salary-compensation-type"> <!-- -->')
                    salary[3] = salary[3].split('</span></span>')[0]
                    print('зарплата от', salary[0], 'до', salary[1], salary[2], salary[3])
                vacantions.append([h.attrs['href'], salary, company, place])
        n_page += 1
    print('Обработано', n_page, 'страниц')
    with open('vacantion.json', 'w') as outfile:
        json.dump(vacantions, outfile)
    return vacantions


@logger('cur.log')
def currency_filter(cur):
    cur_vacantions = []
    with open('vacantion.json', 'r') as infile:
        vacantions = json.load(infile)
        [cur_vacantions.append(vacantion) for vacantion in vacantions if vacantion[1][2] == cur]
    with open('{0}.json'.format(cur), 'w') as outfile:
        json.dump(cur_vacantions, outfile)
    return cur_vacantions


if __name__ == '__main__':
    pprint(get_vakansions('python', 'Flask', 'Django', 29))
    print('____________________________________________')
    pprint(currency_filter('USD'))
