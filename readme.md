<div id="badges" align='center'>
    <a>
        <img src="https://img.shields.io/badge/Python-3.10-green?logo=Python">
    </a>
    <a>
        <img src="https://img.shields.io/badge/FastAPI-0.95-green?logo=fastapi&logoColor=black?style=plastic"/>
    </a>
    <a>
        <img src="https://img.shields.io/badge/alembic-1.10-green?logo=alembic&logoColor=black?style=plastic">
    </a>
    <a>
        <img src="https://img.shields.io/badge/postgresql-13-blue?logo=postgresql&logoColor=white">
    </a>
    <a>
        <img src="https://img.shields.io/badge/SQLalchemy-1.4.41-blue?logo=SQLalchemy">
    </a>
    <a>
        <img src="https://img.shields.io/badge/Docker-20.10.16-green?logo=Docker&logoColor=black?style=plastic">
    </a>
</div>

## Клонируем репозиторий:

    git clone https://github.com/Mitsufiro/bewise_second

## Развертывание

`docker-compose up`

## Migrations

При изменении модели данных необходимо создать миграцию

`docker exec app alembic revision --autogenerate -m "New Migration"`

Для применения изменений, необходимо запустить

`docker exec app alembic upgrade head`

* Создание юзера.

 <img src="screens/user_create.png" width="400" height="200">

* При входе заполняем данные пользователя и просто берем access token, который нам необходим для использования методов. Уникальный идентификатор пользователя вшит в токен.

 <img src="screens/login.png" width="400" height="200">

* Далее в зависиммости от прав юзера можем использовать методы.

* Обновление токена

 <img src="screens/refresh.png" width="400" height="200">

* Обновление данных юзера (Оставляем только те поля, которые нам нужны)

 <img src="screens/update_user.png" width="400" height="200">

* Загрузка файла (При загрузке создается личная папка юзера, файл конвертируется в формат mp3 и данне сохраняются в БД)

 <img src="screens/upload_file.png" width="400" height="200">

* Скачивание файла (Подаем ссылку)

 <img src="screens/download.png" width="400" height="200">

* Можем посмотреть какие файлы можно скачать

 <img src="screens/urls.png" width="400" height="200">

* Удаление юзером собственных файлов
 
 <img src="screens/delete.png" width="400" height="200">

* Удаление админом любых файлов
 
 <img src="screens/admin_delete.png" width="400" height="200">

## Finally:

• Реализован ролевой доступ к API-методам в зависимости от уровня прав пользователя.

• Настроена валидация данных.

• Swagger.

• Подготовлен docker-контейнер с сервисами.

• Универсальный CRUD.

• Реализация асинхронных методов.

• Настроено опциональное изменение данных пользователей (Чтобы изменить нужное поле необходимо оставить только его).

• Настроена аутентификация (Доступ к методам производится путем подачи токена со стороны пользователя).

• Код отредактирован (black, isort).

