import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ─────────────────────────────────────────────────────────────────────────────
# 1. FIX deselectBuilding to zoom back to overview
# ─────────────────────────────────────────────────────────────────────────────
html = html.replace(
    """function deselectBuilding() {
  selectedId = null;
  document.getElementById('place-card').classList.remove('open');
  buildings3D.forEach(mesh => {
    mesh.material = originalMaterials.get(mesh.uuid);
  });
}""",
    """function deselectBuilding() {
  selectedId = null;
  document.getElementById('place-card').classList.remove('open');
  buildings3D.forEach(mesh => {
    const orig = originalMaterials.get(mesh.uuid);
    if(orig) mesh.material = orig;
  });
  // Zoom back to overview
  animateCam(new THREE.Vector3(0, 0, 0), 200);
}"""
)

# ─────────────────────────────────────────────────────────────────────────────
# 2. WAYPOINT CSS
# ─────────────────────────────────────────────────────────────────────────────
waypoint_css = """
/* ====== WAYPOINT / ROUTING PANEL ====== */
#nav-panel {
  position: fixed;
  top: 0; left: -380px;
  width: 360px; max-width: 93vw;
  height: 100vh;
  background: #fff;
  box-shadow: 4px 0 30px rgba(0,0,0,0.22);
  z-index: 5500;
  display: flex; flex-direction: column;
  transition: left 0.35s cubic-bezier(0.4,0,0.2,1);
  overflow: hidden;
}
#nav-panel.open { left: 0; }

.np-header {
  background: linear-gradient(135deg, #2e0c59 0%, #5B2D8E 100%);
  padding: 20px 18px 16px;
  color: #fff;
  flex-shrink: 0;
}
.np-title { font-size: 14px; font-weight: 700; opacity: 0.75; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 14px; }
.np-close { position: absolute; top: 16px; right: 16px; background: rgba(255,255,255,0.15); border: none; color: #fff; width: 32px; height: 32px; border-radius: 50%; font-size: 20px; cursor: pointer; display:flex;align-items:center;justify-content:center; }
.np-close:hover { background: rgba(255,255,255,0.3); }

.np-input-row { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }
.np-dot { width: 12px; height: 12px; border-radius: 50%; flex-shrink: 0; }
.np-dot.green  { background: #22c55e; }
.np-dot.purple { background: #facc15; }
.np-dot.line   { width: 2px; height: 20px; background: rgba(255,255,255,0.3); border-radius: 2px; margin-left: 5px; }
.np-field {
  flex: 1; background: rgba(255,255,255,0.15);
  border: 1px solid rgba(255,255,255,0.25); border-radius: 8px;
  padding: 9px 12px; color: #fff; font-size: 13px;
  font-family: 'Outfit', sans-serif; outline: none;
  cursor: pointer;
}
.np-field::placeholder { color: rgba(255,255,255,0.55); }
.np-swap { background: rgba(255,255,255,0.15); border: none; color: #facc15; width: 32px; height: 32px; border-radius: 50%; font-size: 16px; cursor: pointer; flex-shrink: 0; }
.np-swap:hover { background: rgba(255,255,255,0.3); }

#np-go-btn {
  width: 100%; padding: 12px; margin-top: 8px;
  background: #facc15; color: #2e0c59;
  border: none; border-radius: 10px;
  font-size: 14px; font-weight: 700;
  font-family: 'Outfit', sans-serif;
  cursor: pointer; transition: opacity 0.2s;
}
#np-go-btn:hover { opacity: 0.85; }

.np-body { flex: 1; overflow-y: auto; padding: 0; }
.np-mode-row { display: flex; gap: 0; border-bottom: 1px solid #e5e7eb; flex-shrink: 0; }
.np-mode-btn { flex: 1; padding: 12px 0; font-size: 20px; text-align: center; background: none; border: none; cursor: pointer; border-bottom: 2px solid transparent; transition: all 0.2s; }
.np-mode-btn.active { border-bottom-color: #5B2D8E; background: #f5f3ff; }

.np-route-summary {
  padding: 16px 18px;
  background: linear-gradient(135deg, #f5f3ff, #ede9fe);
  border-bottom: 1px solid #e5e7eb;
}
.np-eta { font-size: 28px; font-weight: 800; color: #2e0c59; }
.np-dist { font-size: 13px; color: #6b7280; margin-top: 2px; }
.np-start-btn {
  margin-top: 12px; width: 100%; padding: 11px;
  background: #2e0c59; color: #facc15;
  border: none; border-radius: 10px;
  font-size: 14px; font-weight: 700;
  font-family: 'Outfit', sans-serif; cursor: pointer;
}
.np-start-btn:hover { background: #5B2D8E; }

.np-steps { padding: 16px 18px; }
.np-step { display: flex; gap: 12px; margin-bottom: 18px; align-items: flex-start; }
.np-step-num {
  width: 26px; height: 26px; border-radius: 50%;
  background: linear-gradient(135deg, #2e0c59, #5B2D8E);
  color: #facc15; font-size: 11px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; box-shadow: 0 2px 6px rgba(46,12,89,0.3);
}
.np-step-text { font-size: 13px; color: #374151; line-height: 1.5; }
.np-step-dist { font-size: 11px; color: #9ca3af; margin-top: 2px; }

/* Dropdown search list */
.np-search-list {
  position: absolute; z-index: 9999;
  background: #fff; border-radius: 10px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.2);
  max-height: 220px; overflow-y: auto;
  left: 18px; right: 18px;
  display: none;
}
.np-search-list.open { display: block; }
.np-search-item { padding: 10px 14px; cursor: pointer; font-size: 13px; border-bottom: 1px solid #f3f4f6; }
.np-search-item:hover { background: #f5f3ff; }
.np-search-item:last-child { border-bottom: none; }

/* Route line animation */
@keyframes dash-move { to { stroke-dashoffset: -20; } }
"""
html = html.replace('</style>', waypoint_css + '\n</style>')

