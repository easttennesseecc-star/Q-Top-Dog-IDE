import React, { useEffect, useRef } from 'react';

type CanvasKind = 'particles' | 'starfield' | 'nebula';

export default function BackgroundCanvas({ kind, count = 40 }: { kind: CanvasKind; count?: number }) {
  const ref = useRef<HTMLCanvasElement | null>(null);
  const raf = useRef<number | null>(null);

  useEffect(() => {
    const canvas = ref.current;
    if (!canvas) return;

    // Decide whether to use WebGL fallback if available and particle count high
    const tryWebGL = (cnt: number) => {
      try {
        const gl = canvas.getContext('webgl2') || canvas.getContext('webgl');
        return !!gl && cnt >= 120;
      } catch (e) { return false; }
    };

    const useGL = tryWebGL(count);
    if (useGL) {
      // Simple WebGL points renderer (positions updated on CPU and uploaded each frame)
  const gl = canvas.getContext('webgl') as WebGLRenderingContext | null;
  if (!gl) return; // fallback to 2d if no gl
  const G: WebGLRenderingContext = gl;
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      let w = canvas.width; let h = canvas.height;

      // Shader sources
      const vs = `attribute vec2 a_pos; attribute float a_size; void main(){ gl_Position = vec4((a_pos.x/` + w + `.0*2.0-1.0), (a_pos.y/` + h + `.0* -2.0+1.0), 0.0, 1.0); gl_PointSize = a_size; }`;
      const fs = `precision mediump float; void main(){ float d = length(gl_PointCoord - vec2(0.5)); if (d > 0.5) discard; gl_FragColor = vec4(0.6,0.9,1.0,1.0); }`;

      function compile(src: string, type: number) {
        const s = G.createShader(type)!; G.shaderSource(s, src); G.compileShader(s); return s;
      }
      const p = G.createProgram()!;
      G.attachShader(p, compile(vs, G.VERTEX_SHADER));
      G.attachShader(p, compile(fs, G.FRAGMENT_SHADER));
      G.linkProgram(p);
      G.useProgram(p);

      // particle data
      const N = Math.max(6, Math.min(1500, count));
      const positions = new Float32Array(N * 2);
      const sizes = new Float32Array(N);
      const vx = new Float32Array(N);
      const vy = new Float32Array(N);
      for (let i = 0; i < N; i++) {
        positions[i*2] = Math.random() * w;
        positions[i*2+1] = Math.random() * h;
        sizes[i] = 1 + Math.random()*3;
        vx[i] = (Math.random()-0.5)*0.6;
        vy[i] = (Math.random()-0.5)*0.6;
      }

  const posBuf = G.createBuffer();
  const sizeBuf = G.createBuffer();
  const a_pos = G.getAttribLocation(p, 'a_pos');
  const a_size = G.getAttribLocation(p, 'a_size');

      function drawGL() {
  G.viewport(0,0,w,h);
  G.clear(G.COLOR_BUFFER_BIT);
        // update positions
        for (let i=0;i<N;i++) {
          positions[i*2] += vx[i];
          positions[i*2+1] += vy[i];
          if (positions[i*2] < -10) positions[i*2] = w + 10;
          if (positions[i*2] > w + 10) positions[i*2] = -10;
          if (positions[i*2+1] < -10) positions[i*2+1] = h + 10;
          if (positions[i*2+1] > h + 10) positions[i*2+1] = -10;
        }
  G.bindBuffer(G.ARRAY_BUFFER, posBuf);
  G.bufferData(G.ARRAY_BUFFER, positions, G.DYNAMIC_DRAW);
  G.enableVertexAttribArray(a_pos);
  G.vertexAttribPointer(a_pos, 2, G.FLOAT, false, 0, 0);

  G.bindBuffer(G.ARRAY_BUFFER, sizeBuf);
  G.bufferData(G.ARRAY_BUFFER, sizes, G.DYNAMIC_DRAW);
  G.enableVertexAttribArray(a_size);
  G.vertexAttribPointer(a_size, 1, G.FLOAT, false, 0, 0);

  G.drawArrays(G.POINTS, 0, N);
        raf.current = requestAnimationFrame(drawGL);
      }

      raf.current = requestAnimationFrame(drawGL);

      const handleResize = () => { w = canvas.width = window.innerWidth; h = canvas.height = window.innerHeight; };
      window.addEventListener('resize', handleResize);
      return () => { if (raf.current) cancelAnimationFrame(raf.current); window.removeEventListener('resize', handleResize); };
    }

    // 2D fallback (existing implementation)
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let w = canvas.width = window.innerWidth;
    let h = canvas.height = window.innerHeight;

    let mouseX = w / 2;
    let mouseY = h / 2;

    const handleResize = () => { w = canvas.width = window.innerWidth; h = canvas.height = window.innerHeight; };
    const handleMove = (e: MouseEvent) => { mouseX = e.clientX; mouseY = e.clientY; };
    window.addEventListener('resize', handleResize);
    window.addEventListener('mousemove', handleMove);

    // particle data
    const N = Math.max(6, Math.min(300, count));
    const particles = new Array(N).fill(0).map((_, i) => ({
      x: Math.random() * w,
      y: Math.random() * h,
      z: 0.2 + Math.random() * 1.2,
      r: 1 + Math.random() * 3,
      vx: (Math.random() - 0.5) * 0.2,
      vy: (Math.random() - 0.5) * 0.2,
      hue: 180 + Math.random() * 60,
    }));

    let t0 = performance.now();

    function draw(time: number) {
      const dt = Math.min(50, time - t0) / 1000;
      t0 = time;
      if (!ctx) return;
      ctx.clearRect(0, 0, w, h);

      if (kind === 'nebula') {
        // layered radial gradients for nebula-ish look
        for (let i = 0; i < 3; i++) {
          const gx = (Math.sin(time / 5000 + i) * 0.3 + 0.5) * w;
          const gy = (Math.cos(time / 7000 + i) * 0.3 + 0.5) * h;
          const g = ctx.createRadialGradient(gx, gy, 0, gx, gy, Math.max(w, h) * (0.25 + i * 0.15));
          const colorA = `hsla(${200 + i * 20},70%,40%,${0.06 + i * 0.02})`;
          const colorB = `hsla(${260 + i * 30},60%,8%,0)`;
          g.addColorStop(0, colorA);
          g.addColorStop(1, colorB);
          ctx.fillStyle = g;
          ctx.fillRect(0, 0, w, h);
        }
      }

      if (kind === 'starfield' || kind === 'particles') {
        for (const p of particles) {
          // simple parallax toward mouse
          const dx = (mouseX - w / 2) * 0.0006 * p.z;
          const dy = (mouseY - h / 2) * 0.0006 * p.z;
          p.x += p.vx + dx * dt * 60;
          p.y += p.vy + dy * dt * 60;
          if (p.x < -10) p.x = w + 10;
          if (p.x > w + 10) p.x = -10;
          if (p.y < -10) p.y = h + 10;
          if (p.y > h + 10) p.y = -10;

          if (kind === 'starfield') {
            const s = Math.max(0.8, p.z * 2.5);
            ctx.fillStyle = `rgba(255,255,255,${0.6 * p.z})`;
            ctx.beginPath();
            ctx.arc(p.x, p.y, s, 0, Math.PI * 2);
            ctx.fill();
          } else {
            const grd = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.r * 3);
            grd.addColorStop(0, `hsla(${p.hue},70%,70%,${0.06 + 0.12 * p.z})`);
            grd.addColorStop(1, `hsla(${p.hue},60%,10%,0)`);
            ctx.fillStyle = grd;
            ctx.fillRect(p.x - p.r * 3, p.y - p.r * 3, p.r * 6, p.r * 6);
          }
        }
      }

      raf.current = requestAnimationFrame(draw);
    }

    raf.current = requestAnimationFrame(draw);

    return () => {
      if (raf.current) cancelAnimationFrame(raf.current);
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('mousemove', handleMove);
    };
  }, [kind, count]);

  return <canvas ref={ref} style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', zIndex: -1 }} />;
}
