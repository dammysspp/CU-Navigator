import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# CSS insertion
css_modal = """
/* ====== UNIVERSAL MODAL ====== */
.modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 8000; display: flex; align-items: center; justify-content: center; opacity: 0; pointer-events: none; transition: opacity 0.2s; backdrop-filter: blur(3px); }
.modal-overlay.open { opacity: 1; pointer-events: auto; }
.modal-box { background: var(--white); width: 90%; max-width: 400px; max-height: 85vh; border-radius: var(--radius); box-shadow: var(--shadow-lg); display: flex; flex-direction: column; transform: translateY(20px); transition: transform 0.2s; overflow: hidden; }
.modal-overlay.open .modal-box { transform: translateY(0); }
.modal-header { padding: 16px 20px; border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; }
.modal-title { font-size: 16px; font-weight: 700; color: var(--cu-purple); }
.modal-close { background: none; border: none; font-size: 24px; color: var(--text-muted); cursor: pointer; line-height: 1; }
.modal-body { padding: 20px; overflow-y: auto; }
.dir-cat { margin-bottom: 15px; }
.dir-cat-title { font-size: 12px; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 8px; }
.dir-item { display: flex; align-items: center; gap: 10px; padding: 10px; border-radius: var(--radius-sm); cursor: pointer; transition: background 0.15s; }
.dir-item:hover { background: var(--surface); }
.dir-ico { width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 15px; }
.dir-info { display: flex; flex-direction: column; }
.dir-name { font-size: 13px; font-weight: 600; color: var(--text); }
.fav-btn { padding: 6px 12px; background: #f3f4f6; border-radius: 99px; font-size: 11px; font-weight: 600; color: #4b5563; border: none; cursor: pointer; margin-left: auto; transition: all 0.2s; }
.fav-btn.active { background: #fef08a; color: #854d0e; }
.generic-content { font-size: 14px; color: var(--text-2); line-height: 1.5; text-align: center; padding: 20px 0; }
"""
html = html.replace('</style>', css_modal + '\n</style>')

# HTML insertion
html_modal = """
<!-- UNIVERSAL MODAL -->
<div id="univ-modal" class="modal-overlay">
  <div class="modal-box">
    <div class="modal-header">
      <div class="modal-title" id="modal-title">Modal</div>
      <button class="modal-close" onclick="closeModal()">×</button>
    </div>
    <div class="modal-body" id="modal-body"></div>
  </div>
</div>
"""
html = html.replace('<div id="toast"></div>', html_modal + '\n<div id="toast"></div>')

# Place Card Button Modification
html = html.replace('<button class="pc-btn pc-btn-secondary" id="btn-info">ℹ️ Info</button>', 
'<button class="pc-btn pc-btn-secondary" id="btn-fav">⭐ Save</button>')

