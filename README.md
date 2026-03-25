# Тестовое задание --- этап 2

Репозиторий содержит воспроизводимый Docker Compose-стек со следующими
компонентами:

-   тестовое приложение на FastAPI
-   PostgreSQL
-   Prometheus
-   Grafana
-   базовый backup/restore для PostgreSQL
-   CI pipeline на GitHub Actions

## Что реализовано

-   приложение запускается через Docker Compose
-   приложение подключается к PostgreSQL и пишет данные в БД
-   Prometheus собирает метрики с `/metrics`
-   Grafana автоматически поднимает datasource и dashboard из
    репозитория
-   backup/restore для PostgreSQL реализованы через shell-скрипты
-   CI выполняет базовую e2e-проверку стека

------------------------------------------------------------------------

## Структура проекта

``` text
.
├── .env.example
├── docker-compose.yml
├── README.md
├── app/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
├── prometheus/
│   └── prometheus.yml
├── grafana/
│   ├── dashboards/
│   │   └── app-overview.json
│   └── provisioning/
│       ├── dashboards/
│       │   └── dashboard.yml
│       └── datasources/
│           └── datasource.yml
├── scripts/
│   ├── backup.sh
│   └── restore.sh
└── .github/
    └── workflows/
        └── ci.yml
```

------------------------------------------------------------------------

## Требования

Для запуска нужны:

-   Docker
-   Docker Compose plugin

Проверить можно так:

``` bash
docker --version
docker compose version
```

------------------------------------------------------------------------

## Настройка

Создать локальный `.env` из примера:

``` bash
cp .env.example .env
```

Содержимое по умолчанию:

``` env
POSTGRES_PASSWORD=change_me
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=admin
```

------------------------------------------------------------------------

## Как запустить

Собрать и поднять стек:

``` bash
docker compose up -d --build
```

Проверить состояние контейнеров:

``` bash
docker compose ps
```

------------------------------------------------------------------------

## Как проверить

### 1. Проверка приложения

Проверка health endpoint:

``` bash
curl http://localhost:8000/health
```

Ожидаемый ответ:

``` json
{"status":"healthy"}
```

Сгенерировать несколько запросов:

``` bash
curl http://localhost:8000/
curl http://localhost:8000/
curl http://localhost:8000/
```

Проверить метрики:

``` bash
curl http://localhost:8000/metrics
```

------------------------------------------------------------------------

### 2. Проверка Prometheus

Открыть:

``` text
http://localhost:9090
```

Пример запроса в Prometheus UI:

``` promql
app_requests_total
```

------------------------------------------------------------------------

### 3. Проверка Grafana

Открыть:

``` text
http://localhost:3000
```

Данные для входа по умолчанию:

-   логин: `admin`
-   пароль: `admin`

### Автоматический подъём datasource и dashboard

Datasource и dashboard поднимаются автоматически из файлов репозитория:

-   datasource: `grafana/provisioning/datasources/datasource.yml`
-   dashboard provider: `grafana/provisioning/dashboards/dashboard.yml`
-   dashboard JSON: `grafana/dashboards/app-overview.json`

После старта `docker compose up -d --build` ручная настройка Grafana не
требуется.

------------------------------------------------------------------------

## Backup

Сделать исполняемыми скрипты:

``` bash
chmod +x scripts/backup.sh scripts/restore.sh
```

Создать backup:

``` bash
./scripts/backup.sh
```

Результат появится в каталоге `backups/`:

``` text
backups/appdb_YYYYMMDD_HHMMSS.sql
```

------------------------------------------------------------------------

## Restore

Восстановить БД из backup-файла:

``` bash
./scripts/restore.sh backups/appdb_YYYYMMDD_HHMMSS.sql
```

------------------------------------------------------------------------

## Что проверяет CI

Pipeline GitHub Actions выполняет:

-   валидацию `docker-compose.yml`
-   сборку образов
-   запуск стека
-   проверку `/health`
-   проверку `/metrics`
-   проверку доступности Prometheus API
-   smoke-test backup script
-   cleanup окружения

------------------------------------------------------------------------

## Инженерная логика решения

В решении использованы следующие базовые практики:

-   зафиксированы версии образов для воспроизводимости
-   у PostgreSQL и приложения добавлены healthcheck'и
-   приложение ждёт доступность БД на старте через retry-механику
-   Prometheus собирает метрики только с реального `/metrics` endpoint
-   Grafana поднимает datasource и dashboard автоматически из
    git-репозитория
-   backup/restore реализованы простым и прозрачным способом через
    `pg_dump` и `psql`

------------------------------------------------------------------------

## Ограничения решения

Это локальный reproducible baseline, а не production / HA решение.

Текущие ограничения:

-   single-node deployment через Docker Compose
-   нет high availability
-   нет автоматического failover
-   секреты хранятся в `.env`, а не во внешнем secret manager
-   backup локальный, в виде SQL dump
-   нет retention policy
-   нет offsite/object storage backup
-   нет автоматической проверки restore
-   нет TLS / ingress / внешней аутентификации
-   нет alerting rules и Alertmanager
-   нет централизованных логов и трассировки
-   нет resource limits / reservations
-   схема БД инициализируется приложением на старте

------------------------------------------------------------------------

## Как развивал бы дальше для production / HA

1.  Перенёс бы deployment с Docker Compose на Kubernetes + Helm.
2.  Использовал бы managed PostgreSQL или PostgreSQL HA-решение.
3.  Вынес бы backup в object storage с retention policy и регулярными
    restore-тестами.
4.  Перевёл бы секреты во внешний secret manager.
5.  Добавил бы ingress + TLS.
6.  Добавил бы alerting через Prometheus rules + Alertmanager.
7.  Добавил бы централизованные логи и tracing.
8.  Ввёл бы resource requests/limits и дополнительные меры hardening.
9.  Вынес бы миграции БД в отдельный lifecycle step.
10. Усилил бы CI проверками безопасности и сканированием образов.

------------------------------------------------------------------------

## Остановка

Остановить стек:

``` bash
docker compose down
```

Остановить стек и удалить volumes:

``` bash
docker compose down -v
```


## Частые проблемы

### PostgreSQL не стартует с ошибкой 
`POSTGRES_PASSWORD is not specified`

Проверьте, что в корне проекта создан `.env` файл и в нём задан непустой `POSTGRES_PASSWORD`.

Пример:

```env
POSTGRES_PASSWORD=change_me
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=admin