# INDEXATOR

Этот файл описывает структуру проекта и назначение ключевых файлов в репозитории.

## Корневая директория

- `.gitignore` — правила для исключения файлов и директорий из индекса Git.
- `README.md` — главный файл описания репозитория, запуск проекта и общая структура.

## BioCult-KB_Aspergillus_sydowii

Основной каталог проекта: знания по культивированию, данные, модель и веб-прототип.

### Документация и планирование

- `BioCult-KB_Aspergillus_sydowii/00_project_passport/project_topic.md` — тема проекта и предметная область.
- `BioCult-KB_Aspergillus_sydowii/00_project_passport/research_goal_and_tasks.md` — задачи и цели исследования.
- `BioCult-KB_Aspergillus_sydowii/00_project_passport/terminology.md` — терминология и словарь предметной области.
- `BioCult-KB_Aspergillus_sydowii/00_project_passport/unresolved_issues.md` — текущие нерешённые вопросы и риски.
- `BioCult-KB_Aspergillus_sydowii/00_project_passport/source_registry.xlsx` — реестр источников и ссылок.

### Штамм

- `BioCult-KB_Aspergillus_sydowii/01_strain/strain_passport.md` — паспорт штамма Aspergillus sydowii.
- `BioCult-KB_Aspergillus_sydowii/01_strain/strain_reactivation_protocol.md` — протокол реактивации культуры.
- `BioCult-KB_Aspergillus_sydowii/01_strain/strain_morphology.md` — морфология и описание культы.
- `BioCult-KB_Aspergillus_sydowii/01_strain/biosafety.md` — оценка биобезопасности и требования.
- `BioCult-KB_Aspergillus_sydowii/01_strain/genome/ncbi_accession.md` — идентификаторы генома и ссылки на NCBI.
- `BioCult-KB_Aspergillus_sydowii/01_strain/genome/protease_candidates.md` — кандидаты на протеазы и коллагеназы.
- `BioCult-KB_Aspergillus_sydowii/01_strain/genome/secretome_candidates.md` — кандидаты на секретируемые белки.
- `BioCult-KB_Aspergillus_sydowii/01_strain/genome/genome_files_manifest.md` — список файлов генома и данных.

### Среды

- `BioCult-KB_Aspergillus_sydowii/02_media/czapek_agar.md` — рецепт агаровой среды Czapek.
- `BioCult-KB_Aspergillus_sydowii/02_media/czapek_dox_collagen.md` — рецепт среды Czapek-Dox с коллагеном.
- `BioCult-KB_Aspergillus_sydowii/02_media/czapek_dox_liquid.md` — жидкая Czapek-Dox среда.
- `BioCult-KB_Aspergillus_sydowii/02_media/optimized_molasses_peptone.md` — оптимизированный рецепт меласса-пептон.
- `BioCult-KB_Aspergillus_sydowii/02_media/media_component_dictionary.xlsx` — словарь компонентов среды.
- `BioCult-KB_Aspergillus_sydowii/02_media/media_comparison_matrix.xlsx` — матрица сравнения сред.

### Процесс культивирования

- `BioCult-KB_Aspergillus_sydowii/03_cultivation_process/bioreactor_batch_protocol.md` — протокол партийного культивирования.
- `BioCult-KB_Aspergillus_sydowii/03_cultivation_process/inoculum_preparation.md` — подготовка инокулята.
- `BioCult-KB_Aspergillus_sydowii/03_cultivation_process/sampling_plan.md` — план отбора проб.
- `BioCult-KB_Aspergillus_sydowii/03_cultivation_process/shake_flask_protocol.md` — протокол в шейк-фляжах.
- `BioCult-KB_Aspergillus_sydowii/03_cultivation_process/process_parameters_dictionary.xlsx` — справочник параметров процесса.
- `BioCult-KB_Aspergillus_sydowii/03_cultivation_process/batch_run_template.xlsx` — шаблон документации партийного запуска.

### Биореактор

