/**
 * main.js — AI Game World Builder frontend logic
 * Handles: SSE streaming, progressive UI population, tab switching
 */

 // ── CONFIGURATION ──────────────────────────────────────── 
 // Set this to your Render backend URL when deploying to Vercel
 // e.g. const API_BASE_URL = 'https://your-backend.onrender.com';
 const API_BASE_URL = ''; 

/* ── TAB SWITCHING ──────────────────────────────────────── */
document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById('tab-' + btn.dataset.tab).classList.add('active');
  });
});

/* ── HELPERS ────────────────────────────────────────────── */
function el(id) { return document.getElementById(id); }
function setText(id, txt) { const e = el(id); if (e) e.textContent = txt || '—'; }
function setHtml(id, html) { const e = el(id); if (e) e.innerHTML = html || ''; }

function makeCard(cls, ...children) {
  const div = document.createElement('div');
  div.className = cls;
  children.forEach(c => {
    if (typeof c === 'string') {
      div.insertAdjacentHTML('beforeend', c);
    } else if (c) {
      div.appendChild(c);
    }
  });
  return div;
}

function geoCard(item, icon, danger = false) {
  const name = item.name || '—';
  const desc = item.description || '';
  return `<div class="geo-card${danger ? ' danger' : ''}">
    <div class="geo-card-icon">${icon}</div>
    <div class="geo-card-name">${name}</div>
    <div class="geo-card-desc">${desc}</div>
  </div>`;
}

function showError(msg) {
  el('errorMessage').textContent = msg;
  el('errorToast').classList.remove('hidden');
}

/* ── PIPELINE PROGRESS ──────────────────────────────────── */
const STEPS = ['world','geography','civilizations','politics','lore','quests','level','game'];
let currentStep = 0;
let currentWorldId = null;

function markStepActive(stepName) {
  const idx = STEPS.indexOf(stepName);
  document.querySelectorAll('.pipe-step').forEach((s, i) => {
    s.classList.remove('active', 'done');
    if (i < idx) s.classList.add('done');
    if (i === idx) s.classList.add('active');
  });
  el('progressBar').style.width = `${Math.round(((idx) / STEPS.length) * 100)}%`;
}

function markStepDone(stepName) {
  const idx = STEPS.indexOf(stepName);
  const s = document.querySelectorAll('.pipe-step')[idx];
  if (s) { s.classList.remove('active'); s.classList.add('done'); }
  el('progressBar').style.width = `${Math.round(((idx + 1) / STEPS.length) * 100)}%`;
}

/* ── RENDER FUNCTIONS ───────────────────────────────────── */

