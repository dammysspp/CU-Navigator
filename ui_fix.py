import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ─────────────────────────────────────────────────────────────────────────────
# 1. PLACE CARD → RIGHT SIDE PANEL (slide in from right)
# ─────────────────────────────────────────────────────────────────────────────
side_card_css = """
/* ====== SIDE PANEL PLACE CARD ====== */
#place-card {
  position: fixed;
  top: 0;
  right: -380px;
  width: 360px;
  max-width: 90vw;
  height: 100vh;
  background: #fff;
  box-shadow: -8px 0 40px rgba(0,0,0,0.25);
  border-radius: 0;
  overflow-y: auto;
  opacity: 0;
  pointer-events: none;
  transition: right 0.35s cubic-bezier(0.4,0,0.2,1), opacity 0.3s;
  z-index: 5000;
  display: flex !important;
  flex-direction: column;
  transform: none !important;
}
#place-card.open {
  right: 0;
  opacity: 1;
  pointer-events: auto;
}
.card-hero {
  position: relative;
  width: 100%;
  height: 220px;
  background: linear-gradient(135deg, #2e0c59 0%, #5B2D8E 100%);
  clip-path: polygon(0 0, 100% 0, 100% 88%, 0 100%);
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
  bottom: 36px; left: 22px; right: 22px; z-index: 2;
}
.card-hero-emoji { font-size: 40px; display: block; margin-bottom: 8px; }
.card-title-3d {
  font-family: 'Fraunces', serif;
  font-size: 28px;
  font-weight: 900;
  color: #facc15;
  text-shadow: 0 3px 10px rgba(0,0,0,0.6);
  line-height: 1.15;
}
.card-close-x {
  position: absolute; top: 14px; right: 14px; z-index: 10;
  color: #facc15; font-size: 22px; cursor: pointer;
  background: rgba(0,0,0,0.35); width: 34px; height: 34px;
  border-radius: 50%; display: flex; align-items: center;
  justify-content: center; border: none; backdrop-filter: blur(4px);
  font-weight: bold;
}
.card-close-x:hover { background: rgba(0,0,0,0.65); }
.card-body {
  padding: 20px 22px 30px;
  background: #fff;
  flex: 1;
  overflow-y: auto;
}
.card-headline { font-size: 15px; font-weight: 800; color: #111827; margin-bottom: 10px; line-height: 1.35; }
.card-text { font-size: 13px; color: #4b5563; line-height: 1.65; margin-bottom: 18px; }

/* Hide old conflicting rules if any */
.pc-handle { display: none !important; }
.pc-top    { display: none !important; }
.pc-desc   { display: none !important; }
"""
# Remove any previous card CSS blocks that conflict
html = re.sub(r'/\* ====== SIDE PANEL PLACE CARD ======.*?\*/', '', html, flags=re.DOTALL)
html = html.replace('</style>', side_card_css + '\n</style>')

# ─────────────────────────────────────────────────────────────────────────────
# 2. COVENANT UNIVERSITY WATERMARK TEXT on the 3D canvas
#    We'll render it as a large CSS2D object anchored near the model center
# ─────────────────────────────────────────────────────────────────────────────
watermark_css = """
/* ====== CAMPUS WATERMARK ====== */
#cu-watermark {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  font-family: 'Fraunces', serif;
  font-size: clamp(32px, 6vw, 80px);
  font-weight: 900;
  color: rgba(255,255,255,0.08);
  letter-spacing: 0.12em;
  text-transform: uppercase;
  pointer-events: none;
  user-select: none;
  white-space: nowrap;
  z-index: 2;
  text-shadow: 0 0 60px rgba(91,45,142,0.3);
}
"""
html = html.replace('</style>', watermark_css + '\n</style>')

# Inject the watermark div into map-wrap
if 'cu-watermark' not in html:
    html = html.replace(
        '<button id="menu-toggle"',
        '<div id="cu-watermark">COVENANT UNIVERSITY</div>\n      <button id="menu-toggle"'
    )

