import telebot
import sqlite3
from telebot import types

# Initialize bot with your bot token
BOT_TOKEN = "7897850545:AAE273cSvEiG80VDc9-JGzXJLRLngeGzjvA"
bot = telebot.TeleBot(BOT_TOKEN)

# Database setup
def init_db():
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        account_login TEXT UNIQUE,
                        telegram_ids TEXT,
                        username TEXT,
                        points INTEGER DEFAULT 0)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS problems (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        photo BLOB,
                        answer TEXT)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS solved_problems (
                        user_id INTEGER,
                        problem_id INTEGER,
                        PRIMARY KEY (user_id, problem_id))''')
    
    conn.commit()
    conn.close()

init_db()

# Helper function to connect to database
def db_connection():
    return sqlite3.connect("bot_database.db")

# Command handlers
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, '''Добро пожаловать в соревнование для поступающих в "Лицей Иннополис" от Ильназа Рафисовича!\n\n'''
                 '''Введите команду /help или нажмите на нее, чтобы узнать все правила.''')
    
@bot.message_handler(commands=['help'])
def send_welcome(message):
    bot.reply_to(message, '''Список команд:\n\n'''
                 '''/register - Зарегестрироваться как новый пользователь\n'''
                 '''Вы можете использовать данную команду, чтобы попасть в общий рейтинг, вам нужно использовать эту команду только один раз, в самом начале\n\n'''
                 '''/login - Войти в аккаунт\n'''
                 '''Это команда создана специально, если вы захотите решать задачи с нескольких телеграм аккаунтов. Используйте ее, чтобы войти в уже существующий аккаунт.\n\n'''
                 '''/solve - Решать задачу\n'''
                 '''Нажав на эту команду, вы получите задачу, вам нужно будет только ввести ответ, за правильный вы получите 1 балл, а за неправильный у вас вычтутся 0.1 балла.\n\n'''
                 '''/ranking - Посмотреть рейтинг\n'''
                 '''Вы получите список всех участников и сможете посмотреть на каком месте находитесь вы''')

@bot.message_handler(commands=['register'])
def register_user(message):
    bot.reply_to(message, "Введите уникальный ключ-пароль, который будет работать как способ входа в аккаунт. Учтите, что вы должны хранить этот ключ в тайне, по нему любой сможет войти в ваш аккаунт.")
    bot.register_next_step_handler(message, process_registration)

def process_registration(message):
    account_login = message.text.strip()
    telegram_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name

    conn = db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (account_login, telegram_ids, username) VALUES (?, ?, ?)", (account_login, str(telegram_id), username))
        conn.commit()
        bot.reply_to(message, "Регистрация выполнена! Теперь вы можете использовать команду /solve чтобы начать решать задачи.")
    except sqlite3.IntegrityError:
        bot.reply_to(message, "Ошибка, попробуйте зарегестрироваться еще раз, используя другой ключ")
    finally:
        conn.close()

@bot.message_handler(commands=['login'])
def login_user(message):
    bot.reply_to(message, "Введите ваш ключ для входа в аккаунт.")
    bot.register_next_step_handler(message, process_login)

def process_login(message):
    account_login = message.text.strip()
    telegram_id = message.from_user.id

    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE account_login = ?", (account_login,))
    user = cursor.fetchone()

    if user:
        telegram_ids = user[2].split(',')
        if str(telegram_id) not in telegram_ids:
            telegram_ids.append(str(telegram_id))
            cursor.execute("UPDATE users SET telegram_ids = ? WHERE account_login = ?", (','.join(telegram_ids), account_login))
            conn.commit()
        bot.reply_to(message, f"Добро пожаловать обратно, {user[3]}! Используйте /solve чтобы начать решать задачи.")
    else:
        bot.reply_to(message, "Аккаунт не найден. Используйте /register, чтобы создать новый аккаунт, или /login, чтобы попробовать еще раз.")
    conn.close()

@bot.message_handler(commands=['solve'])
def send_problem(message):
    telegram_id = message.from_user.id

    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE instr(telegram_ids, ?) > 0", (str(telegram_id),))
    user = cursor.fetchone()

    if not user:
        bot.reply_to(message, "В начале вам нужно зарегестриваться или войти в аккаунт. Используйте /register или /login.")
        conn.close()
        return
    
    user_id = user[0]

    cursor.execute("""
                       SELECT * FROM problems 
                       WHERE id NOT IN (SELECT problem_id FROM solved_problems WHERE user_id = ?)
                       ORDER BY RANDOM() LIMIT 1
                   """, (user_id,))
    problem = cursor.fetchone()
    conn.close()

    if problem:
        problem_id, photo, answer = problem
        bot.send_photo(message.chat.id, photo, caption="Решите данную задачу:")

        bot.register_next_step_handler(message, check_answer, problem_id, answer)
    else:
        bot.reply_to(message, "Никакие задачи пока недоступны. Попробуйте проверить позже.")

def check_answer(message, problem_id, correct_answer):
    user_answer = message.text.strip()
    telegram_id = message.from_user.id

    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE instr(telegram_ids, ?) > 0", (str(telegram_id),))
    user = cursor.fetchone()

    if user:
        user_id = user[0]

        if user_answer == correct_answer:
            cursor.execute("UPDATE users SET points = points + 1 WHERE instr(telegram_ids, ?) > 0", (str(telegram_id),))
            cursor.execute("INSERT INTO solved_problems (user_id, problem_id) VALUES (?, ?)", (user_id, problem_id))
            conn.commit()
            bot.reply_to(message, '''Правильно! Вы получили 1 балл. Что хотите сделать дальше?\n'''
                        '''/solve - Решать задачу\n'''
                        '''/ranking - Посмотреть рейтинг\n''')
        else:
            cursor.execute("UPDATE users SET points = points - 0.1 WHERE instr(telegram_ids, ?) > 0", (str(telegram_id),))
            conn.commit()
            bot.reply_to(message, '''Неправильно. Вы получили штраф в 0.1 балл. Что хотите сделать дальше?\n'''
                        '''/solve - Решать задачу\n'''
                        '''/ranking - Посмотреть рейтинг\n''')
        
        conn.close()

@bot.message_handler(commands=['ranking'])
def show_ranking(message):
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username, points FROM users ORDER BY points DESC")
    leaderboard = cursor.fetchall()
    conn.close()

    if leaderboard:
        ranking = "\U0001F3C6 Leaderboard:\n\n"
        for idx, (username, points) in enumerate(leaderboard, start=1):
            ranking += f"{idx}. {username}: {round(points, 1)} баллов\n"
        bot.reply_to(message, ranking)
    else:
        bot.reply_to(message, "Пока нет пользователей в списке рейтинга.")

# Start polling for messages
bot.polling()
