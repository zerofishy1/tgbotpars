import requests
import json
import schedule
import time


def get_vacancies(keyword):
    url = "https://api.hh.ru/vacancies"
    params = {
        "text": keyword,
        "area": 1,  # Specify the desired area ID (1 is Moscow)
        "per_page": 20,  # Number of vacancies per page
    }
    headers = {
        "User-Agent": "Your User Agent",  # Replace with your User-Agent header
    }

    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        data = response.json()
        vacancies = data.get("items", [])


        vacancy_data = []
        for vacancy in vacancies:
            vacancy_info = {
                "id": vacancy.get("id"),
                "title": vacancy.get("name"),
                "url": vacancy.get("alternate_url"),
                "company": vacancy.get("employer", {}).get("name"),
                "experience": vacancy.get("experience", {}).get("name")
            }
            vacancy_data.append(vacancy_info)

        # Сохраняем данные в файл JSON
        with open("vacancies.json", "w") as f:
            json.dump(vacancy_data, f, indent=4)

        print("Данные о вакансиях сохранены в файл 'vacancies.json'.")
    else:
        print(f"Request failed with status code: {response.status_code}")


get_vacancies("python developer")
schedule.every().day.at("00:00").do(lambda: get_vacancies("python developer"))
while True:
    schedule.run_pending()
    time.sleep(60)