- `BioCult-KB_Aspergillus_sydowii/04_bioreactor/bioreactor_specification.md` — спецификация оборудования.
- `BioCult-KB_Aspergillus_sydowii/04_bioreactor/agitation_and_aeration.md` — перемешивание и аэрация.
- `BioCult-KB_Aspergillus_sydowii/04_bioreactor/sensors_and_control.md` — датчики и системы управления.
- `BioCult-KB_Aspergillus_sydowii/04_bioreactor/calibration_and_readiness.md` — подготовка и калибровка.
- `BioCult-KB_Aspergillus_sydowii/04_bioreactor/geometry_parameters.xlsx` — геометрические параметры аппарата.
- `BioCult-KB_Aspergillus_sydowii/04_bioreactor/3D_models/` — CAD- и 3D-файлы биореактора и крышек.
  - `... .iam`, `.stl`, `.stp` — 3D-модели и сборочные файлы.

### Аналитика

- `BioCult-KB_Aspergillus_sydowii/05_analytics/analytical_controls.md` — контроль качества аналитики.
- `BioCult-KB_Aspergillus_sydowii/05_analytics/biomass_method.md` — метод определения биомассы.
- `BioCult-KB_Aspergillus_sydowii/05_analytics/collagenolytic_activity_method.md` — метод оценки коллагенолитической активности.
- `BioCult-KB_Aspergillus_sydowii/05_analytics/lowry_protein_method.md` — протокол метода Лоуари.
- `BioCult-KB_Aspergillus_sydowii/05_analytics/ninhydrin_method.md` — метод понигидринового анализа.
- `BioCult-KB_Aspergillus_sydowii/05_analytics/pope_stevenson_amino_nitrogen.md` — аминного азота по Попу-Стевонсону.
- `BioCult-KB_Aspergillus_sydowii/05_analytics/sugar_method.md` — метод анализа сахаров.
- `BioCult-KB_Aspergillus_sydowii/05_analytics/calculation_formulas.md` — формулы расчётов.

### Экспериментальные данные

- `BioCult-KB_Aspergillus_sydowii/06_experimental_data/biomass_time_series.xlsx` — набор данных по биомассе.
- `BioCult-KB_Aspergillus_sydowii/06_experimental_data/kla_time_series.xlsx` — данные по KLa.
- `BioCult-KB_Aspergillus_sydowii/06_experimental_data/substrate_time_series.xlsx` — данные по субстратам.
- `BioCult-KB_Aspergillus_sydowii/06_experimental_data/media_optimization_data.xlsx` — данные оптимизации среды.
- `BioCult-KB_Aspergillus_sydowii/06_experimental_data/tidy_dataset_master.xlsx` — основная табличная база данных.
- `BioCult-KB_Aspergillus_sydowii/06_experimental_data/cleaned/README.md` — описание очищенных данных.
- `BioCult-KB_Aspergillus_sydowii/06_experimental_data/raw/README.md` — описание исходных данных.
- `BioCult-KB_Aspergillus_sydowii/06_experimental_data/raw/extracted_tables_raw.json` — исходный JSON с извлечёнными таблицами.
- `BioCult-KB_Aspergillus_sydowii/06_experimental_data/raw/source_texts/*.txt` — исходные текстовые справочные материалы и ссылки.

### Модели

- `BioCult-KB_Aspergillus_sydowii/07_models/growth_model.md` — модель роста.
- `BioCult-KB_Aspergillus_sydowii/07_models/model_assumptions.md` — допущения и границы моделей.
- `BioCult-KB_Aspergillus_sydowii/07_models/morphology_model.md` — модель морфологии.
- `BioCult-KB_Aspergillus_sydowii/07_models/oxygen_transfer_model.md` — модель переноса кислорода.
- `BioCult-KB_Aspergillus_sydowii/07_models/product_formation_model.md` — модель образования продукта.
- `BioCult-KB_Aspergillus_sydowii/07_models/soft_sensor_kla.md` — мягкий датчик KLa.
- `BioCult-KB_Aspergillus_sydowii/07_models/substrate_consumption_model.md` — модель потребления субстратов.
- `BioCult-KB_Aspergillus_sydowii/07_models/*.pdf` — справочные учебные материалы и книги, используемые как источники.

