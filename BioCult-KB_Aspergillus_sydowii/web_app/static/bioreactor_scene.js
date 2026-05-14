import * as THREE from 'https://unpkg.com/three@0.164.1/build/three.module.js';

const canvas = document.getElementById('bioreactor-scene');
const timeInput = document.getElementById('process-time');
const playButton = document.getElementById('scene-play');
const resetButton = document.getElementById('scene-reset');

const metrics = {
  time: document.getElementById('scene-time'),
  biomass: document.getElementById('scene-biomass'),
  po2: document.getElementById('scene-po2'),
  kla: document.getElementById('scene-kla'),
  volume: document.getElementById('scene-volume'),
  rpm: document.getElementById('scene-rpm'),
  medium: document.getElementById('scene-medium'),
};

const sensorGrid = document.getElementById('sensor-readings-grid');
const chartCanvas = document.getElementById('sensor-trend-chart');
const chartButtons = document.querySelectorAll('[data-chart]');
const expertPhase = document.getElementById('expert-phase');
const expertRisk = document.getElementById('expert-risk');
const expertRiskFill = document.getElementById('expert-risk-fill');
const expertAlerts = document.getElementById('expert-alerts');
const expertActions = document.getElementById('expert-actions');
const expertConfidence = document.getElementById('expert-confidence');

const SENSOR_DEFINITIONS = [
  {key: 'rpm', label: 'Перемешивание', unit: 'rpm', digits: 0, min: 160, max: 300, low: 180, high: 280},
  {key: 'pH', label: 'pH', unit: '', digits: 2, min: 6.8, max: 7.6, low: 7.1, high: 7.5},
  {key: 'pO2_percent', label: 'pO2', unit: '%', digits: 0, min: 0, max: 100, low: 25, high: 85},
  {key: 'pCO2_percent', label: 'pCO2', unit: '%', digits: 1, min: 0, max: 6, low: 0.2, high: 5},
  {key: 'level_percent', label: 'Уровнемер', unit: '%', digits: 1, min: 65, max: 75, low: 68, high: 72},
  {key: 'density_g_ml', label: 'Плотномер', unit: 'г/мл', digits: 3, min: 1.01, max: 1.035, low: 1.012, high: 1.03},
  {key: 'viscosity_mpa_s', label: 'Вязкость', unit: 'мПа·с', digits: 2, min: 1, max: 3.2, low: 1, high: 2.8},
  {key: 'temperature_C', label: 'Температура', unit: '°C', digits: 1, min: 23.5, max: 26.5, low: 24, high: 26},
  {key: 'pressure_bar', label: 'Давление', unit: 'bar', digits: 2, min: 0.95, max: 1.15, low: 1, high: 1.1},
  {key: 'humidity_percent', label: 'Влажность', unit: '%', digits: 0, min: 45, max: 75, low: 50, high: 70},
  {key: 'conductivity_ms_cm', label: 'Электропроводность', unit: 'mS/cm', digits: 1, min: 7.5, max: 11.5, low: 8, high: 11},
  {key: 'biomass_g_l', label: 'Биомасса', unit: 'г/л', digits: 2, min: 0, max: 4.2, low: 0, high: 4},
];

const CHART_GROUPS = {
  gases: ['pO2_percent', 'pCO2_percent', 'kla_h'],
  culture: ['biomass_g_l', 'sugars_g_l', 'viscosity_mpa_s'],
  control: ['rpm', 'pH', 'temperature_C', 'pressure_bar'],
  media: ['level_percent', 'density_g_ml', 'conductivity_ms_cm', 'humidity_percent'],
};

let activeChartGroup = 'gases';

