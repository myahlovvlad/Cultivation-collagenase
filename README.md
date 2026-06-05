# Cultivation-collagenase

**BioCult-KB** — это репозиторий знаний и веб-прототип для моделирования культивирования *Aspergillus sydowii* как производителя коллагенолитической активности.

Проект объединяет:
- предметную базу данных по штамму, средам, биореактору, аналитике и экспериментам;
- FastAPI веб-приложение с интерфейсом и API для мониторинга, рекомендаций и расчетов;
- GEM-lite COBRA/SBML модель для оценки биомассы, метаболизма и продукции;
- процессную симуляцию batch/fed-batch/continuous;
- OMICS-пайплайн для сборки и проверки геномных, транскриптомных и аналитических ресурсов.

## Что есть в репозитории

- `BioCult-KB_Aspergillus_sydowii/` — основная база знаний, документы, модели, данные и веб-прототип.
- `BioCult-KB_Aspergillus_sydowii/web_app/` — FastAPI backend, SQLite ORM, API, ETL и frontend-анимация.
- `BioCult-KB_Aspergillus_sydowii/frontend/` — Vite/React интерфейс и ресурсы.
- `BioCult-KB_Aspergillus_sydowii/tests/` — набор автоматических тестов для процесса и биологической оценки.

## Быстрый старт

Выполните команды из корня репозитория:

```powershell
cd "BioCult-KB_Aspergillus_sydowii"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r web_app\requirements.txt
$env:PYTHONPATH = (Resolve-Path .).Path
python -m uvicorn web_app.main:app --host 127.0.0.1 --port 8000
```

Откройте в браузере:

```text
http://127.0.0.1:8000/
```

## Ключевые места

- `README.md` — этот файл.
- `INDEXATOR.md` — подробный файл-индекс с описанием функционала файлов.
- `BioCult-KB_Aspergillus_sydowii/web_app/README.md` — инструкция по веб-приложению.
- `BioCult-KB_Aspergillus_sydowii/09_reports_and_outputs/operation_manual.md` — руководство пользователя.

## Запуск тестов

```powershell
cd "BioCult-KB_Aspergillus_sydowii"
$env:PYTHONPATH = (Resolve-Path .).Path
python -m pytest tests -q
```

## Структура репозитория

- `00_project_passport/` — цели, задачи, терминология и проблемные зоны.
- `01_strain/` — паспорт штамма, геномные данные, безопасность.
- `02_media/` — рецепты сред и словари компонентов.
- `03_cultivation_process/` — протоколы культивирования и планы отбора проб.
- `04_bioreactor/` — спецификации биореактора, датчики и 3D-модели.
- `05_analytics/` — методы аналитики и формулы расчетов.
- `06_experimental_data/` — экспериментальные наборы данных и исходные материалы.
- `07_models/` — моделирование роста, кислородного переноса, потребления и продукции.
- `08_expert_system/` — правила, онтология и рекомендации.
- `09_reports_and_outputs/` — отчёты, планы и операционные документы.
- `frontend/` — статический интерфейс и стили.
- `web_app/` — FastAPI backend и вспомогательные модули.

## Примечание

В репозитории хранятся только подготовленные структуры и документы. Крупные данные NCBI, сырые OMICS-пакеты и временные локальные файлы не включаются автоматически.

