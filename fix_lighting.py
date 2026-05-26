import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update lighting
lighting_old = """const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
scene.add(ambientLight);
const dirLight = new THREE.DirectionalLight(0xffffff, 0.9);"""

lighting_new = """const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
scene.add(ambientLight);
const hemiLight = new THREE.HemisphereLight(0xffffff, 0x444444, 0.6);
hemiLight.position.set(0, 200, 0);
scene.add(hemiLight);
const dirLight = new THREE.DirectionalLight(0xffffff, 0.7);"""

html = html.replace(lighting_old, lighting_new)

# 2. Update quickDefs
quick_old = """const quickDefs=[
  {id:'library',   lbl:'Covenant\\nLibrary', icon:'📚'},
  {id:'chapel',    lbl:'Chapel',            icon:'⛪'},
  {id:'senate',    lbl:'Student\\nCenter',   icon:'🏛️'},
  {id:'printing',  lbl:'ICT Center',        icon:'💻'},
  {id:'cafeteria', lbl:'Cafeteria',         icon:'🍽️'},
  {id:'atm',       lbl:'Bank',              icon:'🏧'},
  {id:'clinic',    lbl:'Medical\\nCenter',   icon:'🏥'},
];"""

quick_new = """const quickDefs=[
  {id:'library',   lbl:'Centre for\\nLearning', icon:'📚'},
  {id:'chapel',    lbl:'University\\nChapel',   icon:'⛪'},
  {id:'senate',    lbl:'Senate\\nBuilding',     icon:'🏛️'},
  {id:'printing',  lbl:'ICT\\nCentre',          icon:'💻'},
  {id:'cafeteria', lbl:'Main\\nCafeteria',      icon:'🍽️'},
  {id:'atm',       lbl:'ATM /\\nBanking',       icon:'🏧'},
  {id:'clinic',    lbl:'Medical\\nCentre',      icon:'🏥'},
];"""

html = html.replace(quick_old, quick_new)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Lighting and quick access updated.")
