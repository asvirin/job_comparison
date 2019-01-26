#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import requests
from terminaltables import AsciiTable
from dotenv import load_dotenv


def get_avarage_salary_for_vacancy(salary_from, salary_to):
    if salary_from == 0 or salary_from is None:
        return salary_to * 0.8
    elif salary_to == 0 or salary_to is None:
        return salary_from * 1.2
    else:
        return (salary_from + salary_to) / 2


def predict_rub_salary_for_headhunter(vacancy_salary):
    if vacancy_salary is None or vacancy_salary['currency'] != 'RUR':
        return None
    else:
        return get_avarage_salary_for_vacancy(vacancy_salary['from'],
                vacancy_salary['to'])


def predict_rub_salary_for_superjob(salary_from, salary_to):
    if salary_from == 0 and salary_to == 0 or salary_from is None \
        and salary_to is None:
        return None
    else:
        return get_avarage_salary_for_vacancy(salary_from, salary_to)


def get_table_for_print(source, vacancies_list):
    title_table = '{} Moscow'.format(source)
    table = AsciiTable(vacancies_list, title_table)
    return table.table


def get_language_statistics(language, source, vacancies_all_pages):
    vacancies_processed = 0
    salary_language_sum = 0

    for vacancy in vacancies_all_pages:
        if source == 'Headhunter':
            predict_salary = \
                predict_rub_salary_for_headhunter(vacancy['salary'])
        else:
            predict_salary = \
                predict_rub_salary_for_superjob(vacancy['payment_from'
                    ], vacancy['payment_to'])
        if predict_salary is not None:
            vacancies_processed += 1
            salary_language_sum += predict_salary

    vacancies_found = len(vacancies_all_pages)

    if vacancies_found == 0:
        return [language, 0, 0, 0]
    elif vacancies_processed == 0:
        return [language, vacancies_found, 0, 0]
    else:
        return [language, vacancies_found, vacancies_processed,
                int(salary_language_sum / vacancies_processed)]


def get_vacancies_statistics_Headhunter(source, languages_list,
        head_table):
    url_api_headhunter = 'https://api.hh.ru/vacancies/'
    specialization = '1.221'
    location = '1'
    period_search = '30'
    result_per_page = '20'
    max_result = '2000'

    vacancies_statistics_list = head_table

    for language in languages_list:
        page = 0
        payload = {
            'specialization': specialization,
            'area': location,
            'period': period_search,
            'per_page': result_per_page,
            'page': page,
            'text': language,
            }
        response = requests.get(url_api_headhunter, params=payload)
        vacancies = response.json()
        vacancies_all_pages = []

        while vacancies['found'] > len(vacancies_all_pages) \
            <= int(max_result) - int(result_per_page):
            payload = {
                'specialization': specialization,
                'area': location,
                'period': period_search,
                'page': page,
                'per_page': result_per_page,
                'text': language,
                }
            response = requests.get(url_api_headhunter, params=payload)
            vacancies = response.json()
            vacancies_all_pages += vacancies['items']
            page += 1

        vacancies_statistics_list.append(get_language_statistics(language,
                source, vacancies_all_pages))

    table_for_print = get_table_for_print(source,
            vacancies_statistics_list)

    return table_for_print


def get_vacancies_statistics_SuperJob(source, languages_list,
        head_table):
    url_api_superjob = 'https://api.superjob.ru/2.0/vacancies/'
    api_key_superjob = os.getenv('api_key_superjob')
    headers = {'X-Api-App-Id': api_key_superjob}
    location = '4'
    keywords_location_search = '1'
    result_per_page = '100'
    period_search = '0'

    vacancies_statistics_list = head_table

    for language in languages_list:
        payload = {
            'town': location,
            'keywords[0][srws]': keywords_location_search,
            'keywords[0][keys]': language,
            'count': result_per_page,
            'period': period_search,
            }
        response = requests.get(url_api_superjob, headers=headers,
                                params=payload)
        vacancies = response.json()

        vacancies_statistics_list.append(get_language_statistics(language,
                source, vacancies['objects']))

    table_for_print = get_table_for_print(source,
            vacancies_statistics_list)

    return table_for_print

if __name__ == '__main__':
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
        
    print(get_vacancies_statistics_Headhunter('Headhunter', languages_list, head_table))
    print(get_vacancies_statistics_SuperJob('SuperJob', languages_list, head_table))