const DEFAULT_CONFIG = {
  vessel_internal_diameter_mm: 130,
  vessel_internal_height_mm: 180,
  glass_thickness_mm: 5,
  full_volume_l: 2.39,
  working_volume_l: 1.7,
  medium_before_inoculation_l: 1.6,
  inoculum_volume_ml: 100,
  impeller_diameter_mm: 40,
  impeller_blade_height_mm: 10,
  baffle_count: 3,
  baffle_height_mm: 230,
  sparger_height_mm: 230,
  service_tube_count: 6,
  process_duration_h: 144,
  setpoints: {
    temperature_C: 25,
    pH_min: 7.1,
    pH_max: 7.5,
    rpm: 220,
    medium_code: 'MOLASSES20_PEPTONE85_V1',
    strain: 'Aspergillus sydowii',
  },
  profile: [
    {time_h: 0, biomass_g_l: 0.12, rpm: 180, pH: 7.35, pO2_percent: 92, pCO2_percent: 0.3, kla_h: 28, sugars_g_l: 20, level_percent: 71.1, density_g_ml: 1.018, viscosity_mpa_s: 1.18, temperature_C: 24.8, pressure_bar: 1.02, humidity_percent: 58, conductivity_ms_cm: 8.4},
    {time_h: 24, biomass_g_l: 0.8, rpm: 220, pH: 7.28, pO2_percent: 64, pCO2_percent: 1.2, kla_h: 42, sugars_g_l: 16, level_percent: 71.0, density_g_ml: 1.019, viscosity_mpa_s: 1.32, temperature_C: 25.0, pressure_bar: 1.04, humidity_percent: 60, conductivity_ms_cm: 8.8},
    {time_h: 48, biomass_g_l: 1.9, rpm: 240, pH: 7.15, pO2_percent: 38, pCO2_percent: 2.8, kla_h: 65, sugars_g_l: 11, level_percent: 70.8, density_g_ml: 1.021, viscosity_mpa_s: 1.72, temperature_C: 25.2, pressure_bar: 1.06, humidity_percent: 62, conductivity_ms_cm: 9.4},
    {time_h: 72, biomass_g_l: 3.1, rpm: 260, pH: 7.08, pO2_percent: 30, pCO2_percent: 4.1, kla_h: 78, sugars_g_l: 7, level_percent: 70.6, density_g_ml: 1.024, viscosity_mpa_s: 2.35, temperature_C: 25.1, pressure_bar: 1.08, humidity_percent: 64, conductivity_ms_cm: 10.1},
    {time_h: 96, biomass_g_l: 3.6, rpm: 260, pH: 7.03, pO2_percent: 34, pCO2_percent: 4.8, kla_h: 82, sugars_g_l: 5, level_percent: 70.3, density_g_ml: 1.026, viscosity_mpa_s: 2.72, temperature_C: 25.0, pressure_bar: 1.07, humidity_percent: 65, conductivity_ms_cm: 10.6},
    {time_h: 120, biomass_g_l: 3.8, rpm: 250, pH: 7.12, pO2_percent: 41, pCO2_percent: 4.4, kla_h: 80, sugars_g_l: 3.8, level_percent: 70.1, density_g_ml: 1.027, viscosity_mpa_s: 2.68, temperature_C: 24.9, pressure_bar: 1.05, humidity_percent: 64, conductivity_ms_cm: 10.7},
    {time_h: 144, biomass_g_l: 3.7, rpm: 240, pH: 7.22, pO2_percent: 48, pCO2_percent: 3.7, kla_h: 76, sugars_g_l: 3.2, level_percent: 69.8, density_g_ml: 1.027, viscosity_mpa_s: 2.55, temperature_C: 24.8, pressure_bar: 1.04, humidity_percent: 63, conductivity_ms_cm: 10.5},
  ],
};

async function loadConfig() {
  try {
    const response = await fetch('/api/bioreactor-scene');
    if (!response.ok) {
      return DEFAULT_CONFIG;
    }
    return response.json();
  } catch {
    return DEFAULT_CONFIG;
  }
}