function renderWorld(d) {
  setText('worldName', d.name);
  setText('worldTagline', d.tagline);
  setText('worldEnvironment', d.environment);
  setText('worldMagic', d.magic_system);
  setText('worldTone', d.tone);

  // Stat counters (others filled later)
  setText('statContinents', d.continents ? d.continents.length : '—');

  // Badges
  const badgeContainer = el('worldBadges');
  badgeContainer.innerHTML = '';
  if (d.theme) badgeContainer.insertAdjacentHTML('beforeend', `<span class="badge">${d.theme}</span>`);
  if (d.name)  badgeContainer.insertAdjacentHTML('beforeend', `<span class="badge">✦ ${d.name}</span>`);

  // Continents list
  const ul = el('worldContinents');
  ul.innerHTML = '';
  (d.continents || []).forEach(c => {
    ul.insertAdjacentHTML('beforeend',
      `<li><b>${c.name}</b>${c.description ? ' — ' + c.description : ''}</li>`);
  });

  // Landmarks
  const lg = el('worldLandmarks');
  lg.innerHTML = '';
  (d.landmarks || []).forEach(lm => {
    lg.insertAdjacentHTML('beforeend',
      `<div class="landmark-item">
        <div class="lm-icon">🏛️</div>
        <div><div class="lm-name">${lm.name}</div><div class="lm-desc">${lm.description}</div></div>
      </div>`);
  });

  // Player character
  if (d.player_character) {
    el('characterDesc').textContent = d.player_character;
    el('charSubtitle').textContent = d.name ? `Hero of ${d.name}` : 'Your hero';
    const actions = ['Move', 'Attack', 'Defend', 'Use Ability', 'Interact'];
    const ac = el('charActions');
    ac.innerHTML = '';
    actions.forEach(a => ac.insertAdjacentHTML('beforeend', `<span class="action-pill">${a}</span>`));
    // Pick avatar emoji based on theme
    const theme = (d.theme || '').toLowerCase();
    const avatarMap = [
      [['dragon','fantasy','magic','sword'],'🧙'],
      [['cyber','hack','tech','neon'], '🤖'],
      [['space','star','galax','alien'], '👾'],
      [['zombie','dead','apocal'], '💀'],
      [['pirate','ocean','sea'], '🏴‍☠️'],
      [['ninja','samurai','japan'], '🥷'],
    ];
    let avatar = '🧙';
    for (const [keys, em] of avatarMap) {
      if (keys.some(k => theme.includes(k))) { avatar = em; break; }
    }
    el('charAvatar').textContent = avatar;

    // Pseudo-random stat generation based on character string hash
    const strHash = (str) => {
      let h = 0;
      for (let i = 0; i < str.length; i++) h = Math.imul(31, h) + str.charCodeAt(i) | 0;
      return Math.abs(h);
    };
    const hash = strHash(d.player_character);
    const setStat = (id, base, variance) => {
      const val = base + (hash % variance);
      el(id).style.width = val + '%';
      el(id + 'Val').textContent = val;
      return val;
    };
    setStat('statStr', 40, 50);
    setStat('statMag', 20, 70);
    setStat('statDef', 30, 60);
    setStat('statAgi', 40, 50);
    setStat('statWis', 30, 60);
  }

  el('dashboard').classList.remove('hidden');
}

function renderGeography(d) {
  const zones = el('climateZones');
  zones.innerHTML = (d.climate_zones || []).map(z => geoCard(z, '🌤️')).join('');

  const cities = el('majorCities');
  cities.innerHTML = (d.major_cities || []).map(c => geoCard(c, '🏙️')).join('');

  const wonders = el('naturalWonders');
  wonders.innerHTML = (d.natural_wonders || []).map(w => geoCard(w, '🌋')).join('');

  const danger = el('dangerousRegions');
  danger.innerHTML = (d.dangerous_regions || []).map(r => geoCard(r, '⚠️', true)).join('');

  const routes = el('tradeRoutes');
  routes.innerHTML = (d.trade_routes || []).map(r => geoCard(r, '🛤️')).join('');
}

function renderCivilizations(d) {
  const container = el('civilizationsContainer');
  container.innerHTML = '';
  const colors = ['#5b5ef4','#7c3aed','#0891b2','#059669','#d97706','#dc2626'];
  (d.civilizations || []).forEach((civ, i) => {
    const color = colors[i % colors.length];
    container.insertAdjacentHTML('beforeend', `
      <div class="civ-card">
        <div class="civ-bar" style="background:linear-gradient(90deg,${color},${colors[(i+1)%colors.length]})"></div>
        <div class="civ-body">
          <div class="civ-name">${civ.name || '—'}</div>
          <div class="civ-race">${civ.race || ''} · ${civ.homeland || ''}</div>
          <div class="civ-row"><span class="civ-lbl">Culture</span><span class="civ-val">${civ.culture || '—'}</span></div>
          <div class="civ-row"><span class="civ-lbl">Traditions</span><span class="civ-val">${civ.traditions || '—'}</span></div>
          <div class="civ-row"><span class="civ-lbl">Social Structure</span><span class="civ-val">${civ.social_structure || '—'}</span></div>
          <div class="civ-row"><span class="civ-lbl">Strengths</span><span class="civ-val">${civ.strengths || '—'}</span></div>
          <div class="civ-row"><span class="civ-lbl">Weaknesses</span><span class="civ-val">${civ.weaknesses || '—'}</span></div>
          <div class="civ-row"><span class="civ-lbl">Appearance</span><span class="civ-val">${civ.appearance || '—'}</span></div>
          ${civ.signature_ability ? `<div class="civ-ability">✨ ${civ.signature_ability}</div>` : ''}
        </div>
      </div>
    `);
  });
  setText('statCivs', (d.civilizations || []).length);
}

