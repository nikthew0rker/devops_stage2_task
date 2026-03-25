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
```

------------------------------------------------------------------------

------------------------------------------------------------------------

# Как развивал бы дальше для production / HA

1. Перенёс бы deployment с Docker Compose на Kubernetes + Helm, чтобы получить декларативный rollout, управление конфигурацией по окружениям и более удобную эксплуатацию.

2. Использовал бы managed PostgreSQL или PostgreSQL HA-решение с автоматическим failover, backup policy и регулярной проверкой восстановления.

3. Вынес бы backup в object storage с retention policy, версионированием и регулярными restore-тестами в отдельном контуре.

4. Перевёл бы секреты во внешний secret manager и убрал бы чувствительные значения из `.env` и runtime-конфигурации контейнеров.

5. Добавил бы ingress + TLS, базовую сетевую сегментацию и контроль внешнего доступа.

6. Добавил бы alerting через Prometheus rules + Alertmanager с разделением на warning / critical и маршрутизацией уведомлений.

7. Добавил бы централизованные логи и tracing для диагностики ошибок, деградации производительности и анализа запросов.

8. Ввёл бы resource requests/limits, probes и дополнительные меры hardening:
   - запуск от non-root пользователя
   - read-only filesystem
   - минимальные capabilities
   - pinning образов по digest

9. Вынес бы миграции БД в отдельный lifecycle step (job / init container / migration service), чтобы не связывать изменение схемы со стартом приложения.

10. Усилил бы CI/CD:
    - image scanning
    - dependency scanning
    - secret scanning
    - policy checks (OPA / Kyverno)
    - lint Helm chart'ов

11. Для observability в Kubernetes использовал бы operator-based подход:
    - **Prometheus Operator** — управление Prometheus, Alertmanager, ServiceMonitor, PodMonitor, PrometheusRule через CRD;
    - **Grafana Operator** — управление Grafana instances, dashboards и datasources декларативно;
    - отказ от ручной настройки через UI в пользу GitOps-подхода.

12. Добавил бы полноценный CI/CD pipeline с деплоем в Kubernetes через Helm и выбором окружения (`dev` / `stage` / `prod`):
    - сборка и push образа
    - тестирование
    - выбор values-файла
    - `helm upgrade --install`
    - post-deploy проверки
    - rollback при неуспехе

---

### Ключевые метрики для production

### Метрики приложения
- `app_requests_total` — общее количество запросов
- RPS (`rate(app_requests_total)`)
- latency (p50 / p95 / p99)
- error rate (доля 5xx)
- success rate по endpoint'ам
- количество активных запросов (in-flight)
- количество рестартов приложения

### Метрики PostgreSQL
- активные соединения
- latency запросов
- slow queries
- deadlocks
- replication lag (если есть реплики)
- размер БД и рост таблиц
- WAL / checkpoint активность
- статус и возраст последнего backup

### Метрики Kubernetes / инфраструктуры
- CPU / memory usage по pod / node
- restart count контейнеров
- OOMKilled события
- pod readiness / availability
- node pressure (memory / disk)
- disk usage и IOPS
- network errors / packet loss

### Метрики observability и delivery
- scrape success / target health в Prometheus
- alert delivery success rate
- deployment frequency
- lead time for changes
- failed deployment rate
- mean time to recovery (MTTR)

---

### Как выглядел бы CI/CD pipeline

Pipeline разбивается на стадии:

### 1. Validate / Lint
- docker compose config
- helm lint
- yaml lint
- проверка структуры проекта

### 2. Build
- сборка Docker image
- tagging (commit SHA / release)
- push в registry

### 3. Test
- smoke tests
- проверка `/health`
- проверка `/metrics`
- e2e через docker compose
- тест backup script

### 4. Security
- image scanning
- dependency scanning
- secret scanning

### 5. Deploy
- выбор окружения: `dev` / `stage` / `prod`
- выбор values-файла Helm
- `helm upgrade --install`
- ожидание rollout (`kubectl rollout status`)
- post-deploy smoke tests
- rollback при ошибке

---

### Стратегия деплоя по окружениям

- `dev` — автоматический деплой при push
- `stage` — деплой после merge / manual approval
- `prod` — только manual approval или release tag

Пример структуры:

```text
helm/app/
  values-dev.yaml
  values-stage.yaml
  values-prod.yaml
```



------------------------------------------------------------------------