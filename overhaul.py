import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. ADD CSS2D SCRIPT
if 'CSS2DRenderer' not in html:
    html = html.replace('</head>', '<script src="https://unpkg.com/three@0.128.0/examples/js/renderers/CSS2DRenderer.js"></script>\n</head>')

# 2. CSS OVERHAUL
# Make app full screen, sidebar floating, place-card redesign
css_overhaul = """
/* ====== IMMERSIVE OVERHAUL ====== */
#app { display: block; width: 100vw; height: 100vh; overflow: hidden; }
#map-wrap { position: absolute; top: 0; left: 0; width: 100vw; height: 100vh; z-index: 1; }
#sidebar { position: fixed; top: 0; left: 0; height: 100vh; z-index: 5000; transform: translateX(-100%); transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1); box-shadow: 10px 0 30px rgba(0,0,0,0.3); }
#sidebar.open { transform: translateX(0); }
#topbar, #feature-strip, #quick-bar { display: none !important; }

#menu-toggle { position: absolute; top: 20px; left: 20px; z-index: 4000; width: 48px; height: 48px; border-radius: 50%; background: var(--white); border: none; box-shadow: var(--shadow-lg); cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 24px; color: var(--cu-purple); transition: transform 0.2s; }
#menu-toggle:hover { transform: scale(1.05); }

/* Place Card The Länd Style */
#place-card { width: 360px; max-width: 90vw; background: var(--white); border-radius: 16px; overflow: hidden; box-shadow: 0 20px 50px rgba(0,0,0,0.3); padding: 0; bottom: auto; top: 50%; left: 50%; transform: translate(-50%, -50%) scale(0.9); opacity: 0; pointer-events: none; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); z-index: 5000; display: flex; flex-direction: column; }
#place-card.open { transform: translate(-50%, -50%) scale(1); opacity: 1; pointer-events: auto; }
.pc-handle, .pc-top, .pc-desc { display: none; } /* Hide old stuff */

.card-hero { position: relative; width: 100%; height: 200px; background: url('https://images.unsplash.com/photo-1541339907198-e08756dedf3f?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80'); background-size: cover; background-position: center; clip-path: polygon(0 0, 100% 0, 100% 85%, 0 100%); }
.card-hero::after { content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: linear-gradient(to bottom, rgba(0,0,0,0.1), rgba(0,0,0,0.7)); }
.card-hero-content { position: absolute; bottom: 30px; left: 20px; right: 20px; z-index: 2; }
.card-title-3d { font-family: 'Fraunces', serif; font-size: 32px; font-weight: 900; color: #facc15; text-shadow: 0 4px 12px rgba(0,0,0,0.5); line-height: 1.1; margin-bottom: 5px; }

.card-close-x { position: absolute; top: 15px; right: 15px; z-index: 10; color: #facc15; font-size: 28px; cursor: pointer; background: rgba(0,0,0,0.3); width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; border: none; backdrop-filter: blur(4px); transition: background 0.2s; }
.card-close-x:hover { background: rgba(0,0,0,0.6); }

.card-body { padding: 20px 24px 24px; background: var(--white); margin-top: -10px; }
.card-headline { font-size: 18px; font-weight: 800; color: var(--text); margin-bottom: 12px; line-height: 1.3; }
.card-text { font-size: 13px; color: var(--text-2); line-height: 1.6; margin-bottom: 20px; }

/* Floating CSS2D Labels */
.floating-label { background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(4px); padding: 8px 16px; border-radius: 99px; font-family: 'Outfit', sans-serif; font-size: 13px; font-weight: 700; color: #1f2937; box-shadow: 0 4px 12px rgba(0,0,0,0.15); pointer-events: none; white-space: nowrap; transition: transform 0.2s, opacity 0.2s; border: 1px solid rgba(255,255,255,0.5); }
.floating-label.hidden { opacity: 0; transform: scale(0.8) translateY(10px); }
.floating-label::after { content: ''; position: absolute; bottom: -6px; left: 50%; transform: translateX(-50%); border-width: 6px 6px 0; border-style: solid; border-color: rgba(255, 255, 255, 0.95) transparent transparent transparent; }
"""
html = html.replace('</style>', css_overhaul + '\n</style>')

# 3. HTML OVERHAUL
# Add menu toggle, rebuild place-card
menu_btn = '<button id="menu-toggle" onclick="document.getElementById(\'sidebar\').classList.toggle(\'open\')">☰</button>'
html = html.replace('<div id="map-wrap">', f'<div id="map-wrap">\n      {menu_btn}')

