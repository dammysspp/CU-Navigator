import sys
import re

with open('cu-navigator (4).html', 'r', encoding='utf-8') as f:
    content = f.read()

# Split around RENDERER
parts = content.split('// =====================================================\n// RENDERER')
if len(parts) < 2:
    print('Could not find RENDERER section')
    sys.exit(1)

pre_renderer = parts[0]
post_renderer_chunk = parts[1]

# Split around SEARCH
parts2 = post_renderer_chunk.split('// =====================================================\n// SEARCH')
if len(parts2) < 2:
    print('Could not find SEARCH section')
    sys.exit(1)

post_search = '// =====================================================\n// SEARCH' + parts2[1]

# Replace ZOOM section in post_search
post_search = re.sub(r"// =====================================================\n// ZOOM\n// =====================================================\n.*?\n// =====================================================\n// DIRECTIONS", """// =====================================================
// ZOOM
// =====================================================
document.getElementById('zoom-in').addEventListener('click', () => { camera.position.multiplyScalar(0.8); });
document.getElementById('zoom-out').addEventListener('click', () => { camera.position.multiplyScalar(1.2); });
document.getElementById('zoom-reset').addEventListener('click', () => { 
  animateCam(new THREE.Vector3(0,0,0));
  deselectBuilding();
  startMarker.visible = false;
  endMarker.visible = false;
  if(routeLine) { scene.remove(routeLine); routeLine = null; }
});

// =====================================================
// DIRECTIONS""", post_search, flags=re.DOTALL)

# Replace getDirections function in post_search
get_dir_replacement = """function getDirections(b){
  const sd=genSteps(b);
  document.getElementById('dir-title').textContent=`To: ${b.name}`;
  document.getElementById('step-list').innerHTML=sd.steps.map((s,i)=>`<li class="dp-step"><div class="dp-num">${i+1}</div><div>${s}</div></li>`).join('');
  document.getElementById('dir-time').innerHTML=`🚶 ${sd.time} walk · ${sd.dist} from Main Gate`;
  document.getElementById('rc-dest').textContent=b.name;
  const rt=document.getElementById('rc-time'); rt.style.display='flex'; document.getElementById('rc-time-val').textContent=sd.time;
  document.getElementById('route-card').classList.add('open');
  document.getElementById('dir-panel').classList.add('open');
  deselectBuilding();
  
  const fromMesh = buildings3D.find(m => m.userData.id === 'gate');
  const toMesh = buildings3D.find(m => m.userData.id === b.id);
  
  if (fromMesh && toMesh) {
    const fromPos = new THREE.Box3().setFromObject(fromMesh).getCenter(new THREE.Vector3());
    const toPos = new THREE.Box3().setFromObject(toMesh).getCenter(new THREE.Vector3());
    
    startMarker.position.copy(fromPos);
    startMarker.userData.baseY = fromPos.y + 10;
    startMarker.visible = true;
    
    endMarker.position.copy(toPos);
    endMarker.userData.baseY = toPos.y + 10;
    endMarker.visible = true;
    
    if(routeLine) scene.remove(routeLine);
    const midPos = new THREE.Vector3().addVectors(fromPos, toPos).multiplyScalar(0.5);
    midPos.y += 20; 
    
    const curve = new THREE.QuadraticBezierCurve3(fromPos, midPos, toPos);
    const points = curve.getPoints(50);
    const geometry = new THREE.BufferGeometry().setFromPoints(points);
    const material = new THREE.LineBasicMaterial({ color: 0x5B2D8E, linewidth: 3 });
    routeLine = new THREE.Line(geometry, material);
    scene.add(routeLine);
    
    animateCam(midPos);
  }
}"""
post_search = re.sub(r"function getDirections\(b\)\{.*?\}\nfunction genSteps", get_dir_replacement + "\nfunction genSteps", post_search, flags=re.DOTALL)

# Replace INIT section in post_search
post_search = re.sub(r"// =====================================================\n// INIT\n// =====================================================.*?</script>", """// =====================================================
// INIT
// =====================================================
setTimeout(()=>showToast('👋 Welcome, Visitor! Tap any building to explore'),3000);
// Register Service Worker for PWA / Offline functionality
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('sw.js').then(reg => {
      console.log('ServiceWorker registration successful with scope: ', reg.scope);
    }).catch(err => {
      console.log('ServiceWorker registration failed: ', err);
    });
  });
}
</script>""", post_search, flags=re.DOTALL)

