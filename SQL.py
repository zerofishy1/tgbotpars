import psycopg2
import json
import schedule
import time
from config import host, user, password, db_name

def load_vacancies():
    connection = None

    try:
        connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=db_name,
            port=5432
        )
        connection.autocommit = True

        with connection.cursor() as cursor:
            # Создаем таблицу (если она еще не существует)

            print("[INFO] Table 'vc' created or already exists.")

            # Читаем данные из JSON-файла
            with open("vacancies.json", "r") as f:
                vacancies = json.load(f)

            # Вставляем данные в таблицу
            for vacancy in vacancies:
                cursor.execute(
                    """INSERT INTO vc (Title, Company, Experience, URL) VALUES (%s, %s, %s, %s)""",
                    (vacancy["title"], vacancy["company"], vacancy["experience"], vacancy["url"])
                )
            print("[INFO] Data inserted into table 'vc'.")

    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL", _ex)
    finally:
        if connection:
            connection.close()
            print("[INFO] PostgreSQL connection closed")

# Запланируем выполнение функции load_vacancies() каждый день в 00:00
schedule.every().day.at("00:00").do(load_vacancies)


while True:
    schedule.run_pending()
    time.sleep(1)
