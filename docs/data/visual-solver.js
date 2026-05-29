
// LF Visual Solver — interactive SVG math visualizations
var LFVisual = {
  _currentStep: 0,
  _steps: [],

  // --- Fraction Bar Model ---
  FractionBar: function(container, numerator, denominator, opts) {
    opts = opts || {};
    var w = opts.width || 300;
    var h = opts.height || 60;
    var svgNS = 'http://www.w3.org/2000/svg';
    var svg = document.createElementNS(svgNS, 'svg');
    svg.setAttribute('viewBox', '0 0 ' + w + ' ' + h);
    svg.setAttribute('width', w);
    svg.setAttribute('height', h);
    svg.style.cssText = 'display:block;margin:12px auto';

    // Whole bar outline
    var whole = document.createElementNS(svgNS, 'rect');
    whole.setAttribute('x', 0); whole.setAttribute('y', 5);
    whole.setAttribute('width', w); whole.setAttribute('height', h - 10);
    whole.setAttribute('fill', '#F3F4F6'); whole.setAttribute('stroke', '#9CA3AF');
    whole.setAttribute('stroke-width', 1); whole.setAttribute('rx', 4);
    svg.appendChild(whole);

    // Divider lines
    for (var i = 1; i < denominator; i++) {
      var line = document.createElementNS(svgNS, 'line');
      line.setAttribute('x1', i * w / denominator);
      line.setAttribute('y1', 5);
      line.setAttribute('x2', i * w / denominator);
      line.setAttribute('y2', h - 5);
      line.setAttribute('stroke', '#D1D5DB');
      line.setAttribute('stroke-width', 1);
      line.setAttribute('stroke-dasharray', '4,2');
      svg.appendChild(line);
    }

    // Filled portion (animate in)
    var fillW = (numerator / denominator) * w;
    var fill = document.createElementNS(svgNS, 'rect');
    fill.setAttribute('x', 0); fill.setAttribute('y', 5);
    fill.setAttribute('width', 0); fill.setAttribute('height', h - 10);
    fill.setAttribute('fill', '#C9A84C'); fill.setAttribute('rx', 4);
    fill.setAttribute('opacity', 0.6);
    svg.appendChild(fill);

    // Fraction label on top
    var label = document.createElementNS(svgNS, 'text');
    label.setAttribute('x', w / 2); label.setAttribute('y', h - 16);
    label.setAttribute('text-anchor', 'middle');
    label.setAttribute('font-size', '14'); label.setAttribute('font-weight', '700');
    label.setAttribute('fill', '#1A3C6D');
    label.textContent = numerator + '/' + denominator;
    svg.appendChild(label);

    container.appendChild(svg);

    // Animate fill
    setTimeout(function() {
      fill.style.transition = 'width 0.8s ease-out';
      fill.setAttribute('width', fillW);
    }, 100);

    return svg;
  },

  // --- Area Model (grid) ---
  AreaModel: function(container, cols, rows, opts) {
    opts = opts || {};
    var cellSize = opts.cellSize || 40;
    var w = cols * cellSize;
    var h = rows * cellSize;
    var svgNS = 'http://www.w3.org/2000/svg';
    var svg = document.createElementNS(svgNS, 'svg');
    svg.setAttribute('viewBox', '0 0 ' + (w + 40) + ' ' + (h + 40));
    svg.setAttribute('width', w + 40);
    svg.setAttribute('height', h + 40);
    svg.style.cssText = 'display:block;margin:12px auto';

    // Grid cells
    for (var r = 0; r < rows; r++) {
      for (var c = 0; c < cols; c++) {
        var cell = document.createElementNS(svgNS, 'rect');
        cell.setAttribute('x', c * cellSize + 20);
        cell.setAttribute('y', r * cellSize + 20);
        cell.setAttribute('width', cellSize - 2);
        cell.setAttribute('height', cellSize - 2);
        cell.setAttribute('fill', '#F0F7FF');
        cell.setAttribute('stroke', '#93C5FD');
        cell.setAttribute('stroke-width', 1);
        cell.setAttribute('rx', 3);
        // Animate cell appearance
        cell.setAttribute('opacity', 0);
        setTimeout(function(el) {
          el.setAttribute('opacity', 1);
          el.style.transition = 'opacity 0.3s ease-in';
        }, (r * cols + c) * 50, cell);
        svg.appendChild(cell);
      }
    }

    // Dimensions labels
    var wLabel = document.createElementNS(svgNS, 'text');
    wLabel.setAttribute('x', 20 + w / 2); wLabel.setAttribute('y', h + 34);
    wLabel.setAttribute('text-anchor', 'middle'); wLabel.setAttribute('font-size', '13');
    wLabel.setAttribute('fill', '#1A3C6D'); wLabel.textContent = cols + ' cm';
    svg.appendChild(wLabel);

    var hLabel = document.createElementNS(svgNS, 'text');
    hLabel.setAttribute('x', 10); hLabel.setAttribute('y', 20 + h / 2);
    hLabel.setAttribute('text-anchor', 'middle'); hLabel.setAttribute('font-size', '13');
    hLabel.setAttribute('fill', '#1A3C6D');
    hLabel.setAttribute('transform', 'rotate(-90,10,' + (20 + h / 2) + ')');
    hLabel.textContent = rows + ' cm';
    svg.appendChild(hLabel);

    container.appendChild(svg);
    return svg;
  },

  // --- Number Line ---
  NumberLine: function(container, start, end, opts) {
    opts = opts || {};
    var w = opts.width || 400;
    var svgNS = 'http://www.w3.org/2000/svg';
    var svg = document.createElementNS(svgNS, 'svg');
    svg.setAttribute('viewBox', '0 0 ' + w + ' 80');
    svg.setAttribute('width', w);
    svg.setAttribute('height', 80);
    svg.style.cssText = 'display:block;margin:12px auto';

    // Main line
    var line = document.createElementNS(svgNS, 'line');
    line.setAttribute('x1', 30); line.setAttribute('y1', 40);
    line.setAttribute('x2', w - 10); line.setAttribute('y2', 40);
    line.setAttribute('stroke', '#1A3C6D'); line.setAttribute('stroke-width', 2);
    svg.appendChild(line);

    // Arrows
    var a1 = document.createElementNS(svgNS, 'polygon');
    a1.setAttribute('points', (w - 10) + ',40 ' + (w - 20) + ',35 ' + (w - 20) + ',45');
    a1.setAttribute('fill', '#1A3C6D');
    svg.appendChild(a1);

    // Tick marks and labels
    var range = end - start;
    var step = range <= 10 ? 1 : range <= 20 ? 2 : range <= 50 ? 5 : 10;
    var xScale = (w - 40) / range;
    for (var v = start; v <= end; v += step) {
      var x = 30 + (v - start) * xScale;
      var tick = document.createElementNS(svgNS, 'line');
      tick.setAttribute('x1', x); tick.setAttribute('y1', 35);
      tick.setAttribute('x2', x); tick.setAttribute('y2', 45);
      tick.setAttribute('stroke', '#6B7280'); tick.setAttribute('stroke-width', 1);
      svg.appendChild(tick);

      var tickLabel = document.createElementNS(svgNS, 'text');
      tickLabel.setAttribute('x', x); tickLabel.setAttribute('y', 62);
      tickLabel.setAttribute('text-anchor', 'middle'); tickLabel.setAttribute('font-size', '11');
      tickLabel.setAttribute('fill', '#374151'); tickLabel.textContent = v;
      svg.appendChild(tickLabel);
    }

    // Highlight markers
    if (opts.markers) {
      opts.markers.forEach(function(m, i) {
        var mx = 30 + (m.value - start) * xScale;
        var dot = document.createElementNS(svgNS, 'circle');
        dot.setAttribute('cx', mx); dot.setAttribute('cy', 40);
        dot.setAttribute('r', 0); dot.setAttribute('fill', m.color || '#DC2626');
        svg.appendChild(dot);
        setTimeout(function() {
          dot.setAttribute('r', 6);
          dot.style.transition = 'r 0.3s ease-out';
        }, 300 + i * 200);

        var ml = document.createElementNS(svgNS, 'text');
        ml.setAttribute('x', mx); ml.setAttribute('y', 22);
        ml.setAttribute('text-anchor', 'middle'); ml.setAttribute('font-size', '10');
        ml.setAttribute('font-weight', '700');
        ml.setAttribute('fill', m.color || '#DC2626');
        ml.textContent = m.label || m.value;
        ml.setAttribute('opacity', 0);
        setTimeout(function() { ml.setAttribute('opacity', 1); ml.style.transition = 'opacity 0.3s'; }, 500 + i * 200);
        svg.appendChild(ml);
      });
    }

    container.appendChild(svg);
    return svg;
  },

  // --- Geometry Shape (with measurements) ---
  GeometryShape: function(container, type, params) {
    var svgNS = 'http://www.w3.org/2000/svg';
    var w = params.width || 300, h = params.height || 200;
    var svg = document.createElementNS(svgNS, 'svg');
    svg.setAttribute('viewBox', '0 0 ' + w + ' ' + h);
    svg.setAttribute('width', w); svg.setAttribute('height', h);
    svg.style.cssText = 'display:block;margin:12px auto';

    if (type === 'rectangle') {
      var rw = params.rectWidth || 120, rh = params.rectHeight || 80;
      var rx = (w - rw) / 2, ry = (h - rh) / 2;
      var rect = document.createElementNS(svgNS, 'rect');
      rect.setAttribute('x', rx); rect.setAttribute('y', ry);
      rect.setAttribute('width', rw); rect.setAttribute('height', rh);
      rect.setAttribute('fill', '#DBEAFE'); rect.setAttribute('stroke', '#1A3C6D');
      rect.setAttribute('stroke-width', 2); rect.setAttribute('rx', 4);
      svg.appendChild(rect);

      // Width label
      var wl = document.createElementNS(svgNS, 'text');
      wl.setAttribute('x', rx + rw / 2); wl.setAttribute('y', ry + rh + 20);
      wl.setAttribute('text-anchor', 'middle'); wl.setAttribute('font-size', '13');
      wl.setAttribute('font-weight', '700'); wl.setAttribute('fill', '#DC2626');
      wl.textContent = (params.labelWidth || rw / 10) + ' cm';
      svg.appendChild(wl);

      // Height label
      var hl = document.createElementNS(svgNS, 'text');
      hl.setAttribute('x', rx - 14); hl.setAttribute('y', ry + rh / 2);
      hl.setAttribute('text-anchor', 'middle'); hl.setAttribute('font-size', '13');
      hl.setAttribute('font-weight', '700'); hl.setAttribute('fill', '#DC2626');
      hl.setAttribute('transform', 'rotate(-90,' + (rx - 14) + ',' + (ry + rh / 2) + ')');
      hl.textContent = (params.labelHeight || rh / 10) + ' cm';
      svg.appendChild(hl);

      // Dimension arrows
      // Width arrow
      var awl = document.createElementNS(svgNS, 'line');
      awl.setAttribute('x1', rx); awl.setAttribute('y1', ry + rh + 10);
      awl.setAttribute('x2', rx + rw); awl.setAttribute('y2', ry + rh + 10);
      awl.setAttribute('stroke', '#DC2626'); awl.setAttribute('stroke-width', 1);
      awl.setAttribute('marker-start', 'url(#arrowhead)'); awl.setAttribute('marker-end', 'url(#arrowhead)');
      svg.appendChild(awl);
    }

    if (type === 'triangle') {
      var base = params.base || 120, triH = params.triHeight || 90;
      var x0 = (w - base) / 2, y0 = h - 30;
      var points = x0 + ',' + y0 + ' ' + (x0 + base) + ',' + y0 + ' ' + (x0 + base / 2) + ',' + (y0 - triH);
      var tri = document.createElementNS(svgNS, 'polygon');
      tri.setAttribute('points', points);
      tri.setAttribute('fill', '#D1FAE5'); tri.setAttribute('stroke', '#065F46');
      tri.setAttribute('stroke-width', 2);
      svg.appendChild(tri);

      // Right angle marker
      if (params.rightAngle) {
        var ra = document.createElementNS(svgNS, 'polyline');
        ra.setAttribute('points', x0 + ', ' + (y0 - 15) + ' ' + (x0 + 15) + ', ' + (y0 - 15) + ' ' + (x0 + 15) + ', ' + y0);
        ra.setAttribute('fill', 'none'); ra.setAttribute('stroke', '#065F46');
        ra.setAttribute('stroke-width', 1);
        svg.appendChild(ra);
      }
    }

    if (type === 'circle') {
      var r = params.radius || 50;
      var cx = w / 2, cy = h / 2;
      var circle = document.createElementNS(svgNS, 'circle');
      circle.setAttribute('cx', cx); circle.setAttribute('cy', cy);
      circle.setAttribute('r', r);
      circle.setAttribute('fill', '#FEF3C7'); circle.setAttribute('stroke', '#92400E');
      circle.setAttribute('stroke-width', 2);
      svg.appendChild(circle);

      // Radius line
      var rl = document.createElementNS(svgNS, 'line');
      rl.setAttribute('x1', cx); rl.setAttribute('y1', cy);
      rl.setAttribute('x2', cx + r); rl.setAttribute('y2', cy);
      rl.setAttribute('stroke', '#DC2626'); rl.setAttribute('stroke-width', 1);
      rl.setAttribute('stroke-dasharray', '4,2');
      svg.appendChild(rl);

      // Center dot
      var cd = document.createElementNS(svgNS, 'circle');
      cd.setAttribute('cx', cx); cd.setAttribute('cy', cy);
      cd.setAttribute('r', 3); cd.setAttribute('fill', '#DC2626');
      svg.appendChild(cd);

      // R label
      var rLabel = document.createElementNS(svgNS, 'text');
      rLabel.setAttribute('x', cx + r / 2); rLabel.setAttribute('y', cy - 8);
      rLabel.setAttribute('text-anchor', 'middle'); rLabel.setAttribute('font-size', '12');
      rLabel.setAttribute('font-weight', '700'); rLabel.setAttribute('fill', '#DC2626');
      rLabel.textContent = 'r=' + r / 10 + 'cm';
      svg.appendChild(rLabel);
    }

    container.appendChild(svg);
    return svg;
  },

  // --- Step-by-Step Solution Walkthrough ---
  SolutionSteps: function(container, steps) {
    this._steps = steps;
    this._currentStep = 0;
    container.innerHTML = '';
    container.style.cssText = 'background:white;border-radius:14px;padding:20px;font-size:14px;line-height:2';

    var self = this;

    // Step content area
    var content = document.createElement('div');
    content.id = 'lf-solution-content';
    content.style.cssText = 'min-height:200px;padding:16px;background:#F9FAFB;border-radius:10px;margin-bottom:12px';
    container.appendChild(content);

    // Step indicator dots
    var dots = document.createElement('div');
    dots.id = 'lf-solution-dots';
    dots.style.cssText = 'display:flex;gap:8px;justify-content:center;margin:12px 0';
    steps.forEach(function(s, i) {
      var dot = document.createElement('div');
      dot.style.cssText = 'width:10px;height:10px;border-radius:50%;background:#E5E7EB;transition:all 0.3s';
      dot.setAttribute('data-step', i);
      dots.appendChild(dot);
    });
    container.appendChild(dots);

    // Navigation buttons
    var nav = document.createElement('div');
    nav.style.cssText = 'display:flex;gap:8px;justify-content:center;flex-wrap:wrap';

    var prevBtn = document.createElement('button');
    prevBtn.textContent = '← 上一步';
    prevBtn.style.cssText = 'padding:8px 16px;border-radius:20px;border:2px solid #E5E7EB;background:white;cursor:pointer;font-weight:700;font-size:12px;font-family:inherit';
    prevBtn.onclick = function() { self.prevStep(); };

    var nextBtn = document.createElement('button');
    nextBtn.textContent = '下一步 →';
    nextBtn.style.cssText = 'padding:8px 16px;border-radius:20px;border:none;background:#1A3C6D;color:white;cursor:pointer;font-weight:700;font-size:12px;font-family:inherit';
    nextBtn.onclick = function() { self.nextStep(); };

    var resetBtn = document.createElement('button');
    resetBtn.textContent = '← 重置';
    resetBtn.style.cssText = 'padding:8px 16px;border-radius:20px;border:2px solid #E5E7EB;background:white;cursor:pointer;font-weight:700;font-size:12px;font-family:inherit';
    resetBtn.onclick = function() { self._currentStep = 0; self._renderStep(); };

    nav.appendChild(prevBtn);
    nav.appendChild(resetBtn);
    nav.appendChild(nextBtn);
    container.appendChild(nav);

    this._container = container;
    this._renderStep();
  },

  _renderStep: function() {
    var content = document.getElementById('lf-solution-content');
    var dots = document.getElementById('lf-solution-dots');
    if (!content || !dots) return;

    var step = this._steps[this._currentStep];
    content.innerHTML = '<div style="font-weight:900;color:#C9A84C;margin-bottom:8px">步驟 ' + (this._currentStep + 1) + '/' + this._steps.length + '</div>' +
                        '<div style="font-size:14px;color:#374151;margin-bottom:10px">' + step.text + '</div>' +
                        '<div id="lf-step-viz"></div>';

    // Render visualization if specified
    var vizContainer = document.getElementById('lf-step-viz');
    if (step.viz && vizContainer) {
      if (step.viz.type === 'fraction') {
        this.FractionBar(vizContainer, step.viz.numerator, step.viz.denominator, step.viz.opts);
      } else if (step.viz.type === 'area') {
        this.AreaModel(vizContainer, step.viz.cols, step.viz.rows, step.viz.opts);
      } else if (step.viz.type === 'numberline') {
        this.NumberLine(vizContainer, step.viz.start, step.viz.end, step.viz.opts);
      } else if (step.viz.type === 'geometry') {
        this.GeometryShape(vizContainer, step.viz.shape, step.viz.params);
      }
    }

    // Update dots
    var dotEls = dots.querySelectorAll('div');
    dotEls.forEach(function(d, i) {
      if (i < this._currentStep) d.style.background = '#16A34A';
      else if (i === this._currentStep) d.style.background = '#C9A84C';
      else d.style.background = '#E5E7EB';
    }, this);

    // Update buttons
    var buttons = this._container.querySelectorAll('button');
    buttons[0].disabled = this._currentStep === 0;
    buttons[0].style.opacity = this._currentStep === 0 ? '0.3' : '1';
    buttons[2].textContent = this._currentStep >= this._steps.length - 1 ? '🏁 完成' : '下一步 →';
  },

  nextStep: function() {
    if (this._currentStep < this._steps.length - 1) {
      this._currentStep++;
      this._renderStep();
    }
  },

  prevStep: function() {
    if (this._currentStep > 0) {
      this._currentStep--;
      this._renderStep();
    }
  },

  // --- All-in-one: create a demo with FractionBar + NumberLine for a fraction problem ---
  FractionDemo: function(container, numerator, denominator, operation, operand) {
    container.innerHTML = '';
    var steps = [
      {
        text: '第一步：視覺化分數 <b>' + numerator + '/' + denominator + '</b>',
        viz: {type: 'fraction', numerator: numerator, denominator: denominator}
      },
      {
        text: '第二步：在數線上找到位置',
        viz: {
          type: 'numberline', start: 0, end: Math.max(denominator, 10),
          opts: {markers: [{value: numerator, label: numerator + '/' + denominator, color: '#DC2626'}]}
        }
      },
    ];
    if (operation && operand) {
      steps.push({
        text: '第三步：執行 <b>' + operation + '</b> 運算',
        viz: {type: 'numberline', start: 0, end: Math.max(denominator + operand, 10),
              opts: {markers: [
                {value: numerator, label: numerator + '/' + denominator, color: '#DC2626'},
                {value: operation === '+' ? numerator + operand : numerator - operand,
                 label: '結果', color: '#16A34A'}
              ]}}
      });
    }
    this.SolutionSteps(container, steps);
  }
};
