from flask import Flask, Response

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Flappy Modi</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Tiro+Devanagari+Hindi&family=Bebas+Neue&display=swap');

  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    background: #0a0a0a;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100vh;
    font-family: 'Bebas Neue', sans-serif;
    overflow: hidden;
  }

  h1 {
    color: #FF9933;
    font-size: 2.5rem;
    letter-spacing: 4px;
    text-shadow: 0 0 20px #FF9933, 0 0 40px #FF6600;
    margin-bottom: 10px;
  }

  #score-display {
    color: #ffffff;
    font-size: 1.2rem;
    letter-spacing: 3px;
    margin-bottom: 15px;
    text-shadow: 0 0 10px #138808;
  }

  canvas {
    border: 3px solid #FF9933;
    border-radius: 4px;
    box-shadow: 0 0 30px #FF9933, 0 0 60px #FF660055;
    background: #000;
  }

  #message {
    margin-top: 15px;
    font-size: 1.4rem;
    color: #FF9933;
    letter-spacing: 3px;
    text-shadow: 0 0 15px #FF9933;
    min-height: 30px;
    text-align: center;
  }

  #instructions {
    margin-top: 8px;
    color: #888;
    font-size: 0.9rem;
    letter-spacing: 2px;
  }
</style>
</head>
<body>

<h1>🇮🇳 FLAPPY MODI 🇮🇳</h1>
<div id="score-display">SCORE: <span id="score">0</span> &nbsp;|&nbsp; BEST: <span id="best">0</span></div>
<canvas id="canvas" width="400" height="500"></canvas>
<div id="message">PRESS SPACE OR TAP TO START</div>
<div id="instructions">SPACE / CLICK / TAP TO FLAP</div>

<script>
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const msg = document.getElementById('message');
const scoreEl = document.getElementById('score');
const bestEl = document.getElementById('best');

const W = canvas.width, H = canvas.height;

// Game state
let state = 'idle'; // idle, playing, dead
let score = 0, best = 0;
let frame = 0;

// Modi bird
const bird = {
  x: 80, y: H / 2,
  vy: 0,
  gravity: 0.45,
  flapStrength: -8,
  size: 36,
  flap() { this.vy = this.flapStrength; }
};

// Pipes (Congress flags)
let pipes = [];
const PIPE_W = 52;
const PIPE_GAP = 150;
const PIPE_SPEED = 2.8;
let pipeTimer = 0;
const PIPE_INTERVAL = 95;

// Particles
let particles = [];

// Colors
const IND_ORANGE = '#FF9933';
const IND_WHITE  = '#FFFFFF';
const IND_GREEN  = '#138808';
const CONGRESS_BLUE = '#1a47a0';
const CONGRESS_HAND = '#ffffff';

function reset() {
  bird.y = H / 2;
  bird.vy = 0;
  pipes = [];
  particles = [];
  score = 0;
  pipeTimer = 0;
  frame = 0;
  scoreEl.textContent = 0;
  msg.textContent = '';
}

function spawnPipe() {
  const top = 80 + Math.random() * (H - PIPE_GAP - 160);
  pipes.push({ x: W + 10, top, bottom: top + PIPE_GAP, scored: false });
}

function drawBackground() {
  // Sky gradient
  const sky = ctx.createLinearGradient(0, 0, 0, H);
  sky.addColorStop(0, '#0a0020');
  sky.addColorStop(1, '#001a0a');
  ctx.fillStyle = sky;
  ctx.fillRect(0, 0, W, H);

  // Subtle stars
  ctx.fillStyle = 'rgba(255,255,255,0.4)';
  for (let i = 0; i < 40; i++) {
    const sx = (i * 137 + frame * 0.1) % W;
    const sy = (i * 97) % (H * 0.6);
    ctx.fillRect(sx, sy, 1, 1);
  }

  // Ground
  ctx.fillStyle = '#1a0a00';
  ctx.fillRect(0, H - 30, W, 30);
  ctx.fillStyle = IND_GREEN;
  ctx.fillRect(0, H - 30, W, 4);
}