# Now construct the new 3D renderer logic
three_js_renderer = """// =====================================================
// 3D RENDERER SETUP
// =====================================================
const mw = document.getElementById('map-wrap');
const scene = new THREE.Scene();
scene.background = new THREE.Color('#cfe8cc');
scene.fog = new THREE.FogExp2('#cfe8cc', 0.002);

const camera = new THREE.PerspectiveCamera(45, mw.clientWidth / mw.clientHeight, 1, 1000);
camera.position.set(0, 80, 150);

const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
renderer.setSize(mw.clientWidth, mw.clientHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

const oldCanvas = document.getElementById('map-canvas');
if (oldCanvas) oldCanvas.remove();
mw.insertBefore(renderer.domElement, mw.firstChild);

const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.05;
controls.maxPolarAngle = Math.PI / 2 - 0.01; 
controls.minDistance = 10;
controls.maxDistance = 400;

// Lighting
const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
scene.add(ambientLight);
const dirLight = new THREE.DirectionalLight(0xffffff, 0.9);
dirLight.position.set(100, 200, 100);
dirLight.castShadow = true;
dirLight.shadow.mapSize.width = 2048;
dirLight.shadow.mapSize.height = 2048;
dirLight.shadow.camera.left = -200;
dirLight.shadow.camera.right = 200;
dirLight.shadow.camera.top = 200;
dirLight.shadow.camera.bottom = -200;
scene.add(dirLight);

// Ground plane
const groundGeo = new THREE.PlaneGeometry(1000, 1000);
const groundMat = new THREE.MeshStandardMaterial({ color: '#c8e4c4', roughness: 1.0 });
const ground = new THREE.Mesh(groundGeo, groundMat);
ground.rotation.x = -Math.PI / 2;
ground.receiveShadow = true;
scene.add(ground);

// Waypoint markers
const markerGeometry = new THREE.ConeGeometry(3, 10, 16);
markerGeometry.translate(0, 5, 0); 
const markerMaterial = new THREE.MeshStandardMaterial({ color: '#5B2D8E', emissive: '#5B2D8E', emissiveIntensity: 0.5 });
const startMarker = new THREE.Mesh(markerGeometry, markerMaterial);
const endMarker = new THREE.Mesh(markerGeometry, new THREE.MeshStandardMaterial({ color: '#d97706', emissive: '#d97706', emissiveIntensity: 0.5 }));
startMarker.visible = false;
endMarker.visible = false;
scene.add(startMarker);
scene.add(endMarker);
let routeLine = null;

// =====================================================
// LOAD 3D MODEL
// =====================================================
const loader = new THREE.GLTFLoader();
let buildings3D = [];
let originalMaterials = new Map();

function getCatColor(cat) {
  if (CATEGORIES[cat]) return CATEGORIES[cat].color;
  return '#ffffff';
}

loader.load('covenant map.glb', (gltf) => {
  const model = gltf.scene;
  model.traverse((child) => {
    if (child.isMesh) {
      child.castShadow = true;
      child.receiveShadow = true;
      
      const bData = BUILDINGS.find(b => child.name.toLowerCase().includes(b.id.toLowerCase()));
      if (bData) {
        buildings3D.push(child);
        child.userData = bData; 
        
        const catColor = getCatColor(bData.cat);
        const newMat = new THREE.MeshStandardMaterial({
            color: catColor,
            roughness: 0.7,
            metalness: 0.1
        });
        originalMaterials.set(child.uuid, newMat);
        child.material = newMat;
      }
    }
  });
  
  const box = new THREE.Box3().setFromObject(model);
  const center = box.getCenter(new THREE.Vector3());
  model.position.sub(center); 
  
  scene.add(model);
}, undefined, (error) => {
  console.error('Error loading 3D model:', error);
});

// =====================================================
// RAYCASTER & INTERACTION
// =====================================================
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();
let selectedId = null;

function onPointerDown(event) {
  if (event.target.closest('#place-card') || event.target.closest('#sidebar') || event.target.closest('#topbar') || event.target.closest('#route-card') || event.target.closest('#dir-panel') || event.target.closest('#map-controls') || event.target.closest('#legend')) return;
  
  const rect = renderer.domElement.getBoundingClientRect();
  const clientX = event.clientX || (event.touches && event.touches[0].clientX);
  const clientY = event.clientY || (event.touches && event.touches[0].clientY);
  if (clientX === undefined) return;
  
  mouse.x = ((clientX - rect.left) / rect.width) * 2 - 1;
  mouse.y = -((clientY - rect.top) / rect.height) * 2 + 1;
  
  raycaster.setFromCamera(mouse, camera);
  const intersects = raycaster.intersectObjects(buildings3D);
  
  if (intersects.length > 0) {
    const clickedMesh = intersects[0].object;
    selectBuilding(clickedMesh.userData.id);
  } else {
    deselectBuilding();
  }
}
renderer.domElement.addEventListener('pointerdown', onPointerDown);
renderer.domElement.addEventListener('touchstart', onPointerDown, {passive: true});

window.addEventListener('resize', () => {
  camera.aspect = mw.clientWidth / mw.clientHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(mw.clientWidth, mw.clientHeight);
});

// =====================================================
// SELECT / DESELECT
// =====================================================
function selectBuilding(id) {
  if(typeof id === 'object') id = id.id;
  selectedId = id;
  const b = BUILDINGS.find(x => x.id === id);
  if (!b) return;
  
  document.getElementById('dir-panel').classList.remove('open');
  const cat=CATEGORIES[b.cat];
  const emo=document.getElementById('card-emoji'); emo.textContent=b.emoji; emo.style.background=cat.bg;
  document.getElementById('card-name').textContent=b.name;
  document.getElementById('card-type').textContent=cat.label; document.getElementById('card-type').style.color=cat.color;
  document.getElementById('card-desc').textContent=b.desc;
  document.getElementById('card-tags').innerHTML=b.tags.map(t=>`<span class="pc-tag">${t}</span>`).join('');
  document.getElementById('card-stats').innerHTML=`
    <div class="pc-stat"><div class="pc-stat-val">~${Math.floor(Math.random()*4+1)} min</div><div class="pc-stat-lbl">from Main Gate</div></div>
    <div class="pc-stat"><div class="pc-stat-val">${b.cat[0].toUpperCase()+b.cat.slice(1)}</div><div class="pc-stat-lbl">Category</div></div>
    <div class="pc-stat"><div class="pc-stat-val" style="color:#15803d">Open</div><div class="pc-stat-lbl">Status</div></div>`;
  document.getElementById('place-card').classList.add('open');
  document.getElementById('rc-dest').textContent=b.name;
  
  buildings3D.forEach(mesh => {
    const origMat = originalMaterials.get(mesh.uuid);
    if (mesh.userData.id === id) {
      mesh.material = new THREE.MeshStandardMaterial({
        color: origMat.color,
        emissive: origMat.color,
        emissiveIntensity: 0.4,
        roughness: 0.2
      });
      const box = new THREE.Box3().setFromObject(mesh);
      const center = box.getCenter(new THREE.Vector3());
      animateCam(center);
    } else {
      mesh.material = origMat;
    }
  });
}

function deselectBuilding() {
  selectedId = null;
  document.getElementById('place-card').classList.remove('open');
  buildings3D.forEach(mesh => {
    mesh.material = originalMaterials.get(mesh.uuid);
  });
}

function animateCam(targetVec) {
  const startPos = controls.target.clone();
  const startCam = camera.position.clone();
  const camOffset = new THREE.Vector3(30, 40, 30);
  const endCam = targetVec.clone().add(camOffset);
  
  const startTime = performance.now();
  const dur = 800;
  
  function step(t) {
    const p = Math.min(1, (t - startTime) / dur);
    const e = 1 - Math.pow(1 - p, 3);
    
    controls.target.lerpVectors(startPos, targetVec, e);
    camera.position.lerpVectors(startCam, endCam, e);
    controls.update();
    
    if (p < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

// =====================================================
// RENDER LOOP
// =====================================================
function render() {
  requestAnimationFrame(render);
  
  const time = performance.now() * 0.003;
  if (startMarker.visible) {
    startMarker.position.y = startMarker.userData.baseY + Math.sin(time) * 1.5;
    startMarker.rotation.y = time * 0.5;
  }
  if (endMarker.visible) {
    endMarker.position.y = endMarker.userData.baseY + Math.sin(time + 1) * 1.5;
    endMarker.rotation.y = time * 0.5;
  }
  
  controls.update();
  renderer.render(scene, camera);
}
render();

"""

final_content = pre_renderer + three_js_renderer + post_search

with open('cu-navigator (4).html', 'w', encoding='utf-8') as f:
    f.write(final_content)

print('Successfully updated cu-navigator (4).html with 3D Three.js renderer')