# ─────────────────────────────────────────────────────────────────────────────
# 3. WAYPOINT PANEL HTML — inject before </body>
# ─────────────────────────────────────────────────────────────────────────────
nav_panel_html = """
<!-- NAVIGATION / WAYPOINT PANEL -->
<div id="nav-panel">
  <div class="np-header">
    <div class="np-title">Get Directions</div>
    <button class="np-close" onclick="closeNavPanel()">×</button>
    <div class="np-input-row">
      <div class="np-dot green"></div>
      <input id="np-from" class="np-field" type="text" placeholder="From: Main Gate" value="Main Gate" readonly
        onclick="openBuildingSearch('np-from')">
    </div>
    <div class="np-input-row">
      <div class="np-dot line"></div>
    </div>
    <div class="np-input-row">
      <div class="np-dot purple"></div>
      <input id="np-to" class="np-field" type="text" placeholder="To: Select destination…" readonly
        onclick="openBuildingSearch('np-to')">
      <button class="np-swap" onclick="swapNavPoints()" title="Swap">⇅</button>
    </div>
    <div id="np-search-list" class="np-search-list"></div>
    <button id="np-go-btn" onclick="calculateRoute()">🗺 Get Directions</button>
  </div>

  <div class="np-mode-row">
    <button class="np-mode-btn active" title="Walking" onclick="setMode('walk',this)">🚶</button>
    <button class="np-mode-btn" title="Cycling" onclick="setMode('bike',this)">🚲</button>
    <button class="np-mode-btn" title="Driving" onclick="setMode('car',this)">🚗</button>
  </div>

  <div class="np-body">
    <div id="np-route-result" style="display:none;">
      <div class="np-route-summary">
        <div class="np-eta" id="np-eta">—</div>
        <div class="np-dist" id="np-dist">Select origin and destination</div>
        <button class="np-start-btn" onclick="startWalkthrough()">▶ Start Navigation</button>
      </div>
      <div class="np-steps" id="np-steps"></div>
    </div>
    <div id="np-empty" style="padding:30px 18px; text-align:center; color:#9ca3af; font-size:13px;">
      Select a starting point and destination to see directions.
    </div>
  </div>
</div>
"""
html = html.replace('</body>', nav_panel_html + '\n</body>')

# ─────────────────────────────────────────────────────────────────────────────
# 4. Also add a floating NAV button on the map (bottom-left)
# ─────────────────────────────────────────────────────────────────────────────
nav_btn_css = """
#open-nav-btn {
  position: absolute;
  bottom: 24px; left: 20px;
  z-index: 4000;
  background: linear-gradient(135deg, #2e0c59, #5B2D8E);
  color: #facc15;
  border: none; border-radius: 99px;
  padding: 12px 22px;
  font-family: 'Outfit', sans-serif;
  font-size: 14px; font-weight: 700;
  cursor: pointer;
  box-shadow: 0 4px 18px rgba(46,12,89,0.45);
  display: flex; align-items: center; gap: 8px;
  transition: transform 0.2s, box-shadow 0.2s;
}
#open-nav-btn:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(46,12,89,0.55); }
"""
html = html.replace('</style>', nav_btn_css + '\n</style>')

