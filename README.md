## Лабораторная работа № 1 "Изучение синхронного инференса с применением веб-сервиса"

## Цель работы

- Изучение процесса инференса в системах машинного обучения.
- Ознакомление с протоколом HTTP и микросервисной архитектурой.
- Реализация веб-сервиса для синхронного инференса модели машинного обучения.
- Получение навыков сохранения моделей и работы с Pipeline.
- Настройка CI/CD для автоматического тестирования сервиса.

---

## Используемый датасет

**California Housing** (CSV, доступен по ссылке: [housing.csv](https://www.kaggle.com/datasets/camnugent/california-housing-prices)).

Признаки:
- `longitude` — географическая долгота района  
- `latitude` — географическая широта района  
- `housing_median_age` — медианный возраст домов  
- `total_rooms` — общее количество комнат  
- `total_bedrooms` — общее количество спален  
- `population` — население района  
- `households` — количество домохозяйств  
- `median_income` — медианный доход  
- `median_house_value` — целевой признак (стоимость домов)

---

## Модель

Использована модель **RandomForestRegressor** с предварительной обработкой всех числовых признаков через Pipeline:

- Пропуски в `total_bedrooms` заполняются медианой (`SimpleImputer`)  
- Все признаки стандартизируются (`StandardScaler`)  
- Лучшие гиперпараметры подбирались через `GridSearchCV`  

Результаты оценки модели:

| Показатель | Значение |
|------------|----------|
| R² на train | 0.96 |
| R² на test | 0.81 |

---

## Веб-сервис

- Реализован с помощью **FastAPI**  
- Endpoint: `/predictions`  
- Требует авторизации через Bearer Token (`00000`)  



## Примеры запросов curl

### Проверка состояния сервиса
```bash
curl http://localhost:8000/healthcheck
```

### Корректный запрос с токеном
```bash
curl -X POST http://localhost:8000/predictions -H "Authorization: Bearer 00000" -H "Content-Type: application/json" -d '{"longitude": -122.23, "latitude": 37.88,"housing_median_age": 41.0, "total_rooms": 880.0, "total_bedrooms": 129.0, "population": 322.0, "households": 126.0, "median_income": 8.3252}'
```

### Запрос без токена
```bash
curl -X POST http://localhost:8000/predictions -H "Content-Type: application/json" -d '{ "longitude": -122.23, "latitude": 37.88, "housing_median_age": 41.0, "total_rooms": 880.0, "total_bedrooms": 129.0, "population": 322.0, "households": 126.0, "median_income": 8.3252}'
```

### Запрос с неверным токеном
```bash
curl -X POST http://localhost:8000/predictions -H "Authorization: Bearer 00002" -H "Content-Type: application/json" -d '{ "longitude": -122.23, "latitude": 37.88, "housing_median_age": 41.0, "total_rooms": 880.0, "total_bedrooms": 129.0, "population": 322.0, "households": 126.0, "median_income": 8.3252}'
```


##  Запуск проекта

```bash
git clone https://github.com/ghotom/cloudcs-lab1
cd CloudCS-Lab1

conda create -n cloudsc-env python=3.10
conda activate cloudsc-env

pip install -r requirements.txt


set PYTHONPATH=./;./src


cd src
set MODEL_PATH=../models/pipeline.pkl
uvicorn main:app --reload


curl http://localhost:8000/healthcheck


set PYTHONPATH=./;./src
pytest test
```