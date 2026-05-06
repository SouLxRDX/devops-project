from flask import Flask, render_template_string

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SNAKE // NEON</title>
<link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@700;900&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #020408;
    --grid: #0a1628;
    --neon-green: #00ff88;
    --neon-pink: #ff0066;
    --neon-blue: #00cfff;
    --neon-yellow: #ffe600;
    --text: #e0ffe0;
  }

  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: 'Share Tech Mono', monospace;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    overflow: hidden;
  }

  body::after {
    content: '';
    position: fixed;
    inset: 0;
    background: repeating-linear-gradient(
      0deg, transparent, transparent 2px,
      rgba(0,0,0,0.08) 2px, rgba(0,0,0,0.08) 4px
    );
    pointer-events: none;
    z-index: 100;
  }

  body::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
      linear-gradient(rgba(0,255,136,0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(0,255,136,0.03) 1px, transparent 1px);
    background-size: 40px 40px;
    animation: gridMove 20s linear infinite;
    z-index: -1;
  }

  @keyframes gridMove {
    0% { transform: translateY(0); }
    100% { transform: translateY(40px); }
  }

  .wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1.2rem;
  }

  .title {
    font-family: 'Orbitron', monospace;
    font-size: clamp(1.8rem, 5vw, 3rem);
    font-weight: 900;
    letter-spacing: 0.3em;
    color: var(--neon-green);
    text-shadow: 0 0 10px var(--neon-green), 0 0 30px var(--neon-green), 0 0 60px rgba(0,255,136,0.4);
    animation: flicker 4s infinite;
  }

  @keyframes flicker {
    0%, 95%, 100% { opacity: 1; }
    96% { opacity: 0.6; }
    97% { opacity: 1; }
    98% { opacity: 0.4; }
    99% { opacity: 1; }
  }

  .hud {
    display: flex;
    gap: 2.5rem;
    width: 100%;
    justify-content: space-between;
    padding: 0 4px;
  }

  .hud-item { display: flex; flex-direction: column; gap: 2px; }
  .hud-label { font-size: 0.6rem; letter-spacing: 0.2em; color: rgba(0,255,136,0.5); text-transform: uppercase; }
  .hud-value { font-family: 'Orbitron', monospace; font-size: 1.3rem; font-weight: 700; color: var(--neon-green); text-shadow: 0 0 10px var(--neon-green); }

  .canvas-wrapper {
    position: relative;
    border: 1px solid rgba(0,255,136,0.3);
    box-shadow: 0 0 20px rgba(0,255,136,0.2), 0 0 60px rgba(0,255,136,0.1), inset 0 0 20px rgba(0,255,136,0.05);
    border-radius: 4px;
  }

  canvas { display: block; background: var(--grid); border-radius: 3px; }

  .overlay {
    position: absolute;
    inset: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: rgba(2,4,8,0.88);
    border-radius: 3px;
    gap: 1rem;
    backdrop-filter: blur(2px);
  }

  .overlay.hidden { display: none; }

  .overlay-title {
    font-family: 'Orbitron', monospace;
    font-size: clamp(1.2rem, 3vw, 2rem);
    font-weight: 900;
    color: var(--neon-pink);
    text-shadow: 0 0 20px var(--neon-pink), 0 0 40px rgba(255,0,102,0.5);
    letter-spacing: 0.2em;
    text-align: center;
  }

  .overlay-score {
    font-family: 'Orbitron', monospace;
    font-size: 0.9rem;
    color: var(--neon-blue);
    text-shadow: 0 0 10px var(--neon-blue);
    letter-spacing: 0.1em;
  }

  .start-btn {
    background: transparent;
    border: 2px solid var(--neon-green);
    color: var(--neon-green);
    font-family: 'Orbitron', monospace;
    font-size: 0.85rem;
    font-weight: 700;
    letter-spacing: 0.2em;
    padding: 0.7rem 2rem;
    cursor: pointer;
    border-radius: 2px;
    text-transform: uppercase;
    transition: all 0.2s;
    text-shadow: 0 0 10px var(--neon-green);
    box-shadow: 0 0 10px rgba(0,255,136,0.2), inset 0 0 10px rgba(0,255,136,0.05);
    margin-top: 0.5rem;
  }

  .start-btn:hover {
    background: rgba(0,255,136,0.15);
    box-shadow: 0 0 25px rgba(0,255,136,0.5);
    transform: scale(1.05);
  }

  .controls-hint { font-size: 0.65rem; color: rgba(0,255,136,0.35); letter-spacing: 0.15em; text-align: center; line-height: 1.8; }
  .level-badge { font-family: 'Orbitron', monospace; font-size: 0.7rem; color: var(--neon-yellow); text-shadow: 0 0 8px var(--neon-yellow); letter-spacing: 0.2em; }

  .mobile-controls {
    display: none;
    grid-template-columns: repeat(3, 52px);
    grid-template-rows: repeat(2, 52px);
    gap: 6px;
  }

  @media (max-width: 600px) { .mobile-controls { display: grid; } }

  .dpad {
    background: rgba(0,255,136,0.08);
    border: 1px solid rgba(0,255,136,0.3);
    color: var(--neon-green);
    font-size: 1.2rem;
    border-radius: 6px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.1s;
    -webkit-tap-highlight-color: transparent;
    user-select: none;
  }

  .dpad:active { background: rgba(0,255,136,0.25); box-shadow: 0 0 12px rgba(0,255,136,0.4); }
  .dpad-up    { grid-column: 2; grid-row: 1; }
  .dpad-left  { grid-column: 1; grid-row: 2; }
  .dpad-down  { grid-column: 2; grid-row: 2; }
  .dpad-right { grid-column: 3; grid-row: 2; }
