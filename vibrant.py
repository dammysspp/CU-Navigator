import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ─────────────────────────────────────────────────────────────────────────────
# 1. REPLACE TRAVERSE/MATERIAL LOGIC
#    Problem: unmatched buildings get dull grey. Fix: EVERY mesh gets a vibrant
#    color either from its category OR from a rich procedural palette by index.
# ─────────────────────────────────────────────────────────────────────────────
OLD_TRAVERSE = '''  model.traverse((child) => {
    if (child.isMesh) {
      child.castShadow = true;
      child.receiveShadow = true;
      
      let matchedData = null;
      let current = child;
      while (current) {
        if (current.name) {
          const bData = BUILDINGS.find(b => current.name.toLowerCase().includes(b.id.toLowerCase()));
          if (bData) {
            matchedData = bData;
            break;
          }
        }
        current = current.parent;
      }
      
      if (matchedData) {
        buildings3D.push(child);
        child.userData = matchedData; 
        
        // Add subtle outlines
        const edges = new THREE.EdgesGeometry(child.geometry);
        const line = new THREE.LineSegments(edges, new THREE.LineBasicMaterial({ color: 0x000000, transparent: true, opacity: 0.15 }));
        child.add(line);
        
        const catColor = getCatColor(matchedData.cat);
        const newMat = new THREE.MeshStandardMaterial({
            color: new THREE.Color(catColor),
            roughness: 0.4,
            metalness: 0.1,
            flatShading: false
        });
        originalMaterials.set(child.uuid, newMat);
        child.material = newMat;
      } else {
        child.material = new THREE.MeshStandardMaterial({
            color: new THREE.Color('#e2e8f0'),
            roughness: 0.6,
            metalness: 0.1
        });
      }
    }
  });'''

NEW_TRAVERSE = '''  // Vibrant palette for unmatched buildings - rich architectural colours
  const VIBRANT_PALETTE = [
    '#7C3AED','#2563EB','#059669','#D97706','#DC2626',
    '#7C3AED','#0891B2','#65A30D','#9333EA','#EA580C',
    '#1D4ED8','#047857','#B45309','#6D28D9','#0369A1',
    '#15803D','#C2410C','#4338CA','#0E7490','#4D7C0F',
  ];
  let meshIndex = 0;

  model.traverse((child) => {
    if (child.isMesh) {
      child.castShadow = true;
      child.receiveShadow = true;
      
      // Walk up the tree to find a matching building
      let matchedData = null;
      let current = child;
      while (current) {
        if (current.name) {
          const lname = current.name.toLowerCase();
          const bData = BUILDINGS.find(b =>
            lname.includes(b.id.toLowerCase()) ||
            lname.includes(b.name.split(' ')[0].toLowerCase())
          );
          if (bData) { matchedData = bData; break; }
        }
        current = current.parent;
      }
      
      let color;
      if (matchedData) {
        buildings3D.push(child);
        child.userData = matchedData;
        color = getCatColor(matchedData.cat);
      } else {
        // Every unmatched mesh gets a vibrant procedural colour by index
        color = VIBRANT_PALETTE[meshIndex % VIBRANT_PALETTE.length];
        meshIndex++;
      }

      const newMat = new THREE.MeshStandardMaterial({
        color: new THREE.Color(color),
        roughness: 0.35,
        metalness: 0.05,
        flatShading: false,
      });

      // Subtle dark edge outline for definition
      const edges = new THREE.EdgesGeometry(child.geometry);
      const line  = new THREE.LineSegments(
        edges,
        new THREE.LineBasicMaterial({ color: 0x000000, transparent: true, opacity: 0.12 })
      );
      child.add(line);

      originalMaterials.set(child.uuid, newMat);
      child.material = newMat;

      // Attach label logic for matched buildings
      if (matchedData && !htmlLabels.find(l => l.id === matchedData.id)) {
        const div = document.createElement('div');
        div.className = 'floating-label';
        const icon = document.createElement('span');
        icon.textContent = matchedData.emoji || '🏛';
        icon.style.fontSize = '13px';
        div.appendChild(icon);
        const txt = document.createElement('span');
        txt.textContent = SHORT_NAMES[matchedData.id] || matchedData.name.substring(0, 16);
        div.appendChild(txt);
        const label = new THREE.CSS2DObject(div);
        const box   = new THREE.Box3().setFromObject(child);
        const size  = box.getSize(new THREE.Vector3());
        label.position.set(0, size.y * 0.25 + 3, 0);
        child.add(label);
        htmlLabels.push({ id: matchedData.id, object: label, div: div });
      }
    }
  });'''

html = html.replace(OLD_TRAVERSE, NEW_TRAVERSE)

# Remove the duplicate label creation that was outside traverse (to avoid double-labelling)
html = re.sub(
    r"        // Add HTML Label\n        if \(!htmlLabels\.find.*?htmlLabels\.push\(.*?\};\n        \}\n",
    '',
    html,
    flags=re.DOTALL
)

# ─────────────────────────────────────────────────────────────────────────────
# 2. RICHER SCENE ATMOSPHERE
#    - Sky gradient using a large sphere instead of flat colour
#    - Brighter, warmer ground
#    - Add soft purple-toned fill light from the side
# ─────────────────────────────────────────────────────────────────────────────
OLD_SCENE_BG = '''scene.background = new THREE.Color(\'#2e0c59\');
scene.fog = new THREE.FogExp2(\'#2e0c59\', 0.0015);'''

