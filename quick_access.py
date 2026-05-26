import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ─────────────────────────────────────────────────────────────────────────────
# 1. REPLACE Quick Access HTML with a dynamic container
# ─────────────────────────────────────────────────────────────────────────────
OLD_QB = '''    <!-- Desktop quick bar -->
    <div id="quick-bar">
      <div class="qb-head">
        <div class="qb-title">Quick Access</div>
        <div class="qb-sub">Frequently visited places</div>
        <div class="qb-more">View all ›</div>
      </div>
      <div class="qb-row" id="quick-row"></div>
    </div>'''

NEW_QB = '''    <!-- Desktop quick bar -->
    <div id="quick-bar">
      <div class="qb-head">
        <div>
          <div class="qb-title">Quick Access</div>
          <div class="qb-sub">Tap a building to fly there</div>
        </div>
        <button class="qb-view-all" onclick="openDirectory()">View all ›</button>
      </div>
      <div class="qb-row" id="quick-row">
        <div class="qb-loading">Loading buildings from map…</div>
      </div>
    </div>'''

html = html.replace(OLD_QB, NEW_QB)

# ─────────────────────────────────────────────────────────────────────────────
# 2. REDESIGN Quick Access CSS
# ─────────────────────────────────────────────────────────────────────────────
qb_css = """
/* ====== QUICK BAR REDESIGN ====== */
#quick-bar {
  background: var(--white);
  border-top: 1px solid var(--border);
  padding: 10px 16px 12px;
  flex-shrink: 0;
}
.qb-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}
.qb-title { font-size: 13px; font-weight: 700; color: var(--text); }
.qb-sub   { font-size: 11px; color: var(--text-muted); margin-top: 1px; }
.qb-view-all {
  font-size: 12px; font-weight: 600; color: var(--cu-purple);
  background: var(--cu-purple-lite); border: none;
  padding: 5px 12px; border-radius: 99px; cursor: pointer;
  font-family: 'Outfit', sans-serif; transition: all 0.15s;
}
.qb-view-all:hover { background: var(--cu-purple); color: #fff; }

.qb-row {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  scrollbar-width: none;
  padding-bottom: 4px;
}
.qb-row::-webkit-scrollbar { display: none; }

.qb-loading {
  font-size: 12px; color: var(--text-muted);
  padding: 8px 0; font-style: italic;
}

.qb-item {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 10px 14px;
  border-radius: 12px;
  cursor: pointer;
  border: 1.5px solid var(--border);
  background: var(--white);
  transition: all 0.18s;
  min-width: 72px;
  max-width: 88px;
  font-family: 'Outfit', sans-serif;
}
.qb-item:hover {
  border-color: var(--cu-purple);
  background: var(--cu-purple-lite);
  transform: translateY(-2px);
  box-shadow: 0 4px 14px rgba(91,45,142,0.18);
}
.qb-icon-wrap {
  width: 40px; height: 40px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  font-size: 20px;
  transition: transform 0.18s;
}
.qb-item:hover .qb-icon-wrap { transform: scale(1.1); }
.qb-lbl {
  font-size: 10px; font-weight: 600;
  color: var(--text-2); text-align: center; line-height: 1.3;
}
.qb-item.live { border-color: rgba(91,45,142,0.2); }
.qb-cat-badge {
  font-size: 9px; font-weight: 700;
  color: var(--text-muted); text-transform: uppercase;
  letter-spacing: 0.06em;
}
"""

# Remove old qb CSS
html = re.sub(r'\.qb-head\{.*?\}', '', html, flags=re.DOTALL)
html = re.sub(r'\.qb-title\{.*?\}', '', html, flags=re.DOTALL)
html = re.sub(r'\.qb-sub\{.*?\}', '', html, flags=re.DOTALL)
html = re.sub(r'\.qb-more\{.*?\}', '', html, flags=re.DOTALL)
html = re.sub(r'\.qb-row\{.*?\}', '', html, flags=re.DOTALL)
html = re.sub(r'\.qb-item\{.*?\}', '', html, flags=re.DOTALL)
html = re.sub(r'\.qb-icon\{.*?\}', '', html, flags=re.DOTALL)
html = re.sub(r'\.qb-lbl\{.*?\}', '', html, flags=re.DOTALL)
html = html.replace('</style>', qb_css + '\n</style>')