function renderPolitics(d) {
  const container = el('factionsContainer');
  container.innerHTML = '';
  const strengthColors = {
    'weak': '#6b7280', 'moderate': '#d97706', 'strong': '#dc2626', 'overwhelming': '#7c3aed'
  };

  (d.factions || []).forEach(f => {
    const strKey = (f.military_strength || '').toLowerCase();
    const strColor = strengthColors[strKey] || 'var(--accent)';
    container.insertAdjacentHTML('beforeend', `
      <div class="faction-card">
        <div class="faction-name">${f.name || '—'}</div>
        <div class="faction-type">${f.type || ''}</div>
        <div class="faction-leader">👑 ${f.leader || '—'}</div>
        <div class="faction-ideology">${f.ideology || '—'}</div>
        <div style="font-size:0.78rem;color:var(--text-3);margin-bottom:0.4rem">📍 ${f.territory || '—'}</div>
        <div class="faction-meta">
          ${f.ally   ? `<span class="faction-tag tag-ally">🤝 ${f.ally}</span>` : ''}
          ${f.enemy  ? `<span class="faction-tag tag-enemy">⚔️ ${f.enemy}</span>` : ''}
          <span class="faction-tag tag-strength" style="color:${strColor}">⚡ ${f.military_strength || '?'}</span>
        </div>
        ${f.current_conflict ? `<div class="faction-conflict">"${f.current_conflict}"</div>` : ''}
      </div>
    `);
  });

  setText('majorAlliance', d.major_alliance);
  setText('majorWar', d.major_war);
  setText('statFactions', (d.factions || []).length);

  // Draw Faction Web
  const svg = el('factionRelSvg');
  if (svg && d.factions && d.factions.length > 0) {
    svg.innerHTML = '';
    const factions = d.factions;
    const n = factions.length;
    const cx = 350, cy = 160, r = 100;
    const pts = [];
    factions.forEach((f, i) => {
      const angle = (i * 2 * Math.PI) / n - Math.PI / 2;
      pts.push({ x: cx + r * Math.cos(angle), y: cy + r * Math.sin(angle), name: f.name });
    });

    // Draw lines ALLY = green, ENEMY = red
    factions.forEach((f, i) => {
      const p1 = pts[i];
      if (f.ally) {
        const allyIdx = pts.findIndex(pt => f.ally.includes(pt.name) || pt.name.includes(f.ally));
        if (allyIdx !== -1 && allyIdx !== i) {
          svg.insertAdjacentHTML('beforeend', `<line x1="${p1.x}" y1="${p1.y}" x2="${pts[allyIdx].x}" y2="${pts[allyIdx].y}" class="rel-line rel-ally"/>`);
        }
      }
      if (f.enemy) {
        const enemyIdx = pts.findIndex(pt => f.enemy.includes(pt.name) || pt.name.includes(f.enemy));
        if (enemyIdx !== -1 && enemyIdx !== i) {
          svg.insertAdjacentHTML('beforeend', `<line x1="${p1.x}" y1="${p1.y}" x2="${pts[enemyIdx].x}" y2="${pts[enemyIdx].y}" class="rel-line rel-enemy"/>`);
        }
      }
    });

    // Draw nodes
    pts.forEach(p => {
      svg.insertAdjacentHTML('beforeend', `<circle cx="${p.x}" cy="${p.y}" r="22" class="rel-node"/>`);
      svg.insertAdjacentHTML('beforeend', `<text x="${p.x}" y="${p.y+4}" class="rel-icon">🏰</text>`);
      svg.insertAdjacentHTML('beforeend', `<text x="${p.x}" y="${p.y+40}" class="rel-label">${p.name.substring(0,14)}</text>`);
    });
  }
}

