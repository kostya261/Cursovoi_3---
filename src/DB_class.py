from contextlib import contextmanager
from typing import Any

import psycopg2

from src.employer import Employer
from src.vacancy import Vacancy


class DBManager:
    def __init__(self, dbname: str, user: str, password: str, host: str = "localhost", port: str = "5432") -> None:
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self._create_database()

    def _create_database(self) -> None:
        """Создает базу данных если ее нет"""
        try:
            # Подключаемся к стандартной базе postgres
            conn = psycopg2.connect(
                dbname="postgres", user=self.user, password=self.password, host=self.host, port=self.port
            )
            conn.autocommit = True

            with conn.cursor() as cur:
                # Пробуем создать базу
                try:
                    cur.execute(f"CREATE DATABASE {self.dbname}")
                    print(f"✅ База {self.dbname} создана успешно!")
                except psycopg2.Error as e:
                    if "already exists" in str(e):
                        print(f"ℹ️ База {self.dbname} уже существует")
                    else:
                        # логируем другие ошибки все равно
                        print(f"⚠️ Предупреждение: {e}")

            conn.close()

        except Exception as e:
            print(f"❌ Не удалось подключиться к PostgreSQL: {e}")
            raise e

    @contextmanager
    def _get_connection(self) -> Any:
        """Контекстный менеджер для подключения к БД"""
        conn = psycopg2.connect(
            dbname=self.dbname, user=self.user, password=self.password, host=self.host, port=self.port
        )
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def create_tables(self) -> None:
        """Создание таблиц в БД"""
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                print("🔄 Создаю таблицы...")

                # Таблица работодателей
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS employers (
                        id VARCHAR(20) PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        url VARCHAR(500),
                        vacancies_url VARCHAR(500),
                        open_vacancies INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                )
                print("✅ Таблица employers создана/проверена")

                # Таблица вакансий
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS vacancies (
                        id VARCHAR(20) PRIMARY KEY,
                        employer_id VARCHAR(20) REFERENCES employers(id) ON DELETE CASCADE,
                        name VARCHAR(500) NOT NULL,
                        salary VARCHAR(50),
                        salary_from INTEGER,
                        salary_to INTEGER,
                        currency VARCHAR(10),
                        url VARCHAR(500),
                        description TEXT,
                        experience VARCHAR(100),
                        employment_type VARCHAR(100),
                        published_at TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                )
                print("✅ Таблица vacancies создана/проверена")

                # Создание индексов
                cur.execute("CREATE INDEX IF NOT EXISTS idx_vacancies_employer_id ON vacancies(employer_id)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_vacancies_salary_from ON vacancies(salary_from)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_vacancies_salary_to ON vacancies(salary_to)")
                print("✅ Индексы созданы/проверены")

    def add_employer(self, employer: Employer) -> None:
        """Добавление работодателя в БД"""
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO employers (id, name, url, vacancies_url, open_vacancies)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    url = EXCLUDED.url,
                    vacancies_url = EXCLUDED.vacancies_url,
                    open_vacancies = EXCLUDED.open_vacancies
                """,
                    (employer.id, employer.name, employer.url, employer.vacancies_url, employer.open_vacancies),
                )

    def add_vacancy(self, vacancy: Vacancy, employer_id: str) -> None:
        """Добавление вакансии в БД"""
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO vacancies (id, employer_id, name, salary_from, salary_to, currency, url,
                                            description, experience, employment_type, published_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    salary_from = EXCLUDED.salary_from,
                    salary_to = EXCLUDED.salary_to,
                    currency = EXCLUDED.currency,
                    url = EXCLUDED.url,
                    description = EXCLUDED.description
                """,
                    (
                        getattr(vacancy, "id", None),  # если есть id в vacancy
                        employer_id,
                        vacancy.title,  # name из json
                        vacancy.salary_from,  # зарплата от
                        vacancy.salary_to,  # зарплата до
                        "RUR",  # просто вручную указал валюту
                        vacancy.url,  # url вакансии
                        vacancy.requirements,  # описание вакансии
                        None,  # experience - пока не используем
                        None,  # employment_type - пока не используем
                        None,  # published_at - пока не используем
                    ),
                )

    def get_companies_and_vacancies_count(self) -> Any:
        """
        Получает список всех компаний и количество вакансий у каждой компании
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT e.name, COUNT(v.id) as vacancy_count
                    FROM employers e
                    LEFT JOIN vacancies v ON e.id = v.employer_id
                    GROUP BY e.id, e.name
                    ORDER BY vacancy_count DESC
                """
                )
                return cur.fetchall()

    def get_all_vacancies(self) -> Any:
        """
        Получает список всех вакансий с указанием названия компании,
        названия вакансии, зарплаты и ссылки на вакансию
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        e.name as company_name,
                        v.name as vacancy_name,
                        CASE
                            WHEN v.salary_from IS NOT NULL AND v.salary_to IS NOT NULL
                                THEN v.salary_from || ' - ' || v.salary_to || ' ' || v.currency
                            WHEN v.salary_from IS NOT NULL
                                THEN 'от ' || v.salary_from || ' ' || v.currency
                            WHEN v.salary_to IS NOT NULL
                                THEN 'до ' || v.salary_to || ' ' || v.currency
                            ELSE 'Не указана'
                        END as salary,
                        v.url
                    FROM vacancies v
                    JOIN employers e ON v.employer_id = e.id
                    ORDER BY e.name, v.name
                """
                )
                return cur.fetchall()

    def get_avg_salary(self) -> Any:
        """
        Получает среднюю зарплату по вакансиям
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        ROUND(AVG(
                            CASE
                                WHEN salary_from IS NOT NULL AND salary_to IS NOT NULL
                                    THEN (salary_from + salary_to) / 2
                                WHEN salary_from IS NOT NULL
                                    THEN salary_from
                                WHEN salary_to IS NOT NULL
                                    THEN salary_to
                                ELSE NULL
                            END
                        )) as avg_salary
                    FROM vacancies
                    WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL
                """
                )
                result = cur.fetchone()
                return result[0] if result else 0

    def get_vacancies_with_higher_salary(self) -> Any:
        """
        Получает список всех вакансий, у которых зарплата выше средней по всем вакансиям
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        e.name as company_name,
                        v.name as vacancy_name,
                        CASE
                            WHEN v.salary_from IS NOT NULL AND v.salary_to IS NOT NULL
                                THEN v.salary_from || ' - ' || v.salary_to || ' ' || v.currency
                            WHEN v.salary_from IS NOT NULL
                                THEN 'от ' || v.salary_from || ' ' || v.currency
                            WHEN v.salary_to IS NOT NULL
                                THEN 'до ' || v.salary_to || ' ' || v.currency
                            ELSE 'Не указана'
                        END as salary,
                        v.url
                    FROM vacancies v
                    JOIN employers e ON v.employer_id = e.id
                    WHERE
                        (v.salary_from > (SELECT AVG(
                            CASE
                                WHEN salary_from IS NOT NULL AND salary_to IS NOT NULL
                                    THEN (salary_from + salary_to) / 2
                                WHEN salary_from IS NOT NULL
                                    THEN salary_from
                                WHEN salary_to IS NOT NULL
                                    THEN salary_to
                                ELSE NULL
                            END
                        ) FROM vacancies WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL))
                        OR
                        (v.salary_to > (SELECT AVG(
                            CASE
                                WHEN salary_from IS NOT NULL AND salary_to IS NOT NULL
                                    THEN (salary_from + salary_to) / 2
                                WHEN salary_from IS NOT NULL
                                    THEN salary_from
                                WHEN salary_to IS NOT NULL
                                    THEN salary_to
                                ELSE NULL
                            END
                        ) FROM vacancies WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL))
                    ORDER BY
                        CASE
                            WHEN v.salary_from IS NOT NULL THEN v.salary_from
                            ELSE v.salary_to
                        END DESC
                """
                )
                return cur.fetchall()

    def get_vacancies_with_keyword(self, keyword: str) -> Any:
        """
        Получает список всех вакансий, в названии которых содержатся переданные в метод слова
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        e.name as company_name,
                        v.name as vacancy_name,
                        CASE
                            WHEN v.salary_from IS NOT NULL AND v.salary_to IS NOT NULL
                                THEN v.salary_from || ' - ' || v.salary_to || ' ' || v.currency
                            WHEN v.salary_from IS NOT NULL
                                THEN 'от ' || v.salary_from || ' ' || v.currency
                            WHEN v.salary_to IS NOT NULL
                                THEN 'до ' || v.salary_to || ' ' || v.currency
                            ELSE 'Не указана'
                        END as salary,
                        v.url
                    FROM vacancies v
                    JOIN employers e ON v.employer_id = e.id
                    WHERE v.name ILIKE %s
                    ORDER BY e.name, v.name
                """,
                    (f"%{keyword}%",),
                )
                return cur.fetchall()

    # Дополнительный полезный метод
    def get_vacancies_count(self) -> Any:
        """Получает общее количество вакансий в базе"""
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM vacancies")
                return cur.fetchone()[0]
