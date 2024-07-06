import telebot
import psycopg2
import json
import schedule
import time
from config import host, user, password, db_name

TOKEN = "7269084463:AAGZBCihckITxWGKiYoplbwCPOV2hYShKrc"
bot = telebot.TeleBot(TOKEN)

# Подключение к базе данных
def connect_to_db():
    try:
        connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=db_name,
            port=5432
        )
        return connection
    except Exception as _ex:
        print("[INFO] Error while connecting to PostgreSQL", _ex)
        return None

# Функция для выполнения SQL-запросов
def execute_query(query):
    connection = connect_to_db()
    if connection:
        with connection.cursor() as cursor:
            try:
                cursor.execute(query)
                result = cursor.fetchall()
                return result
            except Exception as _ex:
                print("[INFO] Error executing query:", _ex)
                return None
        connection.close()
    else:
        return None

# Функция для отправки результата запроса
def send_query_results(message, results):
    if results is not None:
        if len(results) > 0:
            response = "Результат запроса:\n"
            # Проверка, превышает ли результат лимит Telegram
            for i, row in enumerate(results):
                if i > 0 and i % 10 == 0:
                    bot.reply_to(message, response)
                    response = "Результат запроса (продолжение):\n"
                response += str(row) + "\n"
            bot.reply_to(message, response)
        else:
            bot.reply_to(message, "Запрос выполнен, но не вернул результатов.")
    else:
        bot.reply_to(message, "Ошибка выполнения запроса.")

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("Вакансии", callback_data="vacancies"))
    markup.add(telebot.types.InlineKeyboardButton("Кандидаты", callback_data="candidates"))
    bot.reply_to(message, "Добро пожаловать! Выберите категорию:", reply_markup=markup)

# Обработчик callback_data
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == "vacancies":
        bot.reply_to(call.message, "Выберите действие:")
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("Показать все", callback_data="show_all_vacancies"))
        markup.add(telebot.types.InlineKeyboardButton("Поиск по названию", callback_data="search_vacancies_by_title"))
        bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id,
                             text="Выберите действие:", reply_markup=markup)
    elif call.data == "candidates":
        bot.reply_to(call.message, "Выберите действие:")
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("Показать всех", callback_data="show_all_candidates"))
        markup.add(telebot.types.InlineKeyboardButton("Поиск по имени", callback_data="search_candidates_by_name"))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                             text="Выберите действие:", reply_markup=markup)
    elif call.data == "show_all_vacancies":
        results = execute_query("SELECT * FROM vc")
        send_query_results(call.message, results)
    elif call.data == "show_all_candidates":
        results = execute_query("SELECT * FROM vc WHERE Candidates IS NOT NULL")
        send_query_results(call.message, results)
    elif call.data == "search_vacancies_by_title":
        bot.reply_to(call.message, "Введите название вакансии:")
        bot.register_next_step_handler(call.message, handle_search_vacancies_by_title)
    elif call.data == "search_candidates_by_name":
        bot.reply_to(call.message,"Введите имя кандидата:")
        bot.register_next_step_handler(call.message, handle_search_candidates_by_name)

# Обработчики для поиска по названию вакансии и имени кандидата
def handle_search_vacancies_by_title(message):
    title = message.text
    results = execute_query(f"SELECT * FROM vc WHERE VacancyTitle LIKE '%{title}%'")
    send_query_results(message, results)

def handle_search_candidates_by_name(message):
    name = message.text
    results = execute_query(f"SELECT * FROM vc WHERE Candidates LIKE '%{name}%'")
    send_query_results(message, results)

bot.polling()