function renderLore(d) {
  setText('creationMyth', d.creation_myth);
  setText('prophecyText', d.prophecy);
  setText('forbiddenKnowledge', d.forbidden_knowledge);

  // Historical eras
  const tl = el('historicalEras');
  tl.innerHTML = '';
  (d.historical_eras || []).forEach(era => {
    tl.insertAdjacentHTML('beforeend', `
      <div class="timeline-item">
        <div class="timeline-dot"></div>
        <div><div class="tl-name">${era.name}</div><div class="tl-desc">${era.description}</div></div>
      </div>
    `);
  });

  // Heroes
  const hg = el('legendaryHeroes');
  hg.innerHTML = '';
  (d.legendary_heroes || []).forEach(h => {
    hg.insertAdjacentHTML('beforeend', `
      <div class="hero-card">
        <div class="hv-icon">⚔️</div>
        <div><div class="hv-name">${h.name}</div><div class="hv-desc">${h.description}</div></div>
      </div>
    `);
  });

  // Villains
  const vg = el('greatVillains');
  vg.innerHTML = '';
  (d.great_villains || []).forEach(v => {
    vg.insertAdjacentHTML('beforeend', `
      <div class="villain-card">
        <div class="hv-icon">☠️</div>
        <div><div class="hv-name">${v.name}</div><div class="hv-desc">${v.description}</div></div>
      </div>
    `);
  });
}

function renderQuests(d) {
  const container = el('questsContainer');
  container.innerHTML = '';
  (d.quests || []).forEach(q => {
    const diff   = q.difficulty || 'Medium';
    const cls    = diff.toLowerCase();
    container.insertAdjacentHTML('beforeend', `
      <div class="quest-card ${cls}">
        <div class="quest-top">
          <div>
            <div class="quest-title">${q.title || '—'}</div>
            <div class="quest-type">${q.type || ''}</div>
          </div>
          <span class="quest-diff diff-${diff}">${diff}</span>
        </div>
        <p class="quest-objective">${q.objective || '—'}</p>
        <div class="quest-meta">
          <div class="qm-item"><div class="qm-label">📍 Location</div><div class="qm-val">${q.location || '—'}</div></div>
          <div class="qm-item"><div class="qm-label">👾 Enemy</div><div class="qm-val">${q.enemy || '—'}</div></div>
          <div class="qm-item"><div class="qm-label">🧑 Key NPC</div><div class="qm-val">${q.key_npc || '—'}</div></div>
          <div class="qm-item"><div class="qm-label">⚔️ Difficulty</div><div class="qm-val">${diff}</div></div>
        </div>
        ${q.twist ? `<div class="quest-twist"><span class="tw-label">⚡ PLOT TWIST</span>${q.twist}</div>` : ''}
        ${q.reward ? `<div class="quest-reward">🏆 Reward: ${q.reward}</div>` : ''}
      </div>
    `);
  });
  setText('statQuests', (d.quests || []).length);
}

function renderLevel(d) {
  setText('levelName', d.level_name);
  setText('levelEnvironment', d.environment);
  setText('levelWin', d.win_condition);
  setText('levelLose', d.lose_condition);
  setText('levelTime', d.time_limit ? d.time_limit + 's' : '—');

  const renderList = (containerId, items, itemClass, nameClass, descClass) => {
    const c = el(containerId);
    c.innerHTML = '';
    (items || []).forEach(item => {
      c.insertAdjacentHTML('beforeend', `
        <div class="${itemClass}">
          <div class="${nameClass}">${item.name || '—'}</div>
          <div class="${descClass}">${item.description || ''}</div>
        </div>
      `);
    });
  };

  // Layout
  const ll = el('levelLayout');
  ll.innerHTML = '';
  (d.layout || []).forEach(area => {
    ll.insertAdjacentHTML('beforeend', `
      <div class="layout-item">
        <div class="li-name">${area.name || '—'}</div>
        <div class="li-desc">${area.description || ''}</div>
      </div>
    `);
  });

  renderList('levelEnemies',    d.enemies,     'enemy-item',      'en-name', 'en-desc');
  renderList('levelObstacles',  d.obstacles,   'ob-item',         'ob-name', 'ob-desc');
  renderList('levelCollectibles',d.collectibles,'co-item',         'co-name', 'co-desc');
}

