// 粒子引擎配置 - 严禁修改
const CONFIG = {
    count: 320,
    magnetRadius: 320,
    ringRadius: 230,
    waveSpeed: 0.55,
    waveAmplitude: 14,
    particleSize: 26,
    lerpSpeed: 0.07,
    pulseSpeed: 3,
    fieldStrength: 10,
    idleAfterMs: 2200,
    idleAmpX: 140,
    idleAmpY: 95,
    breatheRadius: 260,
    renderRadius: 560,
    cursorSafeRadius: 140,
    zRange: 70
};

// 全局状态变量
let particles = [];
let renderQueue = [];
let mouse = { x: -9999, y: -9999 };
let lastMouseMoveTime = 0;
let lastRealMouse = { x: window.innerWidth / 2, y: window.innerHeight / 2 };
let virtualMouse = { x: window.innerWidth / 2, y: window.innerHeight / 2 };
let globalColor = { r: 255, g: 255, b: 255 };
let targetColor = { r: 255, g: 255, b: 255 };
let lastScrollY = window.scrollY;
let cachedGridRect = null;

// 新增：数据管理变量
let globalMarkets = [];
let currentSortMode = 'arbitrage'; 

const canvas = document.getElementById('particle-canvas');
const ctx = canvas.getContext('2d');

// --- 核心逻辑：粒子引擎 ---

function init() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    particles = [];
    for (let i = 0; i < CONFIG.count; i++) {
        const baseX = Math.random() * canvas.width;
        const baseY = Math.random() * canvas.height;
        particles.push({
            t: Math.random() * 100,
            speed: 0.01 + Math.random() / 200,
            baseX,
            baseY,
            cx: baseX,
            cy: baseY,
            cz: (Math.random() - 0.5) * CONFIG.zRange,
            randomRadiusOffset: (Math.random() - 0.5) * 2,
            size: CONFIG.particleSize
        });
    }
    renderQueue = [...particles];
    updateGridRectCache();
}

function updateGridRectCache() {
    const projectGrid = document.querySelector('.project-grid');
    if (projectGrid) {
        const rect = projectGrid.getBoundingClientRect();
        const padding = 15;
        cachedGridRect = {
            left: rect.left - padding,
            right: rect.right + padding,
            top: rect.top - padding,
            bottom: rect.bottom + padding
        };
    }
}

