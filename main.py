from src.api_hh import ApiHH
from src.DB_class import DBManager
from src.employer import Employer
from src.utils import print_vacancy
from src.vacancy import Vacancy


def main() -> None:
    # Разделитель для красоты
    cutter: str = "═════════════════════════════════════════════════"

    # просто для удобства счетчик организаций для информативности вывода
    counter_employers: int = 0

    # Флаги для отображения той или иной информации из базы данных
    flags_vacancies_count: bool = False
    flags_all_vacancies: bool = False
    flags_avg: bool = False
    flags_higher_salary: bool = False
    flags_vacancies_keywords: bool = False

    flags_create_base: bool = False

    # Слово для поиска
    keywords_for_search: str = ""

    print(cutter)
    print("    ⭐ ⭐ ⭐ Курсовая работа № 3 ⭐ ⭐ ⭐")
    print(cutter)

    data_base_name: str = input("Введите имя базы данных: ")
    password: str = input("Введите пароль базы данных: ")

    try:
        ask = str(input("База уже существует? (Y/N): "))
        if ask.lower() == "y":
            print("Ok")
            flags_create_base = True
    except ValueError:
        flags_create_base = False

    if not flags_create_base:
        try:
            per_page_in_vacancies = int(input("🔔 Введите количество вакансий на организацию (не больше 100!): "))
            print(f"🔍 Поиск {per_page_in_vacancies} вакансий на организацию!")
        except ValueError:
            print("⚠️ Введено не число, используется значение по умолчанию: 10")
            per_page_in_vacancies = 10

    try:
        ask = str(input("Отобразить список всех компаний и количество вакансий у каждой? (Y/N): "))
        if ask.lower() == "y":
            print("Ok")
            flags_vacancies_count = True
    except ValueError:
        flags_vacancies_count = False

    try:
        ask = str(input("Отобразить список всех вакансий с указанием названия компании? (Y/N): "))
        if ask.lower() == "y":
            print("Ok")
            flags_all_vacancies = True
    except ValueError:
        flags_all_vacancies = False

    try:
        ask = str(input("Отобразить среднюю зарплату по вакансиям? (Y/N): "))
        if ask.lower() == "y":
            print("Ok")
            flags_avg = True
    except ValueError:
        flags_avg = False

    try:
        ask = str(input("Отобразить список всех вакансий у которых зарплата выше средней? (Y/N): "))
        if ask.lower() == "y":
            print("Ok")
            flags_higher_salary = True
    except ValueError:
        flags_higher_salary = False

    try:
        ask = str(input("Отобразить список всех вакансий у которых в названии присутствует слово... (Y/N): "))
        if ask.lower() == "y":
            print("Ok")
            flags_vacancies_keywords = True
            keywords_for_search = str(input("Введите искомое слово/ слова: "))
    except ValueError:
        flags_vacancies_keywords = False

    print(cutter)

    # Создаем менеджер БД
    #db = DBManager(dbname="hh_vacancies", user="postgres", password="MegaFon", host="localhost", port="5432")
    db = DBManager(dbname=data_base_name, user="postgres", password=password, host="localhost", port="5432")
    if not flags_create_base:
        # Создаем таблицы базы данных
        db.create_tables()

        print("✅ Таблицы созданы!")

        # Проверим существование таблиц
        # db.check_tables_exist()

        # Список id организаций
        employers_list = [
            "829010",  # Sber
            "39209",  # Газпром бурение
            "39305",  # Газпром энергетика
            "78638",  # T-Bank
            "15478",  # VK
            "1740",  # Yandex
            "2748",  # Rosstech
            "3776",  # MTC
            "4934",  # BeeLine
            "1057",  # Kasperskiy
            "2180",  # Ozon
        ]

        # Список классов организаций
        employers = []

        print(cutter)

        for employ in employers_list:
            try:
                employer_data = ApiHH.get_employer(employ)

                employer = Employer(employer_data)
                db.add_employer(employer)
                employers.append(employer)
                employer_data_ = ApiHH.get_vacancies(employ, per_page=per_page_in_vacancies)
                counter_employers += 1
                print(f"✅ Успешно добавлен: {employer.name}")

                list_vacancies = []
                for vac in employer_data_.get("items"):
                    temp = Vacancy.from_dict(vac)
                    list_vacancies.append(temp)

                employer.add_vacancies(list_vacancies)

                for i in list_vacancies:
                    db.add_vacancy(i, employer.id)

                print(f'   ✅ Вакансии "{employer.name}" успешно добавлены в базу!')

            except Exception as e:
                print(f"❌ Ошибка с работодателем {employ}: {e}")

    print(cutter)
    print(f"✨ Добавлено организаций: {counter_employers}")
    print(cutter)

    if flags_vacancies_count:
        print()
        print("📄 Список всех компаний и количество вакансий у каждой компании!")
        print(cutter)
        vacancies_count = db.get_companies_and_vacancies_count()
        for i in vacancies_count:
            print(f'В бае данных организации "{i[0]}" - {i[1]} вакансий.')

    if flags_all_vacancies:
        print()
        print("📄 Список всех вакансий!")
        print(cutter)
        for i in db.get_all_vacancies():
            print_vacancy(i)
            """print(f'📁 Организация: "{i[0]}", 📄 Наименование вакансии: "{i[1]}"')
            print(f'Зарплата: {i[2]}, URL: {i[3]}')"""

    if flags_avg:
        print()
        print(cutter)
        print("Выводит среднюю зарплату по всем вакансиям в базе!")
        print(f"🎯 Средняя зарплата по вакансиям в базе данных: {db.get_avg_salary()}")

    if flags_higher_salary:
        print()
        print(f"Выводит список вакансий и организаций где зарплата выше средней {db.get_avg_salary()}!")
        print(cutter)
        for i in db.get_vacancies_with_higher_salary():
            print_vacancy(i)

    if flags_vacancies_keywords:
        print(cutter)
        print(f'Выводит список вакансий содержащих слово - "{keywords_for_search}"')
        for i in db.get_vacancies_with_keyword(keywords_for_search):
            print_vacancy(i)


if __name__ == "__main__":
    main()