function renderGame(d) {
  el('gamePlaceholder').classList.add('hidden');
  const iframe = el('gameFrame');
  iframe.src = '/game/' + d.file_name;
  iframe.classList.remove('hidden');

  const link = el('openGameLink');
  link.href = '/game/' + d.file_name;
  link.classList.remove('hidden');
  
  // Show the LLM Prompt / Code logic view
  let gamePromptWrap = el('gamePromptWrap');
  if (!gamePromptWrap) {
      el('tab-game').insertAdjacentHTML('beforeend', `
        <div class="info-card" id="gamePromptWrap" style="margin-top:2rem">
            <div class="card-header">💻 Generated Game Code</div>
            <pre id="gamePromptText" style="white-space:pre-wrap; font-size:0.8rem; background:var(--bg); padding:1rem; border-radius:8px; max-height:400px; overflow-y:auto; font-family:monospace; border:1px solid rgba(0,0,0,0.1)"></pre>
        </div>
      `);
      gamePromptWrap = el('gamePromptWrap');
  }
  
  if (d.code) {
      el('gamePromptText').textContent = d.code;
  } else {
      el('gamePromptText').textContent = "// HTML/JS code generated and saved to " + d.file_name;
  }

  el('gameTitle').innerHTML = `🕹️ Playable Mini-Game <span style="font-size:0.8rem;color:var(--text-light);font-weight:400">— ${d.level_name || 'Level 1'}</span>`;
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  const gameBtn = document.querySelector('[data-tab="game"]');
  if (gameBtn) gameBtn.classList.add('active');
  el('tab-game').classList.add('active');
}

/* ── IMAGES & PROMPTS RENDERER ──────────────────────────── */

function renderImagePrompts(d) {
  const g = el('imagesGrid');
  g.innerHTML = '';
  const prompts = [
    d.prompts.world_shot,
    d.prompts.character,
    d.prompts.villain,
    ...(d.prompts.locations || []),
    ...(d.prompts.civilizations || []),
    ...(d.prompts.factions || [])
  ].filter(Boolean);

  prompts.forEach((p, idx) => {
    const cardId = 'imgCard_' + idx;
    const btnId = 'imgBtn_' + idx;
    g.insertAdjacentHTML('beforeend', `
      <div class="image-prompt-card" id="${cardId}">
        <div class="ip-header">
          <div class="ip-title">${p.icon} ${p.label}</div>
        </div>
        <div class="ip-body">
          <div class="ip-prompt-text">${p.prompt}</div>
          <div class="ip-actions">
            <button class="btn-copy-sm" onclick="copyText('${p.prompt.replace(/'/g, "\\'")}')">📋 Copy Prompt</button>
            ${d.gpu_available ? `<button class="btn-gen-img" id="${btnId}">🎨 Generate Image</button>` : ''}
          </div>
        </div>
        <div class="ip-result hidden"></div>
      </div>
    `);

    // Attach generator listener if GPU
    if (d.gpu_available) {
      setTimeout(() => {
        el(btnId).addEventListener('click', () => {
          el(btnId).textContent = 'Generating... ⏳';
          el(btnId).disabled = true;
          fetch(`${API_BASE_URL}/generate-image`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
              prompt: p.prompt, 
              prefix: 'world',
              world_id: currentWorldId
            })
          }).then(r => r.json()).then(res => {
            const resDiv = el(cardId).querySelector('.ip-result');
            resDiv.classList.remove('hidden');
            if (res.success) {
              resDiv.innerHTML = `<img src="${res.image_url}" alt="${p.label}" class="gen-img-preview"/>`;
              el(btnId).textContent = '✅ Generated';
            } else {
              resDiv.innerHTML = `<div style="color:red;font-size:0.8rem">Failed: ${res.error}</div>`;
              el(btnId).textContent = '🎨 Generate Image';
              el(btnId).disabled = false;
            }
          }).catch(err => {
            el(btnId).textContent = 'Failed';
            el(btnId).disabled = false;
          });
        });
      }, 50);
    }
  });

  // Attach Character prompt to overview tab button
  const charPrompt = d.prompts.character ? d.prompts.character.prompt : '';
  if (charPrompt) {
    el('charPromptBtn').classList.remove('hidden');
    el('charPromptBtn').onclick = () => copyText(charPrompt);
  }
}