place_card_new = """      <!-- Place card Redesign -->
      <div id="place-card">
        <div class="card-hero">
          <button class="card-close-x" onclick="deselectBuilding()">×</button>
          <div class="card-hero-content">
            <div class="card-title-3d" id="card-name-3d">Building Name</div>
          </div>
        </div>
        <div class="card-body">
          <div class="card-headline" id="card-headline">A stunning panorama of excellence.</div>
          <div class="card-text" id="card-desc-3d">Description goes here.</div>
          <div class="pc-stats" id="card-stats-3d"></div>
          <div class="pc-actions" style="margin-top:20px;">
            <button class="pc-btn pc-btn-primary" id="btn-directions-3d" onclick="if(selectedId) { getDirections(BUILDINGS.find(b=>b.id===selectedId)); }">📍 Get Directions</button>
            <button class="pc-btn pc-btn-secondary" id="btn-fav" style="background:#f3f4f6; color:#1f2937;">⭐ Save</button>
          </div>
        </div>
      </div>"""
html = re.sub(r'<!-- Place card -->.*?</div>\s*</div>\s*</div>', place_card_new, html, flags=re.DOTALL)


# 4. JS OVERHAUL
# Background color to deep royal purple
html = html.replace("scene.background = new THREE.Color('#cfe8cc');", "scene.background = new THREE.Color('#2e0c59');")
html = html.replace("scene.fog = new THREE.FogExp2('#cfe8cc', 0.002);", "scene.fog = new THREE.FogExp2('#2e0c59', 0.0015);")
# Tone mapping exposure tweak
html = html.replace("renderer.toneMappingExposure = 1.1;", "renderer.toneMappingExposure = 0.9;")
# Adjust lighting for purple sky
html = html.replace("const hemiLight = new THREE.HemisphereLight(0xffffff, 0x8d8d8d, 0.6);", "const hemiLight = new THREE.HemisphereLight(0x2e0c59, 0xe8f4e5, 0.8);")


# CSS2DRenderer Init
css2d_init = """// =====================================================
// CSS2D RENDERER (FLOATING LABELS)
// =====================================================
const labelRenderer = new THREE.CSS2DRenderer();
labelRenderer.setSize(mw.clientWidth, mw.clientHeight);
labelRenderer.domElement.style.position = 'absolute';
labelRenderer.domElement.style.top = '0px';
labelRenderer.domElement.style.pointerEvents = 'none';
labelRenderer.domElement.style.zIndex = '100';
mw.appendChild(labelRenderer.domElement);

const htmlLabels = [];
"""
html = html.replace("const oldCanvas = document.getElementById('map-canvas');", css2d_init + "\nconst oldCanvas = document.getElementById('map-canvas');")

# CSS2DRenderer Resize
html = html.replace("renderer.setSize(mw.clientWidth, mw.clientHeight);", "renderer.setSize(mw.clientWidth, mw.clientHeight);\n  labelRenderer.setSize(mw.clientWidth, mw.clientHeight);")

# Add labels during traverse
label_logic = """
        const catColor = getCatColor(matchedData.cat);
        
        // Add HTML Label
        if (!htmlLabels.find(l => l.id === matchedData.id)) {
          const div = document.createElement('div');
          div.className = 'floating-label';
          div.textContent = matchedData.name.split(' ')[0] + (matchedData.name.split(' ')[1] ? ' ' + matchedData.name.split(' ')[1] : '');
          
          const label = new THREE.CSS2DObject(div);
          
          // Compute bounding box to place label on top
          const box = new THREE.Box3().setFromObject(child);
          const size = box.getSize(new THREE.Vector3());
          label.position.set(0, size.y + 15, 0); // Hover above
          
          child.add(label);
          htmlLabels.push({ id: matchedData.id, object: label, div: div });
        }
"""
html = html.replace("const catColor = getCatColor(matchedData.cat);", label_logic)

# Render loop update for labelRenderer
html = html.replace("renderer.render(scene, camera);", "renderer.render(scene, camera);\n  labelRenderer.render(scene, camera);")

# 5. Fix Place Card populating
select_replace = """document.getElementById('card-name-3d').textContent = b.name;
  document.getElementById('card-headline').textContent = cat.label + ' Facility';
  document.getElementById('card-desc-3d').textContent = b.desc;
  document.getElementById('card-stats-3d').innerHTML = `
    <div class="pc-stat"><div class="pc-stat-val">~${Math.floor(Math.random()*4+1)} min</div><div class="pc-stat-lbl">from Gate</div></div>
    <div class="pc-stat"><div class="pc-stat-val">${b.cat[0].toUpperCase()+b.cat.slice(1)}</div><div class="pc-stat-lbl">Category</div></div>
  `;
  document.getElementById('place-card').classList.add('open');"""
html = re.sub(r"document\.getElementById\('dir-panel'\)\.classList\.remove\('open'\);.*?document\.getElementById\('place-card'\)\.classList\.add\('open'\);", select_replace, html, flags=re.DOTALL)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Redesign complete.")
