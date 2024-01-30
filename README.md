# Currency pairs

## How to run locally

1. Clone repository `git clone git@github.com:NikolayChernikov/CurrencyPairs.git`
2. Goto folder `cd CurrencyPairs`
3. Build image `DOCKER_BUILDKIT=1 docker build --ssh default . -t currency-pairs/app:latest -f deployment/Dockerfile`
4. Run service `docker-compose up -d`

## Linters

1. Flake8 `flake8 bwg`
2. Isort `isort bwg`
3. PyLint `pylint bwg`
4. MyPy `mypy bwg`

## Locust test
![img.png](tests/locust_result.png)

## Tasks
**Реализовать сервис, через который можно получать курсы валютных пар с биржи**

Необходимо, чтобы сервис возвращал курсы по следующим валютным парам:
- [x] BTC-to-[RUB|USD]
- [x] ETH-to-[RUB|USD]
- [ ] USDTTRC-to-[RUB|USD]
- [ ] USDTERC-to-[RUB|USD]

**Требования:**
- [x] FastAPI в качестве фреймворка и ассинхронная имплементация сервиса
- [ ] Использование очередей (RMQ, ZeroMQ, etc)
- [x] Сервис может обработать до 1500 запросов в ед. времени
- [x] Обновление курсов происходит не дольше чем раз в 5 секунд
- [ ] Сервис работает отказаустойчиво (если одна из бирж перестаёт возвращать курсы, то сервис продолжает работать по другой)
- [x] Уровни логирования должны быть разделены на CRITICAL, ERROR, WARNING, INFO, DEBUG 
- [x] Курсы необходимо получать c Binance, либо c coingeko. Разработанный API сервис при GET запросе на /courses c опциональными query параметрами, должен возвращать ответ формата 
```
  {
    "exchanger": "binance", 
    "courses": [
      {
        "direction": "BTC-USD",
        "value": 54000.000123
      }
    ]
  }
```
- [ ] Работа с биржей происходит по websocket’ам, если биржа это поддерживает
- [x] Нагрузочное тестирование реализовать через locust. Скрины прикрепить в readme
- [x] Необходимо реализовать версионирование API

**Сдача проекта:**
- [x] Опубликовать проект необходимо в github
- [x] Проект должен быть собран в docker контейнеры и в docker-compose файл. Для запуска проекта должно быть достаточно набрать команду `docker compose up --build`
- [x] README заполнить информацией по запуску, заполнению секретов и прикрепить отчет о тестировании

**Будет плюсом:**
- [ ] Использование reverse proxy в качестве балансировщика запросов
- [x] Использование postgres с автоматическим накатываением миграций
- [ ] Использование одного из популярных инструментов для кэширования
- [x] FastAPI в качестве фреймворка и ассинхронная имплементация сервиса
- [x] Использование метрик (grafana, kuma, etc)