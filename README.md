<h1>Телеграам бот - Сервис напоминаний</h1>

<h2>Описание</h2>

Телеграм бот заметок и напоминаний. Данный бот является ui частью приложения напоминаний, использующий сервис напоминаний через API 

[Сервис напоминаний](https://github.com/Jjustunluckybro/NotionServer)

<h2>Запуск в докер контейнере</h2>

1. Создать контейнр
```commandline
docker build -t alarm-bot-tg-client .
```
2. Запустить контейнер, прокинув необходимые переменные окружения (см. `.env-example`)
```commandline
docker run -d -p 87:80
  --restart always 
  --name alarm-bot-tg-client
  --env BACKEND_HOST=$BACKEND_HOST
  --env BACKEND_USER_LOGIN=$BACKEND_USER_LOGIN
  --env BACKEND_USER_PASSWORD=$BACKEND_USER_PASSWORD
  --env BOT_TOKEN=$BOT_TOKEN 
  alarm-bot-tg-client
```

<h2>Файловая структура проекта</h2>

```
- .github
    - workflows // ci/cd конфиги для github actions
- src
    - handlers  // Все ручки для взаимодействия с ботом со стороны пользователя бота
        - user_callbacks  // Все ручки, которые используют inline клавиатуру
            - fsm  // Ручки использующие inline клавиатуру и логику состояний, для проведения пользователя по конкретному сценарию
    - models  // Модели данных
    - services
        - requests // Логика для асинхронных http запросов
        - scheduler
            - jobs         // Джобы запускаемые в шедулере
            - scheduler.py // Шедулер
        - storage // Логика для взаимодействия с API хранилища данных в лице приложения 'Сервис напоминаний'
        - ui      // UI элементы телеграм бота
    - utils
        - exceptions         // Кастомные исключения, используемые в приложении
        - fsm                // Машины состояний используемые в приложении
        - config.py          // Модуль с переменными окружения
        - handler_utils.py   // Доп. функции используемые в ручках взаимодействия с ботом
        - request_methods.py // Методы http запросов для сервиса ассинхронных запросов
        - statuses.py        // Статусы http ответов
    - main.py  // Точка входа при запуске приложения
```