</style>
</head>
<body>
<div class="wrapper">
  <div class="title">// SNAKE //</div>

  <div class="hud">
    <div class="hud-item">
      <span class="hud-label">Score</span>
      <span class="hud-value" id="scoreDisplay">000</span>
    </div>
    <div class="hud-item" style="align-items:center">
      <span class="hud-label">Level</span>
      <span class="hud-value" id="levelDisplay">1</span>
    </div>
    <div class="hud-item" style="align-items:flex-end">
      <span class="hud-label">Best</span>
      <span class="hud-value" id="bestDisplay">000</span>
    </div>
  </div>

  <div class="canvas-wrapper">
    <canvas id="gameCanvas"></canvas>
    <div class="overlay" id="overlay">
      <div class="overlay-title" id="overlayTitle">SNAKE</div>
      <div class="overlay-score" id="overlayScore">NEON EDITION</div>
      <div class="level-badge" id="overlayLevel"></div>
      <button class="start-btn" id="startBtn" onclick="startGame()">[ START GAME ]</button>
      <div class="controls-hint">ARROW KEYS / WASD TO MOVE<br>P TO PAUSE</div>
    </div>
  </div>

  <div class="mobile-controls">
    <button class="dpad dpad-up"    onclick="setDir(0,-1)">▲</button>
    <button class="dpad dpad-left"  onclick="setDir(-1,0)">◀</button>
    <button class="dpad dpad-down"  onclick="setDir(0,1)">▼</button>
    <button class="dpad dpad-right" onclick="setDir(1,0)">▶</button>
  </div>
</div>

