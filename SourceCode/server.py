import json
import socket
import logging
from flask import Flask, render_template, request
import threading

# Создаем экземпляр приложения Flask
app = Flask(__name__)
# Отключаем логирование запросов с кодом ответа 200 (OK)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
# -------------------------------------------------------------
# Замена значение в JSON
def update_json_field(field_name, new_value):
    try:
        # Открываем JSON-файл и загружаем данные
        with open('config.json', 'r') as json_file:
            data = json.load(json_file)

        # Обновляем значение нужного поля
        data[field_name] = new_value

        # Записываем измененные данные обратно в файл
        with open('config.json', 'w') as json_file:
            json.dump(data, json_file, indent=4)
    except:
        print("Ошибка при изменение JSON")

# Функция для получения IP-адреса компьютера и сохранение его в JSON
def get_and_save_ip_address():
    try:
        # Создаем сокет и получаем локальный IP-адрес
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()

        update_json_field("ip", ip_address)

        return ip_address
    except socket.error:
        print("JSON-файл с IP-адресом не найден.")
        return ""

# Возвращает значение IP-адреса из JSON файла 
def get_ip_from_json():
    try:
        # Открываем JSON-файл и загружаем данные
        with open('config.json', 'r') as json_file:
            data = json.load(json_file)
            ip_address = data.get('ip', None)
            return ip_address
    except FileNotFoundError:
        print("JSON-файл с IP-адресом не найден.")
        return ""

# Возвращает значение порта из JSON файла 
def get_port_from_json():
    try:
        # Открываем JSON-файл и загружаем данные
        with open('config.json', 'r') as json_file:
            data = json.load(json_file)
            ip_address = data.get('port', None)
            return ip_address
    except FileNotFoundError:
        print("JSON-файл с портом не найден.")
        return "8080"
# -------------------------------------------------------------


# -------------------------------------------------------------
# Получение IP
def get_ip():
    # Получаем ip из файла
    ip = get_ip_from_json()

    # Если произошла ошибка, или ip в файле не оказалось
    # То получаем его и сохраняем
    if (ip == ""):
        ip = get_and_save_ip_address()

    if (ip == ""):
        raise Exception("Не удалось получить IP-адрес")

    return ip
        
# Получение Port
def get_port():
    port = get_port_from_json()
    try:
        port = int(port)
        return str(port)
    except:
        update_json_field('port', '8080')

        return "8080"
# -------------------------------------------------------------


# -------------------------------------------------------------
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        if name:
            message = f"Кнопку нажал: {name}"
        else:
            message = "Кнопку нажал: Неизвестный"
    else:
        message = ""
    print(message)
    reset_text(message)
    return render_template('index.html', message=message)
# -------------------------------------------------------------


import tkinter as tk

def change_text():
    label.config(text="Ожидание")

def reset_text(new_text):
    if label.cget("text") == "Ожидание":
      label.config(text=new_text)

def reset_text_ip(new_text):
    ip_label.config(text=new_text)

# Создаем окно
root = tk.Tk()
root.title("Своя игра")

# Верхняя надпись
title_label = tk.Label(root, text="Своя игра", font=("Arial", 16))
title_label.pack(pady=10)

# Надпись по центру
label = tk.Label(root, text="Ожидание", bg="gray", width=30, height=10, font=("Arial", 14))
label.pack(pady=20)

reset_button = tk.Button(root, text="Сбросить", command=change_text)
reset_button.pack(pady=5)

# Нижняя надпись с IP-адресом
ip_label = tk.Label(root, text="ip:", font=("Arial", 10))
ip_label.pack(pady=10)


def start_server():
    ip_address = get_ip()
    port = get_port()
    reset_text_ip(ip_address + ":" + port)
    app.run(host=ip_address, port=port)

if __name__ == '__main__':
    server_thread = threading.Thread(target=start_server)
    server_thread.start()

    root.mainloop()
    server_thread.join()
    