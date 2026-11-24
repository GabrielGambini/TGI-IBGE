import { motion } from "framer-motion";
import { ExternalLink, Loader2, Maximize2, WifiOff } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { POWERBI_URL } from "../data";
import { Reveal } from "./ui";

export default function PowerBI() {
  const box = useRef<HTMLDivElement>(null);
  const [loaded, setLoaded] = useState(false);
  const [slow, setSlow] = useState(false);
  useEffect(() => { const t = setTimeout(() => setSlow(true), 20000); return () => clearTimeout(t); }, []);
  const full = () => box.current?.requestFullscreen?.();

  return (
    <section id="dashboard" className="mx-auto max-w-[1400px] px-4 py-20 sm:px-6">
      <Reveal className="mx-auto mb-10 max-w-3xl text-center">
        <h2 className="text-3xl font-bold text-white sm:text-4xl">Explore os dados do IPCA-15</h2>
        <p className="mt-3 text-slate-400">Visualize indicadores, acompanhe variações e explore informações econômicas por meio do nosso painel interativo de Business Intelligence.</p>
      </Reveal>
      <Reveal>
        <div className="glass overflow-hidden rounded-3xl p-2 shadow-2xl shadow-brand/10 sm:p-3">
          <div className="flex flex-wrap items-center justify-between gap-2 px-3 py-2">
            <div>
              <p className="text-xs font-bold tracking-widest text-brand">PAINEL DE BUSINESS INTELLIGENCE</p>
              <p className="text-sm text-slate-400">Análise interativa dos indicadores econômicos</p>
            </div>
            <div className="flex gap-2">
              <button onClick={full} className="inline-flex items-center gap-1.5 rounded-lg border border-white/10 px-3 py-1.5 text-sm transition hover:bg-white/10"><Maximize2 size={14} />Tela cheia</button>
              <a href={POWERBI_URL} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1.5 rounded-lg border border-white/10 px-3 py-1.5 text-sm transition hover:bg-white/10"><ExternalLink size={14} />Abrir no Power BI</a>
            </div>
          </div>
          <div ref={box} className="relative aspect-[4/5] w-full overflow-hidden rounded-2xl bg-bg sm:aspect-[16/10] lg:aspect-[1140/541.25] lg:min-h-[560px]">
            {!loaded && (
              <motion.div exit={{ opacity: 0 }} className="absolute inset-0 z-10 grid place-items-center bg-bg">
                <div className="text-center">
                  {slow ? <WifiOff className="mx-auto text-amber-400" /> : <Loader2 className="mx-auto animate-spin text-brand" />}
                  <p className="mt-3 text-sm text-slate-400">{slow ? "O painel está demorando ou não pôde ser carregado aqui." : "Carregando painel do Power BI…"}</p>
                  {slow && <a href={POWERBI_URL} target="_blank" rel="noopener noreferrer" className="mt-3 inline-flex items-center gap-1.5 rounded-lg bg-brand px-4 py-2 text-sm font-semibold text-white"><ExternalLink size={14} />Abrir relatório no Power BI</a>}
                  {!slow && <div className="mx-auto mt-4 h-2 w-48 skeleton" />}
                </div>
              </motion.div>
            )}
            <iframe title="Dashboard - TGI" className="absolute inset-0 h-full w-full" width="1140" height="541.25"
              src={POWERBI_URL} frameBorder="0" allowFullScreen onLoad={() => setLoaded(true)} />
          </div>
        </div>
      </Reveal>
    </section>
  );
}
