import sqlite3


# Функция для изменения поля пользователя
def update_user_field(user_id, field, new_value):
    # Подключаемся к базе данных
    conn = sqlite3.connect('blogs.db')
    cursor = conn.cursor()

    # Проверяем, существует ли пользователь с указанным ID
    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = cursor.fetchone()
    if user is None:
        print("Пользователь с указанным ID не найден.")
        conn.close()
        return

    # Обновляем указанное поле пользователя
    cursor.execute("UPDATE users SET {}=? WHERE id=?".format(field), (new_value, user_id))
    conn.commit()

    print("Поле '{}' пользователя с ID {} успешно изменено на '{}'.".format(field, user_id, new_value))

    # Закрываем соединение с базой данных
    conn.close()


# Основная функция программы
def main():
    user_id = input("Введите ID пользователя: ")
    field = input("Введите поле для изменения (name, about, rank, email, hashed_password, created_date): ")
    new_value = input("Введите новое значение: ")

    update_user_field(user_id, field, new_value)


if __name__ == "__main__":
    main()