function copyText(txt) {
  navigator.clipboard.writeText(txt).then(() => {
    el('copyToast').classList.remove('hidden');
    setTimeout(() => el('copyToast').classList.add('hidden'), 2000);
  });
}

document.addEventListener('DOMContentLoaded', () => {

  // Start Builder Button
  const startBtn = document.getElementById('startBuilderBtn');
  if (startBtn) {
    startBtn.addEventListener('click', () => {
      document.getElementById('homeView').classList.add('hidden');
      document.getElementById('appView').classList.remove('hidden');
      document.getElementById('themeInput').focus();
    });
  }

  // Bind initial interactions
  bindInteractions();
});

// ── EXPORT WORLD ──────────────────────────────────────
let generatedWorldData = null;

el('exportBtn').addEventListener('click', () => {
    if (!generatedWorldData) return;
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(generatedWorldData, null, 2));
    const dlAnchorElem = document.createElement('a');
    dlAnchorElem.setAttribute("href", dataStr);
    dlAnchorElem.setAttribute("download", "world_bible.json");
    dlAnchorElem.click();
});

el('regenBtn').addEventListener('click', () => {
  window.scrollTo(0,0);
  el('themeInput').focus();
});

/* ── SSE STREAMING ──────────────────────────────────────── */
  el('generateForm').addEventListener('submit', function(e) {
  e.preventDefault();

  const theme = el('themeInput').value.trim();
  if (!theme) return;

  // Reset UI
  currentStep = 0;
  generatedWorldData = null;
  el('progressBar').style.width = '0%';
  el('pipelineProgress').classList.remove('hidden');
  el('dashboard').classList.add('hidden');
  el('actionBar').classList.add('hidden');
  document.querySelectorAll('.pipe-step').forEach(s => s.classList.remove('active', 'done'));
  el('errorToast').classList.add('hidden');
  el('worldMapContainer').innerHTML = '<div class="map-placeholder">Generating SVG Map...</div>';
  el('imagesGrid').innerHTML = '<div class="images-empty">Generating prompts...</div>';

  btn.disabled = true;
  btn.querySelector('.btn-text').textContent = 'Generating…';
 
  const evtSrc = new EventSource(`${API_BASE_URL}/stream?theme=${encodeURIComponent(theme)}`);
 
  evtSrc.addEventListener('progress', ev => {
    let d; try { d = JSON.parse(ev.data); } catch(e) { console.error('JSON parse error', e, ev.data); return; }
    el('statusLabel').textContent = d.label || '';
    markStepActive(d.step);
  });

  evtSrc.addEventListener('world', ev => {
    let d; try { d = JSON.parse(ev.data); } catch(e) { console.error('JSON parse error', e, ev.data); return; }
    currentWorldId = d.id;
    renderWorld(d);
    markStepDone('world');
  });
 Riverside
  evtSrc.addEventListener('geography', ev => {
    let d; try { d = JSON.parse(ev.data); } catch(e) { console.error('JSON parse error', e, ev.data); return; }
    renderGeography(d);
    markStepDone('geography');
  });

  evtSrc.addEventListener('world_map', ev => {
    let d; try { d = JSON.parse(ev.data); } catch(e) { console.error('JSON parse error', e, ev.data); return; }
    if (d.image_url) {
      el('worldMapContainer').innerHTML = `<img src="${d.image_url}" alt="AI World Map" style="width:100%; height:auto; display:block; border-radius:12px;"/>`;
    } else if (d.svg) {
      el('worldMapContainer').innerHTML = d.svg;
    }
  });

  evtSrc.addEventListener('civilizations', ev => {
    let d; try { d = JSON.parse(ev.data); } catch(e) { console.error('JSON parse error', e, ev.data); return; }
    renderCivilizations(d);
    markStepDone('civilizations');
  });

  evtSrc.addEventListener('politics', ev => {
    let d; try { d = JSON.parse(ev.data); } catch(e) { console.error('JSON parse error', e, ev.data); return; }
    renderPolitics(d);
    markStepDone('politics');
  });

  evtSrc.addEventListener('lore', ev => {
    let d; try { d = JSON.parse(ev.data); } catch(e) { console.error('JSON parse error', e, ev.data); return; }
    renderLore(d);
    markStepDone('lore');
  });

  evtSrc.addEventListener('quests', ev => {
    let d; try { d = JSON.parse(ev.data); } catch(e) { console.error('JSON parse error', e, ev.data); return; }
    renderQuests(d);
    markStepDone('quests');
  });

  evtSrc.addEventListener('level', ev => {
    let d; try { d = JSON.parse(ev.data); } catch(e) { console.error('JSON parse error', e, ev.data); return; }
    renderLevel(d);
    markStepDone('level');
  });

  evtSrc.addEventListener('image_prompts', ev => {
    let d; try { d = JSON.parse(ev.data); } catch(e) { console.error('JSON parse error', e, ev.data); return; }
    renderImagePrompts(d);

    const gpuLabel = el('gpuInfoTitle');
    const bIcon = el('gpuIcon');
    const bLbl = el('gpuLabel');
    if (d.gpu_available) {
      gpuLabel.textContent = '✅ NVIDIA NIM Ready (SD3 Medium enabled)';
      gpuLabel.style.color = 'var(--success)';
      bIcon.textContent = '🟢';
      bLbl.textContent = 'Stable Diffusion 3 Medium Enabled';
    } else {
      gpuLabel.textContent = '⚠️ Generating Prompts Only (API Key missing)';
      gpuLabel.style.color = 'var(--warning)';
      bIcon.textContent = '🟡';
      bLbl.textContent = 'Local Fallback Mode';
    }
    markStepDone('image_prompts');
  });



  evtSrc.addEventListener('done', ev => {
    let d; try { d = JSON.parse(ev.data); } catch(e) { console.error('JSON parse error', e, ev.data); return; }
    generatedWorldData = d.world_data;
    evtSrc.close();
    el('statusLabel').textContent = '✅ Generation complete!';
    el('progressBar').style.width = '100%';
    btn.disabled = false;
    btn.querySelector('.btn-text').textContent = 'Generate World';
    el('actionBar').classList.remove('hidden');
  });

  evtSrc.addEventListener('error', ev => {
    try {
      let d; try { d = JSON.parse(ev.data); } catch(e) { console.error('JSON parse error', e, ev.data); return; }
      showError(d.message || 'Generation failed. Check your API key and try again.');
    } catch {
      showError('Connection error. Make sure the server is running.');
    }
    evtSrc.close();
    btn.disabled = false;
    btn.querySelector('.btn-text').textContent = 'Generate World';
  });

  evtSrc.onerror = () => {
    if (evtSrc.readyState === EventSource.CLOSED) return;
    evtSrc.close();
    showError('Lost connection to server.');
    btn.disabled = false;
    btn.querySelector('.btn-text').textContent = 'Generate World';
  };
});
