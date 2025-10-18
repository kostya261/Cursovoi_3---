def print_vacancy(i: list) -> None:
    try:
        print(f'📁 Организация: "{i[0]}", 📄 Наименование вакансии: "{i[1]}"')
        print(f"   Зарплата: {i[2]}, URL: {i[3]}")
    except ValueError:
        print("Нет вакансии!")
