Инструкция по запуску проекта Pincrochet (локально)

Требования
- Python 3.10+ установлен

Шаги

1) Откройте терминал и перейдите в папку проекта (где находится папка pincrochet).
   Пример:
   cd /путь/к/папке/pincrochet

2) Создайте виртуальное окружение:
   Windows:
     python -m venv venv
   macOS / Linux:
     python3 -m venv venv

3) Активируйте виртуальное окружение:
   Windows (PowerShell):
     .\venv\Scripts\Activate.ps1
   Windows (cmd):
     .\venv\Scripts\activate
   macOS / Linux:
     source venv/bin/activate

4) Обновите pip и установите зависимости:
   pip install --upgrade pip
   pip install -r requirements.txt

5) (Необязательно) Установите секретный ключ:
   В app.py по умолчанию app.config['SECRET_KEY'] = 'replace-with-a-secure-key'
   Для разработки можно оставить как есть. Для безопасности замените на случайную строку
   или используйте .env с переменной SECRET_KEY.

6) Запустите приложение:
   python app.py

7) Откройте в браузере:
   http://127.0.0.1:5000/

Тестирование
- Зарегистрируйтесь через /register, затем войдите через /login.
- Откройте схему и нажмите «Сохранить», затем проверьте «Мои подборки».

Примечания
- Изображения берутся по внешним URL, папка static/images может оставаться пустой.
- Проект использует in-memory "базу" (USERS, PATTERNS). Данные не сохраняются после остановки сервера.