function interpolateProfile(profile, timeH) {
  const points = [...profile].sort((a, b) => a.time_h - b.time_h);
  if (timeH <= points[0].time_h) {
    return points[0];
  }

  for (let index = 1; index < points.length; index += 1) {
    const prev = points[index - 1];
    const next = points[index];
    if (timeH <= next.time_h) {
      const ratio = (timeH - prev.time_h) / (next.time_h - prev.time_h);
      const interpolated = {time_h: timeH};
      Object.keys(next).forEach((key) => {
        if (key === 'time_h') {
          return;
        }
        interpolated[key] = THREE.MathUtils.lerp(prev[key], next[key], ratio);
      });
      return interpolated;
    }
  }

  return points[points.length - 1];
}

function createCylinder(radius, height, material, segments = 96, openEnded = false) {
  return new THREE.Mesh(new THREE.CylinderGeometry(radius, radius, height, segments, 1, openEnded), material);
}

function setMetricText(element, value) {
  if (element) {
    element.textContent = value;
  }
}

function formatSensorValue(value, sensor) {
  return `${value.toFixed(sensor.digits)}${sensor.unit ? ` ${sensor.unit}` : ''}`;
}

function getSensorState(value, sensor) {
  if (value < sensor.low || value > sensor.high) {
    return 'warning';
  }
  const span = sensor.high - sensor.low;
  if (value < sensor.low + span * 0.08 || value > sensor.high - span * 0.08) {
    return 'watch';
  }
  return 'ok';
}

function ensureSensorCards() {
  if (!sensorGrid || sensorGrid.children.length) {
    return;
  }
  sensorGrid.innerHTML = SENSOR_DEFINITIONS.map((sensor) => (
    `<div class="sensor-card" data-sensor="${sensor.key}">
      <div class="sensor-topline">
        <span>${sensor.label}</span>
        <span class="sensor-state">OK</span>
      </div>
      <strong>0</strong>
      <div class="sensor-track"><span></span></div>
    </div>`
  )).join('');
}

function updateSensorCards(point) {
  ensureSensorCards();
  SENSOR_DEFINITIONS.forEach((sensor) => {
    const card = sensorGrid?.querySelector(`[data-sensor="${sensor.key}"]`);
    if (!card) {
      return;
    }
    const value = point[sensor.key];
    const state = getSensorState(value, sensor);
    const ratio = THREE.MathUtils.clamp((value - sensor.min) / (sensor.max - sensor.min), 0, 1);
    card.dataset.state = state;
    card.querySelector('strong').textContent = formatSensorValue(value, sensor);
    card.querySelector('.sensor-state').textContent = state === 'ok' ? 'Норма' : state === 'watch' ? 'Контроль' : 'Риск';
    card.querySelector('.sensor-track span').style.width = `${ratio * 100}%`;
  });
}

function getPhase(timeH) {
  if (timeH < 24) {
    return 'Адаптация инокулюма';
  }
  if (timeH < 72) {
    return 'Активный рост';
  }
  if (timeH < 120) {
    return 'Продуктивная фаза';
  }
  return 'Окно сбора культуральной жидкости';
}

