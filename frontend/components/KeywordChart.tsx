"use client";

import { motion } from "framer-motion";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import type { TrendKeyword } from "@/lib/api";

interface KeywordChartProps {
  data: TrendKeyword[];
}

const COLORS = [
  "#a78bfa", "#c084fc", "#e879f9", "#f472b6", "#fb7185",
  "#818cf8", "#93c5fd", "#67e8f9", "#5eead4", "#86efac",
];

export default function KeywordChart({ data }: KeywordChartProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] as [number, number, number, number] }}
      className="glass p-4 relative overflow-hidden"
    >
      <div className="absolute bottom-0 right-0 w-1/2 h-1/2 rounded-full opacity-10 blur-3xl pointer-events-none"
        style={{ background: "radial-gradient(circle, rgba(236,72,153,0.15) 0%, transparent 70%)" }}
      />
      <h3 className="section-title mb-3 relative z-10">Keyword Frequency</h3>
      <div className="h-[220px] relative z-10">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} layout="vertical">
            <XAxis type="number" stroke="rgba(255,255,255,0.08)" fontSize={9} tickLine={false} axisLine={false} />
            <YAxis dataKey="keyword" type="category" stroke="rgba(255,255,255,0.2)" fontSize={9} tickLine={false} axisLine={false} width={60} />
            <Tooltip
              contentStyle={{
                background: "rgba(10, 10, 18, 0.95)",
                border: "1px solid rgba(255,255,255,0.06)",
                borderRadius: "14px",
                boxShadow: "0 8px 32px rgba(0,0,0,0.5)",
                fontSize: "11px",
              }}
            />
            <Bar dataKey="count" radius={[0, 6, 6, 0]}>
              {data.map((_, i) => (
                <Cell key={i} fill={COLORS[i % COLORS.length]} fillOpacity={0.7} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </motion.div>
  );
}
