from typing import Any, Union

import requests


class ApiHH:
    """Класс для работы с API HeadHunter"""

    BASE_URL = "https://api.hh.ru/"

    @staticmethod
    def get_employer(employer_id: str) -> Any:
        """Получить информацию о работодателе по ID"""
        url = f"{ApiHH.BASE_URL}employers/{employer_id}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def get_vacancies(employer_id: str, **params: Any) -> Any:
        """Получить вакансии с возможностью фильтрации"""
        url = f"{ApiHH.BASE_URL}vacancies"

        # Добавляем фильтр по работодателю если передан
        if employer_id:
            params['employer_id'] = employer_id

        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def search_employers(company_name: str) -> Any:
        """Поиск работодателей по названию"""
        url = f"{ApiHH.BASE_URL}employers"
        params = {'text': company_name, 'only_with_vacancies': True}

        print(f"URL: {url}")  # отладочный вывод
        print(f"Params: {params}")  # отладочный вывод

        response = requests.get(url, params=params)

        print(f"Status Code: {response.status_code}")  # отладочный вывод

        response.raise_for_status()
        result = response.json()

        print(f"Found: {result.get('found', 0)} employers")  # отладочный вывод

        return result
