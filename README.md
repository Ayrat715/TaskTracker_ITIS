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
            "task_number": <number>,
            "name": <string>,
            "description": <string>,
            "given_time": <string (ISO 8601 datetime)>,
            "start_time": <string (ISO 8601 datetime)>,
            "end_time": <string (ISO 8601 datetime)>,
            "predicted_duration": <number>,
            "status": <number>,
            "author": <number>,
            "priority": <number>,
            "executors": [<number>],
            "sprints": [<number>]
        }
        ...
    ]

### POST task/tasks/ - Создать новую задачу

#### Тело запроса:

    {
        "executor_ids": [<number>],
        "sprint": [<number>],
        "name": <string>,
        "description": <string>,
        "given_time": <string (ISO 8601 datetime)>,
        "start_time": <string (ISO 8601 datetime)>,
        "end_time": <string (ISO 8601 datetime)>,
        "status": <number>,
        "author": <number>,
        "priority": <number>
    }

### GET task/tasks/{id}/ - Получить детали задачи

#### Ответ (200 OK):

    {
        "id": <number>,
        "task_number": <number>,
        "executor_ids": [<number>],
        "sprint_ids": [<number>],
        "name": <string>,
        "description": <string>,
        "given_time": <string (ISO 8601 datetime)>,
        "start_time": <string (ISO 8601 datetime)>,
        "end_time": <string (ISO 8601 datetime)>,
        "status": <number>,
        "author": <number>,
        "priority": <number>,
        "sprints": [<number>]
    }

### PUT task/tasks/{id}/ - Обновить задачу

#### Ответ (200 OK):

    {
        "executor_ids": [<number>],
        "sprint_ids": [<number>],
        "name": <string>,
        "description": <string>,
        "given_time": <string (ISO 8601 datetime)>,
        "start_time": <string (ISO 8601 datetime)>,
        "end_time": <string (ISO 8601 datetime)>,
        "status": <number>,
        "author": <number>,
        "priority": <number>
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

### GET /project/my-employee-ids/ - получение всех id employee, которыми является данный user
#### Ответ (200 OK):

    [
        {
            "id": <number>,
            "project_id": <number>
        }
        ...
    ]

## Проекты (Projects)

### POST /project/create/ - создание проекта

#### Тело запроса:

    {
        "name": <string>,
        "description": <string>,
        "start_time": <string (ISO 8601 datetime)>,
        "end_time": <string (ISO 8601 datetime)>,
        "group": <number>,
    }

### GET /project/{id}/ - получение данных проекта

#### Ответ (200 OK):

    {
        "id": <number>,
        "name": <string>,
        "description": <string>,
        "start_time": <string (ISO 8601 datetime)>,
        "end_time": <string (ISO 8601 datetime)>,
        "group": <number>,
    }

### PATCH /project/{id}/ - изменение данных проекта
    {
        "id": <number>,
        "name": <string>,
        "description": <string>,
        "start_time": <string (ISO 8601 datetime)>,
        "end_time": <string (ISO 8601 datetime)>,
        "group": <number>
    }

### DELETE /project/{id}/ - для удаления проекта

### GET /project/{id}/employees/ - Все работники конкретного проекта
#### Ответ (200 OK):

    [
        {
            "id": <number>, # employee.id
            "name": <string>
        },
        ...
    ]

### Ошибки:

#### 403 Bad Request - При создании проекта, пользователь должен принадлежать группе, указываемой в поле "Группа":

    {
        "group": ["Invalid group"]
    }

#### 400 Bad Request - Время начала проекта должно быть меньше времени завершения:

    {
        "non_field_errors": ["End time must occur after start time"]
    }

## Группы(Group)

### GET account/users/?email= - поиск пользователей по почте
#### Ответ (200 OK):
    {
        "id": <number>,
        "email": <string>
    }

### GET account/groups/ - список групп
#### Ответ (200 OK):
#### users: list - целочисленный список идентификаторов пользователей
    [
        {
            "id": <number>,
            "name": <string>,
            "users": [<number>]
        }
        ...
    ]

### POST /account/groups/ - создание группы
#### Ответ (201 Created):
    {
      "name": <string>,
      "users": [<number>]
    }

### PUT account/groups/{id} - изменение состава пользователей (добавление нового пользователя)
    {
      "users": [<number>]
    }

### DELETE account/groups-detail/{id} - удаление группы


### DELETE account/groups/{pk}/remove-user/{user_id}/ - удаление пользователя из группы


### GET task/priorities/ - список всех приоритетов
#### Ответ (200 OK):
    [
        {
            "id": <number>,
            "type": <string>,
            "weight": <number>
        }
        ...
    ]
### GET task/statuses/ - список всех статусов
#### Ответ (200 OK):
    [
        {
            "id": <number>,
            "type": <string>
        }
        ...
    ]

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
* * Не может состоять из персональных данных(почта и имя)
## Рекомендации по реализации
* Для работы с датами используйте ISO 8601 формат (YYYY-MM-DDTHH:MM:SSZ)
* При создании/обновлении задач сначала загрузите доступных исполнителей и спринты
* Реализуйте валидацию пароля на фронтенде перед отправкой на сервер