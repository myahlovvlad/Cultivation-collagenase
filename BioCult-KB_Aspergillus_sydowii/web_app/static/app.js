const strainList = document.getElementById('strain-list');
const mediaList = document.getElementById('media-list');
const calculationResult = document.getElementById('calculation-result');
const recommendationResult = document.getElementById('recommendation-result');
const importResult = document.getElementById('import-result');
const optimizerForm = document.getElementById('media-optimizer-form');
const cellProgramList = document.getElementById('cell-program-list');
const processProjectionGrid = document.getElementById('process-projection-grid');
const cultivationOptimizerResult = document.getElementById('cultivation-optimizer-result');
const optimizationRecommendations = document.getElementById('media-optimization-recommendations');
const genomeProcessLinks = document.getElementById('genome-process-links');
const biosynthesisPotentialList = document.getElementById('biosynthesis-potential-list');
const systemBiologySummary = document.getElementById('system-biology-summary');
const systemBiologyCondition = document.getElementById('system-biology-condition');
const systemBiologyPrograms = document.getElementById('system-biology-programs');
const systemBiologyWarnings = document.getElementById('system-biology-warnings');
const systemBiologyInterpretation = document.getElementById('system-biology-interpretation');
const processModeSelect = document.getElementById('process-mode-select');
const gemSummaryGrid = document.getElementById('gem-summary-grid');
const gemFbaGrid = document.getElementById('gem-fba-grid');
const processSimulationGrid = document.getElementById('process-simulation-grid');
const processEquationsList = document.getElementById('process-equations-list');
const omicsForm = document.getElementById('omics-form');
const omicsScaffoldButton = document.getElementById('omics-scaffold-button');
const omicsDiscoverButton = document.getElementById('omics-discover-button');
const omicsDownloadGenomesButton = document.getElementById('omics-download-genomes-button');
const omicsBiosynthesisButton = document.getElementById('omics-biosynthesis-button');
const omicsValidation = document.getElementById('omics-validation');
const omicsCommands = document.getElementById('omics-commands');
const omicsRegistrySummary = document.getElementById('omics-registry-summary');
const omicsToolStatus = document.getElementById('omics-tool-status');
const omicsArtifacts = document.getElementById('omics-artifacts');
let gemProcessUpdateTimer = null;

