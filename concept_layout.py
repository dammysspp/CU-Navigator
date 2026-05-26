import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ─────────────────────────────────────────────────────────────────────────────
# 1. RESTORE STRUCTURED LAYOUT - Remove all the immersive overhaul CSS that
#    made everything full-screen and broke the dashboard layout
# ─────────────────────────────────────────────────────────────────────────────

# Remove all the overhaul CSS blocks we injected
blocks_to_remove = [
    r'/\* ====== IMMERSIVE OVERHAUL ======.*?\n\n',
    r'/\* ====== SIDEBAR TOGGLE ======.*?\n#menu-toggle:hover \{ transform: scale\(1\.08\); background: #fff; \}\n',
    r'/\* ====== SIDE PANEL PLACE CARD ======.*?\.pc-desc\s*\{ display: none !important; \}\n',
    r'/\* ====== CAMPUS WATERMARK ======.*?\}\n',
    r'/\* Hide old conflicting rules if any \*/.*?\.pc-desc \{ display: none !important; \}\n',
]
for pattern in blocks_to_remove:
    html = re.sub(pattern, '', html, flags=re.DOTALL)

# ─────────────────────────────────────────────────────────────────────────────
# 2. INJECT CLEAN LAYOUT CSS that matches the concept image
# ─────────────────────────────────────────────────────────────────────────────
layout_css = """
/* ====== CONCEPT LAYOUT RESTORATION ====== */
#app {
  height: 100dvh;
  display: flex;
  flex-direction: row;
  overflow: hidden;
}
#sidebar {
  width: var(--sidebar-w);
  flex-shrink: 0;
  background: var(--white);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 2px 0 12px rgba(0,0,0,0.06);
  z-index: 300;
  /* Override any transform from old overhaul */
  position: relative !important;
  transform: none !important;
  transition: none !important;
}
#main { flex: 1; display: flex; flex-direction: column; min-width: 0; }
#topbar { display: flex !important; height: var(--header-h); }
#quick-bar { display: flex !important; flex-direction: column; background: var(--white); border-top: 1px solid var(--border); padding: 12px 16px 14px; flex-shrink: 0; }
#feature-strip { display: flex !important; }
#map-wrap { flex: 1; position: relative; overflow: hidden; min-height: 0; }
#menu-toggle { display: none !important; }
#cu-watermark { display: none !important; }
#open-nav-btn { bottom: 16px; left: 16px; }

/* ── Place Card: right-side slide-in ── */
#place-card {
  position: fixed;
  top: 0; right: -380px;
  width: 360px; max-width: 92vw;
  height: 100vh;
  background: var(--white);
  box-shadow: -6px 0 30px rgba(0,0,0,0.18);
  border-radius: 0;
  overflow-y: auto;
  opacity: 0;
  pointer-events: none;
  transition: right 0.32s cubic-bezier(0.4,0,0.2,1), opacity 0.25s;
  z-index: 5000;
  display: flex !important;
  flex-direction: column;
  /* Kill centering from old code */
  transform: none !important;
  left: auto !important;
}
#place-card.open {
  right: 0;
  opacity: 1;
  pointer-events: auto;
}

/* ── Card Hero header ── */
.card-hero {
  position: relative;
  width: 100%;
  height: 215px;
  background: linear-gradient(135deg, #2e0c59 0%, #5B2D8E 60%, #8040b8 100%);
  clip-path: polygon(0 0, 100% 0, 100% 86%, 0 100%);
  flex-shrink: 0;
}
.card-hero::after {
  content: '';
  position: absolute; inset: 0;
  background: linear-gradient(to bottom, rgba(0,0,0,0.04), rgba(0,0,0,0.45));
}
.card-hero-content { position: absolute; bottom: 36px; left: 22px; right: 22px; z-index: 2; }
.card-hero-emoji { font-size: 38px; display: block; margin-bottom: 6px; }
.card-title-3d {
  font-family: 'Fraunces', serif;
  font-size: 26px; font-weight: 900; color: #facc15;
  text-shadow: 0 3px 12px rgba(0,0,0,0.6); line-height: 1.15;
}
.card-close-x {
  position: absolute; top: 14px; right: 14px; z-index: 10;
  color: #facc15; font-size: 20px; cursor: pointer;
  background: rgba(0,0,0,0.3); width: 34px; height: 34px;
  border-radius: 50%; display: flex; align-items: center;
  justify-content: center; border: none; backdrop-filter: blur(4px);
}
.card-close-x:hover { background: rgba(0,0,0,0.6); }
.card-body { padding: 20px 22px 30px; flex: 1; overflow-y: auto; }
.card-headline { font-size: 15px; font-weight: 800; color: #111827; margin-bottom: 10px; line-height: 1.35; }
.card-text { font-size: 13px; color: #4b5563; line-height: 1.65; margin-bottom: 18px; }
.pc-handle, .pc-top, .pc-desc { display: none !important; }

/* ── Floating building labels ── */
.floating-label {
  background: rgba(255,255,255,0.96);
  backdrop-filter: blur(4px);
  padding: 5px 11px;
  border-radius: 99px;
  font-family: 'Outfit', sans-serif;
  font-size: 11px; font-weight: 700;
  color: #1f2937;
  box-shadow: 0 3px 10px rgba(0,0,0,0.18);
  pointer-events: none;
  white-space: nowrap;
  border: 1px solid rgba(255,255,255,0.6);
  display: flex; align-items: center; gap: 5px;
}
.floating-label::after {
  content: '';
  position: absolute; bottom: -5px; left: 50%;
  transform: translateX(-50%);
  border-width: 5px 5px 0;
  border-style: solid;
  border-color: rgba(255,255,255,0.96) transparent transparent;
}

/* ── Nav panel ── */
#nav-panel {
  position: fixed;
  top: 0; left: -380px;
  width: 360px; max-width: 93vw;
  height: 100vh;
  background: var(--white);
  box-shadow: 4px 0 30px rgba(0,0,0,0.22);
  z-index: 5500;
  display: flex; flex-direction: column;
  transition: left 0.35s cubic-bezier(0.4,0,0.2,1);
}
#nav-panel.open { left: 0; }

/* ── Mobile ── */
@media (max-width: 699px) {
  #sidebar { display: none; }
  #topbar  { display: none !important; }
  #feature-strip { display: none !important; }
  #quick-bar { display: none !important; }
  #app { flex-direction: column; }
  #mhdr { height: 50px; background: var(--white); border-bottom: 1px solid var(--border); display: flex !important; align-items: center; gap: 10px; padding: 0 14px; box-shadow: var(--shadow-sm); flex-shrink: 0; z-index: 200; }
  #map-wrap { flex: 1; }
  #mnav { display: flex !important; height: 58px; background: var(--white); border-top: 1px solid var(--border); align-items: center; flex-shrink: 0; z-index: 200; box-shadow: 0 -2px 10px rgba(0,0,0,0.07); }
  #msearch { display: flex !important; position: absolute; top: 58px; left: 12px; right: 12px; z-index: 200; }
  #mqrow { display: flex !important; position: absolute; bottom: 58px; }
  #menu-toggle { display: none !important; }
  #place-card { width: 100% !important; max-width: 100% !important; }
  #nav-panel { width: 100% !important; max-width: 100% !important; }
}
@media (min-width: 700px) {
  #mhdr, #msearch, #mqrow, #mnav { display: none !important; }
  #search-results { position: fixed; top: calc(var(--header-h) + 6px); left: calc(var(--sidebar-w) + 16px); width: 380px; z-index: 500; }
}
"""