function evaluateExpertState(point) {
  const alerts = [];
  const actions = [];
  let risk = 18;

  if (point.pO2_percent < 35) {
    risk += 22;
    alerts.push('pO2 приближается к кислородному ограничению.');
    actions.push('Проверить расход воздуха, пену и эффективность перемешивания.');
  }
  if (point.pCO2_percent > 4.5) {
    risk += 16;
    alerts.push('pCO2 повышен, возможна задержка газообмена.');
    actions.push('Оценить вентиляцию, барботер и противодавление.');
  }
  if (point.pH < 7.1 || point.pH > 7.5) {
    risk += 18;
    alerts.push('pH выходит за целевой коридор 7.1-7.5.');
    actions.push('Сверить калибровку pH-электрода и дозирование корректора.');
  }
  if (point.viscosity_mpa_s > 2.6) {
    risk += 14;
    alerts.push('Вязкость повышена, возрастает риск ухудшения массопереноса.');
    actions.push('Проверить морфологию мицелия и фактический KLA.');
  }
  if (point.temperature_C < 24 || point.temperature_C > 26) {
    risk += 12;
    alerts.push('Температура за пределами 25±1 °C.');
    actions.push('Проверить контур термостатирования рубашки.');
  }
  if (point.time_h >= 120 && point.biomass_g_l >= 3.5 && point.sugars_g_l < 4.5) {
    actions.push('Подготовить контроль активности и рассмотреть сбор на 144 ч.');
  }

  if (!alerts.length) {
    alerts.push('Критических отклонений не обнаружено.');
  }
  if (!actions.length) {
    actions.push('Продолжать мониторинг pO2, pH, вязкости и KLA по плану отбора проб.');
  }

  return {
    phase: getPhase(point.time_h),
    risk: Math.min(100, risk),
    alerts,
    actions,
    confidence: point.time_h >= 48 ? 'Высокая' : 'Средняя',
  };
}

function updateExpertPanel(point) {
  const state = evaluateExpertState(point);
  setMetricText(expertPhase, state.phase);
  setMetricText(expertRisk, `${state.risk}%`);
  setMetricText(expertConfidence, state.confidence);
  if (expertRiskFill) {
    expertRiskFill.style.width = `${state.risk}%`;
    expertRiskFill.dataset.level = state.risk > 65 ? 'high' : state.risk > 42 ? 'medium' : 'low';
  }
  if (expertAlerts) {
    expertAlerts.innerHTML = state.alerts.map((item) => `<li>${item}</li>`).join('');
  }
  if (expertActions) {
    expertActions.innerHTML = state.actions.map((item) => `<li>${item}</li>`).join('');
  }
}