function animate() {
    const now = performance.now();
    const time = now / 1000;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const lerpFactor = 0.05;
    globalColor.r += (targetColor.r - globalColor.r) * lerpFactor;
    globalColor.g += (targetColor.g - globalColor.g) * lerpFactor;
    globalColor.b += (targetColor.b - globalColor.b) * lerpFactor;

    const currentScrollY = window.scrollY;
    const deltaScroll = currentScrollY - lastScrollY;
    lastScrollY = currentScrollY;

    let destX, destY;
    if (mouse.x === -9999) {
        destX = canvas.width / 2;
        destY = canvas.height / 2;
    } else if (now - lastMouseMoveTime > CONFIG.idleAfterMs) {
        destX = lastRealMouse.x + Math.sin(time * 0.55) * CONFIG.idleAmpX;
        destY = lastRealMouse.y + Math.cos(time * 0.85) * CONFIG.idleAmpY;
    } else {
        destX = mouse.x;
        destY = mouse.y;
    }

    const isMoving = (now - lastMouseMoveTime < 120) || Math.abs(deltaScroll) > 1;
    const smooth = isMoving ? 0.24 : 0.12;
    virtualMouse.x += (destX - virtualMouse.x) * smooth;
    virtualMouse.y += (destY - virtualMouse.y) * smooth;

    renderQueue.sort((a, b) => a.cz - b.cz);

    for (let i = 0; i < renderQueue.length; i++) {
        const p = renderQueue[i];
        p.baseY -= deltaScroll * 0.8;
        p.cy -= deltaScroll * 0.8;

        if (p.baseY < 0) { p.baseY += canvas.height; p.cy += canvas.height; }
        else if (p.baseY > canvas.height) { p.baseY -= canvas.height; p.cy -= canvas.height; }

        p.t += p.speed / 2;
        const dx0 = p.baseX - virtualMouse.x;
        const dy0 = p.baseY - virtualMouse.y;
        const dist0 = Math.sqrt(dx0 * dx0 + dy0 * dy0);

        let targetX = p.baseX;
        let targetY = p.baseY;
        let targetZ = p.cz;

        if (dist0 < CONFIG.magnetRadius) {
            const angle = Math.atan2(dy0, dx0);
            const k = Math.pow(Math.max(0, 1 - dist0 / CONFIG.magnetRadius), 1.6);
            const radialWave = Math.sin(p.t * CONFIG.waveSpeed + p.randomRadiusOffset) * (CONFIG.waveAmplitude * 0.9);
            const targetR = Math.max(CONFIG.cursorSafeRadius, dist0) + radialWave * k;
            const swirlK = Math.max(0, 1 - dist0 / (CONFIG.cursorSafeRadius + 140));
            const swirl = (Math.sin(time * 2.0 + p.t) * 10 + Math.cos(p.t * 1.3) * 6) * swirlK * k;
            const rx = Math.cos(angle);
            const ry = Math.sin(angle);
            targetX = virtualMouse.x + (rx * targetR - ry * swirl);
            targetY = virtualMouse.y + (ry * targetR + rx * swirl);
            targetZ = p.cz + Math.sin(p.t * 1.2) * (CONFIG.waveAmplitude * 0.22) * k;
        }

        p.cx += (targetX - p.cx) * CONFIG.lerpSpeed;
        p.cy += (targetY - p.cy) * CONFIG.lerpSpeed;
        p.cz += (targetZ - p.cz) * CONFIG.lerpSpeed;

        if (dist0 > CONFIG.renderRadius) continue;
        const sx = p.cx;
        const sy = p.cy;

        if (cachedGridRect) {
            if (sx > cachedGridRect.left && sx < cachedGridRect.right &&
                sy > cachedGridRect.top && sy < cachedGridRect.bottom) {
                continue;
            }
        }

        const distToCenter = Math.hypot(sx - virtualMouse.x, sy - virtualMouse.y);
        if (distToCenter < CONFIG.cursorSafeRadius) continue;

        const zNorm = (p.cz + CONFIG.zRange / 2) / CONFIG.zRange;
        const breatheK = Math.max(0, 1 - dist0 / CONFIG.breatheRadius);
        const pulse = 0.9 + Math.sin(p.t * CONFIG.pulseSpeed) * (0.2 + 0.3 * breatheK);
        const influence = Math.max(0, 1 - dist0 / CONFIG.magnetRadius);
        const fade = Math.max(0, 1 - (dist0 - CONFIG.magnetRadius) / (CONFIG.renderRadius - CONFIG.magnetRadius));
        const radius = Math.max(2.2, p.size * (0.1 + 0.09 * (0.3 + 0.7 * influence)) * pulse * (0.65 + zNorm * 0.75));
        const alpha = Math.min(1, (0.18 + 0.52 * (0.3 + 0.7 * influence)) * fade * (0.55 + 0.6 * zNorm));

        ctx.fillStyle = `rgba(${Math.round(globalColor.r)}, ${Math.round(globalColor.g)}, ${Math.round(globalColor.b)}, ${alpha})`;
        ctx.shadowColor = `rgba(${Math.round(globalColor.r)}, ${Math.round(globalColor.g)}, ${Math.round(globalColor.b)}, 0.75)`;
        ctx.shadowBlur = 12;
        ctx.beginPath();
        ctx.arc(sx, sy, radius, 0, Math.PI * 2);
        ctx.fill();
        ctx.shadowBlur = 0;
    }

    const titleEl = document.querySelector('.card-title');
    if (titleEl) {
        const rect = titleEl.getBoundingClientRect();
        const textCX = rect.left + rect.width / 2;
        const textCY = rect.top + rect.height / 2;
        const distToText = Math.hypot(textCX - virtualMouse.x, textCY - virtualMouse.y);
        let intensity = Math.pow(Math.max(0, 1 - distToText / 450), 1.5);
        titleEl.style.opacity = 0.15 + 0.85 * intensity;
        titleEl.style.textShadow = `0 0 ${intensity * 40}px rgba(255, 255, 255, ${intensity * 0.6})`;
    }
    requestAnimationFrame(animate);
}