if 'open-nav-btn' not in html:
    html = html.replace(
        '<div id="cu-watermark">',
        '<button id="open-nav-btn" onclick="openNavPanel()">📍 Directions</button>\n      <div id="cu-watermark">'
    )

# ─────────────────────────────────────────────────────────────────────────────
# 5. ROUTING JAVASCRIPT
# ─────────────────────────────────────────────────────────────────────────────
routing_js = """
// =====================================================
// OFFLINE WAYPOINT / ROUTING ENGINE
// =====================================================

// Campus path graph — nodes are building IDs, edges are distances in metres
// Distances are approximate real-world walking distances on campus
const CAMPUS_GRAPH = {
  gate:      { senate:180, stadium:320, secondary:380 },
  senate:    { gate:180, library:120, chapel:200, lt1:250, aldc:270, ceds:180 },
  library:   { senate:120, ceds:80, lt1:160, chapel:150, cafeteria:300, clinic:280, cucrid:200 },
  chapel:    { senate:200, library:150, clds:120, cbs:180, aldc:160 },
  aldc:      { chapel:160, senate:270, staffclub:200 },
  staffclub: { aldc:200, lt2:220, ceng:280 },
  lt1:       { senate:250, library:160, lt2:90, ceds:140, cst:200 },
  lt2:       { lt1:90, ceng:120, cst:150 },
  cst:       { lt1:200, lt2:150, ceng:100, ceds:180 },
  ceng:      { lt2:120, cst:100, stadium:200, secondary:280 },
  ceds:      { senate:180, library:80, lt1:140, cst:180, cucrid:160 },
  clds:      { chapel:120, cbs:80 },
  cbs:       { clds:80, chapel:180, cucrid:120, library:200 },
  cucrid:    { cbs:120, library:200, ceds:160, hall1:200 },
  hall1:     { cucrid:200, hall2:80, hall3:150, cafeteria:180 },
  hall2:     { hall1:80, hall3:200, hall4:80, cafeteria:120, clinic:120, atm:100 },
  hall3:     { hall1:150, hall4:200, hall5:80 },
  hall4:     { hall2:80, hall3:200, hall6:80, cafeteria:100, clinic:100 },
  hall5:     { hall3:80, hall6:200, stadium:150 },
  hall6:     { hall5:200, hall4:80, cafeteria:140, stadium:130 },
  cafeteria: { hall1:180, hall2:120, hall4:100, hall6:140, clinic:80, atm:100, bookshop:80 },
  clinic:    { cafeteria:80, hall2:120, hall4:100, atm:120, library:280 },
  atm:       { cafeteria:100, clinic:120, hall2:100, bookshop:50, salon:80 },
  bookshop:  { cafeteria:80, atm:50, salon:60, printing:60 },
  salon:     { bookshop:60, atm:80, printing:50 },
  printing:  { salon:50, bookshop:60, library:200, senate:250 },
  stadium:   { gate:320, ceng:200, hall5:150, hall6:130, secondary:200 },
  secondary: { gate:380, stadium:200, ceng:280 },
};

// Walking speeds (metres/minute)
const SPEEDS = { walk: 80, bike: 300, car: 600 };
let currentMode = 'walk';
let navFromId = 'gate';
let navToId   = null;
let activeSearchField = null;
let routeLine3D = null;
let walkStep = 0;
let walkPath = [];

function setMode(mode, btn) {
  currentMode = mode;
  document.querySelectorAll('.np-mode-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  if(navToId) calculateRoute();
}

function openNavPanel(presetId) {
  document.getElementById('nav-panel').classList.add('open');
  if(presetId) {
    navToId = presetId;
    const b = BUILDINGS.find(x => x.id === presetId);
    if(b) document.getElementById('np-to').value = b.name;
    calculateRoute();
  }
}

function closeNavPanel() {
  document.getElementById('nav-panel').classList.remove('open');
  clearRoute3D();
}

function openBuildingSearch(fieldId) {
  activeSearchField = fieldId;
  const list = document.getElementById('np-search-list');
  list.innerHTML = BUILDINGS.map(b => {
    const cat = CATEGORIES[b.cat];
    return `<div class="np-search-item" onclick="selectNavBuilding('${b.id}', '${b.name.replace(/'/g,"\\'")}')">
      ${b.emoji} ${b.name} <span style="color:${cat.color}; font-size:11px;">(${cat.label})</span>
    </div>`;
  }).join('');
  list.classList.add('open');
}

document.addEventListener('click', e => {
  if(!e.target.closest('#np-search-list') && !e.target.closest('.np-field')) {
    document.getElementById('np-search-list').classList.remove('open');
  }
});

function selectNavBuilding(id, name) {
  document.getElementById('np-search-list').classList.remove('open');
  if(activeSearchField === 'np-from') {
    navFromId = id;
    document.getElementById('np-from').value = name;
  } else {
    navToId = id;
    document.getElementById('np-to').value = name;
  }
  activeSearchField = null;
}

function swapNavPoints() {
  const tmpId   = navFromId;
  const tmpName = document.getElementById('np-from').value;
  navFromId = navToId || 'gate';
  document.getElementById('np-from').value = document.getElementById('np-to').value || 'Main Gate';
  navToId = tmpId;
  document.getElementById('np-to').value = tmpName;
  if(navToId) calculateRoute();
}

// ── Dijkstra shortest path ────────────────────────────────────────────────
function dijkstra(from, to) {
  const dist  = {};
  const prev  = {};
  const queue = new Set(Object.keys(CAMPUS_GRAPH));
  
  queue.forEach(n => { dist[n] = Infinity; prev[n] = null; });
  dist[from] = 0;
  
  while(queue.size > 0) {
    // Pick unvisited node with smallest dist
    let u = null;
    queue.forEach(n => { if(u === null || dist[n] < dist[u]) u = n; });
    if(u === to) break;
    queue.delete(u);
    
    const neighbours = CAMPUS_GRAPH[u] || {};
    for(const v in neighbours) {
      if(!queue.has(v)) continue;
      const alt = dist[u] + neighbours[v];
      if(alt < dist[v]) { dist[v] = alt; prev[v] = u; }
    }
  }
  
  // Reconstruct path
  const path = [];
  let cur = to;
  while(cur) { path.unshift(cur); cur = prev[cur]; }
  return { path, totalDist: Math.round(dist[to]) };
}

// ── Human-readable step directions ───────────────────────────────────────
const COMPASS_HINTS = {
  gate:      'Enter through the Main Gate and proceed inward',
  senate:    'Pass by the iconic Senate Building',
  chapel:    'Walk past the University Chapel',
  library:   'Pass the Centre for Learning Resources (Library)',
  cafeteria: 'Continue past the Main Cafeteria',
  lt1:       'Walk along Lecture Theatre 1 block',
  lt2:       'Continue through the Lecture Theatre 2 corridor',
  cst:       'Pass through the College of Science & Technology',
  ceng:      'Walk through the Engineering corridor',
  stadium:   'Continue along the Sports Complex fence',
  hall1:     'Walk through Shalom Hall area',
  hall2:     'Continue through Deborah Hall',
  clinic:    'Pass by the Medical Centre',
};

function generateSteps(path) {
  const steps = [];
  for(let i = 0; i < path.length; i++) {
    const id = path[i];
    const b  = BUILDINGS.find(x => x.id === id);
    const name = b ? b.name : id;
    
    if(i === 0)              steps.push({ text: `Start at ${name}`, dist: '' });
    else if(i === path.length-1) steps.push({ text: `Arrive at ${name}`, dist: '', final: true });
    else {
      const edgeDist = CAMPUS_GRAPH[path[i-1]][id] || 0;
      steps.push({ text: COMPASS_HINTS[id] || `Continue towards ${name}`, dist: `~${edgeDist}m` });
    }
  }
  return steps;
}

// ── 3D Route Visualisation ────────────────────────────────────────────────
function clearRoute3D() {
  if(routeLine3D) { scene.remove(routeLine3D); routeLine3D = null; }
  startMarker.visible = false;
  endMarker.visible   = false;
}

function drawRoute3D(path) {
  clearRoute3D();
  
  // Collect 3D positions for each building in the path
  const pts = [];
  path.forEach(id => {
    const b = BUILDINGS.find(x => x.id === id);
    if(!b) return;
    
    // Try to get real 3D position from loaded mesh
    const mesh3D = buildings3D.find(m => m.userData.id === id);
    if(mesh3D) {
      const box = new THREE.Box3().setFromObject(mesh3D);
      const c   = box.getCenter(new THREE.Vector3());
      pts.push(new THREE.Vector3(c.x, c.y + 5, c.z));
    } else {
      // Fall back to 2D data scaled to 3D space (x/y are % of campus)
      pts.push(new THREE.Vector3((b.x - 50) * 2, 5, (b.y - 50) * 2));
    }
  });
  
  if(pts.length < 2) return;
  
  // CatmullRom smooth curve through all waypoints
  const curve  = new THREE.CatmullRomCurve3(pts);
  const points = curve.getPoints(80);
  const geo    = new THREE.BufferGeometry().setFromPoints(points);
  const mat    = new THREE.LineDashedMaterial({
    color: 0xfacc15, linewidth: 2,
    dashSize: 4, gapSize: 2,
  });
  routeLine3D = new THREE.Line(geo, mat);
  routeLine3D.computeLineDistances();
  scene.add(routeLine3D);
  
  // Start / End markers
  startMarker.position.copy(pts[0]);
  startMarker.userData.baseY = pts[0].y;
  startMarker.visible = true;
  
  endMarker.position.copy(pts[pts.length - 1]);
  endMarker.userData.baseY = pts[pts.length - 1].y;
  endMarker.visible = true;
  
  // Fly camera to see the whole route
  const box = new THREE.Box3();
  pts.forEach(p => box.expandByPoint(p));
  const center = box.getCenter(new THREE.Vector3());
  const size   = box.getSize(new THREE.Vector3());
  animateCam(center, Math.max(size.x, size.z) * 1.2 + 80);
}

// ── Main route calculation ────────────────────────────────────────────────
function calculateRoute() {
  if(!navFromId || !navToId) {
    showToast('Please select both a starting point and destination.');
    return;
  }
  if(navFromId === navToId) {
    showToast('Starting point and destination are the same!');
    return;
  }
  if(!CAMPUS_GRAPH[navFromId] || !CAMPUS_GRAPH[navToId]) {
    showToast('No route available between these buildings.');
    return;
  }
  
  const { path, totalDist } = dijkstra(navFromId, navToId);
  if(!path.length || totalDist === Infinity) {
    showToast('Could not find a path. Try different buildings.');
    return;
  }
  
  walkPath = path;
  const speed  = SPEEDS[currentMode];
  const minutes = Math.ceil(totalDist / speed);
  const modeEmoji = { walk:'🚶', bike:'🚲', car:'🚗' }[currentMode];
  
  // Update UI
  document.getElementById('np-eta').textContent  = `${modeEmoji} ${minutes} min`;
  document.getElementById('np-dist').textContent = `${totalDist}m · ${path.length - 1} waypoints`;
  
  const steps = generateSteps(path);
  document.getElementById('np-steps').innerHTML = steps.map((s, i) => `
    <div class="np-step">
      <div class="np-step-num" style="${s.final ? 'background:linear-gradient(135deg,#C8A02A,#facc15);color:#2e0c59;' : ''}">${s.final ? '🏁' : i + 1}</div>
      <div>
        <div class="np-step-text">${s.text}</div>
        ${s.dist ? `<div class="np-step-dist">${s.dist}</div>` : ''}
      </div>
    </div>`).join('');
  
  document.getElementById('np-route-result').style.display = 'block';
  document.getElementById('np-empty').style.display        = 'none';
  
  // Draw on 3D map
  drawRoute3D(path);
}

// ── Step-by-step walkthrough ─────────────────────────────────────────────
function startWalkthrough() {
  walkStep = 0;
  showNextStep();
}

function showNextStep() {
  if(walkStep >= walkPath.length) { showToast('🏁 You have arrived!'); return; }
  const id   = walkPath[walkStep];
  const b    = BUILDINGS.find(x => x.id === id);
  if(b) {
    selectBuilding(id);
    showToast(`Step ${walkStep + 1}/${walkPath.length}: ${b.name}`);
  }
  walkStep++;
  if(walkStep < walkPath.length) {
    setTimeout(showNextStep, 4000);
  }
}

// Hook "Get Directions" button in place card to open nav panel with preset
document.getElementById('btn-directions-3d').addEventListener('click', () => {
  if(selectedId) {
    navToId = selectedId;
    const b = BUILDINGS.find(x => x.id === selectedId);
    if(b) document.getElementById('np-to').value = b.name;
    document.getElementById('place-card').classList.remove('open');
    openNavPanel();
    calculateRoute();
  }
});
"""

# Inject before the last </script>
html = html.replace('</script>\n</body>', routing_js + '\n</script>\n</body>')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Waypoint routing engine injected successfully.')