function drawCongressFlag(x, y, w, h, flipped) {
  // Flag pole
  ctx.fillStyle = '#888';
  if (!flipped) {
    ctx.fillRect(x + w/2 - 3, y, 6, h);
  } else {
    ctx.fillRect(x + w/2 - 3, y, 6, h);
  }

  // Flag body - Congress tricolor (blue/white/green horizontal)
  const fW = w - 10, fH = Math.min(60, h * 0.4);
  const fX = x + 5;
  const fY = flipped ? y + h - fH - 10 : y + 10;

  ctx.fillStyle = CONGRESS_BLUE;
  ctx.fillRect(fX, fY, fW, fH / 3);
  ctx.fillStyle = IND_WHITE;
  ctx.fillRect(fX, fY + fH/3, fW, fH/3);
  ctx.fillStyle = IND_GREEN;
  ctx.fillRect(fX, fY + 2*fH/3, fW, fH/3);

  // Hand symbol on white band
  ctx.fillStyle = CONGRESS_BLUE;
  ctx.font = `bold ${fH * 0.28}px Arial`;
  ctx.textAlign = 'center';
  ctx.fillText('✋', fX + fW/2, fY + fH/3 + fH/3 * 0.75);

  // Pipe body glow
  const grad = ctx.createLinearGradient(x, 0, x + w, 0);
  grad.addColorStop(0, 'rgba(26,71,160,0.9)');
  grad.addColorStop(0.5, 'rgba(60,110,200,0.95)');
  grad.addColorStop(1, 'rgba(26,71,160,0.9)');
  ctx.fillStyle = grad;
  ctx.fillRect(x, y, w, h);

  // Re-draw flag on top of pipe
  ctx.fillStyle = CONGRESS_BLUE;
  ctx.fillRect(fX, fY, fW, fH / 3);
  ctx.fillStyle = IND_WHITE;
  ctx.fillRect(fX, fY + fH/3, fW, fH/3);
  ctx.fillStyle = IND_GREEN;
  ctx.fillRect(fX, fY + 2*fH/3, fW, fH/3);
  ctx.fillStyle = CONGRESS_BLUE;
  ctx.font = `bold ${fH * 0.28}px Arial`;
  ctx.textAlign = 'center';
  ctx.fillText('✋', fX + fW/2, fY + fH/3 + fH/3 * 0.75);

  // Pipe border glow
  ctx.strokeStyle = 'rgba(100,150,255,0.6)';
  ctx.lineWidth = 2;
  ctx.strokeRect(x, y, w, h);
}

function drawPipes() {
  pipes.forEach(p => {
    // Top pipe (upside down)
    drawCongressFlag(p.x, 0, PIPE_W, p.top, true);
    // Bottom pipe
    drawCongressFlag(p.x, p.bottom, PIPE_W, H - p.bottom - 30, false);
  });
}

function drawModi() {
  const { x, y, size } = bird;
  const tilt = Math.max(-30, Math.min(30, bird.vy * 3));

  ctx.save();
  ctx.translate(x, y);
  ctx.rotate(tilt * Math.PI / 180);

  // Body (kurta - saffron/white)
  ctx.fillStyle = IND_WHITE;
  ctx.beginPath();
  ctx.ellipse(0, 4, size * 0.55, size * 0.65, 0, 0, Math.PI * 2);
  ctx.fill();

  // Modi jacket (navy blue)
  ctx.fillStyle = '#1a237e';
  ctx.beginPath();
  ctx.ellipse(0, 6, size * 0.42, size * 0.5, 0, 0, Math.PI * 2);
  ctx.fill();

  // Face
  ctx.fillStyle = '#D4956A';
  ctx.beginPath();
  ctx.arc(0, -size * 0.2, size * 0.38, 0, Math.PI * 2);
  ctx.fill();

  // Modi white hair
  ctx.fillStyle = '#f0f0f0';
  ctx.beginPath();
  ctx.arc(0, -size * 0.35, size * 0.3, Math.PI, 0);
  ctx.fill();

  // Modi white beard
  ctx.fillStyle = '#e8e8e8';
  ctx.beginPath();
  ctx.ellipse(0, -size * 0.05, size * 0.28, size * 0.22, 0, 0, Math.PI * 2);
  ctx.fill();

  // Eyes
  ctx.fillStyle = '#1a0000';
  ctx.beginPath();
  ctx.arc(-size * 0.12, -size * 0.22, size * 0.06, 0, Math.PI * 2);
  ctx.fill();
  ctx.beginPath();
  ctx.arc(size * 0.12, -size * 0.22, size * 0.06, 0, Math.PI * 2);
  ctx.fill();

  // Glasses
  ctx.strokeStyle = '#8B4513';
  ctx.lineWidth = 1.5;
  ctx.strokeRect(-size * 0.22, -size * 0.28, size * 0.18, size * 0.12);
  ctx.strokeRect(size * 0.04, -size * 0.28, size * 0.18, size * 0.12);
  ctx.beginPath();
  ctx.moveTo(-size * 0.04, -size * 0.22);
  ctx.lineTo(size * 0.04, -size * 0.22);
  ctx.stroke();

  // Orange aura glow when flapping
  if (bird.vy < -3) {
    ctx.shadowColor = IND_ORANGE;
    ctx.shadowBlur = 20;
    ctx.strokeStyle = IND_ORANGE;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(0, 0, size * 0.75, 0, Math.PI * 2);
    ctx.stroke();
    ctx.shadowBlur = 0;
  }

  ctx.restore();
}

function spawnParticles(x, y) {
  for (let i = 0; i < 18; i++) {
    const angle = Math.random() * Math.PI * 2;
    const speed = 2 + Math.random() * 4;
    particles.push({
      x, y,
      vx: Math.cos(angle) * speed,
      vy: Math.sin(angle) * speed,
      life: 1,
      color: [IND_ORANGE, IND_WHITE, IND_GREEN][Math.floor(Math.random() * 3)]
    });
  }
}

