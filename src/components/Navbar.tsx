import { AnimatePresence, motion } from "framer-motion";
import { BarChart3, Menu, X } from "lucide-react";
import { useEffect, useState } from "react";

export const links = [
  ["Início", "#inicio"], ["Sobre o IPCA-15", "#sobre"], ["Indicadores", "#indicadores"],
  ["Dashboard", "#dashboard"], ["Metodologia", "#metodologia"], ["Fontes de dados", "#fontes"],
];

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);
  useEffect(() => {
    const f = () => setScrolled(window.scrollY > 20);
    f(); window.addEventListener("scroll", f, { passive: true });
    return () => window.removeEventListener("scroll", f);
  }, []);
  return (
    <header className={`fixed inset-x-0 top-0 z-50 transition-all duration-300 ${scrolled ? "bg-bg/85 backdrop-blur-xl border-b border-white/10" : "bg-transparent"}`}>
      <nav aria-label="Principal" className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6">
        <a href="#inicio" className="flex items-center gap-2 font-bold text-white">
          <span className="grid h-8 w-8 place-items-center rounded-lg bg-brand"><BarChart3 size={18} /></span>
          IPCA15 <span className="text-brand">Analytics</span>
        </a>
        <ul className="hidden items-center gap-6 lg:flex">
          {links.map(([l, h]) => <li key={h}><a href={h} className="text-sm text-slate-300 transition hover:text-white">{l}</a></li>)}
        </ul>
        <button className="lg:hidden" aria-label={open ? "Fechar menu" : "Abrir menu"} aria-expanded={open} onClick={() => setOpen(!open)}>
          {open ? <X /> : <Menu />}
        </button>
      </nav>
      <AnimatePresence>
        {open && (
          <motion.ul initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} exit={{ opacity: 0, height: 0 }}
            className="overflow-hidden border-t border-white/10 bg-bg/95 px-4 backdrop-blur-xl lg:hidden">
            {links.map(([l, h]) => <li key={h}><a href={h} onClick={() => setOpen(false)} className="block py-3 text-slate-200">{l}</a></li>)}
          </motion.ul>
        )}
      </AnimatePresence>
    </header>
  );
}
