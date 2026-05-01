// Shared renderer — call renderVisual(htmlPath, outPath, w, h) from run_script
async function renderVisual(htmlPath, outPath, width, height) {
  const html = await readFile(htmlPath);
  const css = await readFile('visuals/shared.css');
  const inlined = html.replace('<link rel="stylesheet" href="shared.css">', `<style>${css}</style>`);
  const parser = new DOMParser();
  const doc = parser.parseFromString(inlined, 'text/html');

  // Inject font links into our document if not already
  doc.head.querySelectorAll('link[href*="fonts.googleapis"]').forEach(l => {
    if (!document.head.querySelector(`link[href="${l.href}"]`)) {
      const newL = document.createElement('link');
      newL.rel = 'stylesheet'; newL.href = l.href;
      document.head.appendChild(newL);
    }
  });

  const host = document.createElement('div');
  host.id = 'render-host-' + Math.random().toString(36).slice(2);
  host.style.cssText = `position:fixed;top:0;left:0;width:${width}px;height:${height}px;z-index:99999;background:#F4F1EA;overflow:hidden`;
  document.body.appendChild(host);

  const styleBlock = document.createElement('style');
  let cssText = '';
  doc.head.querySelectorAll('style').forEach(s => cssText += s.textContent + '\n');
  cssText = cssText.replace(/(^|[\s,{}])(html,\s*body|html|body)([\s,{])/g, (m, p, sel, post) => `${p}#${host.id}${post}`);
  styleBlock.textContent = cssText;
  document.head.appendChild(styleBlock);

  host.innerHTML = doc.body.innerHTML;
  host.style.width = width + 'px';
  host.style.height = height + 'px';

  await document.fonts.ready;
  await new Promise(r => setTimeout(r, 1500));

  if (!window.htmlToImage) {
    const s = document.createElement('script');
    s.src = 'https://unpkg.com/html-to-image@1.11.11/dist/html-to-image.js';
    document.head.appendChild(s);
    await new Promise(r => s.onload = r);
  }

  const dataUrl = await window.htmlToImage.toPng(host, {
    width, height, pixelRatio: 2, backgroundColor: '#F4F1EA',
  });
  const blob = await (await fetch(dataUrl)).blob();
  await saveFile(outPath, blob);
  host.remove();
  styleBlock.remove();
  return blob.size;
}
window.__renderVisual = renderVisual;
