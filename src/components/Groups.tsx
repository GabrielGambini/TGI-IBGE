import { motion } from "framer-motion";
import { GraduationCap, Heart, House, Car, Shirt, Sofa, User, Utensils, Wifi } from "lucide-react";
import { groups } from "../data";
import { Reveal, Section } from "./ui";

const map = { utensils: Utensils, home: House, sofa: Sofa, shirt: Shirt, car: Car, heart: Heart, user: User, grad: GraduationCap, wifi: Wifi } as const;

export default function Groups() {
  return (
    <Section id="grupos" eyebrow="Composição" title="Grupos que compõem o IPCA-15"
      desc="Os nove grupos de produtos e serviços. Variações e pesos aparecem apenas quando verificados nos dados oficiais.">
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {groups.map((g, k) => {
          const I = map[g.icon as keyof typeof map];
          return (
            <Reveal key={g.name} delay={(k % 3) * 0.08}>
              <motion.div whileHover={{ y: -4 }} className="glass group h-full rounded-2xl p-5 transition hover:border-brand/40">
                <div className="flex items-center gap-3">
                  <span className="rounded-lg bg-brand/15 p-2 text-brand transition group-hover:rotate-6 group-hover:scale-110"><I size={20} /></span>
                  <h3 className="font-semibold text-white">{g.name}</h3>
                </div>
                <p className="mt-3 text-sm text-slate-400">{g.desc}</p>
                <p className="mt-3 text-xs text-slate-500">
                  {g.var !== null ? <>Out/2026: <b className="text-up">+{g.var.toFixed(2).replace(".", ",")}%</b></> : "Variação: consulte o SIDRA"}
                </p>
              </motion.div>
            </Reveal>
          );
        })}
      </div>
    </Section>
  );
}
