/**
 * LF Academy Graphics Engine v1.0
 * 霖楓學苑圖形引擎 — 瀏覽器端數學圖形生成
 * 
 * 三種模式：
 * 1. SVG Template: 即時插入預製SVG模板
 * 2. Chart.js: 數據圖表（棒形/折線/圓形圖）
 * 3. Canvas 2D: 自訂幾何繪圖
 */

const LFGraphics = {
    // ========================================
    // 預製SVG圖形庫（直接注入HTML）
    // ========================================
    shapes: {
        // 平行四邊形 (附底高標註)
        parallelogram: (base = 8, height = 5, unit = 'cm') => `
            <svg viewBox="0 0 300 180" class="math-diagram">
                <polygon points="50,140 200,140 250,40 100,40" 
                    fill="rgba(66,133,244,0.15)" stroke="#4285f4" stroke-width="2"/>
                <line x1="50" y1="155" x2="200" y2="155" stroke="#ea4335" stroke-width="2" 
                    marker-start="url(#arrow)" marker-end="url(#arrow)"/>
                <text x="125" y="172" text-anchor="middle" font-size="14" fill="#ea4335">底 = ${base}${unit}</text>
                <line x1="140" y1="140" x2="140" y2="40" stroke="#34a853" stroke-width="2" 
                    stroke-dasharray="5,3"/>
                <text x="150" y="95" font-size="14" fill="#34a853">高 = ${height}${unit}</text>
                <defs><marker id="arrow" markerWidth="8" markerHeight="6" refX="4" refY="3" orient="auto">
                    <polygon points="0,0 8,3 0,6" fill="#ea4335"/></marker></defs>
            </svg>`,

        // 三角形 (底高標註)
        triangle: (base = 6, height = 4) => `
            <svg viewBox="0 0 240 180" class="math-diagram">
                <polygon points="20,150 220,150 120,20" 
                    fill="rgba(66,133,244,0.15)" stroke="#4285f4" stroke-width="2"/>
                <line x1="20" y1="165" x2="220" y2="165" stroke="#ea4335" stroke-width="2"/>
                <text x="120" y="178" text-anchor="middle" font-size="14" fill="#ea4335">底 = ${base}cm</text>
                <line x1="120" y1="150" x2="120" y2="20" stroke="#34a853" stroke-width="2" stroke-dasharray="5,3"/>
                <text x="132" y="90" font-size="14" fill="#34a853">高 = ${height}cm</text>
                <rect x="110" y="140" width="16" height="16" fill="none" stroke="#34a853" stroke-width="1"/>
            </svg>`,

        // 長方體 (3D透視)
        cuboid: (l = 4, w = 3, h = 2) => `
            <svg viewBox="0 0 280 220" class="math-diagram">
                <polygon points="40,100 180,100 210,70 70,70" 
                    fill="rgba(66,133,244,0.2)" stroke="#4285f4" stroke-width="2"/>
                <polygon points="70,70 210,70 210,30 70,30" 
                    fill="rgba(52,168,83,0.2)" stroke="#34a853" stroke-width="2"/>
                <polygon points="180,100 210,70 210,30 180,60" 
                    fill="rgba(251,188,4,0.2)" stroke="#fbbc04" stroke-width="2"/>
                <line x1="40" y1="100" x2="70" y2="70" stroke="#4285f4" stroke-width="1"/>
                <line x1="40" y1="100" x2="180" y2="100" stroke="#4285f4"/>
                <line x1="40" y1="100" x2="40" y2="140" stroke="#4285f4"/>
                <rect x="40" y="100" width="140" height="40" fill="rgba(66,133,244,0.1)" stroke="#4285f4" stroke-width="1"/>
            </svg>`,

        // 圓形 (半徑標註)
        circle: (r = 5) => `
            <svg viewBox="0 0 220 220" class="math-diagram">
                <circle cx="110" cy="110" r="80" fill="rgba(66,133,244,0.1)" stroke="#4285f4" stroke-width="2"/>
                <line x1="110" y1="110" x2="190" y2="110" stroke="#ea4335" stroke-width="2"/>
                <text x="150" y="100" font-size="14" fill="#ea4335">r = ${r}cm</text>
                <circle cx="110" cy="110" r="3" fill="#ea4335"/>
            </svg>`,

        // 梯形
        trapezoid: () => `
            <svg viewBox="0 0 260 160" class="math-diagram">
                <polygon points="30,120 230,120 190,40 70,40"
                    fill="rgba(66,133,244,0.15)" stroke="#4285f4" stroke-width="2"/>
                <line x1="30" y1="135" x2="230" y2="135" stroke="#ea4335" stroke-width="2"/>
                <text x="130" y="150" text-anchor="middle" font-size="12" fill="#ea4335">下底</text>
                <line x1="70" y1="28" x2="190" y2="28" stroke="#ea4335" stroke-width="2"/>
                <text x="130" y="22" text-anchor="middle" font-size="12" fill="#ea4335">上底</text>
            </svg>`,

        // 分數圓模型
        fractionCircle: (numerator = 1, denominator = 4) => {
            let sectors = '';
            for (let i = 0; i < numerator; i++) {
                const startAngle = i * (360/denominator);
                const endAngle = (i+1) * (360/denominator);
                const x1 = 100 + 80 * Math.cos(startAngle * Math.PI/180);
                const y1 = 100 + 80 * Math.sin(startAngle * Math.PI/180);
                const x2 = 100 + 80 * Math.cos(endAngle * Math.PI/180);
                const y2 = 100 + 80 * Math.sin(endAngle * Math.PI/180);
                sectors += `<path d="M100,100 L${x1},${y1} A80,80 0 0,1 ${x2},${y2} Z" 
                    fill="rgba(251,188,4,0.4)" stroke="#fbbc04" stroke-width="1"/>`;
            }
            // 分割線
            let lines = '';
            for (let i = 0; i < denominator; i++) {
                const angle = i * (360/denominator) * Math.PI/180;
                const x = 100 + 80 * Math.cos(angle);
                const y = 100 + 80 * Math.sin(angle);
                lines += `<line x1="100" y1="100" x2="${x}" y2="${y}" stroke="#ccc" stroke-width="0.5"/>`;
            }
            return `
            <svg viewBox="0 0 200 200" class="math-diagram">
                <circle cx="100" cy="100" r="80" fill="none" stroke="#4285f4" stroke-width="2"/>
                ${lines}
                ${sectors}
                <text x="100" y="195" text-anchor="middle" font-size="16" fill="#333">
                    ${numerator}/${denominator}
                </text>
            </svg>`;
        },

        // 數線
        numberLine: (start = 0, end = 10, marks = []) => `
            <svg viewBox="0 0 500 60" class="math-diagram">
                <line x1="30" y1="30" x2="470" y2="30" stroke="#333" stroke-width="2"/>
                <polygon points="470,30 460,25 460,35" fill="#333"/>
                ${Array.from({length: end-start+1}, (_,i) => {
                    const x = 30 + (440/(end-start)) * i;
                    const label = start + i;
                    return `<line x1="${x}" y1="25" x2="${x}" y2="35" stroke="#333" stroke-width="1"/>
                        <text x="${x}" y="50" text-anchor="middle" font-size="11">${label}</text>`;
                }).join('')}
                ${marks.map(m => {
                    const x = 30 + (440/(end-start)) * (m.pos - start);
                    return `<circle cx="${x}" cy="30" r="4" fill="${m.color || '#ea4335'}"/>
                        <text x="${x}" y="18" text-anchor="middle" font-size="11" fill="${m.color || '#ea4335'}">${m.label || ''}</text>`;
                }).join('')}
            </svg>`,
    },

    // ========================================
    // Chart.js 數據圖表生成器
    // ========================================
    initChart: function(canvasId, config) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return null;
        const ctx = canvas.getContext('2d');
        return new Chart(ctx, config);
    },

    // 快速棒形圖
    barChart: function(canvasId, labels, values, title = '', yLabel = '') {
        return this.initChart(canvasId, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: title,
                    data: values,
                    backgroundColor: ['#4285f4','#ea4335','#fbbc04','#34a853','#ff6d01','#46bdc6'],
                    borderRadius: 6,
                    borderSkipped: false,
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: { display: !!title, text: title, font: { size: 16 } },
                    legend: { display: false }
                },
                scales: {
                    y: { 
                        beginAtZero: true,
                        title: { display: !!yLabel, text: yLabel },
                        grid: { color: '#e8e8e8' }
                    },
                    x: { grid: { display: false } }
                }
            }
        });
    },

    // 快速折線圖
    lineChart: function(canvasId, labels, values, title = '') {
        return this.initChart(canvasId, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: title,
                    data: values,
                    borderColor: '#4285f4',
                    backgroundColor: 'rgba(66,133,244,0.1)',
                    fill: true,
                    tension: 0.3,
                    pointRadius: 4,
                    pointBackgroundColor: '#4285f4',
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: { display: !!title, text: title, font: { size: 16 } },
                    legend: { display: false }
                },
                scales: {
                    y: { beginAtZero: true, grid: { color: '#e8e8e8' } },
                    x: { grid: { display: false } }
                }
            }
        });
    },

    // 快速圓形圖
    pieChart: function(canvasId, labels, values, title = '') {
        return this.initChart(canvasId, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: ['#4285f4','#ea4335','#fbbc04','#34a853','#ff6d01','#46bdc6'],
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: { display: !!title, text: title, font: { size: 16 } },
                    legend: { position: 'bottom' }
                }
            }
        });
    },

    // ========================================
    // Canvas 2D 進階繪圖
    // ========================================
    drawShape: function(canvasId, drawFn) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        const dpr = window.devicePixelRatio || 1;
        canvas.width = canvas.offsetWidth * dpr;
        canvas.height = canvas.offsetHeight * dpr;
        ctx.scale(dpr, dpr);
        drawFn(ctx, canvas.offsetWidth, canvas.offsetHeight);
    },

    // 互動幾何：可拖動的三角形（驗證面積公式）
    interactiveTriangle: function(canvasId) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        let points = [{x:100,y:250},{x:400,y:250},{x:250,y:50}];
        let dragging = -1;

        function draw() {
            const dpr = window.devicePixelRatio || 1;
            canvas.width = canvas.offsetWidth * dpr;
            canvas.height = canvas.offsetHeight * dpr;
            ctx.scale(dpr, dpr);
            const w = canvas.offsetWidth, h = canvas.offsetHeight;
            
            ctx.clearRect(0,0,w,h);
            // 三角形
            ctx.beginPath();
            ctx.moveTo(points[0].x, points[0].y);
            ctx.lineTo(points[1].x, points[1].y);
            ctx.lineTo(points[2].x, points[2].y);
            ctx.closePath();
            ctx.fillStyle = 'rgba(66,133,244,0.15)';
            ctx.fill();
            ctx.strokeStyle = '#4285f4';
            ctx.lineWidth = 2;
            ctx.stroke();
            
            // 頂點拖動點
            points.forEach((p,i) => {
                ctx.beginPath();
                ctx.arc(p.x, p.y, 8, 0, Math.PI*2);
                ctx.fillStyle = '#ea4335';
                ctx.fill();
            });
            
            // 計算面積
            const area = Math.abs((points[0].x*(points[1].y-points[2].y) + 
                points[1].x*(points[2].y-points[0].y) + 
                points[2].x*(points[0].y-points[1].y))/2);
            
            ctx.fillStyle = '#333';
            ctx.font = '14px sans-serif';
            ctx.fillText(`面積 ≈ ${Math.round(area)} 平方單位`, 10, h-10);
        }

        canvas.addEventListener('mousedown', (e) => {
            const rect = canvas.getBoundingClientRect();
            const mx = e.clientX - rect.left;
            const my = e.clientY - rect.top;
            dragging = points.findIndex(p => 
                Math.hypot(p.x-mx, p.y-my) < 12);
        });
        
        canvas.addEventListener('mousemove', (e) => {
            if (dragging < 0) return;
            const rect = canvas.getBoundingClientRect();
            points[dragging].x = e.clientX - rect.left;
            points[dragging].y = e.clientY - rect.top;
            draw();
        });
        
        canvas.addEventListener('mouseup', () => { dragging = -1; });
        draw();
    }
};

// 自動注入：當頁面有 data-lf-chart 屬性時自動生成圖表
document.addEventListener('DOMContentLoaded', () => {
    // 自動棒形圖
    document.querySelectorAll('[data-lf-chart="bar"]').forEach(el => {
        const labels = JSON.parse(el.dataset.labels || '[]');
        const values = JSON.parse(el.dataset.values || '[]');
        const title = el.dataset.title || '';
        const canvas = document.createElement('canvas');
        el.appendChild(canvas);
        LFGraphics.barChart(canvas, labels, values, title);
    });

    // 自動折線圖
    document.querySelectorAll('[data-lf-chart="line"]').forEach(el => {
        const labels = JSON.parse(el.dataset.labels || '[]');
        const values = JSON.parse(el.dataset.values || '[]');
        const title = el.dataset.title || '';
        const canvas = document.createElement('canvas');
        el.appendChild(canvas);
        LFGraphics.lineChart(canvas.id || ('chart_'+Date.now()), labels, values, title);
    });
});

console.log('LF Graphics Engine loaded - shapes, charts, interactive geometry ready');
