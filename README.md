# Foodgram - продуктовый помощник.
## Что это такое?
Foodgram - это сервис, в котором пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## v1.0 Установка локально:
- Склонируйте репозиторий на свой компьютер.
- Создайте и активируйте виртуальное окружение:
```
python -m venv venv
. venv/Scripts/activate
```
- Установите зависимости: ``` pip install -r requirements.txt ```
- ВАЖНО: проект подразумевает использование СУБД postgres, поэтому убедитесь, что заранее запустили сервер postgres и создали базу данных. Подробности: https://www.postgresql.org/docs/
- Создайте .env файл в той же директории, где находится файл settings.py, и укажите данные для работы с базой данных в таком формате: DATABASE_URL=psql://database_user:database_password@host:port/database_name
- Проведите миграции: ``` python manage.py migrate ```
- Опционально можете загрузить список ингредиентов ``` python manage.py loaddata ingredients.json ```
- Запустите сервер ``` python manage.py runserver ```

## Технологии и источники:
- Python https://www.python.org/
- Django https://www.djangoproject.com/
- DRF https://www.django-rest-framework.org/
- Postgres https://www.postgresql.org/