<script>
  const canvas = document.getElementById('gameCanvas');
  const ctx = canvas.getContext('2d');

  const maxSize = Math.min(window.innerWidth - 40, window.innerHeight - 260, 480);
  const COLS = 20, ROWS = 20;
  const CELL = Math.floor(maxSize / COLS);
  canvas.width  = COLS * CELL;
  canvas.height = ROWS * CELL;

  let snake, dir, nextDir, food, score, best, level, speed, gameLoop, running, paused;

  best = parseInt(localStorage.getItem('snakeBest') || '0');
  document.getElementById('bestDisplay').textContent = String(best).padStart(3,'0');

  function init() {
    snake   = [{x:10,y:10},{x:9,y:10},{x:8,y:10}];
    dir     = {x:1,y:0};
    nextDir = {x:1,y:0};
    score   = 0;
    level   = 1;
    speed   = 150;
    running = false;
    paused  = false;
    spawnFood();
    updateHUD();
    drawFrame();
  }

  function spawnFood() {
    let pos;
    do { pos = {x:Math.floor(Math.random()*COLS), y:Math.floor(Math.random()*ROWS)}; }
    while (snake.some(s => s.x===pos.x && s.y===pos.y));
    food = pos;
  }

  function startGame() {
    document.getElementById('overlay').classList.add('hidden');
    init();
    running = true;
    if (gameLoop) clearTimeout(gameLoop);
    tick();
  }

  function tick() {
    if (!running || paused) return;
    update();
    drawFrame();
    gameLoop = setTimeout(tick, speed);
  }

  function update() {
    dir = {...nextDir};
    const head = {x: snake[0].x + dir.x, y: snake[0].y + dir.y};
    if (head.x < 0 || head.x >= COLS || head.y < 0 || head.y >= ROWS) return gameOver();
    if (snake.some(s => s.x===head.x && s.y===head.y)) return gameOver();
    snake.unshift(head);
    if (head.x === food.x && head.y === food.y) {
      score += 10 * level;
      if (score > best) { best = score; localStorage.setItem('snakeBest', best); }
      spawnFood();
      if (snake.length % 5 === 0) { level++; speed = Math.max(60, speed - 12); }
      updateHUD();
    } else {
      snake.pop();
    }
  }

  function drawFrame() {
    ctx.fillStyle = '#0a1628';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.strokeStyle = 'rgba(0,255,136,0.04)';
    ctx.lineWidth = 0.5;
    for (let x = 0; x <= COLS; x++) { ctx.beginPath(); ctx.moveTo(x*CELL,0); ctx.lineTo(x*CELL,canvas.height); ctx.stroke(); }
    for (let y = 0; y <= ROWS; y++) { ctx.beginPath(); ctx.moveTo(0,y*CELL); ctx.lineTo(canvas.width,y*CELL); ctx.stroke(); }

    if (food) {
      ctx.save();
      ctx.shadowColor = '#ff0066';
      ctx.shadowBlur = 18;
      ctx.fillStyle = '#ff0066';
      ctx.beginPath();
      ctx.arc(food.x*CELL+CELL/2, food.y*CELL+CELL/2, CELL/2-CELL*0.18, 0, Math.PI*2);
      ctx.fill();
      ctx.shadowBlur = 5;
      ctx.fillStyle = '#ffaacc';
      ctx.beginPath();
      ctx.arc(food.x*CELL+CELL/2-2, food.y*CELL+CELL/2-2, CELL*0.12, 0, Math.PI*2);
      ctx.fill();
      ctx.restore();
    }

    snake.forEach((seg, i) => {
      ctx.save();
      const isHead = i === 0;
      const t = 1 - (i / snake.length) * 0.6;
      ctx.shadowColor = isHead ? '#00ff88' : '#00cc66';
      ctx.shadowBlur  = isHead ? 18 : 8;
      const green = Math.floor(200 + 55 * t);
      ctx.fillStyle = isHead ? '#00ff88' : `rgb(0,${green},${Math.floor(80*t)})`;
      const pad = isHead ? CELL*0.06 : CELL*0.12;
      roundRect(ctx, seg.x*CELL+pad, seg.y*CELL+pad, CELL-pad*2, CELL-pad*2, isHead ? 4 : 3);
      ctx.fill();
      if (isHead) {
        ctx.shadowBlur = 0;
        ctx.fillStyle = '#020408';
        const cx = seg.x*CELL+CELL/2, cy = seg.y*CELL+CELL/2;
        const eyeR = CELL*0.1, offset = CELL*0.18;
        const px = dir.y, py = -dir.x;
        ctx.beginPath(); ctx.arc(cx+dir.x*offset+px*offset, cy+dir.y*offset+py*offset, eyeR, 0, Math.PI*2); ctx.fill();
        ctx.beginPath(); ctx.arc(cx+dir.x*offset-px*offset, cy+dir.y*offset-py*offset, eyeR, 0, Math.PI*2); ctx.fill();
      }
      ctx.restore();
    });
  }

  function roundRect(ctx, x, y, w, h, r) {
    ctx.beginPath();
    ctx.moveTo(x+r,y); ctx.lineTo(x+w-r,y); ctx.quadraticCurveTo(x+w,y,x+w,y+r);
    ctx.lineTo(x+w,y+h-r); ctx.quadraticCurveTo(x+w,y+h,x+w-r,y+h);
    ctx.lineTo(x+r,y+h); ctx.quadraticCurveTo(x,y+h,x,y+h-r);
    ctx.lineTo(x,y+r); ctx.quadraticCurveTo(x,y,x+r,y);
    ctx.closePath();
  }

  function gameOver() {
    running = false;
    clearTimeout(gameLoop);
    let flashes = 0;
    const fi = setInterval(() => {
      ctx.fillStyle = `rgba(255,0,102,${0.15 - flashes*0.02})`;
      ctx.fillRect(0,0,canvas.width,canvas.height);
      flashes++;
      if (flashes > 6) {
        clearInterval(fi);
        document.getElementById('overlayTitle').textContent = 'GAME OVER';
        document.getElementById('overlayScore').textContent = `SCORE: ${String(score).padStart(3,'0')}  |  BEST: ${String(best).padStart(3,'0')}`;
        document.getElementById('overlayLevel').textContent = `LEVEL ${level} REACHED`;
        document.getElementById('startBtn').textContent = '[ PLAY AGAIN ]';
        document.getElementById('overlay').classList.remove('hidden');
      }
    }, 80);
  }

  function updateHUD() {
    document.getElementById('scoreDisplay').textContent = String(score).padStart(3,'0');
    document.getElementById('levelDisplay').textContent = level;
    document.getElementById('bestDisplay').textContent  = String(best).padStart(3,'0');
  }

  function setDir(x, y) {
    if (!running) return;
    if (x === -dir.x && y === -dir.y) return;
    nextDir = {x, y};
  }

  document.addEventListener('keydown', e => {
    const map = {
      'ArrowUp':[0,-1],'w':[0,-1],'W':[0,-1],
      'ArrowDown':[0,1],'s':[0,1],'S':[0,1],
      'ArrowLeft':[-1,0],'a':[-1,0],'A':[-1,0],
      'ArrowRight':[1,0],'d':[1,0],'D':[1,0],
    };
    if (map[e.key]) { e.preventDefault(); setDir(...map[e.key]); }
    if (e.key==='p'||e.key==='P') { if (!running) return; paused=!paused; if (!paused) tick(); }
  });

  init();
  drawFrame();
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/health')
def health():
    return {"status": "running", "game": "snake"}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)