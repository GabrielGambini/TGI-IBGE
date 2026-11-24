import { motion } from "framer-motion";
import { ArrowRight, BookOpen } from "lucide-react";
import { useEffect, useRef } from "react";

function Particles() {
  const ref = useRef<HTMLCanvasElement>(null);
  useEffect(() => {
    const cv = ref.current!, ctx = cv.getContext("2d")!;
    const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
    let w = 0, h = 0, raf = 0, t = 0;
    const pts = Array.from({ length: 40 }, () => ({ x: Math.random(), y: Math.random(), vx: (Math.random() - .5) * 2e-4, vy: (Math.random() - .5) * 2e-4 }));
    const resize = () => { w = cv.width = cv.offsetWidth; h = cv.height = cv.offsetHeight; };
    resize(); addEventListener("resize", resize);
    const draw = () => {
      t += 0.004; ctx.clearRect(0, 0, w, h);
      ctx.strokeStyle = "rgba(59,130,246,.55)"; ctx.lineWidth = 2; ctx.beginPath();
      for (let x = 0; x <= w; x += 12) { const y = h * .62 - Math.sin(x / 140 + t) * 36 - x * .12 + Math.sin(x / 40 + t * 2) * 8; x ? ctx.lineTo(x, y) : ctx.moveTo(x, y); }
      ctx.stroke();
      for (const p of pts) { p.x = (p.x + p.vx + 1) % 1; p.y = (p.y + p.vy + 1) % 1; ctx.fillStyle = "rgba(148,163,184,.4)"; ctx.fillRect(p.x * w, p.y * h, 2, 2); }
      if (!reduce) raf = requestAnimationFrame(draw);
    };
    draw();
    return () => { cancelAnimationFrame(raf); removeEventListener("resize", resize); };
  }, []);
  return <canvas ref={ref} aria-hidden className="absolute inset-0 h-full w-full" />;
}

export default function Hero() {
  return (
    <section id="inicio" className="relative flex min-h-screen items-center overflow-hidden pt-16">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,rgba(59,130,246,.18),transparent_60%)]" />
      <Particles />
      <div className="relative mx-auto max-w-5xl px-4 text-center sm:px-6">
        <motion.span initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="glass inline-block rounded-full px-4 py-1.5 text-xs text-slate-300">
          Dados oficiais do IBGE | Inteligência de dados | Economia brasileira
        </motion.span>
        <motion.h1 initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: .1, duration: .6 }}
          className="mt-6 text-4xl font-extrabold leading-tight text-white sm:text-6xl">
          Entenda a inflação. Explore os dados. <span className="bg-gradient-to-r from-brand to-cyan-300 bg-clip-text text-transparent">Descubra tendências.</span>
        </motion.h1>
        <motion.p initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: .2, duration: .6 }}
          className="mx-auto mt-6 max-w-2xl text-lg text-slate-400">
          Uma plataforma interativa para acompanhar, analisar e compreender o comportamento da inflação brasileira por meio do IPCA-15.
        </motion.p>
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: .4 }} className="mt-10 flex flex-col justify-center gap-3 sm:flex-row">
          <motion.a whileHover={{ scale: 1.04 }} whileTap={{ scale: .96 }} href="#dashboard" className="inline-flex items-center justify-center gap-2 rounded-xl bg-brand px-6 py-3 font-semibold text-white shadow-lg shadow-brand/30">
            Explorar Dashboard <ArrowRight size={18} />
          </motion.a>
          <motion.a whileHover={{ scale: 1.04 }} whileTap={{ scale: .96 }} href="#sobre" className="glass inline-flex items-center justify-center gap-2 rounded-xl px-6 py-3 font-semibold text-white">
            <BookOpen size={18} /> Conhecer o indicador
          </motion.a>
        </motion.div>
      </div>
    </section>
  );
}