NEW_SCENE_BG = '''// Sky gradient via ShaderMaterial on a large sphere
const skyGeo  = new THREE.SphereGeometry(700, 32, 15);
const skyMat  = new THREE.ShaderMaterial({
  uniforms: {
    topColor:    { value: new THREE.Color('#1a044a') },
    bottomColor: { value: new THREE.Color('#7b4fc9') },
    offset:      { value: 400 },
    exponent:    { value: 0.6 }
  },
  vertexShader: `
    varying vec3 vWorldPosition;
    void main() {
      vec4 worldPosition = modelMatrix * vec4(position, 1.0);
      vWorldPosition = worldPosition.xyz;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }`,
  fragmentShader: `
    uniform vec3 topColor;
    uniform vec3 bottomColor;
    uniform float offset;
    uniform float exponent;
    varying vec3 vWorldPosition;
    void main() {
      float h = normalize(vWorldPosition + offset).y;
      gl_FragColor = vec4(mix(bottomColor, topColor, max(pow(max(h, 0.0), exponent), 0.0)), 1.0);
    }`,
  side: THREE.BackSide,
});
const sky = new THREE.Mesh(skyGeo, skyMat);
scene.add(sky);
scene.fog = new THREE.FogExp2(\'#4a1c8a\', 0.0012);'''

html = html.replace(OLD_SCENE_BG, NEW_SCENE_BG)

# ─────────────────────────────────────────────────────────────────────────────
# 3. RICHER GROUND — warm olive/campus-green with slight texture feel
# ─────────────────────────────────────────────────────────────────────────────
html = html.replace(
    "const groundMat = new THREE.MeshStandardMaterial({ color: '#e8f4e5', roughness: 0.8, metalness: 0.1 });",
    "const groundMat = new THREE.MeshStandardMaterial({ color: '#3d7a3a', roughness: 0.95, metalness: 0.0 });"
)

# Also make ground slightly bigger to hide edges
html = html.replace(
    'const groundGeo = new THREE.PlaneGeometry(1000, 1000);',
    'const groundGeo = new THREE.PlaneGeometry(2000, 2000);'
)

# ─────────────────────────────────────────────────────────────────────────────
# 4. BETTER LIGHTING — warm key light + cool fill + strong rim
# ─────────────────────────────────────────────────────────────────────────────
OLD_LIGHTING = '''const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
scene.add(ambientLight);
const hemiLight = new THREE.HemisphereLight(0x2e0c59, 0xe8f4e5, 0.8);
hemiLight.position.set(0, 200, 0);
scene.add(hemiLight);
const dirLight = new THREE.DirectionalLight(0xffffff, 1.2);
dirLight.position.set(150, 250, 100);
dirLight.castShadow = true;
dirLight.shadow.bias = -0.001;'''

NEW_LIGHTING = '''// Soft base ambient
const ambientLight = new THREE.AmbientLight(0xffeedd, 0.5);
scene.add(ambientLight);
// Sky/ground hemisphere
const hemiLight = new THREE.HemisphereLight(0x9b59b6, 0x3d7a3a, 0.7);
hemiLight.position.set(0, 200, 0);
scene.add(hemiLight);
// Warm key sunlight from upper-right (like a late afternoon on campus)
const dirLight = new THREE.DirectionalLight(0xfff5e0, 1.6);
dirLight.position.set(200, 300, 100);
dirLight.castShadow = true;
dirLight.shadow.bias = -0.001;
dirLight.shadow.normalBias = 0.02;
// Cool blue-purple fill from left
const fillLight = new THREE.DirectionalLight(0x8b6fbf, 0.4);
fillLight.position.set(-150, 100, -100);
scene.add(fillLight);'''

html = html.replace(OLD_LIGHTING, NEW_LIGHTING)

# ─────────────────────────────────────────────────────────────────────────────
# 5. TONE MAPPING — increase exposure for punchier colours
# ─────────────────────────────────────────────────────────────────────────────
html = html.replace(
    'renderer.toneMappingExposure = 0.9;',
    'renderer.toneMappingExposure = 1.25;'
)

# ─────────────────────────────────────────────────────────────────────────────
# 6. LABEL PILL STYLING — more vivid with category-coloured left border
# ─────────────────────────────────────────────────────────────────────────────
new_label_css = """
/* ====== REFINED FLOATING LABELS ====== */
.floating-label {
  background: rgba(255,255,255,0.97);
  backdrop-filter: blur(6px);
  padding: 5px 10px 5px 8px;
  border-radius: 99px;
  font-family: 'Outfit', sans-serif;
  font-size: 11px;
  font-weight: 700;
  color: #1a1a2e;
  box-shadow: 0 4px 14px rgba(0,0,0,0.25), 0 1px 3px rgba(0,0,0,0.15);
  pointer-events: none;
  white-space: nowrap;
  border: 1.5px solid rgba(255,255,255,0.8);
  display: flex;
  align-items: center;
  gap: 5px;
  position: relative;
}
.floating-label::after {
  content: '';
  position: absolute;
  bottom: -6px;
  left: 50%;
  transform: translateX(-50%);
  border-width: 6px 5px 0;
  border-style: solid;
  border-color: rgba(255,255,255,0.97) transparent transparent;
}
"""
# Remove any old floating-label CSS block
html = re.sub(r'/\* ====== REFINED FLOATING LABELS ======.*?\*/', '', html, flags=re.DOTALL)
# Also remove older .floating-label blocks inserted previously
html = re.sub(r'\.floating-label \{.*?border: 1px solid rgba\(255,255,255,0\.6\);\n\}\n\.floating-label::after \{.*?\}\n', '', html, flags=re.DOTALL)
html = html.replace('</style>', new_label_css + '\n</style>')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Colorful vibrant visual overhaul complete.')
