import { BarChart3 } from "lucide-react";
import { IBGE_URL } from "../data";
import { links } from "./Navbar";

export default function Footer() {
  return (
    <footer className="border-t border-white/10 bg-card/40">
      <div className="mx-auto grid max-w-7xl gap-8 px-4 py-12 sm:px-6 md:grid-cols-3">
        <div>
          <p className="flex items-center gap-2 font-bold text-white"><span className="grid h-8 w-8 place-items-center rounded-lg bg-brand"><BarChart3 size={18} /></span>IPCA15 Analytics</p>
          <p className="mt-3 text-sm text-slate-400">Plataforma de análise da inflação brasileira com dados oficiais e dashboard interativo.</p>
        </div>
        <ul className="grid grid-cols-2 gap-2 text-sm">{links.map(([l, h]) => <li key={h}><a className="text-slate-400 hover:text-white" href={h}>{l}</a></li>)}</ul>
        <div className="text-sm text-slate-400">
          <p>Fonte oficial: <a className="text-brand underline" href={IBGE_URL} target="_blank" rel="noopener noreferrer">IBGE</a></p>
          <p className="mt-2"><a className="text-brand underline" href="#dashboard">Dashboard Power BI</a></p>
        </div>
      </div>
      <div className="border-t border-white/10 px-4 py-6 text-center text-xs text-slate-500">
        © {new Date().getFullYear()} IPCA15 Analytics. Projeto desenvolvido para fins informativos e educacionais, com base em informações disponibilizadas pelo Instituto Brasileiro de Geografia e Estatística (IBGE).
      </div>
    </footer>
  );
}
