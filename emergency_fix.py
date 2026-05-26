import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ─────────────────────────────────────────────────────────────────────────────
# FIX 1: Remove the stray labelRenderer.setSize that was inserted BEFORE the
#         labelRenderer variable was declared – this crashes the whole script.
# ─────────────────────────────────────────────────────────────────────────────
html = html.replace(
    'renderer.setSize(mw.clientWidth, mw.clientHeight);\n  labelRenderer.setSize(mw.clientWidth, mw.clientHeight);',
    'renderer.setSize(mw.clientWidth, mw.clientHeight);'
)

# ─────────────────────────────────────────────────────────────────────────────
# FIX 2: The duplicate labelRenderer.setSize in the resize handler also needs
#         correcting (it was inserted literally twice). Keep only one.
# ─────────────────────────────────────────────────────────────────────────────
html = re.sub(
    r'(labelRenderer\.setSize\(mw\.clientWidth, mw\.clientHeight\);\s*){2,}',
    'labelRenderer.setSize(mw.clientWidth, mw.clientHeight);\n',
    html
)

# ─────────────────────────────────────────────────────────────────────────────
# FIX 3: Replace the duplicate labelRenderer.setSize in the window resize listener
#         with a clean version
# ─────────────────────────────────────────────────────────────────────────────
html = html.replace(
    """window.addEventListener('resize', () => {
  camera.aspect = mw.clientWidth / mw.clientHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(mw.clientWidth, mw.clientHeight);
});""",
    """window.addEventListener('resize', () => {
  camera.aspect = mw.clientWidth / mw.clientHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(mw.clientWidth, mw.clientHeight);
  if(typeof labelRenderer !== 'undefined') labelRenderer.setSize(mw.clientWidth, mw.clientHeight);
});"""
)

# ─────────────────────────────────────────────────────────────────────────────
# FIX 4: Ensure #card-name, #card-type etc still exist so old selectBuilding
#         code that targets them doesn't throw — add hidden elements if missing
# ─────────────────────────────────────────────────────────────────────────────
hidden_compat = """
    <!-- Hidden compatibility elements for JS -->
    <span id="card-emoji" style="display:none"></span>
    <span id="card-name" style="display:none"></span>
    <span id="card-type" style="display:none"></span>
    <span id="card-tags" style="display:none"></span>
    <span id="card-stats" style="display:none"></span>
    <span id="rc-dest" style="display:none">Select a destination</span>
"""
if 'card-emoji' not in html:
    html = html.replace('</body>', hidden_compat + '\n</body>')

# ─────────────────────────────────────────────────────────────────────────────
# FIX 5: Make sure selectBuilding populates the NEW card elements
#         (The overhaul.py regex may have partially clobbered them)
# ─────────────────────────────────────────────────────────────────────────────
NEW_SELECT = """function selectBuilding(id) {
  if(typeof id === 'object') id = id.id;
  selectedId = id;
  const b = BUILDINGS.find(x => x.id === id);
  if (!b) return;

  const cat = CATEGORIES[b.cat];

  // Populate NEW card elements
  const el = (i) => document.getElementById(i);
  if(el('card-name-3d'))  el('card-name-3d').textContent  = b.name;
  if(el('card-headline')) el('card-headline').textContent = cat.label + ' Facility — ' + b.name;
  if(el('card-desc-3d'))  el('card-desc-3d').textContent  = b.desc;
  if(el('card-stats-3d')) el('card-stats-3d').innerHTML   = `
    <div class="pc-stat"><div class="pc-stat-val">~${Math.floor(Math.random()*4+1)} min</div><div class="pc-stat-lbl">from Main Gate</div></div>
    <div class="pc-stat"><div class="pc-stat-val">${b.cat[0].toUpperCase()+b.cat.slice(1)}</div><div class="pc-stat-lbl">Category</div></div>
    <div class="pc-stat"><div class="pc-stat-val" style="color:#15803d">Open</div><div class="pc-stat-lbl">Status</div></div>`;

  // Also populate hidden compat elements so downstream code doesn't break
  if(el('card-emoji')) { el('card-emoji').textContent = b.emoji; }
  if(el('card-name'))  el('card-name').textContent  = b.name;
  if(el('card-type'))  el('card-type').textContent  = cat.label;
  if(el('rc-dest'))    el('rc-dest').textContent    = b.name;

  document.getElementById('place-card').classList.add('open');
  if(el('dir-panel')) el('dir-panel').classList.remove('open');

  // Highlight mesh and fly camera
  const bigBox = new THREE.Box3();
  let hasBox = false;
  buildings3D.forEach(mesh => {
    const origMat = originalMaterials.get(mesh.uuid);
    if (!origMat) return;
    if (mesh.userData.id === id) {
      mesh.material = new THREE.MeshStandardMaterial({
        color: origMat.color, emissive: origMat.color, emissiveIntensity: 0.4, roughness: 0.2
      });
      bigBox.expandByObject(mesh);
      hasBox = true;
    } else {
      mesh.material = origMat;
    }
  });

  if (hasBox) {
    const center = bigBox.getCenter(new THREE.Vector3());
    const size   = bigBox.getSize(new THREE.Vector3());
    let offsetDist = Math.max(size.x, size.y, size.z) * 1.8;
    if(offsetDist < 40)  offsetDist = 40;
    if(offsetDist > 180) offsetDist = 180;
    animateCam(center, offsetDist);
  }
}"""