# ─────────────────────────────────────────────────────────────────────────────
# 3. JS: After model loads, rebuild quick-row from ACTUAL loaded buildings3D
# ─────────────────────────────────────────────────────────────────────────────
dynamic_qb_js = """
// =====================================================
// DYNAMIC QUICK ACCESS — built from actual loaded meshes
// =====================================================
function buildQuickAccess() {
  const qRow  = document.getElementById('quick-row');
  const mqRow = document.getElementById('mqrow');
  if (!qRow) return;

  // Deduplicate by building ID (one card per building)
  const seen  = new Set();
  const items = [];

  buildings3D.forEach(mesh => {
    const b = mesh.userData;
    if (!b || !b.id || seen.has(b.id)) return;
    seen.add(b.id);
    items.push(b);
  });

  // Sort: put key campus landmarks first
  const PRIORITY = ['library','chapel','senate','cafeteria','clinic','atm','printing','stadium','lt1','ceng','cst'];
  items.sort((a, b) => {
    const ai = PRIORITY.indexOf(a.id);
    const bi = PRIORITY.indexOf(b.id);
    if (ai === -1 && bi === -1) return 0;
    if (ai === -1) return 1;
    if (bi === -1) return -1;
    return ai - bi;
  });

  // Show max 12 on desktop quick bar
  const desktop = items.slice(0, 12);

  qRow.innerHTML = desktop.map(b => {
    const cat    = CATEGORIES[b.cat] || {};
    const bg     = cat.bg    || 'rgba(91,45,142,0.10)';
    const short  = SHORT_NAMES[b.id] || b.name.split(' ').slice(0, 2).join(' ');
    return `
      <button class="qb-item live" data-id="${b.id}"
        title="${b.name}"
        style="border-color:${(cat.color||'#5B2D8E')}22;">
        <div class="qb-icon-wrap" style="background:${bg}">
          ${b.emoji}
        </div>
        <div class="qb-lbl">${short}</div>
      </button>`;
  }).join('');

  // Wire click
  qRow.querySelectorAll('.qb-item').forEach(btn => {
    btn.addEventListener('click', () => {
      const b = BUILDINGS.find(x => x.id === btn.dataset.id);
      if (b) selectBuilding(b.id);
    });
  });

  // Mobile quick row
  if (mqRow) {
    const mobile = items.slice(0, 8);
    mqRow.innerHTML = mobile.map(b => {
      const cat   = CATEGORIES[b.cat] || {};
      const bg    = cat.bg || 'rgba(91,45,142,0.10)';
      const short = SHORT_NAMES[b.id] || b.name.split(' ')[0];
      return `
        <button class="mq-item" data-id="${b.id}">
          <div style="font-size:22px;background:${bg};border-radius:10px;padding:4px 8px;">${b.emoji}</div>
          <div class="mq-lbl">${short}</div>
        </button>`;
    }).join('');

    mqRow.querySelectorAll('.mq-item').forEach(btn => {
      btn.addEventListener('click', () => selectBuilding(btn.dataset.id));
    });
  }

  console.log(`Quick access built with ${desktop.length} real buildings from the 3D map.`);
}
"""

# Inject after the model loads (after scene.add(model))
html = html.replace(
    '  scene.add(model);\n}, undefined, (error) => {',
    '  scene.add(model);\n\n  // Rebuild quick access from actual 3D building names\n  setTimeout(buildQuickAccess, 100);\n}, undefined, (error) => {'
)

# Inject buildQuickAccess function before </script>
html = html.replace('</script>\n</body>', dynamic_qb_js + '\n</script>\n</body>')

# ─────────────────────────────────────────────────────────────────────────────
# 4. Remove old hardcoded quickDefs JS block entirely
# ─────────────────────────────────────────────────────────────────────────────
html = re.sub(
    r'// =====================================================\n// QUICK ACCESS\n// =====================================================\nconst quickDefs=\[.*?\]\);\n\}',
    '// Quick access is now dynamically built in buildQuickAccess()',
    html,
    flags=re.DOTALL
)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Dynamic quick access rebuilt from 3D building names.')
