import { ExternalLink } from "lucide-react";
import { DATA_META, sources } from "../data";
import { Reveal, Section } from "./ui";

export default function Sources() {
  return (
    <Section id="fontes" eyebrow="Transparência" title="Fontes de dados"
      desc={`Fonte principal: IBGE — Instituto Brasileiro de Geografia e Estatística. Dados de ${DATA_META.referencia}, divulgados em ${DATA_META.divulgacao}.`}>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {sources.map((s, k) => (
          <Reveal key={s.t} delay={k * 0.05}>
            <a href={s.u} target="_blank" rel="noopener noreferrer" className="glass flex items-center justify-between rounded-xl p-4 transition hover:border-brand/40 hover:text-white">
              {s.t}<ExternalLink size={16} className="text-brand" />
            </a>
          </Reveal>
        ))}
      </div>
    </Section>
  );
}