function escapeHtml(value) {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

function displayPath(value) {
  const raw = String(value ?? '');
  if (!raw) {
    return 'не задано';
  }
  const normalized = raw.replaceAll('\\', '/');
  const anchors = [
    'BioCult-KB_Aspergillus_sydowii/',
    'web_app/',
    'data/omics/',
    'data/models/',
  ];
  for (const anchor of anchors) {
    const index = normalized.indexOf(anchor);
    if (index >= 0) {
      return normalized.slice(index);
    }
  }
  return normalized.split('/').pop() || normalized;
}

function uniqueStrings(items) {
  const seen = new Set();
  return (items || []).filter((item) => {
    const key = String(item);
    if (seen.has(key)) {
      return false;
    }
    seen.add(key);
    return true;
  });
}

function translateConfidence(value) {
  const labels = {high: 'высокая', medium: 'средняя', low: 'низкая'};
  return labels[String(value || '').toLowerCase()] || value || 'не задана';
}

function translateStatus(value) {
  const labels = {
    optimal: 'оптимально',
    available: 'доступно',
    degraded: 'ограниченный режим',
    unknown: 'неизвестно',
    active: 'активно',
    balanced: 'сбалансировано',
    limiting: 'лимитирует',
    watch: 'контроль',
    reference: 'референсная',
    not_run: 'не запускалось',
    ready: 'готово',
  };
  return labels[String(value || '').toLowerCase()] || value || 'неизвестно';
}

function translateMode(value) {
  const labels = {
    batch: 'периодический',
    fed_batch: 'отъёмно-доливной',
    continuous: 'непрерывный',
  };
  return labels[String(value || '').toLowerCase()] || value || 'не задан';
}

function translateObjective(value) {
  const labels = {
    biomass: 'биомасса',
    collagenolytic_product: 'коллагенолитический продукт',
    balanced: 'сбалансированная цель',
  };
  return labels[String(value || '').toLowerCase()] || value || 'сбалансированная цель';
}

function translateProgramName(value) {
  const labels = {
    'Carbon and redox capacity': 'Углеродный и redox-потенциал',
    'Secreted protease potential': 'Потенциал секретируемых протеаз',
    'Oxygen and transport readiness': 'Готовность кислорода и транспорта',
    'Cell cycle evidence layer': 'Аннотационный слой клеточного цикла',
    'Secondary metabolism pressure': 'Давление вторичного метаболизма',
    'Proteases and peptidases': 'Протеазы и пептидазы',
    'Secretory and extracellular apparatus': 'Секреторный и внеклеточный аппарат',
    'Transporters and permeases': 'Транспортеры и пермеазы',
    'Central carbon, redox, and respiration': 'Центральный углеродный обмен, redox и дыхание',
    'Secondary metabolism': 'Вторичный метаболизм',
    'Cell cycle and division markers': 'Маркеры клеточного цикла и деления',
  };
  return labels[value] || value || '-';
}

function translateText(value) {
  const labels = {
    'Carbon/redox annotation is weighted by molasses availability, oxygen transfer, and transporter evidence.': 'Аннотация углеродного/redox-обмена взвешена доступностью мелассы, переносом кислорода и доказательствами транспортеров.',
    'Protease/peptidase evidence is activated by nitrogen supply, collagen substrate, secretion evidence, and pH fit.': 'Доказательства протеаз/пептидаз усиливаются снабжением азотом, коллагеновым субстратом, признаками секреции и соответствием pH.',
    'Aeration/rpm and transporter evidence define the process reserve for aerobic metabolism.': 'Аэрация, перемешивание и доказательства транспортеров задают процессный резерв аэробного метаболизма.',
    'Cell-cycle markers support growth potential, but v1 does not simulate G1/S/G2/M dynamics.': 'Маркеры клеточного цикла поддерживают потенциал роста, но v1 не симулирует динамику G1/S/G2/M.',
    'BGC-adjacent evidence becomes more relevant under stress, high load, and oxygen pressure.': 'BGC-связанные признаки становятся значимее при стрессе, высокой нагрузке и кислородном давлении.',
    'COBRA/SBML execution failed; process simulation must report degraded mode.': 'Расчёт COBRA/SBML не выполнен; симуляция процесса должна перейти в ограниченный режим.',
    'Process simulation uses COBRA/FBA as a capacity layer and empirical kinetics for time dynamics.': 'Симуляция процесса использует COBRA/FBA как слой предельной мощности и эмпирическую кинетику для динамики во времени.',
    'Medium composition is tracked as proxy components, not chemically complete molasses/peptone speciation.': 'Состав среды отслеживается прокси-компонентами, а не полной химической спецификацией мелассы и пептона.',
    'COBRA/SBML degraded mode was detected in at least one simulation step.': 'Ограниченный режим COBRA/SBML обнаружен минимум на одном шаге симуляции.',
  };
  return labels[value] || value;
}

async function fetchJson(path, options = {}) {
  const response = await fetch(path, options);
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${path}`);
  }
  return response.json();
}

async function loadShortcuts() {
  try {
    const [strains, media] = await Promise.all([
      fetchJson('/api/strains'),
      fetchJson('/api/media'),
    ]);
    strainList.innerHTML = strains
      .map((strain) => `<li>${escapeHtml(strain.species)} (${escapeHtml(strain.collection_number || '—')})</li>`)
      .join('');
    mediaList.innerHTML = media
      .map((item) => `<li>${escapeHtml(item.name)} / ${escapeHtml(translateStatus(item.status || '—'))}</li>`)
      .join('');
  } catch (error) {
    strainList.innerHTML = '<li>Не удалось загрузить справочник штаммов.</li>';
    mediaList.innerHTML = '<li>Не удалось загрузить справочник сред.</li>';
  }
}

async function calculateMetrics(event) {
  event.preventDefault();
  const form = event.target;
  const result = await fetchJson('/api/calculate', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      observations: [{
        time_h: Number(form.time_h.value),
        pO2_percent: Number(form.pO2_percent.value) || null,
        biomass: Number(form.biomass.value) || null,
        kla: Number(form.kla.value) || null,
        protein: Number(form.protein.value) || null,
        sugars: Number(form.sugars.value) || null,
      }],
    }),
  });
  calculationResult.innerHTML = `<pre>${escapeHtml(JSON.stringify(result, null, 2))}</pre>`;
}

async function requestRecommendations(event) {
  event.preventDefault();
  const form = event.target;
  const result = await fetchJson('/api/recommend', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      controls_present: form.controls_present.checked,
      collection_time_h: Number(form.collection_time_h.value) || null,
      last_pO2_percent: Number(form.last_pO2_percent.value) || null,
    }),
  });
  recommendationResult.innerHTML = result.recommendations
    .map((item) => `<p>${escapeHtml(item)}</p>`)
    .join('');
}

async function importExcel() {
  importResult.textContent = 'Импорт данных...';
  const result = await fetchJson('/api/import-excel', {method: 'POST'});
  importResult.innerHTML = `<pre>${escapeHtml(JSON.stringify(result, null, 2))}</pre>`;
  loadShortcuts();
}

function readOptimizerInput() {
  const formData = new FormData(optimizerForm);
  return {
    molasses_g_l: Number(formData.get('molasses_g_l')),
    peptone_g_l: Number(formData.get('peptone_g_l')),
    collagen_g_l: Number(formData.get('collagen_g_l')),
    mineral_factor: Number(formData.get('mineral_factor')),
    pH: Number(formData.get('pH')),
    aeration_vvm: Number(formData.get('aeration_vvm')),
    rpm: Number(formData.get('rpm')),
  };
}

function updateOptimizerLabels() {
  if (!optimizerForm) {
    return;
  }
  optimizerForm.querySelectorAll('input[type="range"]').forEach((input) => {
    const output = optimizerForm.querySelector(`[data-value-for="${input.name}"]`);
    if (output) {
      output.textContent = input.value;
    }
  });
}

function renderDefinitionGrid(container, items) {
  if (!container) {
    return;
  }
  container.innerHTML = items.map(([label, value, meta]) => `
    <div>
      <dt>${escapeHtml(label)}</dt>
      <dd>${escapeHtml(value)}</dd>
      ${meta ? `<span>${escapeHtml(meta)}</span>` : ''}
    </div>
  `).join('');
}

function renderOptimization(result) {
  cellProgramList.innerHTML = result.cell_programs.map((program) => `
    <article class="program-card" data-status="${escapeHtml(program.status)}">
      <div class="sensor-topline">
        <span>${escapeHtml(program.name)}</span>
        <strong>${program.score}%</strong>
      </div>
      <div class="sensor-track"><span style="width: ${program.score}%"></span></div>
      <p>${escapeHtml(program.rationale)}</p>
    </article>
  `).join('');

  const projection = result.projection;
  renderDefinitionGrid(processProjectionGrid, [
    ['Биомасса', `${projection.predicted_biomass_g_l} г/л`, `${projection.biomass_index}%`],
    ['Коллагеназа', `${projection.predicted_collagenase_u_ml} U/ml`, `${projection.collagenase_activity_index}%`],
    ['Потребность O₂', `${projection.oxygen_demand_index}%`, `${projection.predicted_pO2_percent}% pO₂`],
    ['pCO₂', `${projection.predicted_pCO2_percent}%`, 'газообмен'],
    ['Вязкость', `${projection.predicted_viscosity_mpa_s} мПа·с`, `${projection.viscosity_risk_index}% риск`],
    ['Сбор', `${projection.recommended_harvest_time_h} ч`, 'окно процесса'],
  ]);

  optimizationRecommendations.innerHTML = result.recommendations
    .map((item) => `<li>${escapeHtml(item)}</li>`)
    .join('');

  genomeProcessLinks.innerHTML = Object.entries(result.genome_process_links)
    .map(([key, value]) => `
      <div>
        <dt>${escapeHtml(key.replaceAll('_', ' '))}</dt>
        <dd>${escapeHtml(value)}</dd>
      </div>
    `)
    .join('');
}

async function updateMediaOptimization() {
  if (!optimizerForm) {
    return;
  }
  updateOptimizerLabels();
  const result = await fetchJson('/api/media-optimization', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(readOptimizerInput()),
  });
  renderOptimization(result);
  updateSystemBiologyEvaluation();
  scheduleGemAndProcessUpdate();
}

function renderCultivationOptimizer(result) {
  const best = result.best;
  renderDefinitionGrid(cultivationOptimizerResult, [
    ['Целевая функция', best.objective_score],
    ['Меласса', `${best.input.molasses_g_l} г/л`],
    ['Пептон', `${best.input.peptone_g_l} г/л`],
    ['Коллаген', `${best.input.collagen_g_l} г/л`],
    ['Аэрация / перемешивание', `${best.input.aeration_vvm} vvm / ${best.input.rpm} об/мин`],
    ['Прогноз активности', `${best.projection.predicted_collagenase_u_ml} U/ml`],
  ]);
}

function renderConditionEvaluation(evaluation) {
  if (!evaluation || !systemBiologyCondition || !systemBiologyPrograms) {
    return;
  }
  const projection = evaluation.projection || {};
  renderDefinitionGrid(systemBiologyCondition, [
    ['Потенциал биомассы', `${projection.biomass_potential_index ?? '-'}%`, 'с учётом условий'],
    ['Коллагенолитический потенциал', `${projection.collagenolytic_potential_index ?? '-'}%`, translateConfidence(projection.confidence)],
    ['Кислородный риск', `${projection.oxygen_process_risk_index ?? '-'}%`, 'процессное ограничение'],
    ['Давление вязкости', `${projection.viscosity_pressure_index ?? '-'}%`, 'мицелиальная нагрузка'],
    ['Давление вторичного обмена', `${projection.secondary_metabolism_pressure_index ?? '-'}%`, 'BGC/стресс-слой'],
  ]);

  systemBiologyPrograms.innerHTML = (evaluation.programs || []).map((program) => `
    <article class="program-card" data-status="${escapeHtml(program.status)}">
      <div class="sensor-topline">
        <span>${escapeHtml(translateProgramName(program.name))}</span>
        <strong>${escapeHtml(program.score)}%</strong>
      </div>
      <div class="sensor-track"><span style="width: ${Number(program.score) || 0}%"></span></div>
      <p>${escapeHtml(translateText(program.rationale))}</p>
    </article>
  `).join('');

  if (systemBiologyInterpretation) {
    systemBiologyInterpretation.innerHTML = (evaluation.interpretation || [])
      .map((item) => `<li>${escapeHtml(translateText(item))}</li>`)
      .join('');
  }
}

function renderSystemBiology(result) {
  const report = result.genome_report || {};
  const summary = report.genome_summary || {};
  renderDefinitionGrid(systemBiologySummary, [
    ['Сборка', `${result.primary_accession || report.accession || '-'} / ${summary.assembly_name || '-'}`, summary.source || 'источник'],
    ['Размер генома', `${Number(summary.total_bp || 0).toLocaleString()} п.н.`, `${summary.sequence_count || 0} последовательностей`],
    ['N50', `${Number(summary.n50_bp || 0).toLocaleString()} п.н.`, summary.level || 'уровень'],
    ['Гены / белки', `${summary.gene_count || 0} / ${summary.protein_count || 0}`, 'аннотация NCBI'],
    ['CDS / RNA', `${summary.cds_count || 0} / ${summary.rna_count || 0}`, 'локальные файлы'],
  ]);

  biosynthesisPotentialList.innerHTML = (report.categories || []).map((item) => `
    <article class="program-card" data-status="${escapeHtml(item.confidence === 'high' ? 'active' : 'balanced')}">
      <div class="sensor-topline">
        <span>${escapeHtml(translateProgramName(item.label || item.name))}</span>
        <strong>${escapeHtml(item.score)}%</strong>
      </div>
      <div class="sensor-track"><span style="width: ${Number(item.score) || 0}%"></span></div>
      <p>${escapeHtml(item.match_count)} строк доказательств / ${escapeHtml(item.source_count)} источников / уверенность: ${escapeHtml(translateConfidence(item.confidence))}</p>
    </article>
  `).join('');

  if (systemBiologyWarnings) {
    const direct = report.direct_collagenase_evidence || {};
    const directNote = direct.found_direct_annotation
      ? `Прямые collagenase-like keyword-hit: ${(direct.gbff_match_count || 0) + (direct.protein_match_count || 0)}.`
      : 'Прямые keyword-hit collagenase в GBFF/protein: 0; используется только вывод через протеазы и секрецию.';
    const warnings = uniqueStrings([directNote, ...(report.warnings || [])])
      .filter((item) => !String(item).includes('No direct collagenase'));
    systemBiologyWarnings.innerHTML = warnings
      .map((item) => `<li>${escapeHtml(translateText(item))}</li>`)
      .join('');
  }

  renderConditionEvaluation(result.condition_evaluation);
}

async function loadSystemBiologyWidgets() {
  if (!cultivationOptimizerResult || !biosynthesisPotentialList) {
    return;
  }
  const [optimizer, systemBiology] = await Promise.all([
    fetchJson('/api/cultivation-optimizer'),
    fetchJson('/api/system-biology-model'),
  ]);
  renderCultivationOptimizer(optimizer);
  renderSystemBiology(systemBiology);
}

async function updateSystemBiologyEvaluation() {
  if (!optimizerForm || !systemBiologyCondition) {
    return;
  }
  const result = await fetchJson('/api/system-biology-model/evaluate', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(readOptimizerInput()),
  });
  renderConditionEvaluation(result);
}

async function loadGemSummary() {
  if (!gemSummaryGrid) {
    return;
  }
  const summary = await fetchJson('/api/gem/summary');
  renderDefinitionGrid(gemSummaryGrid, [
    ['Статус', translateStatus(summary.status || 'unknown'), summary.available ? 'COBRA готова' : 'ограниченный режим'],
    ['SBML', summary.sbml_exists ? 'сформирован' : 'отсутствует', summary.model_id || '-'],
    ['Реакции', summary.reaction_count ?? '-', `${summary.metabolite_count ?? '-'} метаболитов`],
    ['Гены', summary.gene_count ?? 0, 'доказательства в notes, GPR не курирован'],
    ['Решатель', summary.dependency?.solver || '-', `cobra ${summary.dependency?.cobra || '-'}`],
  ]);
}

function readGemMediumPayload() {
  return {
    medium: readOptimizerInput(),
    objective: 'balanced',
    growth_floor: 0.05,
  };
}

async function updateGemAndProcess() {
  if (!optimizerForm || !gemFbaGrid || !processSimulationGrid) {
    return;
  }
  const medium = readOptimizerInput();
  const [fba, simulation] = await Promise.all([
    fetchJson('/api/gem/fba', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(readGemMediumPayload()),
    }),
    fetchJson('/api/process-simulation', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        process_mode: processModeSelect?.value || 'batch',
        medium,
        duration_h: 144,
        step_h: 12,
        initial_biomass_g_l: 0.12,
        initial_volume_l: 1.7,
        feed_rate_l_h: 0.005,
        bleed_rate_l_h: 0.005,
      }),
    }),
  ]);

  renderDefinitionGrid(gemFbaGrid, [
    ['Статус', translateStatus(fba.status || 'unknown'), fba.available ? 'доступно' : translateText(fba.error || 'degraded')],
    ['Целевая функция', translateObjective(fba.objective || 'balanced'), fba.objective_value ?? '-'],
    ['Поглощение углерода', fba.exchange_bounds?.EX_molasses_proxy_e ?? '-', 'прокси мелассы'],
    ['Поглощение кислорода', fba.exchange_bounds?.EX_o2_e ?? '-', 'граница O₂'],
    ['Поток продукта', fba.fluxes?.EX_collagenolytic_product_e ?? '-', 'секретируемый прокси'],
    ['Лимитирует', (fba.limiting_exchange_reactions || []).join(', ') || 'нет', 'обменные реакции'],
  ]);

  const last = (simulation.profile || [])[simulation.profile.length - 1] || {};
  renderDefinitionGrid(processSimulationGrid, [
    ['Режим', translateMode(simulation.process_mode || '-'), simulation.degraded_mode ? 'ограниченный режим' : translateStatus(simulation.fba_status)],
    ['Финальная биомасса', `${last.biomass_g_l ?? '-'} г/л`, `${last.volume_l ?? '-'} л`],
    ['Прокси продукта', `${last.product_u_ml ?? '-'} U/ml`, `${last.protein_mg_ml ?? '-'} мг/мл белка`],
    ['Остаток мелассы', `${last.molasses_g_l ?? '-'} г/л`, `${last.collagen_g_l ?? '-'} г/л коллагена`],
    ['Вязкость', `${last.viscosity_mpa_s ?? '-'} мПа·с`, `${last.density_g_ml ?? '-'} г/мл`],
    ['pO₂', `${last.pO2_percent ?? '-'}%`, `FBA μ ${last.fba_mu_capacity_h ?? '-'}`],
  ]);

  if (processEquationsList) {
    processEquationsList.innerHTML = [...(simulation.mass_balance_equations || []), ...(simulation.notes || [])]
      .map((item) => `<li>${escapeHtml(translateText(item))}</li>`)
      .join('');
  }
}

function scheduleGemAndProcessUpdate() {
  if (gemProcessUpdateTimer) {
    window.clearTimeout(gemProcessUpdateTimer);
  }
  gemProcessUpdateTimer = window.setTimeout(() => {
    updateGemAndProcess().catch((error) => {
      if (gemFbaGrid) {
        renderDefinitionGrid(gemFbaGrid, [['Ошибка', error.message, 'обновление COBRA/SBML не выполнено']]);
      }
    });
  }, 350);
}

function readOmicsInput() {
  const formData = new FormData(omicsForm);
  return {
    genome_accession: String(formData.get('genome_accession') || '').trim(),
    transcriptome_bioproject: String(formData.get('transcriptome_bioproject') || '').trim(),
    metabolome_label: String(formData.get('metabolome_label') || '').trim(),
  };
}

function renderToolStatus(toolStatus) {
  omicsToolStatus.innerHTML = Object.entries(toolStatus)
    .map(([tool, available]) => `<span data-ok="${available}">${escapeHtml(tool)}: ${available ? 'найден' : 'нет'}</span>`)
    .join('');
}

function renderRegistry(registry) {
  const groups = [
    ['genomes', 'Сборки генома'],
    ['transcriptomes', 'Транскриптом'],
    ['metabolomes', 'Метаболомика'],
  ];
  omicsRegistrySummary.innerHTML = groups.map(([key, label]) => {
    const items = registry[key] || [];
    const verified = items.filter((item) => String(item.verification_status).startsWith('verified')).length;
    const candidate = items.filter((item) => item.verification_status === 'candidate').length;
    return `
      <div>
        <dt>${escapeHtml(label)}</dt>
        <dd>${items.length}</dd>
        <span>${verified} проверено / ${candidate} кандидатов</span>
      </div>
    `;
  }).join('');
}

function renderOmicsPreview(result) {
  const validation = result.validation;
  const errors = validation.manifest_errors || [];
  omicsValidation.innerHTML = `
    <div data-ok="${validation.genome_accession_valid}">Доступ генома: ${validation.genome_accession_valid ? 'OK' : 'ошибка'}</div>
    <div data-ok="${validation.transcriptome_bioproject_valid}">BioProject: ${validation.transcriptome_bioproject_valid ? 'OK' : 'ошибка'}</div>
    <div data-ok="${validation.manifest_valid}">Манифест: ${validation.manifest_valid ? 'валиден' : escapeHtml(errors.join('; '))}</div>
  `;
  omicsCommands.textContent = Object.entries(result.commands)
    .map(([name, command]) => `${name}:\n${command}`)
    .join('\n\n');
}

function renderArtifacts(result) {
  omicsArtifacts.innerHTML = Object.entries(result.artifacts)
    .map(([name, path]) => `
      <div>
        <dt>${escapeHtml(name)}</dt>
        <dd>${escapeHtml(displayPath(path))}</dd>
      </div>
    `)
    .join('');
}

async function loadOmicsRegistry() {
  if (!omicsForm) {
    return;
  }
  const result = await fetchJson('/api/omics/registry');
  renderRegistry(result.registry);
  renderToolStatus(result.tool_status);
}

async function updateOmicsPreview() {
  if (!omicsForm) {
    return;
  }
  const result = await fetchJson('/api/omics/manifest', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(readOmicsInput()),
  });
  renderOmicsPreview(result);
}

async function scaffoldOmicsProject() {
  omicsScaffoldButton.disabled = true;
  omicsScaffoldButton.textContent = 'Создание...';
  try {
    const result = await fetchJson('/api/omics/scaffold', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(readOmicsInput()),
    });
    renderOmicsPreview(result);
    renderToolStatus(result.tool_status);
    renderArtifacts(result);
  } finally {
    omicsScaffoldButton.disabled = false;
    omicsScaffoldButton.textContent = 'Создать артефакты';
  }
}

async function runOmicsAction(button, path, label) {
  button.disabled = true;
  button.textContent = 'Выполняю...';
  try {
    const result = await fetchJson(path, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: path.includes('download-genomes') || path.includes('biosynthesis-report') ? undefined : JSON.stringify(readOmicsInput()),
    });
    if (result.artifacts) {
      renderArtifacts(result);
    } else if (result.downloaded) {
      omicsArtifacts.innerHTML = result.downloaded.map((item) => `
        <div>
          <dt>${escapeHtml(item.accession)}</dt>
          <dd>${item.ok ? `${escapeHtml(displayPath(item.zip_path))} / артефактов: ${item.asset_count}` : escapeHtml(item.error || 'ошибка')}</dd>
        </div>
      `).join('');
    } else if (result.run_ids) {
      omicsArtifacts.innerHTML = `
        <div><dt>RunInfo</dt><dd>${escapeHtml(displayPath(result.runinfo_path))}</dd></div>
        <div><dt>Запуски</dt><dd>${escapeHtml(result.run_ids.join(', '))}</dd></div>
        <div><dt>Суммарный объём</dt><dd>${escapeHtml(result.total_size_MB)} MB</dd></div>
      `;
    } else if (result.categories) {
      omicsArtifacts.innerHTML = Object.entries(result.categories).map(([name, payload]) => `
        <div>
          <dt>${escapeHtml(name)}</dt>
          <dd>${payload.evidence_file_count} файлов доказательств</dd>
        </div>
      `).join('');
    }
  } finally {
    button.disabled = false;
    button.textContent = label;
  }
}

window.addEventListener('DOMContentLoaded', () => {
  loadShortcuts();
  document.getElementById('calculate-form').addEventListener('submit', calculateMetrics);
  document.getElementById('recommendation-form').addEventListener('submit', requestRecommendations);
  document.getElementById('import-button').addEventListener('click', importExcel);
  if (optimizerForm) {
    optimizerForm.addEventListener('input', updateMediaOptimization);
    if (processModeSelect) {
      processModeSelect.addEventListener('change', scheduleGemAndProcessUpdate);
    }
    updateMediaOptimization();
    loadSystemBiologyWidgets();
    loadGemSummary();
    scheduleGemAndProcessUpdate();
  }
  if (omicsForm) {
    omicsForm.addEventListener('input', updateOmicsPreview);
    omicsScaffoldButton.addEventListener('click', scaffoldOmicsProject);
    omicsDiscoverButton.addEventListener('click', () => runOmicsAction(omicsDiscoverButton, '/api/omics/discover-transcriptome', 'Найти RunInfo'));
    omicsDownloadGenomesButton.addEventListener('click', () => runOmicsAction(omicsDownloadGenomesButton, '/api/omics/download-genomes', 'Пакеты геномов'));
    omicsBiosynthesisButton.addEventListener('click', () => runOmicsAction(omicsBiosynthesisButton, '/api/omics/biosynthesis-report', 'Отчёт биосинтеза'));
    loadOmicsRegistry();
    updateOmicsPreview();
  }
});