### Экспертная система

- `BioCult-KB_Aspergillus_sydowii/08_expert_system/ontology.md` — онтология и переменные экспертной системы.
- `BioCult-KB_Aspergillus_sydowii/08_expert_system/entity_relationship_schema.md` — ER-схема данных.
- `BioCult-KB_Aspergillus_sydowii/08_expert_system/decision_tree.md` — логика ветвления решений.
- `BioCult-KB_Aspergillus_sydowii/08_expert_system/expert_rules.md` — правила и выводы.
- `BioCult-KB_Aspergillus_sydowii/08_expert_system/recommendation_templates.md` — шаблоны рекомендаций.
- `BioCult-KB_Aspergillus_sydowii/08_expert_system/feedback_loop.md` — механика обратной связи.

### Отчёты и выводы

- `BioCult-KB_Aspergillus_sydowii/09_reports_and_outputs/cultivation_program_v1.md` — черновик программы культивирования.
- `BioCult-KB_Aspergillus_sydowii/09_reports_and_outputs/prototype_requirements.md` — требования к прототипу.
- `BioCult-KB_Aspergillus_sydowii/09_reports_and_outputs/data_quality_report.md` — отчёт о качестве данных.
- `BioCult-KB_Aspergillus_sydowii/09_reports_and_outputs/knowledge_map.md` — карта знаний.
- `BioCult-KB_Aspergillus_sydowii/09_reports_and_outputs/operation_manual.md` — руководство пользователя.
- `BioCult-KB_Aspergillus_sydowii/09_reports_and_outputs/operation_manual.pdf` — PDF версия руководства.

### Веб-frontend

- `BioCult-KB_Aspergillus_sydowii/frontend/index.html` — статический интерфейс приложения.
- `BioCult-KB_Aspergillus_sydowii/frontend/src/main.jsx` — точка входа React/Vite.
- `BioCult-KB_Aspergillus_sydowii/frontend/src/styles.css` — стили интерфейса.
- `BioCult-KB_Aspergillus_sydowii/vite.config.js` — конфигурация сборки фронтенда.
- `BioCult-KB_Aspergillus_sydowii/package.json` — зависимости и сценарии frontend.
- `BioCult-KB_Aspergillus_sydowii/package-lock.json` — зафиксированные версии npm.

### Тесты

- `BioCult-KB_Aspergillus_sydowii/tests/test_gem_cobra_process.py` — тесты GEM/FBA процесса.
- `BioCult-KB_Aspergillus_sydowii/tests/test_system_biology.py` — тесты системы биологии и отчетов.
- `BioCult-KB_Aspergillus_sydowii/tests/test_v2_platform.py` — тесты платформы v2.

## Веб-приложение FastAPI

