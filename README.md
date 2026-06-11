## Лабораторная работа № 2 "Изучение контейнеризации, аутентификации и авторизации сервисов"

### Дисциплина: "Облачные вычислительные системы"

#### Цели и задачи работы:

1. Познакомиться со способами аутентификации и авторизации сервисов в 
   облачных системах.
2. Изучить принципы работы сервиса аутентификации и авторизации `Keycloak`.
3. Изучить особенности контейнеризации сервисов с использованием `Docker`.
4. Доработать код сервиса инференса из первой лабораторной работы для 
   реализации его аутентификации через `OAuth2` с помощью системы `Keycloak`.
5. Контейнеризовать доработанный сервис с использованием `Docker`, реализовать 
   оркестрацию используемых в работе сервисов с помощью `docker-compose`
6. Настроить автоматическую публикацию образов сервисов в репозиторий 
   `DockerHub` с помощью `Github Actions`.

#### Порядок выполнения работы

1. Создайте папку на компьютере для проекта и склонируйте в нее содержимое 
   репозитория:

> `git clone https://github.com/kpdvstu/CloudCS-Lab2.git`

2. Изучите реализованный в проекте способ определения наличия прав клиента на 
   выполнение операции инференса.
3. Изучите файл `docker-compose.yml`. Разберитесь, каким образом будут 
   выполняться Docker-контейнеры. Образы, собираемые в проекте, доступны в 
   [DockerHub репозитории](https://hub.docker.com/r/kpdvstu/cloud-cs/tags).
4. Запустите контейнеры `keycloak` и `postgres` с помощью нижеприведенной 
   команды. Сервис `inference` _пока запускать **не нужно**_, поскольку он 
   требует уже настроенного Keycloak!

> `docker-compose up -d postgres keycloak`

5. Дождитесь окончания процессов запуска и инициализации контейнеров. Статус 
   их работы можно посмотреть с помощью команды:

> `docker-compose logs`

6. Удостоверившись в корректном запуске сервисов `postgres` и `keycloak`, 
   передите в браузере по адресу https://localhost:8443.
7. В открывшемся окне перейдите в раздел "Administration Console" и 
   авторизуйтесь от имени администратора Keycloak (логин: `admin`, пароль 
   указан в файле `.env`). В случае успешной авторизации перед Вами 
   откроется веб-панель управления системой `Keycloak`.
8. Теперь необходимо настроить Keycloak для корректной работы с ним сервиса 
   инференса. Создайте новую область безопасности (`realm`) с именем `inference` 
   (см. [документацию](https://www.keycloak.org/docs/latest/server_admin/#proc-creating-a-realm_server_administration_guide)). 
   Настраивать область безопасности не нужно.
9. В созданной области безопасности создайте клиента (см. [документацию](https://www.keycloak.org/docs/latest/server_admin/#proc-creating-oidc-client_server_administration_guide))
   со следующими параметрами:
   * `Client ID`: **inference-client**
   * `Always Display in Console`: **On**
   * `Client authentication`: **On**
   * `Authorization`: **On**
   * `Authentication flow`: только **Service accounts roles**, остальные 
     галочки нужно снять. При включении опции авторизации **Service accounts 
     roles** параметр включится автоматически, и отключить его не получится.
   * `Web Origins`: *
   * Остальные опции следует оставить по умолчанию.

10. На панели слева выберите пункт `Clients`, выберите вновь созданного 
    клиента и перейдите на вкладку `Credentials`. Значение **Client secret** 
    на данной вкладке вместе с указанным ранее значением **Client ID** 
    необходимо указать в файле `.env` в соответствующих полях.
11. Аналогичным образом создайте еще два клиента с теми же настройками:
    * `Privileged-client`, которому будет разрешено выполнять инференс;
    * `Unprivileged-client`, которому данное действие будет запрещено.
    
    Запишите их **Client ID** и **Client secret**, они понадобятся позже при 
    выполнении запросов к сервису.
12. Теперь нужно настроить привелегированному клиенту права на доступ к 
    ресурсу инференса. На панели слева выберите пункт `Clients`, выберите 
    клиента **inference-client** и перейдите на вкладку `Authorization`. Далее, 
    перейдите на вкладку `Scopes`. Создайте новый scope с именем `doInfer`.
13. Перейдите на вкладку `Resourses`. Создайте новый ресурс, соответствующий 
    ресурсу сервиса `/predictions`, отвечающего за инференс. Параметры ресурса:
    * `Name`: **infer_endpoint**
    * `URIs`: **/predictions**
    * `Authorization scopes`: **doInfer**
    * Остальные опции следует оставить по умолчанию.
14. Перейдите на вкладку `Policies`. Создайте новую политику типа `Client` с 
    параметрами:
    * `Name`: **inference-policy**
    * `Clients`: **privileged-client**
    * `Logic`: **Positive**
15. Перейдите на вкладку `Permissions`. Создайте новое разрешение типа 
    `scope-based permission` с параметрами:
    * `Name`: **inference-permission**
    * `Resources`: **infer_endpoint**
    * `Authorization scopes`: **doInfer**
    * `Policies`: **inference-policy**
    * `Decision strategy`: **Unanimous**
    * Остальные опции следует оставить по умолчанию.
16. Теперь можно запускать сервис инференса. Выполните команду:

> `docker-compose up -d inference`

17. Убедитесь, что сервис успешно запустился. Если в процессе запуска 
    появились ошибки, исправьте их (как правило, это связано с неправильным 
    конфигурированием `Keycloak`).
18. Проверьте работоспособность сервиса, перейдя в браузере по адресу: 
    http://localhost:8000/healthcheck.
19. Получите токен доступа привилегированного сервиса c использованием `curl` 
    (или любого другого клиента, например, `telnet`, `PuTTY`, `Postman` и др.):
> `curl --insecure --request POST
https://localhost:8443/realms/inference/protocol/openid-connect/token 
--header 'Content-Type: application/x-www-form-urlencoded'
--data-urlencode 'client_id=privileged-client'
--data-urlencode 'client_secret=<privileged-client-secret>'
--data-urlencode 'grant_type=client_credentials'` 

20. Выполните запрос на инференс от имени привилегированного пользователя:
> `curl -X POST http://localhost:8000/predictions -H "Authorization: Bearer 
<access-token>" -H 'Content-Type: application/json' -d '{"cylinders": 4, 
"displacement": 113.0, "horsepower": 95.0, "weight": 2228.0, 
"acceleration": 14.0, "model_year": 71, "origin": 3}'`

21. Убедитесь в работоспособности инференса для привилегированного 
    пользователя. Аналогичным образом запросите токен для 
    непривилегированного пользователя и попробуйте выполнить инференс с ним. 
    Убедитесь в отсутствии доступа.

#### Индивидуальное задание

*Данная лабораторная работа является составной частью курсовой работы, защищаемой студентами в конце семестра.*
При выполнении лабораторной работы можно использовать **любые** языки и фреймворки, позволяющие выполнить поставленную задачу.

1. Для своего сервиса, разработанного в процессе выполнения *первой* 
   лабораторной работы, реализуйте аутентификацию и авторизацию с 
   использованием `Keycloak`. Воспользуйтесь представленным проектом как 
   образцом.
2. Выполните контейнеризацию разработанного Вами сервиса, составьте 
   соответствующий `Dockerfile`.
3. Выполните оркестрацию всех сервисов, используемых в работе, с 
   использованием инструмента `docker-compose`. Составьте соответствующий 
   `docker-compose.yml`.
4. Добейтесь работоспособности сервиса, продемонстрируйте корректную 
   обработку запросов преподавателю для привилегированного и 
   непривилегированного пользователей.

5. Создайте свой репозиторий на `GitHub` с разработанным проектом. 
   Реализуйте CI/CD-конвейер в `GitHub Actions` для тестирования сервиса, 
   сборки Docker-образов и размещения их в DockerHub. Убедитесь в его 
   работоспособности. **Не забудьте прописать корректные [GitHub Secrets](https://docs.github.com/ru/actions/security-guides/encrypted-secrets)
   для сохранения в GitHub конфиденциальных данных!** 

6. Оформите вторую главу пояснительной записки к **курсовой работе**, описав 
   в ней следующие моменты:

* Постановку задачи.
* Реализацию модулей сервиса, ответственных за выполнение аутентификации и 
  авторизации с помощью `Keycloak`.
* Процесс настройки `Keycloak` для различных категорий пользователей, 
  использующихся в работе.
* Структуру созданных `Dockerfile` и `docker-compose.yml`, обоснование 
  применения используемых в них инструкций.
* Команды сборки образов и запуска контейнеров со скринами, 
  подтверждающими успешность их выполнения.
* Тестирование работоспособности сервиса и CI/CD (содержание запросов, 
  содержание ответов, демонстрация корректной обработки сервисом различных 
  сценариев, возникающих в процессе его использования (в том числе, 
  ошибочных), скрины с результатами тестирования и их пояснением).
* Выводы по главе с анализом полученных результатов.

Privileg

curl.exe --insecure --request POST "https://localhost:8443/realms/inference/protocol/openid-connect/token" --header "Content-Type: application/x-www-form-urlencoded" --data-urlencode "client_id=privileged-client" --data-urlencode "client_secret=u37TsN0ZS2QyTPYxcttmLECQzIgZrORU" --data-urlencode "grant_type=client_credentials"

curl.exe -X POST http://localhost:8000/predictions -H "Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJlbUNDYVliYU9PbWZxWWE5VmtTbkZsMWhHR3pJbzROVF92Y001S2VfUFdVIn0.eyJleHAiOjE3ODExMTMyMTAsImlhdCI6MTc4MTExMjkxMCwianRpIjoiZDk5NTU5NTMtNDBhMi00NzZkLTg5Y2UtNzEwOTMzZTI3NjUzIiwiaXNzIjoiaHR0cHM6Ly9sb2NhbGhvc3Q6ODQ0My9yZWFsbXMvaW5mZXJlbmNlIiwiYXVkIjoiYWNjb3VudCIsInN1YiI6Ijc3YzkyNTI0LWU2MTgtNGNhZC1hYzRmLTA2YTNiYzZkMTNlMCIsInR5cCI6IkJlYXJlciIsImF6cCI6InByaXZpbGVnZWQtY2xpZW50IiwiYWNyIjoiMSIsImFsbG93ZWQtb3JpZ2lucyI6WyIvKiJdLCJyZWFsbV9hY2Nlc3MiOnsicm9sZXMiOlsiZGVmYXVsdC1yb2xlcy1pbmZlcmVuY2UiLCJvZmZsaW5lX2FjY2VzcyIsInVtYV9hdXRob3JpemF0aW9uIl19LCJyZXNvdXJjZV9hY2Nlc3MiOnsicHJpdmlsZWdlZC1jbGllbnQiOnsicm9sZXMiOlsidW1hX3Byb3RlY3Rpb24iXX0sImFjY291bnQiOnsicm9sZXMiOlsibWFuYWdlLWFjY291bnQiLCJtYW5hZ2UtYWNjb3VudC1saW5rcyIsInZpZXctcHJvZmlsZSJdfX0sInNjb3BlIjoiZW1haWwgcHJvZmlsZSIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwiY2xpZW50SG9zdCI6IjE3Mi4yMC4wLjEiLCJjbGllbnRJZCI6InByaXZpbGVnZWQtY2xpZW50IiwicHJlZmVycmVkX3VzZXJuYW1lIjoic2VydmljZS1hY2NvdW50LXByaXZpbGVnZWQtY2xpZW50IiwiY2xpZW50QWRkcmVzcyI6IjE3Mi4yMC4wLjEifQ.Z1SbXW4ca3iBYq0Bj0D19JdrljpMHYvoPCIkkTlIyDVHkoUOrvfICMrY8SfsIoYkFvq7hBZbucF4ncJluW6LVyZytrOx1uogDse7erp84bx0k2cZD1bmEEXUthJTjWTnzCdT0YfVn2vXPMi0PbMBky9LLnvdYHxWsEuKCzdDKZP-OQt91rSDaHOXMtgqcXijfLFQBI0eBWfz0XXyhmbYiwANooFYfFQ6RlKf95W6XTl0Sex3cODqAkpz6SAVusSH-aXSx2-sXAl_gfzJj6OYxkJB4IZLk7JgGcfaceKiX96fJ1SQc4hUidFEmxImm3T3C3lhkHy4YSt-XMpZ2JuPyQ" -H "Content-Type: application/json" -d "{\"longitude\": -122.23, \"latitude\": 37.88, \"housing_median_age\": 41.0, \"total_rooms\": 880.0, \"total_bedrooms\": 129.0, \"population\": 322.0, \"households\": 126.0, \"median_income\": 8.3252}"

UNORIVILEG

curl.exe --insecure --request POST "https://localhost:8443/realms/inference/protocol/openid-connect/token" --header "Content-Type: application/x-www-form-urlencoded" --data-urlencode "client_id=unprivileged-client" --data-urlencode "client_secret=cyB35L9bDyM4GBwoC6h2tDYpc7sRv8xt" --data-urlencode "grant_type=client_credentials"

curl.exe -X POST http://localhost:8000/predictions -H "Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJlbUNDYVliYU9PbWZxWWE5VmtTbkZsMWhHR3pJbzROVF92Y001S2VfUFdVIn0.eyJleHAiOjE3ODExMTM0OTYsImlhdCI6MTc4MTExMzE5NiwianRpIjoiODBkN2VjYmYtZjI2My00NWU4LTgxNDItMjNhOWNjZjE2MWUyIiwiaXNzIjoiaHR0cHM6Ly9sb2NhbGhvc3Q6ODQ0My9yZWFsbXMvaW5mZXJlbmNlIiwiYXVkIjoiYWNjb3VudCIsInN1YiI6IjVjYTVmNDdhLTQ2OGItNDAwMy05NGY1LTEwMjg4ODExMjE4ZCIsInR5cCI6IkJlYXJlciIsImF6cCI6InVucHJpdmlsZWdlZC1jbGllbnQiLCJhY3IiOiIxIiwiYWxsb3dlZC1vcmlnaW5zIjpbIi8qIl0sInJlYWxtX2FjY2VzcyI6eyJyb2xlcyI6WyJkZWZhdWx0LXJvbGVzLWluZmVyZW5jZSIsIm9mZmxpbmVfYWNjZXNzIiwidW1hX2F1dGhvcml6YXRpb24iXX0sInJlc291cmNlX2FjY2VzcyI6eyJ1bnByaXZpbGVnZWQtY2xpZW50Ijp7InJvbGVzIjpbInVtYV9wcm90ZWN0aW9uIl19LCJhY2NvdW50Ijp7InJvbGVzIjpbIm1hbmFnZS1hY2NvdW50IiwibWFuYWdlLWFjY291bnQtbGlua3MiLCJ2aWV3LXByb2ZpbGUiXX19LCJzY29wZSI6ImVtYWlsIHByb2ZpbGUiLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsImNsaWVudElkIjoidW5wcml2aWxlZ2VkLWNsaWVudCIsImNsaWVudEhvc3QiOiIxNzIuMjAuMC4xIiwicHJlZmVycmVkX3VzZXJuYW1lIjoic2VydmljZS1hY2NvdW50LXVucHJpdmlsZWdlZC1jbGllbnQiLCJjbGllbnRBZGRyZXNzIjoiMTcyLjIwLjAuMSJ9.By2VWOWKMrlLdsprif9o68woWHWsCVBLPVPVYe6GGnp_KaSAsPSch4pVNcsmSVILlrx2WEgcWP4IeCeBrumffovvYo4EpAaZ_600Ore1dVtr0vqzl1E1eK7mOhxu73o83PzVqT6c3UIa0wNqld_8Wwo92PrL4iNTbEgyU30knZuhOcbejX4icJXRW1We2nLEHmcbyUR0o9qglXdT8cY4emxqt7uBub8wvsDg4OpkPLmmSRbQVP3TXoxrS8fNION6Li9xoJka7Gv95kJYSLSJxfGwwyN1voVBkAWhap6Imi6BXw5LAhQC3zcnMoIBccl-bsCYQ9Z4gqcG9WscvmgvmA" -H "Content-Type: application/json" -d "{\"longitude\": -122.23, \"latitude\": 37.88, \"housing_median_age\": 41.0, \"total_rooms\": 880.0, \"total_bedrooms\": 129.0, \"population\": 322.0, \"households\": 126.0, \"median_income\": 8.3252}"