# JS insertion
js_additions = """
// =====================================================
// PWA INSTALL (DOWNLOAD OFFLINE)
// =====================================================
let deferredPrompt;
window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault();
  deferredPrompt = e;
});

function promptInstall() {
  if (deferredPrompt) {
    deferredPrompt.prompt();
    deferredPrompt.userChoice.then((choiceResult) => {
      if (choiceResult.outcome === 'accepted') {
        showToast('✅ Installing CU Navigator...');
      }
      deferredPrompt = null;
    });
  } else {
    showToast('App is already installed or not supported on this browser. Try "Add to Home Screen" from the browser menu.');
  }
}

// =====================================================
// MODAL SYSTEM
// =====================================================
const modalOverlay = document.getElementById('univ-modal');
const modalTitle = document.getElementById('modal-title');
const modalBody = document.getElementById('modal-body');

function openModal(title, contentHTML) {
  modalTitle.textContent = title;
  modalBody.innerHTML = contentHTML;
  modalOverlay.classList.add('open');
}

function closeModal() {
  modalOverlay.classList.remove('open');
}

modalOverlay.addEventListener('click', (e) => {
  if (e.target === modalOverlay) closeModal();
});

// =====================================================
// DIRECTORY
// =====================================================
function openDirectory() {
  let html = '';
  for (const catKey in CATEGORIES) {
    const blds = BUILDINGS.filter(b => b.cat === catKey);
    if(blds.length === 0) continue;
    const cat = CATEGORIES[catKey];
    html += `<div class="dir-cat"><div class="dir-cat-title" style="color:${cat.color}">${cat.label}</div>`;
    blds.forEach(b => {
      html += `<div class="dir-item" onclick="closeModal(); selectBuilding('${b.id}');">
        <div class="dir-ico" style="background:${cat.bg}">${b.emoji}</div>
        <div class="dir-info"><div class="dir-name">${b.name}</div></div>
      </div>`;
    });
    html += `</div>`;
  }
  openModal('Campus Directory', html);
}

// =====================================================
// FAVOURITES
// =====================================================
let favourites = JSON.parse(localStorage.getItem('cu_favs') || '[]');

function toggleFavourite(id) {
  if (favourites.includes(id)) {
    favourites = favourites.filter(f => f !== id);
    showToast('Removed from Favourites');
  } else {
    favourites.push(id);
    showToast('⭐ Saved to Favourites');
  }
  localStorage.setItem('cu_favs', JSON.stringify(favourites));
  updateFavButton(id);
}

function updateFavButton(id) {
  const btn = document.getElementById('btn-fav');
  if (favourites.includes(id)) {
    btn.classList.add('active');
    btn.innerHTML = '⭐ Saved';
  } else {
    btn.classList.remove('active');
    btn.innerHTML = '⭐ Save';
  }
}

document.getElementById('btn-fav').addEventListener('click', () => {
  if(selectedId) toggleFavourite(selectedId);
});

// Inject updateFavButton into selectBuilding
const oldSelectBuilding = selectBuilding;
selectBuilding = function(id) {
  oldSelectBuilding(id);
  if(selectedId) updateFavButton(selectedId);
};

function openFavourites() {
  if (favourites.length === 0) {
    openModal('Favourites', '<div class="generic-content">You have no saved places yet.<br><br>Click the ⭐ Save button on any building card to add it here.</div>');
    return;
  }
  let html = '<div class="dir-cat">';
  favourites.forEach(id => {
    const b = BUILDINGS.find(x => x.id === id);
    if(b) {
      const cat = CATEGORIES[b.cat];
      html += `<div class="dir-item" onclick="closeModal(); selectBuilding('${b.id}');">
        <div class="dir-ico" style="background:${cat.bg}">${b.emoji}</div>
        <div class="dir-info"><div class="dir-name">${b.name}</div></div>
      </div>`;
    }
  });
  html += '</div>';
  openModal('Your Saved Places', html);
}

// =====================================================
// 2D / 3D TOGGLE
// =====================================================
let is2D = false;
document.querySelector('.mc-pill').addEventListener('click', function() {
  is2D = !is2D;
  this.textContent = is2D ? '3D' : '2D';
  if (is2D) {
    controls.maxPolarAngle = 0;
    controls.minPolarAngle = 0;
    animateCam(controls.target, 200); 
    showToast('Switched to 2D Top-Down View');
  } else {
    controls.maxPolarAngle = Math.PI / 2 - 0.01;
    controls.minPolarAngle = 0;
    animateCam(controls.target, 120);
    showToast('Switched to 3D View');
  }
});

// =====================================================
// EXPLORE (CINEMATIC TOUR)
// =====================================================
let tourInterval;
function startExploreTour() {
  showToast('🚁 Starting Campus Tour...');
  deselectBuilding();
  
  let i = 0;
  const tourBuildings = [...BUILDINGS].sort(() => 0.5 - Math.random()).slice(0, 3);
  
  function nextStop() {
    if (i >= tourBuildings.length) {
      showToast('Tour Complete! Feel free to explore.');
      return;
    }
    selectBuilding(tourBuildings[i].id);
    i++;
    tourInterval = setTimeout(nextStop, 5000);
  }
  
  nextStop();
}

renderer.domElement.addEventListener('pointerdown', () => {
  if(tourInterval) { clearTimeout(tourInterval); tourInterval = null; }
});

// =====================================================
// WIRE UP THE DYSFUNCTIONAL BUTTONS
// =====================================================
document.querySelectorAll('.nav-item, .tb-link, .mn-item, .sb-help').forEach(btn => {
  const text = btn.textContent || '';
  if (text.includes('Directory')) {
    btn.onclick = openDirectory;
  } else if (text.includes('Explore')) {
    btn.onclick = startExploreTour;
  } else if (text.includes('Favourites')) {
    btn.onclick = openFavourites;
  } else if (text.includes('Offline Maps')) {
    btn.onclick = promptInstall;
  } else if (text.includes('Settings')) {
    btn.onclick = () => openModal('Settings', '<div class="generic-content">⚙️ Settings menu is coming in v2.0.<br><br>Features will include Dark Mode, Map Themes, and Accessibility toggles.</div>');
  } else if (text.includes('Events')) {
    btn.onclick = () => openModal('Campus Events', '<div class="generic-content">📅 No upcoming events scheduled for this week.</div>');
  } else if (text.includes('Help')) {
    btn.onclick = () => openModal('Help & Resources', '<div class="generic-content">Need assistance navigating campus?<br><br>📞 Security: 0800-CU-SECURE<br>🚑 Medical: 0800-CU-CLINIC<br>📧 Support: nav@covenantuniversity.edu.ng<br><br><button class="pc-btn pc-btn-primary" style="margin-top:15px;" onclick="promptInstall()">⬇️ Download App for Offline</button></div>');
  }
});
"""

# Only inject if not already injected
if "MODAL SYSTEM" not in html:
    # Need to insert JS before the </script> closing tag
    html = html.replace('</script>\n</body>', js_additions + '\n</script>\n</body>')
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Injected successfully!")
else:
    print("Already injected.")
