from src.vacancy import Vacancy


class Employer:
    def __init__(self, employer_data_: dict) -> None:
        self.id = employer_data_.get("id")
        self.name = employer_data_.get("name")
        self.url = employer_data_.get("alternate_url")
        self.vacancies_url = employer_data_.get("vacancies_url")
        self.open_vacancies = employer_data_.get("open_vacancies", 0)
        self.vacancies: list = []  # Список вакансий

    def add_vacancy(self, vacancy: Vacancy) -> None:
        """Добавляет вакансию к работодателю"""

        self.vacancies.append(vacancy)

    def add_vacancies(self, vacancy: list) -> None:
        """Добавляет вакансию к работодателю"""
        for i in vacancy:
            self.vacancies.append(i)

    def get_vacancies_count(self) -> int:
        """Возвращает количество вакансий"""
        return len(self.vacancies)

    def get_average_salary(self) -> float:
        """Средняя зарплата по вакансиям"""
        salaries = [v.salary for v in self.vacancies if v.salary]
        return sum(salaries) / len(salaries) if salaries else 0

    def get_list_vacancies(self) -> list:
        return self.vacancies

    def __str__(self) -> str:
        return f"Компания: {self.name} (ID: {self.id}), Вакансий: {self.open_vacancies}, URL: {self.url}"
