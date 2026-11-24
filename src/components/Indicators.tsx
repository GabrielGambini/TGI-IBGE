import { motion } from "framer-motion";
import { Calendar, CalendarRange, GitCompare, TrendingDown, TrendingUp, Percent, AlertCircle } from "lucide-react";
import { DATA_META, indicators, SIDRA_URL } from "../data";
import { Counter, Reveal, Section } from "./ui";

const icons = { month: Calendar, ytd: CalendarRange, y12: Percent, cmp: GitCompare, max: TrendingUp, min: TrendingDown };

export default function Indicators() {
  return (
    <Section id="indicadores" eyebrow="Indicadores" title="Indicadores econômicos"
      desc={`Fonte: ${DATA_META.fonte} · Referência: ${DATA_META.referencia} · Divulgado em ${DATA_META.divulgacao}.`}>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {indicators.map((x, k) => {
          const I = icons[x.icon];
          const neg = x.value !== null && x.value < 0;
          return (
            <Reveal key={x.id} delay={k * 0.07}>
              <motion.article whileHover={{ y: -4 }} className="glass h-full rounded-2xl p-6">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-400">{x.label}</span>
                  <motion.span whileHover={{ rotate: 12, scale: 1.15 }} className="rounded-lg bg-brand/15 p-2 text-brand"><I size={18} /></motion.span>
                </div>
                {x.value !== null ? (
                  <p className={`mt-4 text-4xl font-extrabold ${x.id === "c" ? (neg ? "text-down" : "text-up") : "text-white"}`}>
                    {x.id === "c" && !neg ? "+" : ""}<Counter value={x.value} suffix={x.id === "c" ? " p.p." : "%"} />
                  </p>
                ) : (
                  <div className="mt-4"><div className="skeleton h-9 w-24" />
                    <p className="mt-3 flex items-center gap-1 text-xs text-amber-400"><AlertCircle size={14} />Dado a atualizar</p></div>
                )}
                <p className="mt-2 text-sm text-slate-400">{x.desc}</p>
                <p className="mt-3 text-xs text-slate-500">Período: {x.period}{x.prev ? ` · ${x.prev}` : ""}</p>
              </motion.article>
            </Reveal>
          );
        })}
      </div>
      <p className="mt-4 text-xs text-slate-500">Valores do IPCA-15 de outubro/2026 conforme divulgação do IBGE. Para o grupo de menor variação e demais grupos, consulte a <a className="text-brand underline" href={SIDRA_URL} target="_blank" rel="noopener noreferrer">tabela do SIDRA</a>.</p>
    </Section>
  );
}
