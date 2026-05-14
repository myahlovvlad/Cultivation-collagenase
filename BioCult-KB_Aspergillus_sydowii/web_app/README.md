# BioCult-KB Web Prototype

Веб-прототип для базы знаний `BioCult-KB_Aspergillus_sydowii`.

## Что реализовано

- FastAPI backend с моделями данных на основе ER-схемы.
- SQLite база данных для справочников и наблюдений.
- API для расчетов, рекомендаций и конфигурации 3D-сцены биореактора.
- Импорт компонентов среды из Excel (`02_media/media_component_dictionary.xlsx`).
- Одностраничный UI для просмотра справочников, запуска расчетов и получения рекомендаций.
- Интерактивный Three.js-рендер лабораторного биореактора и процесса batch-культивирования `Aspergillus sydowii`.
- Стенд датчиков, временные графики и аналитическая панель экспертной системы для оценки состояния процесса.
- Omics ETL-раздел: registry источников, manifest preview, команды NCBI Datasets/EDirect/SRA Toolkit и генерация scaffold-артефактов.

## Запуск

Выполняйте команды из корня проекта:

```bash
python -m venv web_app/.venv
web_app/.venv/Scripts/activate
pip install -r web_app/requirements.txt
python -m uvicorn web_app.main:app --reload --host 127.0.0.1 --port 8000
```

Откройте `http://127.0.0.1:8000`.

## Расширение

- Добавить импорт шаблонов запуска в формате Excel/CSV.
- Связать данные наблюдений из `06_experimental_data` с 3D-профилем процесса.
- Построить отчетную страницу на основе расчетов.
- Интегрировать правила экспертной системы из `08_expert_system`.
- Реализовать следующий слой: gene -> protein -> enzyme mapping, pathway mapping и draft genome-scale metabolic model.