- `BioCult-KB_Aspergillus_sydowii/web_app/README.md` — документация по веб-приложению.
- `BioCult-KB_Aspergillus_sydowii/web_app/requirements.txt` — Python зависимости для FastAPI.
- `BioCult-KB_Aspergillus_sydowii/web_app/main.py` — точка входа FastAPI, маршруты, статические файлы и начальный загрузочный код.
- `BioCult-KB_Aspergillus_sydowii/web_app/db.py` — конфигурация SQLite базы данных и инициализация схемы.
- `BioCult-KB_Aspergillus_sydowii/web_app/models.py` — SQLAlchemy ORM схемы, справочники, наблюдения и аудит.
- `BioCult-KB_Aspergillus_sydowii/web_app/schemas.py` — Pydantic схемы API и входные/выходные модели.
- `BioCult-KB_Aspergillus_sydowii/web_app/gem_cobra.py` — построение GEM-lite модели, SBML экспорт и расчет FBA по среде.
- `BioCult-KB_Aspergillus_sydowii/web_app/process_simulation.py` — динамическая моделизация batch/fed-batch/continuous процессов и каскадные расчеты.
- `BioCult-KB_Aspergillus_sydowii/web_app/system_biology.py` — анализ геномных данных, аннотаций и биологические доказательства.
- `BioCult-KB_Aspergillus_sydowii/web_app/recommendations.py` — генерация рекомендаций на основе текущих наблюдений и состава среды.
- `BioCult-KB_Aspergillus_sydowii/web_app/calculations.py` — вспомогательные расчёты, метрики и служебные функции.
- `BioCult-KB_Aspergillus_sydowii/web_app/cell_process.py` — обработка клеточного состояния и взаимодействие с процессами.
- `BioCult-KB_Aspergillus_sydowii/web_app/data_import.py` — импорт данных и загрузка справочников среды.
- `BioCult-KB_Aspergillus_sydowii/web_app/omics_pipeline.py` — ETL-скелет для OMICS-источников, загрузки и манифестов.
- `BioCult-KB_Aspergillus_sydowii/web_app/omics_registry.py` — реестр и валидация OMICS-ресурсов.
- `BioCult-KB_Aspergillus_sydowii/web_app/omics_validation.py` — проверки структуры OMICS-манифестов и данных.
- `BioCult-KB_Aspergillus_sydowii/web_app/static/index.html` — базовый UI загрузки приложения.
- `BioCult-KB_Aspergillus_sydowii/web_app/static/app.js` — фронтенд логика и взаимодействие с API.
- `BioCult-KB_Aspergillus_sydowii/web_app/static/bioreactor_scene.js` — визуализация биореактора и показателей процесса.
- `BioCult-KB_Aspergillus_sydowii/web_app/static/styles.css` — стили приложения.
- `BioCult-KB_Aspergillus_sydowii/web_app/static/v2/index.html` — вторая версия фронтенда и сцены.
- `BioCult-KB_Aspergillus_sydowii/web_app/static/v2/assets/index-BnQrMxM5.css` — собранный CSS для версии v2.
- `BioCult-KB_Aspergillus_sydowii/web_app/static/v2/assets/index-CBMtwvHN.js` — собранный JavaScript для версии v2.
- `BioCult-KB_Aspergillus_sydowii/web_app/data/models/aspergillus_sydowii_gem_lite_v1.xml` — SBML модель GEM-lite.
- `BioCult-KB_Aspergillus_sydowii/web_app/data/omics/aspergillus_sydowii/reports/manifest.json` — текущий манифест OMICS ресурсов.
- `BioCult-KB_Aspergillus_sydowii/web_app/data/omics/aspergillus_sydowii/reports/assets_index.json` — индекс ресурсов.
- `BioCult-KB_Aspergillus_sydowii/web_app/data/omics/aspergillus_sydowii/reports/biosynthesis_potential_report.json` — отчет потенциала биосинтеза.
- `BioCult-KB_Aspergillus_sydowii/web_app/data/omics/aspergillus_sydowii/reports/PRJNA542911_sample_sheet.tsv` — готовый табличный образец для загрузки RNA-seq.
- `BioCult-KB_Aspergillus_sydowii/web_app/data/omics/aspergillus_sydowii/reports/PRJNA542911_runinfo.csv` — метаданные SRA по биопроекту.
- `BioCult-KB_Aspergillus_sydowii/web_app/data/omics/aspergillus_sydowii/reports/PRJNA542911_summary.json` — сводный отчет Bioproject.
- `BioCult-KB_Aspergillus_sydowii/web_app/data/omics/aspergillus_sydowii/reports/PRJNA542911_download_reads.sh` — скрипт для загрузки чтений.
- `BioCult-KB_Aspergillus_sydowii/web_app/data/omics/aspergillus_sydowii/transcriptome/test_tpm.csv` — тестовый TPM-файл транскриптома.

## Как использовать этот документ

- `README.md` объясняет общую цель проекта и запуск.
- `BioCult-KB_Aspergillus_sydowii/web_app/README.md` описывает веб-приложение и его запуск.
- `INDEXATOR.md` содержит файл-ориентированное описание функционала и структуру репозитория.