function updateParticles() {
  particles = particles.filter(p => p.life > 0);
  particles.forEach(p => {
    p.x += p.vx;
    p.y += p.vy;
    p.vy += 0.15;
    p.life -= 0.03;
    ctx.globalAlpha = p.life;
    ctx.fillStyle = p.color;
    ctx.fillRect(p.x, p.y, 4, 4);
    ctx.globalAlpha = 1;
  });
}

function checkCollision(p) {
  const r = bird.size * 0.4;
  const bx = bird.x, by = bird.y;
  if (bx + r > p.x && bx - r < p.x + PIPE_W) {
    if (by - r < p.top || by + r > p.bottom) return true;
  }
  if (by + r > H - 30) return true;
  if (by - r < 0) return true;
  return false;
}

function drawHUD() {
  // Score
  ctx.fillStyle = IND_ORANGE;
  ctx.font = 'bold 28px Bebas Neue';
  ctx.textAlign = 'center';
  ctx.shadowColor = IND_ORANGE;
  ctx.shadowBlur = 10;
  ctx.fillText(score, W / 2, 45);
  ctx.shadowBlur = 0;
}

function drawDeathScreen() {
  ctx.fillStyle = 'rgba(0,0,0,0.7)';
  ctx.fillRect(0, 0, W, H);

  ctx.textAlign = 'center';

  ctx.fillStyle = IND_ORANGE;
  ctx.font = 'bold 42px Bebas Neue';
  ctx.shadowColor = '#FF0000';
  ctx.shadowBlur = 20;
  ctx.fillText('ABKI BAAR...', W/2, H/2 - 60);

  ctx.fillStyle = '#FF4444';
  ctx.font = 'bold 36px Bebas Neue';
  ctx.fillText('GAME OVER! 😭', W/2, H/2 - 15);
  ctx.shadowBlur = 0;

  ctx.fillStyle = IND_WHITE;
  ctx.font = '22px Bebas Neue';
  ctx.fillText(`SCORE: ${score}`, W/2, H/2 + 30);

  if (score >= best && score > 0) {
    ctx.fillStyle = IND_GREEN;
    ctx.font = '20px Bebas Neue';
    ctx.fillText('🏆 NEW BEST!', W/2, H/2 + 60);
  }

  ctx.fillStyle = '#aaa';
  ctx.font = '18px Bebas Neue';
  ctx.fillText('PRESS SPACE / TAP TO RETRY', W/2, H/2 + 100);
}

function drawIdleScreen() {
  ctx.textAlign = 'center';
  ctx.fillStyle = IND_ORANGE;
  ctx.font = 'bold 26px Bebas Neue';
  ctx.shadowColor = IND_ORANGE;
  ctx.shadowBlur = 15;
  ctx.fillText('HELP MODI JI FLY!', W/2, H/2 + 80);
  ctx.shadowBlur = 0;

  ctx.fillStyle = '#aaa';
  ctx.font = '18px Bebas Neue';
  ctx.fillText('AVOID CONGRESS FLAGS', W/2, H/2 + 110);
}

function gameLoop() {
  frame++;
  ctx.clearRect(0, 0, W, H);

  drawBackground();
  drawPipes();
  drawModi();
  updateParticles();

  if (state === 'playing') {
    // Physics
    bird.vy += bird.gravity;
    bird.y += bird.vy;

    // Pipes
    pipeTimer++;
    if (pipeTimer >= PIPE_INTERVAL) {
      spawnPipe();
      pipeTimer = 0;
    }

    pipes.forEach(p => p.x -= PIPE_SPEED);
    pipes = pipes.filter(p => p.x + PIPE_W > 0);

    // Score
    pipes.forEach(p => {
      if (!p.scored && p.x + PIPE_W < bird.x) {
        p.scored = true;
        score++;
        scoreEl.textContent = score;
        if (score > best) {
          best = score;
          bestEl.textContent = best;
        }
      }
    });

    // Collision
    if (pipes.some(p => checkCollision(p))) {
      spawnParticles(bird.x, bird.y);
      state = 'dead';
      msg.textContent = '';
    }

    drawHUD();
  }

  if (state === 'dead') drawDeathScreen();
  if (state === 'idle') drawIdleScreen();

  requestAnimationFrame(gameLoop);
}

function handleInput() {
  if (state === 'idle') {
    state = 'playing';
    reset();
    msg.textContent = '';
  } else if (state === 'playing') {
    bird.flap();
  } else if (state === 'dead') {
    state = 'playing';
    reset();
  }
}

document.addEventListener('keydown', e => {
  if (e.code === 'Space') { e.preventDefault(); handleInput(); }
});
canvas.addEventListener('click', handleInput);
canvas.addEventListener('touchstart', e => { e.preventDefault(); handleInput(); });

gameLoop();
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return Response(HTML, mimetype='text/html')

@app.route('/health')
def health():
    return {'status': 'healthy'}

@app.route('/metrics')
def metrics():
    return '# Flappy Modi Metrics\napp_requests_total 1\n'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)