# TaskTracker_ITIS
This is a project on the discipline "Digital Departments", the purpose of which will be to create a website for tracking tasks within projects for the Institute of Information Technology and Intelligent Systems.
API Endpoints

### Все API endpoints доступны по базовому URL (без деплоя пока https://localhost:8000/)

## Спринты (Sprints)
### Обязательные поля при создании: name, start_time, project

### GET task/sprints/ - Получить список всех спринтов

#### Ответ (200 OK):

    [
        {
            "id": <number>,
            "name": <string>,
            "description": <string>,
            "start_time": <string>,
            "end_time": <string (ISO 8601 datetime)>,
            "project": <number>
        },
        {
            "id": <number>,
            "name": <string>,
            "description": <string>,
            "start_time": <string (ISO 8601 datetime)>,
            "end_time": <string (ISO 8601 datetime)>,
            "project": <number>
        }
        ...
    ]

### POST task/sprints/ - Создать новый спринт

#### Тело запроса:

    {
        "name": <string>,
        "description": <string>,
        "start_time": <string (ISO 8601 datetime)>,
        "end_time": <string (ISO 8601 datetime)>,
        "project": <number>
    }

#### Ответ (201 Created):

    {
        "id": <number>,
        "name": <string>,
        "description": <string>,
        "start_time": <string (ISO 8601 datetime)>,
        "end_time": <string (ISO 8601 datetime)>,
        "project": <number>
    }

### GET task/sprints/{id}/ - Получить детали спринта

#### Ответ (200 OK):

    {
        "id": <number>,
        "name": <string>,
        "description": <string>,
        "start_time": <string (ISO 8601 datetime)>,
        "end_time": <string (ISO 8601 datetime)>,
        "project": <number>
    }

### PUT task/sprints/{id}/ - Обновить спринт

#### Тело запроса:

    {
        "id": <number>,
        "name": <string>,
        "description": <string>,
        "start_time": <string (ISO 8601 datetime)>,
        "end_time": <string (ISO 8601 datetime)>,
        "project": <number>
    }

#### Ответ (200 OK):

    {
        "id": <number>,
        "name": <string>,
        "description": <string>,
        "start_time": <string (ISO 8601 datetime)>,
        "end_time": <string (ISO 8601 datetime)>,
        "project": <number>
    }

### PATCH task/sprints/{id}/ - Частично обновить спринт

### DELETE task/sprints/{id}/ - Удалить спринт

## Ошибки:

#### 400 Bad Request - Время начала спринта должно быть меньше времени завершения:

    {
        "non_field_errors": ["End time must occur after start time"]
    }

## Задачи (Tasks)
### Обязательные поля при создании: name, executor, sprint(массив), start_time, author

### GET task/tasks/ - Получить список всех задач

#### Ответ (200 OK):

    [
        {
            "id": <number>,
            "name": <string>,
            "description": <string>,
            "status": <number>,
            "executor": <number>,
            "sprint": [<number>], 
            "given_time": <string (ISO 8601 datetime)>,
            "start_time": <string (ISO 8601 datetime)>,
            "end_time": <string (ISO 8601 datetime)>,
            "priority": <number>,
            "category": <number>,
            "nlp_metadata": JSON
        }
    ]

### POST task/tasks/ - Создать новую задачу

#### Тело запроса:

    {
        "name": <string>,
        "description": <string>,
        "status": <number>,
        "executor": <number>,
        "sprint": [<number>], 
        "given_time": <string (ISO 8601 datetime)>,
        "start_time": <string (ISO 8601 datetime)>,
        "end_time": <string (ISO 8601 datetime)>,
        "priority": <number>,
        "category": <number>,
        "nlp_metadata": JSON
    }


### GET task/tasks/{id}/ - Получить детали задачи

