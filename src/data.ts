// Fonte: IBGE — IPCA-15 de outubro/2026 (divulgado em 23/10/2026).
// Atualize este arquivo a cada divulgação, ou troque por consulta à API SIDRA (tabela 3065).
// Valores ausentes = null → a interface mostra "dados a atualizar" (nada é inventado).
export const IBGE_URL = "https://www.ibge.gov.br/estatisticas/economicas/precos-e-custos/9260-indice-nacional-de-precos-ao-consumidor-amplo-15.html";
export const SIDRA_URL = "https://sidra.ibge.gov.br/tabela/3065";
export const POWERBI_URL =
  "https://app.powerbi.com/view?r=eyJrIjoiNWMzOGI2YjMtMGMwMC00MTA2LTgzY2QtOWViMjEwYmU5YTZlIiwidCI6ImU0Y2MyMmIwLWM0M2YtNGUzMi1hMmU1LWEwMzRkN2RmMzUwMCJ9";

export const DATA_META = { referencia: "Outubro de 2026", divulgacao: "23/10/2026", fonte: "IBGE" };

export interface Indicator { id: string; label: string; desc: string; value: number | null; text?: string; prev?: string; period: string; icon: "month"|"ytd"|"y12"|"cmp"|"max"|"min"; }
export const indicators: Indicator[] = [
  { id: "m", label: "Variação mensal", desc: "Variação do IPCA-15 no mês", value: 0.32, prev: "Set/26: 0,70% · Out/25: 0,18%", period: "Out/2026", icon: "month" },
  { id: "y", label: "Acumulado no ano", desc: "De janeiro a outubro de 2026", value: 4.15, period: "Jan–Out/2026", icon: "ytd" },
  { id: "12", label: "Acumulado em 12 meses", desc: "Acima do teto da meta (4,5%)", value: 4.62, prev: "Anterior: 4,47%", period: "Nov/25–Out/26", icon: "y12" },
  { id: "c", label: "Comparação com o mês anterior", desc: "Diferença da taxa mensal (p.p.)", value: -0.38, prev: "0,32% vs 0,70%", period: "Out vs Set/2026", icon: "cmp" },
  { id: "max", label: "Maior variação", desc: "Alimentação e bebidas (impacto de 0,19 p.p.)", value: 0.88, period: "Out/2026", icon: "max" },
  { id: "min", label: "Menor variação", desc: "Dado do grupo ainda não carregado — consulte o SIDRA", value: null, period: "Out/2026", icon: "min" },
];
export interface Group { name: string; desc: string; icon: string; var: number | null; }
export const groups: Group[] = [
  { name: "Alimentação e bebidas", desc: "Alimentos no domicílio, fora de casa e bebidas.", icon: "utensils", var: 0.88 },
  { name: "Habitação", desc: "Aluguel, condomínio, energia elétrica, água e gás.", icon: "home", var: null },
  { name: "Artigos de residência", desc: "Móveis, eletrodomésticos e utensílios.", icon: "sofa", var: null },
  { name: "Vestuário", desc: "Roupas, calçados e acessórios.", icon: "shirt", var: null },
  { name: "Transportes", desc: "Combustíveis, passagens, veículos e manutenção.", icon: "car", var: null },
  { name: "Saúde e cuidados pessoais", desc: "Medicamentos, planos de saúde e higiene.", icon: "heart", var: null },
  { name: "Despesas pessoais", desc: "Serviços pessoais, recreação e fumo.", icon: "user", var: null },
  { name: "Educação", desc: "Cursos regulares, livros e materiais.", icon: "grad", var: null },
  { name: "Comunicação", desc: "Telefonia, internet e equipamentos.", icon: "wifi", var: null },
];
export const sources = [
  { t: "Página oficial do IPCA-15", u: IBGE_URL },
  { t: "Séries históricas (SIDRA)", u: SIDRA_URL },
  { t: "Publicações oficiais", u: IBGE_URL },
  { t: "Notas metodológicas", u: IBGE_URL },
  { t: "Calendário de coleta e divulgação", u: IBGE_URL },
  { t: "Informações técnicas", u: IBGE_URL },
];
