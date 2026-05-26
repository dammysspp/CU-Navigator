import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Add tone mapping to renderer
renderer_old = """const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
renderer.setSize(mw.clientWidth, mw.clientHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;"""

renderer_new = """const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
renderer.setSize(mw.clientWidth, mw.clientHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputEncoding = THREE.sRGBEncoding;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.1;"""

html = html.replace(renderer_old, renderer_new)

# Update lighting
lighting_old = """const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
scene.add(ambientLight);
const hemiLight = new THREE.HemisphereLight(0xffffff, 0x444444, 0.6);
hemiLight.position.set(0, 200, 0);
scene.add(hemiLight);
const dirLight = new THREE.DirectionalLight(0xffffff, 0.7);
dirLight.position.set(100, 200, 100);
dirLight.castShadow = true;"""

lighting_new = """const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
scene.add(ambientLight);
const hemiLight = new THREE.HemisphereLight(0xffffff, 0x8d8d8d, 0.6);
hemiLight.position.set(0, 200, 0);
scene.add(hemiLight);
const dirLight = new THREE.DirectionalLight(0xffffff, 1.2);
dirLight.position.set(150, 250, 100);
dirLight.castShadow = true;
dirLight.shadow.bias = -0.001;"""

html = html.replace(lighting_old, lighting_new)

# Update ground
ground_old = """const groundMat = new THREE.MeshStandardMaterial({ color: '#c8e4c4', roughness: 1.0 });"""
ground_new = """const groundMat = new THREE.MeshStandardMaterial({ color: '#e8f4e5', roughness: 0.8, metalness: 0.1 });"""
html = html.replace(ground_old, ground_new)

# Update materials
mat_old = """const newMat = new THREE.MeshStandardMaterial({
            color: new THREE.Color(catColor),
            roughness: 0.7,
            metalness: 0.1
        });"""
mat_new = """const newMat = new THREE.MeshStandardMaterial({
            color: new THREE.Color(catColor),
            roughness: 0.4,
            metalness: 0.1,
            flatShading: false
        });"""
html = html.replace(mat_old, mat_new)

unassigned_old = """child.material = new THREE.MeshStandardMaterial({
            color: new THREE.Color('#f0f0f0'),
            roughness: 0.9,
            metalness: 0.0
        });"""
unassigned_new = """child.material = new THREE.MeshStandardMaterial({
            color: new THREE.Color('#e2e8f0'),
            roughness: 0.6,
            metalness: 0.1
        });"""
html = html.replace(unassigned_old, unassigned_new)

# Add outline effect to buildings!
# We can just add an EdgesGeometry to make it pop like a beautiful architectural model.
edges_logic_old = """buildings3D.push(child);
        child.userData = matchedData; 
        
        const catColor = getCatColor(matchedData.cat);"""
edges_logic_new = """buildings3D.push(child);
        child.userData = matchedData; 
        
        // Add subtle outlines
        const edges = new THREE.EdgesGeometry(child.geometry);
        const line = new THREE.LineSegments(edges, new THREE.LineBasicMaterial({ color: 0x000000, transparent: true, opacity: 0.15 }));
        child.add(line);
        
        const catColor = getCatColor(matchedData.cat);"""
html = html.replace(edges_logic_old, edges_logic_new)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Visuals enhanced.")
