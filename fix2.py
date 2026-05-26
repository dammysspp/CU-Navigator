import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update maxDistance
html = re.sub(r'controls\.maxDistance\s*=\s*400;', 'controls.maxDistance = 250;', html)

# 2. Fix onPointerDown UI exclusion
pointer_down_check = """function onPointerDown(event) {
  if (event.target.closest('#place-card') || event.target.closest('#sidebar') || event.target.closest('#topbar') || event.target.closest('#route-card') || event.target.closest('#dir-panel') || event.target.closest('#map-controls') || event.target.closest('#legend') || event.target.closest('#quick-bar') || event.target.closest('#mqrow') || event.target.closest('#search-results') || event.target.closest('#msearch') || event.target.closest('#mhdr')) return;"""
html = re.sub(r'function onPointerDown\(event\) \{\s*if \(event\.target\.closest.*?return;', pointer_down_check, html, flags=re.DOTALL)

# 3. Fix close-card focusing on all buildings
close_card_fix = """document.getElementById('close-card').addEventListener('click', () => {
  deselectBuilding();
  animateCam(new THREE.Vector3(0, 0, 0), 200);
});"""
html = re.sub(r"document\.getElementById\('close-card'\)\.addEventListener\('click',\s*deselectBuilding\);", close_card_fix, html)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Fixes applied.")