function drawTrendChart(config, currentTimeH) {
  if (!chartCanvas) {
    return;
  }
  const ctx = chartCanvas.getContext('2d');
  const rect = chartCanvas.getBoundingClientRect();
  const scale = Math.min(window.devicePixelRatio || 1, 2);
  chartCanvas.width = Math.floor(rect.width * scale);
  chartCanvas.height = Math.floor(rect.height * scale);
  ctx.setTransform(scale, 0, 0, scale, 0, 0);

  const width = rect.width;
  const height = rect.height;
  const pad = {left: 42, right: 18, top: 24, bottom: 34};
  const plotW = width - pad.left - pad.right;
  const plotH = height - pad.top - pad.bottom;
  const keys = CHART_GROUPS[activeChartGroup];
  const colors = ['#255c99', '#b98220', '#167c74', '#7b5ea7'];

  ctx.clearRect(0, 0, width, height);
  ctx.fillStyle = '#f9fbfc';
  ctx.fillRect(0, 0, width, height);
  ctx.strokeStyle = '#d7e0e6';
  ctx.lineWidth = 1;
  for (let index = 0; index <= 4; index += 1) {
    const y = pad.top + (plotH / 4) * index;
    ctx.beginPath();
    ctx.moveTo(pad.left, y);
    ctx.lineTo(width - pad.right, y);
    ctx.stroke();
  }

  keys.forEach((key, index) => {
    const sensor = SENSOR_DEFINITIONS.find((item) => item.key === key) || {label: key, min: 0, max: Math.max(...config.profile.map((point) => point[key] || 0))};
    const color = colors[index % colors.length];
    ctx.strokeStyle = color;
    ctx.lineWidth = 2.4;
    ctx.beginPath();
    config.profile.forEach((point, pointIndex) => {
      const x = pad.left + (point.time_h / config.process_duration_h) * plotW;
      const y = pad.top + (1 - THREE.MathUtils.clamp((point[key] - sensor.min) / (sensor.max - sensor.min), 0, 1)) * plotH;
      if (pointIndex === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    });
    ctx.stroke();

    ctx.fillStyle = color;
    ctx.font = '12px Inter, sans-serif';
    ctx.fillText(sensor.label, pad.left + index * 128, 15);
  });

  const markerX = pad.left + (currentTimeH / config.process_duration_h) * plotW;
  ctx.strokeStyle = '#172126';
  ctx.lineWidth = 1.5;
  ctx.setLineDash([5, 5]);
  ctx.beginPath();
  ctx.moveTo(markerX, pad.top);
  ctx.lineTo(markerX, pad.top + plotH);
  ctx.stroke();
  ctx.setLineDash([]);

  ctx.fillStyle = '#5b6872';
  ctx.font = '12px Inter, sans-serif';
  ctx.fillText('0 ч', pad.left, height - 10);
  ctx.fillText(`${config.process_duration_h} ч`, width - pad.right - 44, height - 10);
}

function buildBioreactorScene(config) {
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0xf4f7fb);

  const camera = new THREE.PerspectiveCamera(42, 1, 0.1, 100);
  camera.position.set(3.6, 2.4, 5.1);
  camera.lookAt(0, 0.15, 0);

  const renderer = new THREE.WebGLRenderer({canvas, antialias: true, alpha: false});
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.outputColorSpace = THREE.SRGBColorSpace;

  scene.add(new THREE.HemisphereLight(0xeaf6ff, 0xb7a37a, 2.2));

  const keyLight = new THREE.DirectionalLight(0xffffff, 2.6);
  keyLight.position.set(3, 4, 5);
  scene.add(keyLight);

  const rimLight = new THREE.DirectionalLight(0xb7fff3, 1.3);
  rimLight.position.set(-4, 2, -3);
  scene.add(rimLight);

  const mainGroup = new THREE.Group();
  scene.add(mainGroup);

  const vesselHeight = 3.2;
  const vesselRadius = 1.15;
  const liquidHeight = vesselHeight * (config.working_volume_l / config.full_volume_l);
  const liquidBottomY = -vesselHeight / 2;
  const liquidTopY = liquidBottomY + liquidHeight;
  const impellerRadius = vesselRadius * (config.impeller_diameter_mm / config.vessel_internal_diameter_mm);
  const bladeHeight = vesselHeight * (config.impeller_blade_height_mm / config.vessel_internal_height_mm);

  const glassMaterial = new THREE.MeshPhysicalMaterial({
    color: 0xcfeeff,
    transparent: true,
    opacity: 0.24,
    roughness: 0.12,
    metalness: 0,
    side: THREE.DoubleSide,
  });
  const metalMaterial = new THREE.MeshStandardMaterial({color: 0x8a96a3, roughness: 0.38, metalness: 0.78});
  const darkMetalMaterial = new THREE.MeshStandardMaterial({color: 0x55616c, roughness: 0.42, metalness: 0.72});
  const liquidMaterial = new THREE.MeshPhysicalMaterial({
    color: 0xc79a42,
    transparent: true,
    opacity: 0.52,
    roughness: 0.42,
    metalness: 0,
    side: THREE.DoubleSide,
  });
  const foamMaterial = new THREE.MeshStandardMaterial({color: 0xf6edd4, transparent: true, opacity: 0.48});
  const biomassMaterial = new THREE.MeshStandardMaterial({color: 0x556b2f, transparent: true, opacity: 0.72, roughness: 0.8});
  const bubbleMaterial = new THREE.MeshStandardMaterial({color: 0xe8fbff, transparent: true, opacity: 0.68, roughness: 0.05});

  const jacket = createCylinder(vesselRadius + 0.14, vesselHeight + 0.34, glassMaterial, 96, true);
  jacket.position.y = 0.02;
  mainGroup.add(jacket);

  const vessel = createCylinder(vesselRadius, vesselHeight, glassMaterial, 96, true);
  mainGroup.add(vessel);

  const topRing = new THREE.Mesh(new THREE.TorusGeometry(vesselRadius, 0.025, 16, 120), metalMaterial);
  topRing.rotation.x = Math.PI / 2;
  topRing.position.y = vesselHeight / 2;
  mainGroup.add(topRing);

  const bottomRing = topRing.clone();
  bottomRing.position.y = -vesselHeight / 2;
  mainGroup.add(bottomRing);

  const jacketTop = new THREE.Mesh(new THREE.TorusGeometry(vesselRadius + 0.14, 0.018, 12, 120), glassMaterial);
  jacketTop.rotation.x = Math.PI / 2;
  jacketTop.position.y = vesselHeight / 2 + 0.17;
  mainGroup.add(jacketTop);

  const liquid = createCylinder(vesselRadius * 0.92, liquidHeight, liquidMaterial, 96, false);
  liquid.position.y = liquidBottomY + liquidHeight / 2;
  mainGroup.add(liquid);

  const surface = createCylinder(vesselRadius * 0.93, 0.018, liquidMaterial, 96, false);
  surface.position.y = liquidTopY + 0.011;
  mainGroup.add(surface);

  const foamRing = new THREE.Mesh(new THREE.TorusGeometry(vesselRadius * 0.72, 0.035, 16, 96), foamMaterial);
  foamRing.rotation.x = Math.PI / 2;
  foamRing.position.y = liquidTopY + 0.045;
  mainGroup.add(foamRing);

  for (let index = 0; index < config.baffle_count; index += 1) {
    const angle = (index / config.baffle_count) * Math.PI * 2;
    const baffle = new THREE.Mesh(new THREE.BoxGeometry(0.055, vesselHeight * 0.88, 0.16), metalMaterial);
    baffle.position.set(Math.cos(angle) * vesselRadius * 0.88, -0.03, Math.sin(angle) * vesselRadius * 0.88);
    baffle.rotation.y = -angle;
    mainGroup.add(baffle);
  }

  const shaft = createCylinder(0.035, vesselHeight + 0.82, darkMetalMaterial, 32, false);
  shaft.position.y = 0.23;
  mainGroup.add(shaft);

  const impellerGroup = new THREE.Group();
  mainGroup.add(impellerGroup);

  function addImpeller(y) {
    const hub = createCylinder(0.08, 0.12, darkMetalMaterial, 32, false);
    hub.position.y = y;
    impellerGroup.add(hub);

    for (let index = 0; index < 4; index += 1) {
      const blade = new THREE.Mesh(new THREE.BoxGeometry(impellerRadius * 0.95, Math.max(bladeHeight, 0.08), 0.06), metalMaterial);
      blade.position.set(Math.cos((index * Math.PI) / 2) * impellerRadius * 0.42, y, Math.sin((index * Math.PI) / 2) * impellerRadius * 0.42);
      blade.rotation.y = (index * Math.PI) / 2 + 0.32;
      impellerGroup.add(blade);
    }
  }

  addImpeller(liquidBottomY + 0.58);
  addImpeller(liquidBottomY + 1.38);

  const sparger = new THREE.Mesh(new THREE.TorusGeometry(impellerRadius * 0.92, 0.018, 12, 96), metalMaterial);
  sparger.rotation.x = Math.PI / 2;
  sparger.position.y = liquidBottomY + 0.28;
  mainGroup.add(sparger);

  const airStem = createCylinder(0.018, 1.9, metalMaterial, 16, false);
  airStem.position.set(-impellerRadius * 0.9, liquidBottomY + 1.12, 0);
  mainGroup.add(airStem);

  for (let index = 0; index < config.service_tube_count; index += 1) {
    const angle = (index / config.service_tube_count) * Math.PI * 2 + 0.2;
    const tube = createCylinder(0.023, 0.82, metalMaterial, 18, false);
    tube.position.set(Math.cos(angle) * vesselRadius * 0.42, vesselHeight / 2 + 0.36, Math.sin(angle) * vesselRadius * 0.42);
    mainGroup.add(tube);
  }

  const bubbles = new THREE.Group();
  const bubbleGeometry = new THREE.SphereGeometry(0.025, 12, 8);
  for (let index = 0; index < 96; index += 1) {
    const bubble = new THREE.Mesh(bubbleGeometry, bubbleMaterial);
    bubble.userData = {
      angle: Math.random() * Math.PI * 2,
      radius: Math.sqrt(Math.random()) * vesselRadius * 0.58,
      phase: Math.random(),
      speed: 0.35 + Math.random() * 0.55,
      size: 0.55 + Math.random() * 1.25,
    };
    bubbles.add(bubble);
  }
  mainGroup.add(bubbles);

  const biomass = new THREE.Group();
  const pelletGeometry = new THREE.SphereGeometry(0.028, 10, 8);
  for (let index = 0; index < 160; index += 1) {
    const pellet = new THREE.Mesh(pelletGeometry, biomassMaterial);
    pellet.userData = {
      angle: Math.random() * Math.PI * 2,
      radius: Math.sqrt(Math.random()) * vesselRadius * 0.76,
      y: liquidBottomY + 0.22 + Math.random() * (liquidHeight - 0.32),
      phase: Math.random() * Math.PI * 2,
      size: 0.6 + Math.random() * 1.6,
    };
    biomass.add(pellet);
  }
  mainGroup.add(biomass);

  const basePlate = new THREE.Mesh(new THREE.CylinderGeometry(1.65, 1.65, 0.07, 96), new THREE.MeshStandardMaterial({color: 0xd8dde3, roughness: 0.55, metalness: 0.25}));
  basePlate.position.y = liquidBottomY - 0.12;
  mainGroup.add(basePlate);

  let currentTimeH = 0;
  let currentRpm = config.setpoints.rpm;
  let elapsed = 0;
  let playing = false;
  let targetRotation = -0.45;
  let dragStartX = 0;
  let dragRotation = targetRotation;
  let dragging = false;

  const maxBiomass = Math.max(...config.profile.map((point) => point.biomass_g_l));
  const maxKla = Math.max(...config.profile.map((point) => point.kla_h));

  function updateForTime(timeH) {
    currentTimeH = THREE.MathUtils.clamp(timeH, 0, config.process_duration_h);
    const point = interpolateProfile(config.profile, currentTimeH);
    const biomassRatio = point.biomass_g_l / maxBiomass;
    const klaRatio = point.kla_h / maxKla;
    const oxygenRatio = point.pO2_percent / 100;
    currentRpm = point.rpm;

    const earlyColor = new THREE.Color(0xd3a84b);
    const matureColor = new THREE.Color(0x6f7a3c);
    liquidMaterial.color.copy(earlyColor.lerp(matureColor, biomassRatio));
    liquidMaterial.opacity = 0.42 + biomassRatio * 0.22;
    foamMaterial.opacity = 0.18 + biomassRatio * 0.46;
    foamRing.scale.setScalar(0.72 + biomassRatio * 0.28);

    bubbles.children.forEach((bubble, index) => {
      const activeLimit = 34 + Math.round(klaRatio * 62);
      bubble.visible = index < activeLimit;
      const data = bubble.userData;
      const travel = (elapsed * data.speed * (0.7 + klaRatio * 0.7) + data.phase + currentTimeH / 180) % 1;
      const swirl = data.angle + elapsed * (0.55 + klaRatio);
      bubble.position.set(
        Math.cos(swirl) * data.radius * (0.6 + 0.35 * travel),
        liquidBottomY + 0.28 + travel * (liquidHeight - 0.22),
        Math.sin(swirl) * data.radius * (0.6 + 0.35 * travel),
      );
      bubble.scale.setScalar(data.size * (0.75 + oxygenRatio * 0.45));
    });

    biomass.children.forEach((pellet) => {
      const data = pellet.userData;
      const swirl = data.angle + elapsed * (0.12 + klaRatio * 0.22) + Math.sin(elapsed + data.phase) * 0.08;
      const lift = Math.sin(elapsed * 0.8 + data.phase) * 0.035;
      pellet.position.set(Math.cos(swirl) * data.radius, data.y + lift, Math.sin(swirl) * data.radius);
      pellet.scale.setScalar(data.size * (0.28 + biomassRatio * 1.15));
    });

    setMetricText(metrics.time, `${Math.round(currentTimeH)} ч`);
    setMetricText(metrics.biomass, `${point.biomass_g_l.toFixed(2)} г/л`);
    setMetricText(metrics.po2, `${point.pO2_percent.toFixed(0)}%`);
    setMetricText(metrics.kla, `${point.kla_h.toFixed(0)} ч⁻¹`);
    setMetricText(metrics.rpm, `${point.rpm.toFixed(0)} rpm`);
    updateSensorCards(point);
    updateExpertPanel(point);
    drawTrendChart(config, currentTimeH);

    if (timeInput && Number(timeInput.value) !== Math.round(currentTimeH)) {
      timeInput.value = String(Math.round(currentTimeH));
    }
  }

  function resize() {
    const rect = canvas.parentElement.getBoundingClientRect();
    const width = Math.max(320, Math.floor(rect.width));
    const height = Math.max(360, Math.floor(rect.height));
    renderer.setSize(width, height, false);
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
  }

  function animate() {
    requestAnimationFrame(animate);
    const delta = Math.min(clock.getDelta(), 0.05);
    elapsed += delta;

    if (playing) {
      updateForTime(currentTimeH + delta * 9);
      if (currentTimeH >= config.process_duration_h) {
        playing = false;
        playButton.textContent = 'Пуск';
      }
    } else {
      updateForTime(currentTimeH);
    }

    impellerGroup.rotation.y += delta * (currentRpm / 18);
    mainGroup.rotation.y += (targetRotation - mainGroup.rotation.y) * 0.08;
    renderer.render(scene, camera);
  }

  const clock = new THREE.Clock();
  resize();
  updateForTime(0);
  animate();

  chartButtons.forEach((button) => {
    button.addEventListener('click', () => {
      activeChartGroup = button.dataset.chart;
      chartButtons.forEach((item) => item.classList.toggle('active', item === button));
      drawTrendChart(config, currentTimeH);
    });
  });

  if (timeInput) {
    timeInput.max = String(config.process_duration_h);
    const handleTimeInput = () => {
      playing = false;
      playButton.textContent = 'Пуск';
      updateForTime(Number(timeInput.value));
    };
    timeInput.addEventListener('input', handleTimeInput);
    timeInput.addEventListener('change', handleTimeInput);
  }

  if (playButton) {
    playButton.addEventListener('click', () => {
      playing = !playing;
      playButton.textContent = playing ? 'Пауза' : 'Пуск';
    });
  }

  if (resetButton) {
    resetButton.addEventListener('click', () => {
      playing = false;
      playButton.textContent = 'Пуск';
      updateForTime(0);
    });
  }

  canvas.addEventListener('pointerdown', (event) => {
    dragging = true;
    dragStartX = event.clientX;
    dragRotation = targetRotation;
    canvas.setPointerCapture(event.pointerId);
  });

  canvas.addEventListener('pointermove', (event) => {
    if (!dragging) {
      return;
    }
    targetRotation = dragRotation + (event.clientX - dragStartX) * 0.01;
  });

  canvas.addEventListener('pointerup', () => {
    dragging = false;
  });

  window.addEventListener('resize', resize);

  setMetricText(metrics.volume, `${config.working_volume_l.toFixed(1)} л`);
  setMetricText(metrics.medium, config.setpoints.medium_code);
}

if (canvas) {
  loadConfig().then(buildBioreactorScene);
}
