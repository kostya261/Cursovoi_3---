import re
from typing import Any


class Vacancy:
    __slots__ = ["id", "title", "url", "salary", "requirements", "salary_from", "salary_to"]

    def __init__(
        self, id: str = "", title: str = "Водитель", url: str = "http:", salary_str: str = "", requirements: str = ""
    ) -> None:

        # self.vacancy_id = None
        self.id = id  # id вакансии
        self.title = title  # Название вакансии
        self.url = url  # ссылка на вакансию
        self.salary = salary_str  # зарплата
        self.requirements = requirements  # краткое описание или требование
        self.salary_from, self.salary_to = self.parse_salary(salary_str)  # диапазон зарплаты
        self.__validate_data()  # проверка параметров на валидность

    def __validate_data(self) -> None:
        if not isinstance(self.id, str):
            raise TypeError("Название должно быть строкой")
        if not isinstance(self.title, str):
            raise TypeError("Название должно быть строкой")
        if not isinstance(self.url, str):
            raise TypeError("Ссылка должна быть строкой")
        if not isinstance(self.salary, str):
            raise TypeError("Зарплата должна быть строкой")
        if not isinstance(self.requirements, str) and not None:
            self.requirements = ""
            # raise TypeError("Описание должно быть строкой")

    def __repr__(self) -> str:
        return f"Vacancy('{self.title}', {self.url}, {self.salary}, {self.requirements})"

    @staticmethod
    def parse_salary(salary_str: str) -> tuple:
        """
        Парсит строку зарплаты с помощью регулярных выражений
        """
        if not salary_str or "не указан" in salary_str.lower():
            return 0, 0

        # Ищем числа в строке (с учетом разделителей тысяч)
        numbers = re.findall(r"[\d\s]+(?:\s*\d{3})*", salary_str.replace(",", ""))
        numbers = [int(num.replace(" ", "")) for num in numbers if num.strip()]

        if not numbers:
            return 0, 0

        clean_str = salary_str.lower().replace(" ", "")

        # Определяем тип формата
        if "-" in clean_str or "—" in clean_str:
            # Диапазон "86000-115000"
            if len(numbers) >= 2:
                return numbers[0], numbers[1]
            elif len(numbers) == 1:
                return numbers[0], numbers[0]
        elif "до" in clean_str:
            # "до 100000"
            return 0, numbers[0]
        elif "от" in clean_str:
            # "от 100000"
            return numbers[0], 0
        else:
            # Просто число
            return numbers[0], numbers[0]

        return 0, 0

    @property
    def avg_salary(self) -> Any:
        if self.salary_from and self.salary_to:
            return (self.salary_from + self.salary_to) / 2
        return self.salary_from or self.salary_to or 0

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "url": self.url,
            "salary": self.salary,
            "requirements": self.requirements,
        }

    @classmethod
    def cast_to_object_list(cls, data: dict) -> list[dict]:
        vacancys: list[dict] = []
        if not data:
            raise TypeError("Нет данных!")

        for vacancy_ in data:
            vacancys.append(vacancy_)

        return vacancys

    @classmethod
    def from_dict(cls, data: dict) -> "Vacancy":
        """Создает Vacancy из словаря API"""
        # Преобразуем словарь зарплаты в строку
        salary_info = data.get("salary", {})
        salary_str = cls._salary_dict_to_string(salary_info)

        return cls(
            id=data.get("id", ""),
            title=data.get("name", ""),
            url=data.get("alternate_url", ""),
            salary_str=salary_str,  # Теперь передаем строку!
            requirements=data.get("snippet", {}).get("requirement", ""),
        )

    @staticmethod
    def _salary_dict_to_string(salary_data: dict) -> str:
        """Преобразует словарь зарплаты в строку для парсинга"""
        if not salary_data or not isinstance(salary_data, dict):
            return "не указана"

        salary_from = salary_data.get("from")
        salary_to = salary_data.get("to")
        currency = salary_data.get("currency", "руб.")

        if salary_from and salary_to:
            return f"{salary_from}-{salary_to} {currency}"
        elif salary_from:
            return f"от {salary_from} {currency}"
        elif salary_to:
            return f"до {salary_to} {currency}"
        else:
            return "не указана"

    def __str__(self) -> str:
        return (
            f"ID: {self.id}, Наименование: {self.title}, "
            f"URL: {self.url}, Зарплата: {self.salary}, Описание: {self.requirements}"
        )

    def __eq__(self, other: Any) -> Any:
        if not isinstance(other, Vacancy):
            return NotImplemented
        return self.avg_salary == other.avg_salary

    def __lt__(self, other: Any) -> Any:
        if not isinstance(other, Vacancy):
            return NotImplemented
        # print(self.avg_salary, other.avg_salary)
        return self.avg_salary < other.avg_salary

    @property
    def get_title(self) -> str:
        return self.title

    def set_title(self, value: str) -> None:
        if not isinstance(value, str):
            raise ValueError("Текст должен быть строкой")
        self.title = value

    @property
    def get_url(self) -> str:
        return self.url

    def set_url(self, value: str) -> None:
        if not isinstance(value, str):
            raise ValueError("Текст должен быть строкой")
        self.url = value

    @property
    def get_salary(self) -> str:
        return self.salary

    def set_salary(self, value: str) -> Any:
        if not isinstance(value, str):
            raise ValueError("Текст должен быть строкой")
        self.salary = value

    @property
    def get_requirements(self) -> str:
        return self.requirements

    def set_requirements(self, value: str) -> Any:
        if not isinstance(value, str):
            raise ValueError("Текст должен быть строкой")
        self.requirements = value
