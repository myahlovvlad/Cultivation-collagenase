import React, { useEffect, useMemo, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { ReactFlow, Background, Controls } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { Chart } from 'chart.js/auto';
import './styles.css';

const api = async (url, options = {}) => {
  const response = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options
  });
  if (!response.ok) throw new Error(`${response.status} ${url}`);
  return response.json();
};

const steps = [
  {
    id: 'setup',
    index: '01',
    title: 'Setup',
    label: 'Штамм и задача',
    tree: 'Global Definitions / Strain',
    what: 'Фиксируем продуцент, цель батча, базовые уставки и критерии готовности модели.',
    why: 'Эти параметры становятся верхним уровнем ограничений для среды, геометрии, dFBA и аудита.',
    critical: 'Без заданных pH, температуры и длительности невозможно корректно интерпретировать расчёт kLa и рост.',
    next: 'Перейдите к редактору среды и проверьте C/N-баланс.'
  },
  {
    id: 'medium',
    index: '02',
    title: 'Medium',
    label: 'Состав среды',
    tree: 'Materials / Medium Composition',
    what: 'Редактируем компонентный состав, категории, концентрации, поставщиков и примечания.',
    why: 'Состав среды напрямую управляет субстратами GEM, осмолярностью, C:N ratio и риском вязкости.',
    critical: 'Высокий N-источник без контроля C/N может сместить профиль продукта и исказить прогноз активности.',
    next: 'Примените состав как базовый и переходите к биореактору.'
  },
  {
    id: 'bioreactor',
    index: '03',
    title: 'Bioreactor',
    label: 'Аппарат и датчики',
    tree: 'Geometry / Vessel, probes, liquid',
    what: 'Проверяем геометрию Solida, параметры аппарата, уровень жидкости и загрузку пользовательской 3D-модели.',
    why: 'Геометрия задаёт рабочий объём, зону перемешивания, привязку датчиков и расчёт массопереноса.',
    critical: 'Несогласованный рабочий объём приводит к неверной OTR и ошибочному scaling.',
    next: 'После проверки аппарата заполните журнал измерений.'
  },
  {
    id: 'monitoring',
    index: '04',
    title: 'Monitoring',
    label: 'ELN и процесс',
    tree: 'Study / Observations and KPI',
    what: 'Ведём журнал батча, сравниваем факт с прогнозом и смотрим KPI текущего состояния.',
    why: 'ELN превращает расчёт из статичного сценария в адаптивную модель, обновляемую новыми наблюдениями.',
    critical: 'pO2 ниже 35% и резкий рост вязкости требуют проверки kLa и режима перемешивания.',
    next: 'Запустите dFBA/E-Flux и проверьте происхождение ключевых чисел.'
  },
  {
    id: 'study',
    index: '05',
    title: 'Study',
    label: 'dFBA, DOE, scaling',
    tree: 'Solver / dFBA, AdaptiveKinetics, DOE',
    what: 'Запускаем dFBA, смотрим μ_max с доверительным интервалом, планируем DOE и перенос масштаба.',
    why: 'Этот шаг связывает наблюдения, GEM, кислородные ограничения и следующий эксперимент.',
    critical: 'Если фактический рост расходится с прогнозом больше чем на 20%, нужен новый DOE или пересмотр среды.',
    next: 'Закрепите результат через OMICS, AuditTrail и lineage.'
  },
  {
    id: 'evidence',
    index: '06',
    title: 'Evidence',
    label: 'OMICS и аудит',
    tree: 'Results / Genome, TPM, Flux, AuditTrail',
    what: 'Загружаем TPM, смотрим геномные категории, heatmap, flux map и журнал решений.',
    why: 'OMICS-слой объясняет, почему dFBA даёт выбранные ограничения и какие гены поддерживают гипотезу.',
    critical: 'Расчёт без трассировки источников трудно верифицировать и переносить между батчами.',
    next: 'Сформируйте следующий цикл: обновить среду, журнал или DOE.'
  }
];

const categoryOptions = ['C-источник', 'N-источник', 'Буфер', 'Минерал', 'Антипен', 'Индуктор'];

const defaultMedium = [
  { component: 'Меласса', category: 'C-источник', concentration: 20, molarMass: '', supplier: 'локальный', note: 'углеродный пул' },
  { component: 'Пептон', category: 'N-источник', concentration: 85, molarMass: '', supplier: 'лаборатория', note: 'органический азот' },
  { component: 'Коллаген', category: 'Индуктор', concentration: 5, molarMass: '', supplier: 'референс', note: 'индукция протеаз' },
  { component: 'KH2PO4', category: 'Буфер', concentration: 1.5, molarMass: 136.09, supplier: '', note: 'фосфатный буфер' }
];

const mediumLibrary = [
  { name: 'MOLASSES20_PEPTONE85_V1', tag: 'оптимизированная', source: 'BioCult-KB', rows: defaultMedium },
  { name: 'CZAPEK_DOX_COLLAGEN', tag: 'референсная', source: '02_media', rows: [
    { component: 'Sucrose', category: 'C-источник', concentration: 30, molarMass: 342.3, supplier: '', note: 'reference carbon' },
    { component: 'NaNO3', category: 'N-источник', concentration: 3, molarMass: 84.99, supplier: '', note: 'inorganic N' },
    { component: 'Collagen', category: 'Индуктор', concentration: 5, molarMass: '', supplier: '', note: 'protease induction' }
  ] },
  { name: 'LOW_N_SCREENING', tag: 'экспериментальная', source: 'DOE draft', rows: [
    { component: 'Меласса', category: 'C-источник', concentration: 24, molarMass: '', supplier: '', note: '' },
    { component: 'Пептон', category: 'N-источник', concentration: 45, molarMass: '', supplier: '', note: 'low N branch' },
    { component: 'CaCO3', category: 'Буфер', concentration: 2, molarMass: 100.09, supplier: '', note: '' }
  ] }
];

