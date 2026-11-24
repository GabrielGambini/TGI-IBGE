import { Calendar, Info, Target, Users } from "lucide-react";
import { Reveal, Section } from "./ui";

const cards = [
  { i: Info, t: "O que é?", d: "O IPCA-15 é o Índice Nacional de Preços ao Consumidor Amplo 15, produzido pelo IBGE, que mede a variação dos preços de produtos e serviços consumidos pelas famílias brasileiras." },
  { i: Target, t: "Qual é sua finalidade?", d: "Acompanhar a evolução dos preços e fornecer uma prévia do comportamento da inflação oficial brasileira." },
  { i: Calendar, t: "Como funciona?", d: "O período de coleta de preços ocorre, em geral, entre o dia 16 do mês anterior e o dia 15 do mês de referência." },
  { i: Users, t: "Quem é considerado?", d: "Famílias com rendimentos de 1 a 40 salários mínimos, residentes nas áreas geográficas abrangidas pela pesquisa." },
];

export default function About() {
  return (
    <Section id="sobre" eyebrow="Sobre o indicador" title="O que é o IPCA-15?">
      <div className="grid gap-4 sm:grid-cols-2">
        {cards.map(({ i: I, t, d }, k) => (
          <Reveal key={t} delay={k * 0.08}>
            <div className="glass h-full rounded-2xl p-6 transition hover:-translate-y-1 hover:border-brand/40">
              <I className="text-brand" /><h3 className="mt-3 text-lg font-semibold text-white">{t}</h3><p className="mt-2 text-sm text-slate-400">{d}</p>
            </div>
          </Reveal>
        ))}
      </div>
      <Reveal className="mt-6">
        <div className="glass rounded-2xl p-6">
          <h3 className="font-semibold text-white">IPCA × IPCA-15</h3>
          <p className="mt-1 text-sm text-slate-400">Objetivos semelhantes; diferem principalmente no período de coleta e na abrangência geográfica.</p>
          <div className="mt-4 grid gap-4 sm:grid-cols-2">
            <div className="rounded-xl border border-white/10 p-4"><b className="text-brand">IPCA</b><p className="mt-1 text-sm text-slate-400">Inflação oficial. Coleta cobre, em geral, o mês-calendário de referência.</p></div>
            <div className="rounded-xl border border-white/10 p-4"><b className="text-brand">IPCA-15</b><p className="mt-1 text-sm text-slate-400">Prévia. Coleta do dia 16 do mês anterior ao dia 15 do mês de referência, em menos áreas.</p></div>
          </div>
        </div>
      </Reveal>
    </Section>
  );
}