// --- 数据渲染与交互逻辑 ---
async function fetchAndRenderMarkets() {
    try {
        // 确保地址与后端一致
        const response = await fetch('http://127.0.0.1:5000/api/markets');
        const data = await response.json();
        
        // 核心修改：直接赋值，不再检查 length，不再使用模拟数据
        globalMarkets = data; 
        
        if (globalMarkets.length === 0) {
            console.warn("后端返回了 0 条真实数据，请检查网络是否能访问 Polymarket");
        }
        
        renderGrid();
    } catch (e) {
        console.error("请求后端失败:", e);
        // 即使报错也不加载模拟数据，保持页面真实
        globalMarkets = [];
        renderGrid();
    }
}
function renderGrid() {
    const grid = document.getElementById('market-grid');
    if (!grid) return;
    grid.innerHTML = ''; 

    let sortedData = [...globalMarkets];
    // 排序逻辑
    if (currentSortMode === 'arbitrage') {
        sortedData.sort((a, b) => (a.total || 999) - (b.total || 999));
    } else if (currentSortMode === 'volume') {
        sortedData.sort((a, b) => b.pool - a.pool);
    }

    sortedData.forEach(m => {
        const card = document.createElement('a');
        const detailUrl = `detail.html?title=${encodeURIComponent(m.title)}&yes=${m.yes}&no=${m.no}&img=${encodeURIComponent(m.image)}&pool=${m.pool}&total=${m.total}&desc=${encodeURIComponent(m.description)}`;
        card.href = detailUrl;
        
        // 强制显示：直接注入类名和内联样式，确保万无一失
        card.className = 'project-card show'; 
        card.style.opacity = '1';
        card.style.transform = 'translateY(0)';
        card.style.display = 'block';
        
        const yesPrice = parseFloat(m.yes) || 0;
        const noPrice = parseFloat(m.no) || 0;
        const theme = m.total < 1.0 ? '#4ade80' : '#a259ff';
        card.style.setProperty('--theme', theme);
card.innerHTML = `
    <div style="height:180px; width:100%; background:#000; display:flex; align-items:center; justify-content:center;">
        <img src="${m.image}" style="max-width:100%; max-height:100%; object-fit:contain;">
    </div>
    <div style="padding:15px; background:#1a1a1a;">
        <h3 style="font-size:0.9rem; color:#fff; height:40px; overflow:hidden; margin-bottom:10px;">${m.title}</h3>
        <div style="display:flex; justify-content:space-between; font-weight:bold;">
            <span style="color:#4ade80;">YES: ${(yesPrice * 100).toFixed(1)}%</span>
            <span style="color:#f87171;">NO: ${(noPrice * 100).toFixed(1)}%</span>
        </div>
        <div style="font-size:0.7rem; color:#666; margin-top:8px;">
            VOL: $${Math.round(m.pool).toLocaleString()}
        </div>
    </div>
`;
        grid.appendChild(card);
    });

    // 关键：通知粒子引擎重新计算避让位置
    setTimeout(() => {
        updateGridRectCache();
        setupProjectCards(); // 重新绑定悬停变色效果
    }, 100);
}

  
    
function setupProjectCards() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.classList.add('show');
                observer.unobserve(entry.target);
            }
        }); 
    }, { threshold: 0.1 });

    document.querySelectorAll('.project-card:not(.show), .primary-btn, .sort-btn').forEach((el) => {
        observer.observe(el);
    });

    // 悬停变色逻辑 - 联动粒子
    document.querySelectorAll('.project-card').forEach((card) => {
        card.addEventListener('mouseenter', function () {
            const themeColor = getComputedStyle(this).getPropertyValue('--theme').trim();
            if (themeColor.startsWith('#')) {
                const r = parseInt(themeColor.slice(1, 3), 16);
                const g = parseInt(themeColor.slice(3, 5), 16);
                const b = parseInt(themeColor.slice(5, 7), 16);
                targetColor = { r, g, b };
            }
        });
        card.addEventListener('mouseleave', () => {
            targetColor = { r: 255, g: 255, b: 255 };
        });
    });
}

function setupEventListeners() {
    window.addEventListener('mousemove', (e) => {
        mouse.x = e.clientX; mouse.y = e.clientY;
        lastMouseMoveTime = performance.now();
        lastRealMouse.x = e.clientX; lastRealMouse.y = e.clientY;
    });
    window.addEventListener('resize', init);
    window.addEventListener('scroll', updateGridRectCache, { passive: true });

    // 绑定排序按钮逻辑
    document.querySelectorAll('.sort-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.sort-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            currentSortMode = e.target.getAttribute('data-sort');
            renderGrid();
        });
    });
}

// 统一启动入口
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    init();
    animate();
    fetchAndRenderMarkets();
    setInterval(fetchAndRenderMarkets, 60000); // 每一分钟自动静默刷新
});