import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Fix: #app was set to display:block by overhaul.py — remove all overriding rules
# The layout CSS we just injected has correct #app { display: flex; flex-direction: row }

# Remove any leftover `#app { display: block; ... }` from old overhauls
html = re.sub(r'#app \{ display: block; width: 100vw; height: 100vh; overflow: hidden; \}', '', html)

# Make sure the old CSS that hid topbar/feature-strip/quick-bar is gone
html = re.sub(r'#topbar, #feature-strip, #quick-bar \{ display: none !important; \}', '', html)

# Remove any duplicate `.floating-label` blocks (keep newest)
# Count occurrences
count = html.count('.floating-label {')
if count > 1:
    # Remove the first (older) occurrence only - keep the second
    idx = html.find('.floating-label {')
    idx2 = html.find('}', idx)
    first_block = html[idx:idx2+1]
    html = html.replace(first_block, '', 1)

# Fix camera initial position to match the concept (slightly elevated angle, not too far)
html = html.replace(
    'camera.position.set(0, 80, 150);',
    'camera.position.set(0, 120, 180);'
)

# Make sure maxDistance is reasonable
html = html.replace(
    'controls.maxDistance = 250;',
    'controls.maxDistance = 300;'
)

# Ensure the canvas/renderer fills map-wrap properly
renderer_size_fix = """
// Fix canvas sizing on DOMContentLoaded
window.addEventListener('DOMContentLoaded', () => {
  setTimeout(() => {
    const mwRect = document.getElementById('map-wrap').getBoundingClientRect();
    renderer.setSize(mwRect.width, mwRect.height);
    if(typeof labelRenderer !== 'undefined') labelRenderer.setSize(mwRect.width, mwRect.height);
    camera.aspect = mwRect.width / mwRect.height;
    camera.updateProjectionMatrix();
  }, 100);
});
"""
if 'DOMContentLoaded' not in html:
    html = html.replace('</script>\n</body>', renderer_size_fix + '\n</script>\n</body>')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Cleanup complete.')