html = html.replace('</style>', layout_css + '\n</style>')

# ─────────────────────────────────────────────────────────────────────────────
# 3. LOWER THE LABEL POSITIONS
#    Change label y-offset from (size.y + 15) to just (size.y * 0.3 + 4)
#    so labels sit just at the top of buildings, not floating high above
# ─────────────────────────────────────────────────────────────────────────────
html = html.replace(
    'label.position.set(0, size.y + 15, 0); // Hover above',
    'label.position.set(0, size.y * 0.25 + 3, 0); // Sit near building top'
)

# Add emoji to label
html = html.replace(
    "div.textContent = SHORT_NAMES[matchedData.id] || matchedData.name.substring(0, 18);",
    """const icon = document.createElement('span');
          icon.textContent = matchedData.emoji || '🏛';
          icon.style.fontSize = '13px';
          div.appendChild(icon);
          const txt = document.createElement('span');
          txt.textContent = SHORT_NAMES[matchedData.id] || matchedData.name.substring(0, 16);
          div.appendChild(txt);"""
)

# ─────────────────────────────────────────────────────────────────────────────
# 4. FIX: Remove stray #sidebar.open transform that's still being applied
# ─────────────────────────────────────────────────────────────────────────────
# Keep the sidebar always visible on desktop (remove the transform:translateX(-100%))
html = html.replace(
    '#sidebar {\n  position: fixed !important;\n  top: 0; left: 0; height: 100vh; z-index: 5000;\n  transform: translateX(-100%) !important;\n  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;\n  box-shadow: 4px 0 30px rgba(0,0,0,0.3);\n}\n#sidebar.open { transform: translateX(0) !important; }',
    '/* sidebar always visible on desktop, see layout CSS */'
)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Concept layout + label fix applied.')