#### Ответ (200 OK):

    {
        "id": <number>,
        "name": <string>,
        "description": <string>,
        "status": <number>,
        "executor": <number>,
        "sprint": [<number>], 
        "given_time": <string (ISO 8601 datetime)>,
        "start_time": <string (ISO 8601 datetime)>,
        "end_time": <string (ISO 8601 datetime)>,
        "priority": <number>,
        "category": <number>,
        "nlp_metadata": JSON
    }

### PUT task/tasks/{id}/ - Обновить задачу

#### Ответ (200 OK):

    {
        "id": <number>,
        "name": <string>,
        "description": <string>,
        "status": <number>,
        "executor": <number>,
        "sprint": [<number>], 
        "given_time": <string (ISO 8601 datetime)>,
        "start_time": <string (ISO 8601 datetime)>,
        "end_time": <string (ISO 8601 datetime)>,
        "priority": <number>,
        "category": <number>,
        "nlp_metadata": JSON
    }

### PATCH task/tasks/{id}/ - Частично обновить задачу

### DELETE task/tasks/{id}/ - Удалить задачу

### Ошибки:

#### 400 Bad Request - Время начала выполнения задачи должно быть меньше времени завершения:

    {
        "non_field_errors": ["End time must occur after start time"]
    }

#### 400 Bad Request - Ошибка отсутствующих спринтов:

    {
        "sprint": ["Some sprints do not exist."]
    }

#### 403 Bad Request - Исполнитель не принадлежит проекту:

    {
        "executor": ["The executor does not belong to any of the selected sprints' projects."]
    }



## Регистрация пользователя

#### Тело запроса:

    {
        "name": <string>,
        "email": <string>,
        "password": "<string>,
        "password2": <string>
    }

### POST /account/registration-user/ - Регистрация нового пользователя

## Авторизация пользователя

### POST /account/login-user/ - Вход в систему

    {
        "email": <string>,
        "password": <string>
    }

#### Успешный ответ (200 OK):

    {
        "message": "Login successful"
    }

#### 400 Bad Request - неверные учетные данные:

    {
        "email": ["Email or password is incorrect"]
    }

## Проекты (Projects)

### POST /project/create/ - для создания проекта

#### Тело запроса:

    {
        "name": <string>,
        "description": <string>,
        "start_time": <string (ISO 8601 datetime)>,
        "end_time": <string (ISO 8601 datetime)>,
        "group": <number>,
    }

### GET /project/{id}/ - для получения данных проекта

#### Ответ (200 OK):

    {
        "id": <number>,
        "name": <string>,
        "description": <string>,
        "start_time": <string (ISO 8601 datetime)>,
        "end_time": <string (ISO 8601 datetime)>,
        "group": <number>,
    }

### PATCH /project/{id}/ - для изменения данных проекта

### DELETE /project/{id}/ - для удаления проекта

### Ошибки:

#### 403 Bad Request - При создании проекта, пользователь должен принадлежать группе, указываемой в поле "Группа":

    {
        "group": ["Invalid group"]
    }

#### 400 Bad Request - Время начала проекта должно быть меньше времени завершения:

    {
        "non_field_errors": ["End time must occur after start time"]
    }



## Дополнительная информация
## Статусы задач (Status)
### Доступные типы статусов:
* required check
* planned
* active
* completed
* archived
## Приоритеты задач (Priority)
### Доступные типы приоритетов:
* high (вес 4)
* medium (вес 3)
* low (вес 2)
* default (вес 1)
## Категории задач (TaskCategory)
### Содержат:
* name - название категории
* description - описание
* keywords - ключевые слова для автоматической классификации
## Регистрация пользователя
### Требования:
* Пароль и его подтверждение должны совпадать
* Также пароль должен соответствовать стандартным требованиям Django:
* * Должен содержать минимум 8 символов
* * Не может быть полностью числовым
* * Не может быть слишком простым/распространенным
## Рекомендации по реализации
* Для работы с датами используйте ISO 8601 формат (YYYY-MM-DDTHH:MM:SSZ)
* При создании/обновлении задач сначала загрузите доступных исполнителей и спринты
* Реализуйте валидацию пароля на фронтенде перед отправкой на сервер