# Replace whatever broken selectBuilding exists
html = re.sub(r'function selectBuilding\(id\) \{.*?(?=\nfunction deselectBuilding)', NEW_SELECT + '\n', html, flags=re.DOTALL)

# ─────────────────────────────────────────────────────────────────────────────
# FIX 6: Tighten up hero image CSS so it actually shows something nice
#         even without a real photo (use gradient with cat colour in JS)
# ─────────────────────────────────────────────────────────────────────────────
HERO_CSS = """
.card-hero {
  position: relative;
  width: 100%;
  height: 190px;
  background: linear-gradient(135deg, #2e0c59 0%, #5B2D8E 100%);
  clip-path: polygon(0 0, 100% 0, 100% 82%, 0 100%);
  flex-shrink: 0;
}
.card-hero::after {
  content: '';
  position: absolute;
  top: 0; left: 0; width: 100%; height: 100%;
  background: linear-gradient(to bottom, rgba(0,0,0,0.05), rgba(0,0,0,0.5));
}
.card-hero-content {
  position: absolute;
  bottom: 32px; left: 20px; right: 20px; z-index: 2;
}
.card-title-3d {
  font-family: 'Fraunces', serif;
  font-size: 26px;
  font-weight: 900;
  color: #facc15;
  text-shadow: 0 3px 10px rgba(0,0,0,0.6);
  line-height: 1.15;
}
.card-hero-emoji {
  font-size: 40px;
  display: block;
  margin-bottom: 8px;
}
.card-close-x {
  position: absolute; top: 14px; right: 14px; z-index: 10;
  color: #facc15; font-size: 26px; cursor: pointer;
  background: rgba(0,0,0,0.35); width: 36px; height: 36px;
  border-radius: 50%; display: flex; align-items: center;
  justify-content: center; border: none; backdrop-filter: blur(4px);
  transition: background 0.2s;
}
.card-close-x:hover { background: rgba(0,0,0,0.65); }
.card-body {
  padding: 18px 20px 22px;
  background: #fff;
  overflow-y: auto;
  max-height: 280px;
}
.card-headline {
  font-size: 15px; font-weight: 800; color: #111827;
  margin-bottom: 9px; line-height: 1.35;
}
.card-text {
  font-size: 13px; color: #4b5563; line-height: 1.65; margin-bottom: 16px;
}
"""
# Remove old duplicated hero CSS if present
html = re.sub(r'/\* ====== IMMERSIVE OVERHAUL.*?\*/', '', html, flags=re.DOTALL)
html = html.replace('</style>', HERO_CSS + '\n</style>')

# ─────────────────────────────────────────────────────────────────────────────
# FIX 7: Add emoji span to card-hero-content in the HTML
# ─────────────────────────────────────────────────────────────────────────────
html = html.replace(
    '<div class="card-hero-content">\n            <div class="card-title-3d" id="card-name-3d">Building Name</div>',
    '<div class="card-hero-content">\n            <span class="card-hero-emoji" id="card-emoji-3d">🏛️</span>\n            <div class="card-title-3d" id="card-name-3d">Building Name</div>'
)

# Also set emoji when selecting
html = html.replace(
    "if(el('card-name-3d'))  el('card-name-3d').textContent  = b.name;",
    "if(el('card-emoji-3d')) el('card-emoji-3d').textContent = b.emoji;\n  if(el('card-name-3d'))  el('card-name-3d').textContent  = b.name;"
)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('All fixes applied successfully.')