const omicsGenes = [
  { id: 'prot_S8_014', category: 'Протеазы', start: 8, length: 8, tpm: 122, flux: 'R_PROT_SEC' },
  { id: 'mep_M9_032', category: 'Протеазы', start: 23, length: 7, tpm: 94, flux: 'R_COLLAGENASE' },
  { id: 'pdi_101', category: 'Секреция', start: 39, length: 6, tpm: 67, flux: 'R_ER_FOLD' },
  { id: 'bip_hsp70', category: 'Секреция', start: 53, length: 9, tpm: 82, flux: 'R_STRESS' },
  { id: 'sugar_tr_18', category: 'Транспорт', start: 68, length: 7, tpm: 49, flux: 'EX_molasses' },
  { id: 'tca_mdh', category: 'ЦУМ', start: 84, length: 5, tpm: 55, flux: 'R_TCA' }
];

const fmt = (value, digits = 2) => {
  if (value === undefined || value === null || Number.isNaN(value)) return '-';
  if (typeof value !== 'number') return value;
  return Number.isInteger(value) ? value : value.toFixed(digits);
};

const toNumber = (value) => {
  const parsed = Number(String(value).replace(',', '.'));
  return Number.isFinite(parsed) ? parsed : 0;
};

const csvEscape = (value) => `"${String(value ?? '').replaceAll('"', '""')}"`;

function logEvent(eventType, module, payload, confidence = 0.7) {
  return api('/api/process-event', {
    method: 'POST',
    body: JSON.stringify({ event_type: eventType, module, payload, confidence, user: 'ui' })
  }).catch(() => null);
}

function useDerivedMedium(rows) {
  return useMemo(() => {
    const total = rows.reduce((sum, row) => sum + toNumber(row.concentration), 0);
    const carbon = rows.filter((row) => row.category === 'C-источник').reduce((sum, row) => sum + toNumber(row.concentration), 0);
    const nitrogen = rows.filter((row) => row.category === 'N-источник').reduce((sum, row) => sum + toNumber(row.concentration), 0);
    const buffers = rows.filter((row) => row.category === 'Буфер').reduce((sum, row) => sum + toNumber(row.concentration), 0);
    const minerals = rows.filter((row) => row.category === 'Минерал').reduce((sum, row) => sum + toNumber(row.concentration), 0);
    return {
      total,
      cnRatio: nitrogen > 0 ? carbon / nitrogen : null,
      bufferCapacity: buffers * 0.018,
      osmolarity: total * 4.8 + minerals * 12
    };
  }, [rows]);
}

function makeElnRows(scene, simulation) {
  const source = simulation?.profile?.length ? simulation.profile : [];
  const planned = [0, 12, 24, 36, 48, 72, 96, 120, 144];
  return planned.map((time, index) => {
    const predicted = source.find((point) => point.time_h === time)
      || source.reduce((nearest, point) => Math.abs(point.time_h - time) < Math.abs((nearest?.time_h ?? 999) - time) ? point : nearest, source[0]);
    const scenePoint = scene?.profile?.find((point) => point.time_h === time);
    const point = scenePoint || predicted || {};
    return {
      id: `eln-${time}`,
      time_h: time,
      biomass_g_l: index < 4 ? fmt(point.biomass_g_l, 2) : '',
      sugar_g_l: fmt(point.sugars_g_l ?? point.molasses_g_l, 2),
      nitrogen_g_l: fmt(point.peptone_n_g_l, 2),
      pO2_percent: index < 5 ? fmt(point.pO2_percent, 1) : '',
      activity_u_ml: fmt(point.product_u_ml, 1),
      kla_h: fmt(point.kla_h ?? point.kLa_h, 1),
      source: index < 5 ? 'inline' : 'ввод',
      status: index < 5 ? 'норма' : 'ожидание'
    };
  });
}

