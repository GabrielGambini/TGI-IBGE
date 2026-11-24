import { Reveal, Section } from "./ui";

const steps = [
  ["Definição da população", "Famílias com rendimentos de 1 a 40 salários mínimos nas áreas abrangidas."],
  ["Seleção de produtos e serviços", "Define-se a cesta de itens consumidos pelas famílias."],
  ["Coleta de preços", "Preços coletados, em geral, do dia 16 do mês anterior ao dia 15 do mês de referência."],
  ["Pesos das categorias", "Cada grupo recebe um peso conforme sua participação nas despesas."],
  ["Cálculo das variações", "Comparam-se os preços do período com os do período anterior."],
  ["Divulgação", "O IBGE divulga os resultados mensalmente."],
];

export default function Methodology() {
  return (
    <Section id="metodologia" eyebrow="Metodologia" title="Como o IBGE produz o IPCA-15">
      <ol className="grid gap-6 lg:grid-cols-6 lg:gap-3">
        {steps.map(([t, d], k) => (
          <Reveal key={t} delay={k * 0.07}>
            <li className="relative list-none border-l-2 border-brand/40 pl-6 lg:border-l-0 lg:border-t-2 lg:pl-0 lg:pt-6">
              <span className="absolute -left-[9px] top-0 grid h-4 w-4 place-items-center rounded-full bg-brand text-[9px] font-bold text-white lg:-top-[9px] lg:left-0">{k + 1}</span>
              <h3 className="font-semibold text-white">{t}</h3><p className="mt-1 text-sm text-slate-400">{d}</p>
            </li>
          </Reveal>
        ))}
      </ol>
      <Reveal className="mt-10">
        <div className="glass rounded-2xl p-6"><h3 className="font-semibold text-white">E o IPCA-E?</h3>
          <p className="mt-2 text-sm text-slate-400">O IPCA-E corresponde ao acumulado trimestral do IPCA-15.</p></div>
      </Reveal>
    </Section>
  );
}
