
import requests
import os
from terminaltables import AsciiTable
from dotenv import load_dotenv


def predict_rub_salary_for_headhunter(vacancy_salary):
    if vacancy_salary == None or vacancy_salary['currency'] != 'RUR':
        return None
    elif (vacancy_salary['from'] and vacancy_salary['to']) != None:
        return (vacancy_salary['from'] + vacancy_salary['to']) / 2
    elif vacancy_salary['from'] != None:
        return vacancy_salary['from'] * 1.2
    else:
        return vacancy_salary['to'] * 0.8


def predict_rub_salary_for_superjob(salary_from, salary_to):
    if salary_from == 0 and salary_to == 0:
        return None
    elif salary_from == 0:
        return salary_to * 0.8
    elif salary_to == 0:
        return salary_from * 1.2
    else:
        return (salary_from + salary_to) / 2


def get_vacancies_statistics_headhunter(languages_list, head_table):
    vacancies_statistics_headhunter_list = head_table

    url_api_headhunter = 'https://api.hh.ru/vacancies/'

    for language in languages_list:
        page = 0
        vacancies_processed = 0
        salary_language_sum = 0

        payload = {
            'specialization': 1.221,
            'area': 1,
            'period': 30,
            'text': language,
            }
        response = requests.get(url_api_headhunter, params=payload)
        vacancies = response.json()

        vacancies_all_pages = []

        while vacancies['found'] > len(vacancies_all_pages) <= 1980:
            payload = {
                'specialization': 1.221,
                'area': 1,
                'period': 30,
                'page': page,
                'text': language,
                }
            response = requests.get(url_api_headhunter, params=payload)
            vacancies = response.json()
            vacancies_all_pages += vacancies['items']
            page += 1

        for vacancy in vacancies_all_pages:
            predict_salary = \
                predict_rub_salary_for_headhunter(vacancy['salary'])
            if predict_salary != None:
                vacancies_processed += 1
                salary_language_sum += predict_salary

        vacancies_found = len(vacancies_all_pages)
        try:
            vacancies_statistics_headhunter_list.append([language,
                    vacancies_found, vacancies_processed,
                    int(salary_language_sum / vacancies_processed)])
        except ZeroDivisionError:

            vacancies_statistics_headhunter_list.append([language,
                    vacancies_found, 0, 0])

    return vacancies_statistics_headhunter_list


def get_vacancies_statistics_superjob(languages_list, head_table):
    vacancies_statistics_superjob_list = head_table

    url_api_superjob = 'https://api.superjob.ru/2.0/vacancies/'
    api_key_superjob = os.getenv("api_key_superjob")
    headers = {'X-Api-App-Id': api_key_superjob}

    for language in languages_list:
        vacancies_processed = 0
        salary_language_sum = 0

        payload = {
            'town': 4,
            'keywords[0][srws]': 1,
            'keywords[0][keys]': language,
            'count': 100,
            'period': 0,
            }
        response = requests.get(url_api_superjob, headers=headers,
                                params=payload)
        vacancies = response.json()
        if vacancies['objects'] == 0:
            vacancies_statistics_superjob_list.append([language, 0, 0,
                    0])
        else:

            for vacancy in vacancies['objects']:
                predict_salary = \
                    predict_rub_salary_for_superjob(vacancy['payment_from'
                        ], vacancy['payment_to'])
                if predict_salary != None:
                    vacancies_processed += 1
                    salary_language_sum += predict_salary

        vacancies_found = len(vacancies['objects'])

        try:
            vacancies_statistics_superjob_list.append([language,
                    vacancies_found, vacancies_processed,
                    int(salary_language_sum / vacancies_processed)])
        except ZeroDivisionError:

            vacancies_statistics_superjob_list.append([language,
                    vacancies_found, 0, 0])

    return vacancies_statistics_superjob_list


def main(vacancies_list, title_table):
    table_for_print = AsciiTable(vacancies_list, title_table)
    return table_for_print.table

if __name__ == '__main__':
    load_dotenv()
    languages_list =[
          'Java',
          'Python',
          'Ruby',
          'C++',
          'TypeScript',
          'Kotlin',
          'GO',
          ]
    head_table = \
        [['Язык\nпрограммирования',
         'Вакансий\nнайдено',
         'Вакансий\nобработано',
         'Средняя\nзарплата'
         ]]

    title_table_data_headhunter = 'Headhunter Moscow'
    title_table_data_superjob = 'SuperJob Moscow'

    headhunter_table = \
        main(get_vacancies_statistics_headhunter(languages_list,
             head_table), title_table_data_headhunter)
    superjob_table = \
        main(get_vacancies_statistics_superjob(languages_list,
             head_table), title_table_data_superjob)
    print(headhunter_table)
    print(superjob_table)
