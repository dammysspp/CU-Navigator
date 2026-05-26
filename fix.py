import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update the traverse logic in LOAD 3D MODEL
traverse_replacement = """  model.traverse((child) => {
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
        
        const catColor = getCatColor(matchedData.cat);
        const newMat = new THREE.MeshStandardMaterial({
            color: new THREE.Color(catColor),
            roughness: 0.7,
            metalness: 0.1
        });
        originalMaterials.set(child.uuid, newMat);
        child.material = newMat;
      } else {
        child.material = new THREE.MeshStandardMaterial({
            color: new THREE.Color('#f0f0f0'),
            roughness: 0.9,
            metalness: 0.0
        });
      }
    }
  });"""

html = re.sub(r'  model\.traverse\(\(child\) => \{.*?    \}\n  \}\);\n', traverse_replacement + "\n", html, flags=re.DOTALL)

# 2. Update selectBuilding logic to properly highlight and compute bounding box of ALL meshes for the building
select_replacement = """function selectBuilding(id) {
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
  
  const bigBox = new THREE.Box3();
  let hasBox = false;

  buildings3D.forEach(mesh => {
    const origMat = originalMaterials.get(mesh.uuid);
    if (mesh.userData.id === id) {
      mesh.material = new THREE.MeshStandardMaterial({
        color: origMat.color,
        emissive: origMat.color,
        emissiveIntensity: 0.4,
        roughness: 0.2
      });
      bigBox.expandByObject(mesh);
      hasBox = true;
    } else {
      mesh.material = origMat;
    }
  });

  if (hasBox) {
    const center = bigBox.getCenter(new THREE.Vector3());
    const size = bigBox.getSize(new THREE.Vector3());
    let offsetDist = Math.max(size.x, size.y, size.z) * 1.8;
    if(offsetDist < 40) offsetDist = 40;
    if(offsetDist > 200) offsetDist = 200;
    animateCam(center, offsetDist);
  }
}"""

html = re.sub(r'function selectBuilding\(id\) \{.*?function deselectBuilding', select_replacement + "\n\nfunction deselectBuilding", html, flags=re.DOTALL)

# 3. Update animateCam
animate_replacement = """function animateCam(targetVec, offsetDist = 60) {
  const startPos = controls.target.clone();
  const startCam = camera.position.clone();
  const camOffset = new THREE.Vector3(offsetDist*0.6, offsetDist, offsetDist*0.6);
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
}"""

html = re.sub(r'function animateCam\(targetVec\) \{.*?\}\n  requestAnimationFrame\(step\);\n\}', animate_replacement, html, flags=re.DOTALL)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Updated index.html to fix camera clipping and coloring logic')