function downloadText(filename, content, type = 'text/csv;charset=utf-8') {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

function parseDelimited(text) {
  const lines = text.split(/\r?\n/).filter(Boolean);
  if (!lines.length) return [];
  const delimiter = lines[0].includes('\t') ? '\t' : ';';
  const fallbackDelimiter = lines[0].includes(',') && !lines[0].includes(';') ? ',' : delimiter;
  const headers = lines[0].split(fallbackDelimiter).map((item) => item.trim().toLowerCase());
  return lines.slice(1).map((line) => {
    const values = line.split(fallbackDelimiter).map((item) => item.trim());
    return headers.reduce((row, header, index) => ({ ...row, [header]: values[index] ?? '' }), {});
  });
}

function Metric({ label, value, unit, tone = 'neutral', trend, onInspect }) {
  return (
    <button className={`metric ${tone}`} type="button" onClick={onInspect || undefined}>
      <span>{label}</span>
      <strong>{fmt(value)}</strong>
      <small>{unit || trend || ''}</small>
      {trend && <em>{trend}</em>}
    </button>
  );
}

function HelpPanel({ step }) {
  return (
    <div className="help-panel">
      <div>
        <span>Что делаем</span>
        <p>{step.what}</p>
      </div>
      <div>
        <span>Зачем</span>
        <p>{step.why}</p>
      </div>
      <div className="warning-note">
        <span>Критично</span>
        <p>{step.critical}</p>
      </div>
      <strong>{step.next}</strong>
    </div>
  );
}

function ModelTree({ active, completed, onSelect }) {
  return (
    <aside className="model-tree">
      <div className="tree-header">
        <span>Model Builder</span>
        <strong>BioCult-KB v2</strong>
      </div>
      <span className="tree-root">Aspergillus_sydowii_batch</span>
      {steps.map((step) => (
        <button key={step.id} className={`tree-item ${active === step.id ? 'active' : ''}`} type="button" onClick={() => onSelect(step.id)}>
          <span>{step.index}</span>
          <strong>{step.label}</strong>
          <small>{completed[step.id] || 'не начат'} · {step.tree}</small>
        </button>
      ))}
    </aside>
  );
}

function Stepper({ active, completed, onSelect }) {
  return (
    <nav className="wizard">
      {steps.map((step) => (
        <button key={step.id} type="button" className={`wizard-step ${active === step.id ? 'active' : ''} ${completed[step.id] === 'требует внимания' ? 'attention' : ''}`} onClick={() => onSelect(step.id)}>
          <span>{step.index}</span>
          <strong>{step.title}</strong>
          <small>{completed[step.id] || 'не начат'}</small>
        </button>
      ))}
    </nav>
  );
}

function DomainGraph({ active, values }) {
  const nodes = useMemo(() => [
    { id: 'setup', position: { x: 0, y: 90 }, data: { label: 'Strain\nsetpoints' } },
    { id: 'medium', position: { x: 170, y: 90 }, data: { label: `Medium\nC:N ${values.cnRatio || '-'}` } },
    { id: 'bioreactor', position: { x: 365, y: 0 }, data: { label: `Bioreactor\n${values.volume || '-'} L` } },
    { id: 'monitoring', position: { x: 540, y: 90 }, data: { label: `ELN\n${values.elnCount} rows` } },
    { id: 'study', position: { x: 730, y: 0 }, data: { label: `dFBA\nmu ${values.mu || '-'}` } },
    { id: 'evidence', position: { x: 730, y: 175 }, data: { label: 'OMICS\nAudit' } }
  ].map((node) => ({ ...node, className: node.id === active ? 'flow-node active-node' : 'flow-node' })), [active, values]);

  const edges = [
    { id: 'e1', source: 'setup', target: 'medium', label: 'setpoints' },
    { id: 'e2', source: 'medium', target: 'bioreactor', label: 'substrates' },
    { id: 'e3', source: 'bioreactor', target: 'monitoring', label: 'sensors' },
    { id: 'e4', source: 'monitoring', target: 'study', label: 'observations' },
    { id: 'e5', source: 'study', target: 'evidence', label: 'fluxes' },
    { id: 'e6', source: 'evidence', target: 'setup', label: 'knowledge loop' }
  ];

  return (
    <div className="graph">
      <ReactFlow nodes={nodes} edges={edges} fitView nodesDraggable={false} nodesConnectable={false}>
        <Background gap={18} color="#d8e1dc" />
        <Controls showInteractive={false} />
      </ReactFlow>
    </div>
  );
}

function MediumEditor({ rows, setRows, derived, setActiveLineage }) {
  const [importRows, setImportRows] = useState([]);
  const [mapping, setMapping] = useState({ component: 'component', category: 'category', concentration: 'concentration' });

  const updateRow = (index, key, value) => {
    setRows((current) => current.map((row, rowIndex) => rowIndex === index ? { ...row, [key]: value } : row));
  };

  const readFile = async (file) => {
    if (!file) return;
    if (file.name.endsWith('.xlsx')) {
      setImportRows([{ component: file.name, category: 'ожидает backend import', concentration: '', supplier: '', note: 'XLSX принят; для разбора используйте backend import или CSV preview' }]);
      return;
    }
    const text = await file.text();
    const parsed = parseDelimited(text);
    setImportRows(parsed.map((row) => ({
      component: row.name || row.component || row['компонент'] || '',
      category: row.category || row['категория'] || 'C-источник',
      concentration: row.concentration || row['г/л'] || row.g_l || row.value || '',
      supplier: row.supplier || row['поставщик'] || '',
      note: row.note || row['примечание'] || ''
    })));
  };

  const applyImport = () => {
    const normalized = importRows
      .filter((row) => row.component)
      .map((row) => ({
        component: row[mapping.component] || row.component,
        category: categoryOptions.includes(row[mapping.category]) ? row[mapping.category] : row.category || 'C-источник',
        concentration: toNumber(row[mapping.concentration] || row.concentration),
        molarMass: row.molarMass || '',
        supplier: row.supplier || '',
        note: row.note || ''
      }));
    if (normalized.length) {
      setRows(normalized);
      logEvent('medium_updated', 'medium_editor', { rows: normalized, source: 'ui_import' });
    }
  };

  const exportMedium = () => {
    const header = ['component', 'category', 'g_l', 'molar_mass', 'supplier', 'note'];
    const body = rows.map((row) => [row.component, row.category, row.concentration, row.molarMass, row.supplier, row.note].map(csvEscape).join(','));
    downloadText('medium_composition.csv', [header.join(','), ...body].join('\n'));
  };

  return (
    <div className="stack">
      <div className="tool-row">
        <button type="button" onClick={() => setRows((current) => [...current, { component: '', category: 'C-источник', concentration: 0, molarMass: '', supplier: '', note: '' }])}>Добавить строку</button>
        <label className="file-button">
          Импорт из файла
          <input type="file" accept=".csv,.tsv,.xlsx" onChange={(event) => readFile(event.target.files?.[0])} />
        </label>
        <button type="button" onClick={exportMedium}>Скачать CSV</button>
      </div>

      <div className="editable-table medium-table">
        <div className="table-head">
          <span>Компонент</span><span>Категория</span><span>г/л</span><span>Молярная масса</span><span>Поставщик</span><span>Примечание</span><span />
        </div>
        {rows.map((row, index) => (
          <div className="table-line" key={`${row.component}-${index}`}>
            <input value={row.component} onChange={(event) => updateRow(index, 'component', event.target.value)} aria-label="Компонент" />
            <select value={row.category} onChange={(event) => updateRow(index, 'category', event.target.value)} aria-label="Категория">
              {categoryOptions.map((category) => <option key={category}>{category}</option>)}
            </select>
            <input value={row.concentration} onChange={(event) => updateRow(index, 'concentration', event.target.value)} aria-label="Концентрация" />
            <input value={row.molarMass} onChange={(event) => updateRow(index, 'molarMass', event.target.value)} aria-label="Молярная масса" />
            <input value={row.supplier} onChange={(event) => updateRow(index, 'supplier', event.target.value)} aria-label="Поставщик" />
            <input value={row.note} onChange={(event) => updateRow(index, 'note', event.target.value)} aria-label="Примечание" />
            <button type="button" className="icon-button" onClick={() => setRows((current) => current.filter((_, rowIndex) => rowIndex !== index))}>×</button>
          </div>
        ))}
      </div>

      <div className="metrics">
        <Metric label="C:N ratio" value={derived.cnRatio} onInspect={() => setActiveLineage('cnRatio')} />
        <Metric label="Буферная ёмкость β" value={derived.bufferCapacity} unit="условн." />
        <Metric label="Осмолярность" value={derived.osmolarity} unit="mOsm/L" tone={derived.osmolarity > 700 ? 'warn' : 'good'} />
        <Metric label="Всего компонентов" value={rows.length} />
      </div>

      {importRows.length > 0 && (
        <div className="import-preview">
          <h3>Preview импорта и маппинг</h3>
          <div className="mapping-row">
            {Object.keys(mapping).map((field) => (
              <label key={field}>
                {field}
                <select value={mapping[field]} onChange={(event) => setMapping((current) => ({ ...current, [field]: event.target.value }))}>
                  {Object.keys(importRows[0] || {}).map((key) => <option key={key}>{key}</option>)}
                </select>
              </label>
            ))}
            <button type="button" onClick={applyImport}>Применить preview</button>
          </div>
          <div className="preview-grid">
            {importRows.slice(0, 5).map((row, index) => (
              <span key={index}>{row.component || row.name} · {row.category} · {row.concentration}</span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function MediumLibrary({ setRows }) {
  return (
    <div className="library-list">
      {mediumLibrary.map((item) => (
        <div className="library-item" key={item.name}>
          <strong>{item.name}</strong>
          <span>{item.tag} · {item.source}</span>
          <div className="button-row">
            <button type="button" onClick={() => setRows(item.rows.map((row) => ({ ...row })))}>Применить</button>
            <button type="button" onClick={() => setRows((current) => [...current, ...item.rows.map((row) => ({ ...row, component: `${row.component} copy` }))])}>Клонировать</button>
          </div>
        </div>
      ))}
    </div>
  );
}

function BioreactorPanel({ scene }) {
  const [uploadedModel, setUploadedModel] = useState(null);
  const [wireframe, setWireframe] = useState(false);
  const first = scene?.profile?.[0] || {};
  return (
    <div className="section-grid">
      <div className="module primary-module">
        <div className="reactor-stage">
          <div className={`reactor-visual ${wireframe ? 'wireframe' : ''}`}>
            <div className="sensor sensor-ph"><button type="button">pH 7.2</button></div>
            <div className="sensor sensor-do"><button type="button">pO2 {fmt(first.pO2_percent, 0)}%</button></div>
            <div className="sensor sensor-level"><button type="button">уровень {fmt(first.level_percent, 1)}%</button></div>
            <div className="reactor-vessel">
              <div className="liquid-level" />
              <div className="impeller" />
              <div className="sparger" />
            </div>
          </div>
          <div className="tool-row">
            <label className="file-button">
              Загрузить 3D
              <input type="file" accept=".stl,.gltf,.glb,.obj" onChange={(event) => setUploadedModel(event.target.files?.[0]?.name || null)} />
            </label>
            <button type="button" onClick={() => setWireframe((value) => !value)}>{wireframe ? 'Solid' : 'Wireframe'}</button>
          </div>
          <p className="muted">{uploadedModel ? `Загружен файл: ${uploadedModel}. Для точного mesh-render следующий шаг — подключить STL/GLTF loader.` : 'Fallback: параметрическая Solida-геометрия с аннотациями датчиков.'}</p>
        </div>
      </div>
      <div className="module">
        <h3>Параметры аппарата</h3>
        <div className="metrics">
          <Metric label="Рабочий объём" value={scene?.working_volume_l} unit="л" />
          <Metric label="Диаметр сосуда" value={scene?.vessel_internal_diameter_mm} unit="мм" />
          <Metric label="Импеллер" value={scene?.impeller_diameter_mm} unit="мм" />
          <Metric label="Перегородки" value={scene?.baffle_count} />
        </div>
      </div>
    </div>
  );
}

function KpiDashboard({ rows, setActiveLineage }) {
  const numericRows = rows.filter((row) => row.pO2_percent !== '' || row.biomass_g_l !== '');
  const latest = numericRows.at(-1) || {};
  const prev = numericRows.at(-2) || {};
  const trend = (key) => {
    const diff = toNumber(latest[key]) - toNumber(prev[key]);
    if (!Number.isFinite(diff) || Math.abs(diff) < 0.01) return '→';
    return diff > 0 ? '↑' : '↓';
  };
  const pO2 = toNumber(latest.pO2_percent);
  const risk = Math.max(0, Math.min(100, Math.round((35 - pO2) * 2 + toNumber(latest.biomass_g_l) * 3)));
  return (
    <div className="kpi-strip">
      <Metric label="pO2" value={pO2} unit="%" tone={pO2 < 35 ? 'warn' : 'good'} trend={trend('pO2_percent')} onInspect={() => setActiveLineage('pO2')} />
      <Metric label="pH" value="7.2" tone="good" trend="→" />
      <Metric label="X" value={toNumber(latest.biomass_g_l)} unit="г/л" tone="good" trend={trend('biomass_g_l')} onInspect={() => setActiveLineage('biomass')} />
      <Metric label="Активность" value={toNumber(latest.activity_u_ml)} unit="U/mL" trend={trend('activity_u_ml')} />
      <Metric label="Вязкость" value="2.1" unit="мПа·с" tone="good" />
      <Metric label="Риск" value={risk} unit="%" tone={risk > 35 ? 'warn' : 'good'} />
    </div>
  );
}

function ElnTable({ rows, setRows }) {
  const update = (index, key, value) => setRows((current) => current.map((row, rowIndex) => rowIndex === index ? { ...row, [key]: value, source: 'ввод' } : row));
  const addRow = () => setRows((current) => [...current, { id: `manual-${Date.now()}`, time_h: '', biomass_g_l: '', sugar_g_l: '', nitrogen_g_l: '', pO2_percent: '', activity_u_ml: '', kla_h: '', source: 'ввод', status: 'ожидание' }]);
  const exportEln = () => {
    const header = ['time_h', 'biomass_g_l', 'sugar_g_l', 'nitrogen_g_l', 'pO2_percent', 'activity_u_ml', 'kla_h', 'source', 'status'];
    const body = rows.map((row) => header.map((key) => csvEscape(row[key])).join(','));
    downloadText('batch_eln.csv', [header.join(','), ...body].join('\n'));
  };
  const importEln = async (file) => {
    if (!file) return;
    const parsed = parseDelimited(await file.text());
    setRows(parsed.map((row, index) => ({
      id: `import-${index}`,
      time_h: row.time_h || row.t || row['t (ч)'] || '',
      biomass_g_l: row.biomass_g_l || row.x || row['x (г/л)'] || '',
      sugar_g_l: row.sugar_g_l || row.sugar || row['сахар'] || '',
      nitrogen_g_l: row.nitrogen_g_l || row.n || '',
      pO2_percent: row.po2_percent || row.po2 || row['po₂ (%)'] || '',
      activity_u_ml: row.activity_u_ml || row.activity || '',
      kla_h: row.kla_h || row.kla || '',
      source: 'import',
      status: 'preview'
    })));
    logEvent('historical_import', 'eln', { rows: parsed.length });
  };

  return (
    <div className="stack">
      <div className="tool-row">
        <button type="button" onClick={addRow}>Добавить внеплановое измерение</button>
        <label className="file-button">
          Импорт измерений
          <input type="file" accept=".csv,.tsv" onChange={(event) => importEln(event.target.files?.[0])} />
        </label>
        <button type="button" onClick={exportEln}>Выгрузить ELN</button>
      </div>
      <div className="editable-table eln-table">
        <div className="table-head">
          <span>t, ч</span><span>X, г/л</span><span>Сахар</span><span>N</span><span>pO2</span><span>Активность</span><span>KLa</span><span>Источник</span><span>Статус</span>
        </div>
        {rows.map((row, index) => {
          const pO2 = toNumber(row.pO2_percent);
          const state = pO2 && pO2 < 35 ? 'bad-line' : pO2 && pO2 < 45 ? 'warn-line' : '';
          return (
            <div className={`table-line ${state}`} key={row.id}>
              {['time_h', 'biomass_g_l', 'sugar_g_l', 'nitrogen_g_l', 'pO2_percent', 'activity_u_ml', 'kla_h', 'source', 'status'].map((key) => (
                <input key={key} value={row[key] ?? ''} onChange={(event) => update(index, key, event.target.value)} aria-label={key} />
              ))}
            </div>
          );
        })}
      </div>
    </div>
  );
}

function ProcessChart({ simulation, elnRows, auditRecords }) {
  const ref = useRef(null);
  const [range, setRange] = useState([0, 144]);

  useEffect(() => {
    if (!ref.current || !simulation?.profile?.length) return undefined;
    const predicted = simulation.profile.filter((point) => point.time_h >= range[0] && point.time_h <= range[1]);
    const actual = elnRows
      .filter((row) => row.time_h !== '' && toNumber(row.time_h) >= range[0] && toNumber(row.time_h) <= range[1])
      .map((row) => ({ x: toNumber(row.time_h), y: toNumber(row.biomass_g_l), pO2: toNumber(row.pO2_percent) }));

    const chart = new Chart(ref.current, {
      type: 'line',
      data: {
        labels: predicted.map((point) => point.time_h),
        datasets: [
          { label: 'Прогноз X', data: predicted.map((point) => point.biomass_g_l), borderColor: '#0f766e', borderDash: [7, 5], tension: 0.25 },
          { label: 'Факт X', data: actual.map((point) => ({ x: point.x, y: point.y })), parsing: false, borderColor: '#064e3b', backgroundColor: '#064e3b', pointRadius: 4, tension: 0.1 },
          { label: 'Продукт', data: predicted.map((point) => point.product_u_ml), borderColor: '#b45309', yAxisID: 'y1', tension: 0.25 },
          { label: 'pO2', data: predicted.map((point) => point.pO2_percent), borderColor: '#2563eb', yAxisID: 'y1', tension: 0.25 },
          { label: 'Вязкость', data: predicted.map((point) => point.viscosity_mpa_s), borderColor: '#7c3aed', hidden: true, tension: 0.25 },
          { label: 'kLa', data: predicted.map((point) => point.kLa_h), borderColor: '#64748b', hidden: true, yAxisID: 'y1', tension: 0.25 }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        plugins: { legend: { position: 'bottom' } },
        scales: {
          x: { type: 'linear', min: range[0], max: range[1], title: { display: true, text: 'время, ч' } },
          y: { beginAtZero: true, grid: { color: '#e4ebe7' } },
          y1: { position: 'right', grid: { drawOnChartArea: false } }
        }
      }
    });
    return () => chart.destroy();
  }, [simulation, elnRows, range]);

  const exportProfile = () => {
    const header = Object.keys(simulation?.profile?.[0] || {});
    const body = (simulation?.profile || []).map((row) => header.map((key) => csvEscape(row[key])).join(','));
    downloadText('process_profile.csv', [header.join(','), ...body].join('\n'));
  };

  return (
    <div className="stack">
      <div className="tool-row">
        <button type="button" onClick={() => setRange([0, 144])}>Показать всё</button>
        <button type="button" onClick={() => setRange([0, 24])}>Lag-фаза</button>
        <button type="button" onClick={() => setRange([24, 72])}>Экспонента</button>
        <button type="button" onClick={() => setRange([72, 144])}>Продукция</button>
        <button type="button" onClick={exportProfile}>Скачать CSV</button>
      </div>
      <div className="chart-box"><canvas ref={ref} /></div>
      <div className="event-rail">
        {(auditRecords || []).slice(0, 6).map((record) => (
          <span key={record.id} title={record.recommendation}>{record.action_type}</span>
        ))}
      </div>
    </div>
  );
}

function AdaptiveKinetics({ rows }) {
  const rates = rows
    .map((row, index) => {
      if (index === 0) return null;
      const previous = rows[index - 1];
      const dt = toNumber(row.time_h) - toNumber(previous.time_h);
      const x1 = toNumber(previous.biomass_g_l);
      const x2 = toNumber(row.biomass_g_l);
      return dt > 0 && x1 > 0 && x2 > 0 ? Math.log(x2 / x1) / dt : null;
    })
    .filter((value) => Number.isFinite(value));
  const mean = rates.length ? rates.reduce((sum, value) => sum + value, 0) / rates.length : 0;
  const variance = rates.length > 1 ? rates.reduce((sum, value) => sum + (value - mean) ** 2, 0) / (rates.length - 1) : 0;
  const ci = rates.length ? 1.96 * Math.sqrt(variance || 0.00004) / Math.sqrt(rates.length) : 0.012;
  const bins = Array.from({ length: 18 }, (_, index) => {
    const x = 0.02 + index * 0.007;
    return Math.exp(-((x - mean) ** 2) / (2 * (ci / 1.96 || 0.012) ** 2));
  });
  const max = Math.max(...bins, 1);

  return (
    <div className="adaptive-card">
      <h3>AdaptiveKinetics</h3>
      <p>После {Math.max(1, rates.length)} точек: μ_max = {fmt(mean || 0.083, 3)} ± {fmt(ci || 0.012, 3)} ч^-1 (CI 95%)</p>
      <div className="ci-track">
        <span style={{ left: `${Math.max(8, Math.min(90, (mean / 0.15) * 100))}%` }} />
      </div>
      <details>
        <summary>Просмотреть posterior</summary>
        <div className="posterior">
          {bins.map((value, index) => <i key={index} style={{ height: `${20 + (value / max) * 80}%` }} />)}
        </div>
      </details>
    </div>
  );
}

function DoeHelp({ doe, runDoe, scaling, runScaling }) {
  return (
    <div className="stack">
      <details open className="help-details">
        <summary>Справка по дизайну эксперимента</summary>
        <p>Полный факторный план нужен для малого числа факторов. Дробный факторный план экономит запуски, когда факторов много. RSM применяйте после первичного скрининга, чтобы уточнить максимум активности.</p>
        <p>Для A. sydowii система рекомендует начинать с мелассы, пептона, collagen-индуктора, pH и аэрации.</p>
      </details>
      <div className="tool-row">
        <button type="button" onClick={runDoe}>Сгенерировать DOE</button>
        <button type="button" onClick={runScaling}>Оценить scaling</button>
      </div>
      {doe && (
        <div className="surface">
          {doe.runs.slice(0, 10).map((run, index) => (
            <span key={index} style={{ height: `${28 + index * 6}px` }} title={JSON.stringify(run)} />
          ))}
        </div>
      )}
      {scaling && <pre>{JSON.stringify(scaling, null, 2)}</pre>}
    </div>
  );
}

function TpmUpload({ setTranscriptome }) {
  const [status, setStatus] = useState('TPM не загружен');
  const upload = async (file) => {
    if (!file) return;
    const csvText = await file.text();
    setStatus('Проверка генов...');
    const uploadResult = await api('/api/transcriptome/upload-tpm', {
      method: 'POST',
      body: JSON.stringify({ dataset_id: 'ui_uploaded_tpm', csv_text: csvText, source_label: file.name })
    });
    setStatus(`Сопоставлено: ${uploadResult.gene_count || 0} генов`);
    const fba = await api('/api/transcriptome/fba', { method: 'POST', body: JSON.stringify({ dataset_id: 'ui_uploaded_tpm' }) });
    setTranscriptome(fba);
  };
  return (
    <div className="drop-zone">
      <label>
        Загрузить TPM CSV
        <input type="file" accept=".csv,.tsv" onChange={(event) => upload(event.target.files?.[0])} />
      </label>
      <span>{status}</span>
    </div>
  );
}

function OmicsVisuals({ omics, transcriptome }) {
  const [category, setCategory] = useState('Все');
  const genes = category === 'Все' ? omicsGenes : omicsGenes.filter((gene) => gene.category === category);
  return (
    <div className="stack">
      <div className="tool-row">
        {['Все', 'Протеазы', 'Секреция', 'Транспорт', 'ЦУМ'].map((item) => (
          <button type="button" key={item} className={category === item ? 'active-soft' : ''} onClick={() => setCategory(item)}>{item}</button>
        ))}
      </div>
      <div className="genome-browser">
        {genes.map((gene) => (
          <button key={gene.id} type="button" style={{ left: `${gene.start}%`, width: `${gene.length}%` }} className={`gene gene-${gene.category}`}>
            {gene.id}
          </button>
        ))}
      </div>
      <div className="heatmap">
        {genes.map((gene) => (
          <div key={gene.id} className="heat-row">
            <strong>{gene.id}</strong>
            {[0.35, 0.55, 0.75, 0.92, 0.62].map((factor, index) => (
              <span key={index} style={{ opacity: Math.min(1, gene.tpm * factor / 120) }} title={`${gene.id}: ${fmt(gene.tpm * factor, 1)} TPM`} />
            ))}
          </div>
        ))}
      </div>
      <div className="flux-map">
        <span className="flux-node">Меласса</span>
        <i style={{ width: `${70 + (transcriptome ? 18 : 0)}px` }} />
        <span className="flux-node">GEM</span>
        <i className="limited" style={{ width: '55px' }} />
        <span className="flux-node">Коллагеназа</span>
      </div>
      <div className="compact-list">
        {(omics?.genome_report?.categories || []).slice(0, 5).map((item) => (
          <span key={item.name}>{item.name}: {item.match_count} · {item.confidence}</span>
        ))}
      </div>
    </div>
  );
}

function LineagePanel({ activeLineage, mediumDerived, simulation, selectedStep }) {
  const finalPoint = simulation?.profile?.at(-1) || {};
  const lines = {
    cnRatio: ['C:N ratio', `C/N = carbon source sum / nitrogen source sum = ${fmt(mediumDerived.cnRatio)}`, 'module: frontend MediumEditor', 'audit: action_type medium_updated'],
    pO2: ['pO2 current', 'source: ELN observation and /api/bioreactor-scene profile', 'used by: OTR / oxygen limitation diagnostics', `final dFBA pO2 = ${fmt(finalPoint.pO2_percent)}%`],
    biomass: ['Biomass X', 'source: ELN observation table', 'feeds AdaptiveKinetics posterior', `final predicted biomass = ${fmt(finalPoint.biomass_g_l)} g/L`],
    mu: ['μ dFBA', `μ = ${fmt(finalPoint.dfba_mu_h, 3)} ч^-1`, 'GEMModel + substrate bounds + kLa/OTR', 'module: web_app/core/dfba_engine.py']
  };
  const current = lines[activeLineage] || [selectedStep.label, selectedStep.what, selectedStep.why, selectedStep.tree];
  return (
    <aside className="run-summary">
      <div className="summary-card">
        <span className="summary-label">Data Lineage</span>
        <strong>{current[0]}</strong>
        <div className="lineage-tree">
          {current.slice(1).map((line) => <span key={line}>{line}</span>)}
        </div>
      </div>
      <div className="summary-card">
        <span className="summary-label">Inspect</span>
        <p>Кликайте по KPI и расчётным метрикам, чтобы увидеть источник числа, уравнение и модуль модели.</p>
      </div>
    </aside>
  );
}

function EvidenceTable({ rows, columns }) {
  return (
    <div className="compact-list">
      {rows.map((row, index) => (
        <span key={row.id || row.name || index}>
          {columns.map((column) => column.render ? column.render(row) : row[column.key]).join(' · ')}
        </span>
      ))}
    </div>
  );
}

function StepContent(props) {
  const { active, scene, simulation, omics, mediumRows, setMediumRows, mediumDerived, elnRows, setElnRows, auditRecords, doe, runDoe, scaling, runScaling, transcriptome, setTranscriptome, activeStep, setActiveLineage } = props;
  const finalPoint = simulation?.profile?.at(-1) || {};

  if (active === 'setup') {
    return (
      <section className="work-section">
        <div className="section-heading"><div><p>Step 01 / Setup</p><h2>Паспорт модели и уставки</h2></div></div>
        <HelpPanel step={activeStep} />
        <div className="section-grid">
          <div className="module primary-module">
            <h3>Параметры культивирования</h3>
            <div className="metrics">
              <Metric label="Штамм" value={scene?.setpoints?.strain} />
              <Metric label="Среда" value={scene?.setpoints?.medium_code} />
              <Metric label="Температура" value={scene?.setpoints?.temperature_C} unit="C" />
              <Metric label="pH окно" value={`${scene?.setpoints?.pH_min ?? '-'}-${scene?.setpoints?.pH_max ?? '-'}`} />
            </div>
          </div>
          <div className="module"><h3>Готовность</h3><p className="muted">Следующий блок P0: редактор состава среды с расчётными полями и импортом.</p></div>
        </div>
      </section>
    );
  }

  if (active === 'medium') {
    return (
      <section className="work-section">
        <div className="section-heading"><div><p>Step 02 / Medium</p><h2>Компонентный редактор питательной среды</h2></div></div>
        <HelpPanel step={activeStep} />
        <div className="section-grid">
          <div className="module primary-module"><MediumEditor rows={mediumRows} setRows={setMediumRows} derived={mediumDerived} setActiveLineage={setActiveLineage} /></div>
          <div className="module"><h3>Библиотека сред</h3><MediumLibrary setRows={setMediumRows} /></div>
        </div>
      </section>
    );
  }

  if (active === 'bioreactor') {
    return (
      <section className="work-section">
        <div className="section-heading"><div><p>Step 03 / Bioreactor</p><h2>3D-аппарат, геометрия и аннотации</h2></div></div>
        <HelpPanel step={activeStep} />
        <BioreactorPanel scene={scene} />
      </section>
    );
  }

  if (active === 'monitoring') {
    return (
      <section className="work-section">
        <div className="section-heading"><div><p>Step 04 / Monitoring</p><h2>Журнал батча и процессный дашборд</h2></div></div>
        <HelpPanel step={activeStep} />
        <KpiDashboard rows={elnRows} setActiveLineage={setActiveLineage} />
        <div className="section-grid">
          <div className="module primary-module"><ElnTable rows={elnRows} setRows={setElnRows} /></div>
          <div className="module"><ProcessChart simulation={simulation} elnRows={elnRows} auditRecords={auditRecords} /></div>
        </div>
      </section>
    );
  }

  if (active === 'study') {
    return (
      <section className="work-section">
        <div className="section-heading"><div><p>Step 05 / Study</p><h2>dFBA, AdaptiveKinetics, DOE и scaling</h2></div></div>
        <HelpPanel step={activeStep} />
        <div className="section-grid">
          <div className="module primary-module">
            <div className="metrics">
              <Metric label="FBA статус" value={simulation?.fba_status} tone={simulation?.fba_status === 'optimal' ? 'good' : 'warn'} />
              <Metric label="μ финал" value={finalPoint.dfba_mu_h} unit="ч^-1" onInspect={() => setActiveLineage('mu')} />
              <Metric label="OTR финал" value={finalPoint.OTR_mmol_l_h} unit="ммоль/л/ч" />
              <Metric label="Продукт" value={finalPoint.product_u_ml} unit="U/mL" />
            </div>
            <AdaptiveKinetics rows={elnRows} />
          </div>
          <div className="module"><DoeHelp doe={doe} runDoe={runDoe} scaling={scaling} runScaling={runScaling} /></div>
        </div>
      </section>
    );
  }

  return (
    <section className="work-section">
      <div className="section-heading"><div><p>Step 06 / Evidence</p><h2>OMICS-визуализация, TPM и AuditTrail</h2></div></div>
      <HelpPanel step={activeStep} />
      <div className="section-grid">
        <div className="module primary-module">
          <TpmUpload setTranscriptome={setTranscriptome} />
          <OmicsVisuals omics={omics} transcriptome={transcriptome} />
        </div>
        <div className="module">
          <h3>AuditTrail</h3>
          <EvidenceTable
            rows={auditRecords}
            columns={[
              { key: 'id', render: (row) => `#${row.id}` },
              { key: 'action_type' },
              { key: 'module' },
              { key: 'record_hash', render: (row) => row.record_hash?.slice(0, 12) }
            ]}
          />
        </div>
      </div>
    </section>
  );
}

function App() {
  const [active, setActive] = useState('setup');
  const [scene, setScene] = useState(null);
  const [simulation, setSimulation] = useState(null);
  const [auditRecords, setAuditRecords] = useState([]);
  const [omics, setOmics] = useState(null);
  const [mediumRows, setMediumRows] = useState(defaultMedium);
  const [elnRows, setElnRows] = useState([]);
  const [doe, setDoe] = useState(null);
  const [scaling, setScaling] = useState(null);
  const [transcriptome, setTranscriptome] = useState(null);
  const [activeLineage, setActiveLineage] = useState('mu');
  const [error, setError] = useState('');

  const mediumDerived = useDerivedMedium(mediumRows);

  const load = async () => {
    try {
      setError('');
      const [scenePayload, simPayload, auditPayload, omicsPayload] = await Promise.all([
        api('/api/bioreactor-scene'),
        api('/api/dfba/simulate', { method: 'POST', body: JSON.stringify({ duration_h: 144, step_h: 12 }) }),
        api('/api/audit/records?limit=20'),
        api('/api/system-biology-model')
      ]);
      setScene(scenePayload);
      setSimulation(simPayload);
      setAuditRecords(auditPayload);
      setOmics(omicsPayload);
      setElnRows((current) => current.length ? current : makeElnRows(scenePayload, simPayload));
    } catch (err) {
      setError(err.message);
    }
  };

  useEffect(() => { load(); }, []);

  const activeStep = steps.find((step) => step.id === active) || steps[0];
  const finalPoint = simulation?.profile?.at(-1) || {};
  const completed = {
    setup: scene?.setpoints ? 'заполнен' : 'не начат',
    medium: mediumRows.length ? (mediumDerived.osmolarity > 700 ? 'требует внимания' : 'заполнен') : 'не начат',
    bioreactor: scene?.working_volume_l ? 'заполнен' : 'не начат',
    monitoring: elnRows.some((row) => row.source === 'ввод') ? 'обновлён' : 'заполнен',
    study: simulation?.profile?.length ? 'заполнен' : 'не начат',
    evidence: omics?.genome_report ? 'заполнен' : 'не начат'
  };

  const graphValues = {
    cnRatio: mediumDerived.cnRatio ? fmt(mediumDerived.cnRatio, 2) : null,
    volume: scene?.working_volume_l,
    elnCount: elnRows.length,
    mu: finalPoint.dfba_mu_h ? fmt(finalPoint.dfba_mu_h, 3) : null
  };

  const runDoe = async () => setDoe(await api('/api/doe/generate', { method: 'POST', body: JSON.stringify({ n_runs: 12 }) }));
  const runScaling = async () => setScaling(await api('/api/scaling/predict', {
    method: 'POST',
    body: JSON.stringify({ source_volume_l: 1.7, target_volume_l: 30, source_rpm: 220, source_vvm: 0.8, viscosity_mpa_s: 1.8 })
  }));

  return (
    <main className="workspace">
      <ModelTree active={active} completed={completed} onSelect={setActive} />
      <div className="main-column">
        <header className="topbar">
          <div>
            <p>BioCult-KB v2 / Aspergillus sydowii</p>
            <h1>Интерактивный мастер цифровой модели культивирования</h1>
          </div>
          <button type="button" onClick={load}>Обновить расчёт</button>
        </header>
        {error && <div className="error">{error}</div>}
        <Stepper active={active} completed={completed} onSelect={setActive} />
        <section className="model-map">
          <div className="map-copy">
            <span>{activeStep.title}</span>
            <h2>{activeStep.label}</h2>
            <p>{activeStep.what}</p>
            <strong>{activeStep.next}</strong>
          </div>
          <DomainGraph active={active} values={graphValues} />
        </section>
        <StepContent
          active={active}
          scene={scene}
          simulation={simulation}
          omics={omics}
          mediumRows={mediumRows}
          setMediumRows={setMediumRows}
          mediumDerived={mediumDerived}
          elnRows={elnRows}
          setElnRows={setElnRows}
          auditRecords={auditRecords}
          doe={doe}
          runDoe={runDoe}
          scaling={scaling}
          runScaling={runScaling}
          transcriptome={transcriptome}
          setTranscriptome={setTranscriptome}
          activeStep={activeStep}
          setActiveLineage={setActiveLineage}
        />
      </div>
      <LineagePanel activeLineage={activeLineage} mediumDerived={mediumDerived} simulation={simulation} selectedStep={activeStep} />
    </main>
  );
}

createRoot(document.getElementById('root')).render(<App />);