# ─────────────────────────────────────────────────────────────────────────────
# 3. SHORT LABEL NAMES for the floating bubbles
# ─────────────────────────────────────────────────────────────────────────────
short_name_fn = """
// Short names for floating labels
const SHORT_NAMES = {
  'gate':      'Main Gate',
  'senate':    'Senate Bldg',
  'cucrid':    'CUCRID',
  'cst':       'Sci & Tech',
  'ceng':      'Engineering',
  'cbs':       'Business',
  'clds':      'Leadership',
  'ceds':      'CEDS',
  'lt1':       'LT1',
  'lt2':       'LT2',
  'library':   'Library',
  'chapel':    'Chapel',
  'hall1':     'Shalom Hall',
  'hall2':     'Deborah Hall',
  'hall3':     'Peter Hall',
  'hall4':     'Mary Hall',
  'hall5':     'Joshua Hall',
  'hall6':     'Esther Hall',
  'cafeteria': 'Cafeteria',
  'clinic':    'Medical Ctr',
  'aldc':      'ALDC',
  'atm':       'ATM / Bank',
  'bookshop':  'Bookshop',
  'salon':     'Salon',
  'printing':  'ICT Centre',
  'stadium':   'Stadium',
  'staffclub': 'Guest House',
  'secondary': 'Sec. School',
};
"""
# Insert before the RENDERER SETUP section
html = html.replace(
    '// =====================================================\n// 3D RENDERER SETUP',
    short_name_fn + '\n// =====================================================\n// 3D RENDERER SETUP'
)

# Use SHORT_NAMES in label creation
html = html.replace(
    "div.textContent = matchedData.name.split(' ')[0] + (matchedData.name.split(' ')[1] ? ' ' + matchedData.name.split(' ')[1] : '');",
    "div.textContent = SHORT_NAMES[matchedData.id] || matchedData.name.substring(0, 18);"
)

# ─────────────────────────────────────────────────────────────────────────────
# 4. MENU TOGGLE — make it properly toggle open/close
# ─────────────────────────────────────────────────────────────────────────────
# Already uses classList.toggle — but sidebar has no 'open' class by default, check CSS:
sidebar_toggle_css = """
/* ====== SIDEBAR TOGGLE ====== */
#sidebar {
  position: fixed !important;
  top: 0; left: 0; height: 100vh; z-index: 5000;
  transform: translateX(-100%) !important;
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
  box-shadow: 4px 0 30px rgba(0,0,0,0.3);
}
#sidebar.open { transform: translateX(0) !important; }
#app { display: block; width: 100vw; height: 100vh; overflow: hidden; }
#map-wrap { position: absolute !important; top: 0; left: 0; width: 100vw; height: 100vh; z-index: 1; }
#topbar, #feature-strip, #quick-bar { display: none !important; }
#menu-toggle {
  position: absolute; top: 18px; left: 18px; z-index: 4000;
  width: 46px; height: 46px; border-radius: 50%; background: rgba(255,255,255,0.92);
  border: none; box-shadow: 0 4px 16px rgba(0,0,0,0.2); cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  font-size: 20px; color: #2e0c59; backdrop-filter: blur(8px);
  transition: transform 0.2s, background 0.2s;
}
#menu-toggle:hover { transform: scale(1.08); background: #fff; }
"""
# Remove old overhaul CSS if still present
html = re.sub(r'/\* ====== IMMERSIVE OVERHAUL.*?#mhdr,#msearch,#mqrow,#mnav\{display:none;\}\s*}', '', html, flags=re.DOTALL)
html = html.replace('</style>', sidebar_toggle_css + '\n</style>')

# Make toggle button close when sidebar is open (update onclick text)
html = html.replace(
    "onclick=\"document.getElementById('sidebar').classList.toggle('open')\"",
    "onclick=\"toggleSidebar(this)\""
)

# Add toggleSidebar function right before the closing </script> or at the end of JS
toggle_fn = """
// ─── SIDEBAR TOGGLE ────────────────────────────────────────────────────────
function toggleSidebar(btn) {
  const sb = document.getElementById('sidebar');
  sb.classList.toggle('open');
  btn.textContent = sb.classList.contains('open') ? '×' : '☰';
}
"""
html = html.replace('</script>\n</body>', toggle_fn + '\n</script>\n</body>')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('All UI fixes applied.')
