// ───────────── motion + interaction ─────────────

// 1. Nav scroll state + progress bar
const nav = document.getElementById('nav');
const navProgress = document.getElementById('navProgress');

function onScroll(){
  const y = window.scrollY;
  if(y > 24) nav.classList.add('scrolled'); else nav.classList.remove('scrolled');

  const max = document.documentElement.scrollHeight - window.innerHeight;
  const pct = max > 0 ? (y / max) * 100 : 0;
  navProgress.style.width = pct + '%';

  // update side guide active step
  let activeId = null;
  document.querySelectorAll('main > section, section.end').forEach(sec => {
    const r = sec.getBoundingClientRect();
    if(r.top < window.innerHeight * 0.4 && r.bottom > window.innerHeight * 0.4){
      activeId = sec.id;
    }
  });
  document.querySelectorAll('.guide-step').forEach(s => {
    s.classList.toggle('active', s.dataset.target === activeId);
  });
}
window.addEventListener('scroll', onScroll, {passive:true});
onScroll();

// 2. Smooth scroll for nav anchors + guide rail + buttons
document.querySelectorAll('a[href^="#"], [data-scroll], .guide-step').forEach(el => {
  el.addEventListener('click', e => {
    const target = el.dataset.scroll || el.dataset.target ||
      (el.getAttribute('href') || '').replace('#','');
    if(!target || target === 'top'){
      // top anchor still works default
      if(el.getAttribute('href') === '#top'){
        e.preventDefault();
        window.scrollTo({top:0, behavior:'smooth'});
      }
      return;
    }
    const node = document.getElementById(target);
    if(node){
      e.preventDefault();
      const top = node.getBoundingClientRect().top + window.scrollY - 60;
      window.scrollTo({top, behavior:'smooth'});
    }
  });
});

// 3. IntersectionObserver — section reveals + bar fills
const io = new IntersectionObserver((entries) => {
  entries.forEach(en => {
    if(en.isIntersecting){
      en.target.classList.add('in','in-view');
    }
  });
}, {threshold:0.18, rootMargin:'0px 0px -10% 0px'});

// add reveal class to section heads, cards, mbars, etc.
document.querySelectorAll('.section-head, .tcard, .mbar, .sg-cell, .mf-step, .method-callout, .class-strip, .end-inner').forEach(el => {
  el.classList.add('reveal');
  io.observe(el);
});
document.querySelectorAll('.threat-cards, .scope-grid, .method-flow, .end-actions').forEach(el => {
  el.classList.add('reveal-stagger');
  io.observe(el);
});

// 4. Hero ticker — count-up the ASR numbers when visible
const heroTicker = document.querySelector('.hero-ticker');
if(heroTicker){
  const tio = new IntersectionObserver((entries) => {
    entries.forEach(en => {
      if(en.isIntersecting){
        en.target.querySelectorAll('.ticker-row .num').forEach(n => {
          const target = parseFloat(n.textContent);
          let cur = 0;
          const dur = 1100;
          const start = performance.now();
          const step = (now) => {
            const t = Math.min(1, (now - start) / dur);
            const eased = 1 - Math.pow(1 - t, 4);
            const v = (cur + (target - cur) * eased);
            n.textContent = v.toFixed(2);
            if(t < 1) requestAnimationFrame(step);
          };
          requestAnimationFrame(step);
        });
        tio.unobserve(en.target);
      }
    });
  }, {threshold: 0.5});
  tio.observe(heroTicker);
}

// 5. The marquee $62,000 number — count up when in view
const figEl = document.getElementById('figCount');
if(figEl){
  const fio = new IntersectionObserver((entries) => {
    entries.forEach(en => {
      if(en.isIntersecting){
        const target = 62000;
        const dur = 1600;
        const start = performance.now();
        const step = (now) => {
          const t = Math.min(1, (now - start) / dur);
          const eased = 1 - Math.pow(1 - t, 4);
          const v = Math.round(target * eased);
          figEl.textContent = v.toLocaleString();
          if(t < 1) requestAnimationFrame(step);
        };
        requestAnimationFrame(step);
        fio.unobserve(en.target);
      }
    });
  }, {threshold:0.4});
  fio.observe(figEl);
}

// 6. Attack rows — accordion open/close
document.querySelectorAll('.atk-row').forEach(row => {
  row.addEventListener('click', () => {
    const open = row.classList.contains('open');
    // close all others
    document.querySelectorAll('.atk-row.open').forEach(r => {
      if(r !== row) r.classList.remove('open');
    });
    row.classList.toggle('open', !open);
  });
});

