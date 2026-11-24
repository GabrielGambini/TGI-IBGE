import { animate, motion, useInView } from "framer-motion";
import { useEffect, useRef, useState, type ReactNode } from "react";

export const fadeUp = { hidden: { opacity: 0, y: 24 }, show: { opacity: 1, y: 0, transition: { duration: 0.5 } } };

export function Reveal({ children, delay = 0, className = "" }: { children: ReactNode; delay?: number; className?: string }) {
  return (
    <motion.div className={className} variants={fadeUp} initial="hidden" whileInView="show" viewport={{ once: true, margin: "-60px" }} transition={{ delay }}>
      {children}
    </motion.div>
  );
}

export function Section({ id, eyebrow, title, desc, children }: { id: string; eyebrow: string; title: string; desc?: string; children: ReactNode }) {
  return (
    <section id={id} className="mx-auto max-w-7xl px-4 py-20 sm:px-6">
      <Reveal className="mb-10 max-w-2xl">
        <p className="text-xs font-semibold uppercase tracking-widest text-brand">{eyebrow}</p>
        <h2 className="mt-2 text-3xl font-bold text-white sm:text-4xl">{title}</h2>
        {desc && <p className="mt-3 text-slate-400">{desc}</p>}
      </Reveal>
      {children}
    </section>
  );
}

export function Counter({ value, suffix = "%" }: { value: number; suffix?: string }) {
  const ref = useRef<HTMLSpanElement>(null);
  const inView = useInView(ref, { once: true });
  const [v, setV] = useState(0);
  useEffect(() => {
    if (!inView) return;
    const c = animate(0, value, { duration: 1.2, ease: "easeOut", onUpdate: setV });
    return () => c.stop();
  }, [inView, value]);
  return <span ref={ref}>{v.toFixed(2).replace(".", ",")}{suffix}</span>;
}
