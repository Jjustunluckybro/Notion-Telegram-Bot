# Базовый образ с Python
FROM python:3.11


# Создание директории проекта
RUN mkdir /bot
WORKDIR /bot

# Копирование файлов зависимостей в контейнер
COPY pyproject.toml poetry.lock /./

# Установка poetry
RUN pip install poetry

# Установка зависимостей в контейнере
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root --no-dev

# Копирование исходного кода приложения в контейнер
COPY . .

# Запуск приложения
CMD [ "python", "-m", "src.main" ]