// auto-open the featured attack when scrolled into view, once
const featured = document.querySelector('.atk-row.featured');
if(featured){
  const aio = new IntersectionObserver((entries) => {
    entries.forEach(en => {
      if(en.isIntersecting && !featured.dataset.opened){
        // small delay so user sees the row arrive first
        setTimeout(() => {
          featured.classList.add('open');
          featured.dataset.opened = '1';
        }, 400);
        aio.unobserve(en.target);
      }
    });
  }, {threshold:0.5});
  aio.observe(featured);
}

// 7. Build the TPR visualization — 30 scenarios, 3 columns
// Values approximate the POC findings: T1 mean 1.15 (peak 2.0), T2 mean 1.80 (peak 3.0), T4 mean 1.35 (peak 2.0)
const tprData = {
  T1: [
    {id:'T1-0001', v:1.0}, {id:'T1-0002', v:1.0}, {id:'T1-0003', v:1.0},
    {id:'T1-0004', v:1.0}, {id:'T1-0005', v:2.0}, {id:'T1-0006', v:1.0},
    {id:'T1-0007', v:1.0}, {id:'T1-0008', v:1.5}, {id:'T1-0009', v:1.0},
    {id:'T1-0010', v:1.0},
  ],
  T2: [
    {id:'T2-0001', v:2.0, fail:true}, {id:'T2-0002', v:2.0, fail:true},
    {id:'T2-0003', v:1.5}, {id:'T2-0004', v:2.0}, {id:'T2-0005', v:1.5},
    {id:'T2-0006', v:1.5}, {id:'T2-0007', v:1.5}, {id:'T2-0008', v:1.5},
    {id:'T2-0009', v:3.0}, {id:'T2-0010', v:1.5, fail:true},
  ],
  T4: [
    {id:'T4-0001', v:1.0}, {id:'T4-0002', v:1.5}, {id:'T4-0003', v:1.5},
    {id:'T4-0004', v:1.5}, {id:'T4-0005', v:2.0}, {id:'T4-0006', v:1.0},
    {id:'T4-0007', v:1.5}, {id:'T4-0008', v:1.5}, {id:'T4-0009', v:1.0, fail:true},
    {id:'T4-0010', v:1.0},
  ],
};

const tprRows = document.getElementById('tprRows');
if(tprRows){
  // axis is 1× → 3×, so width % = ((v - 1) / 2) * 100
  const colNames = {T1:'T1 · Privilege Composition', T2:'T2 · Cascading State', T4:'T4 · Structured-Field Injection'};
  const means = {T1:1.15, T2:1.80, T4:1.35};

  Object.entries(tprData).forEach(([cls, rows]) => {
    const col = document.createElement('div');
    col.className = 'tpr-col';
    col.innerHTML = `
      <div class="tpr-col-head">
        <span>${colNames[cls]}</span>
        <span style="color:var(--ink-2)">μ ${means[cls].toFixed(2)}</span>
      </div>
    `;
    rows.forEach(r => {
      const w = Math.max(2, ((r.v - 1) / 2) * 100);
      const high = r.v >= 2;
      const bar = document.createElement('div');
      bar.className = `tpr-bar ${high ? 'high' : ''}`;
      bar.innerHTML = `
        <span class="tpr-id">${r.id}${r.fail ? ' ●' : ''}</span>
        <div class="tpr-track"><div class="tpr-fill" style="width:${w}%"></div></div>
        <span class="tpr-val">${r.v.toFixed(2)}×</span>
      `;
      col.appendChild(bar);
    });
    tprRows.appendChild(col);
  });

  // animate when in view
  const tprIo = new IntersectionObserver((entries) => {
    entries.forEach(en => {
      if(en.isIntersecting){
        en.target.classList.add('in-view');
        tprIo.unobserve(en.target);
      }
    });
  }, {threshold:0.2});
  tprRows.querySelectorAll('.tpr-bar').forEach((b, i) => {
    b.style.transitionDelay = (i * 14) + 'ms';
    tprIo.observe(b);
  });
}

// 8. Hero subtle parallax on the gradient backgrounds
const hero = document.getElementById('hero');
if(hero){
  window.addEventListener('mousemove', e => {
    const x = (e.clientX / window.innerWidth - 0.5) * 8;
    const y = (e.clientY / window.innerHeight - 0.5) * 8;
    hero.style.backgroundPosition = `${50 + x}% ${30 + y}%, ${20 - x}% ${80 - y}%`;
  });
}

// 9. Make sure ticker rows reveal nicely too
document.querySelectorAll('.ticker-row').forEach((r, i) => {
  r.style.opacity = '0';
  r.style.transform = 'translateY(8px)';
  r.style.transition = `opacity .6s ${(2.7 + i*0.08)}s var(--ease-out), transform .6s ${(2.7 + i*0.08)}s var(--ease-out)`;
  requestAnimationFrame(() => {
    setTimeout(() => {
      r.style.opacity = '1';
      r.style.transform = 'translateY(0)';
    }, 50);
  });
});
