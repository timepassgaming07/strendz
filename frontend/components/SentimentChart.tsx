"use client";

import { motion } from "framer-motion";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import type { TimelinePoint } from "@/lib/api";

interface SentimentChartProps {
  data: TimelinePoint[];
}

export default function SentimentChart({ data }: SentimentChartProps) {
  const formatted = data.map((d) => ({
    ...d,
    time: d.time.slice(11, 16),
  }));

  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-40px" }}
      transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] as [number, number, number, number] }}
      className="glass p-5 relative overflow-hidden"
    >
      <div
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-3/4 h-3/4 rounded-full opacity-10 blur-3xl pointer-events-none"
        style={{ background: "radial-gradient(circle, rgba(139,92,246,0.12) 0%, transparent 70%)" }}
      />
      <h3 className="section-title mb-4 relative z-10">Sentiment Timeline</h3>
      <div className="h-[260px] relative z-10">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={formatted}>
            <defs>
              <linearGradient id="gradPositive" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#4ade80" stopOpacity={0.3} />
                <stop offset="100%" stopColor="#4ade80" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="gradNeutral" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#a78bfa" stopOpacity={0.2} />
                <stop offset="100%" stopColor="#a78bfa" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="gradNegative" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#f87171" stopOpacity={0.25} />
                <stop offset="100%" stopColor="#f87171" stopOpacity={0} />
              </linearGradient>
            </defs>
            <XAxis dataKey="time" stroke="rgba(255,255,255,0.08)" fontSize={9} tickLine={false} axisLine={false} />
            <YAxis stroke="rgba(255,255,255,0.08)" fontSize={9} tickLine={false} axisLine={false} />
            <Tooltip
              contentStyle={{
                background: "rgba(8, 8, 15, 0.95)",
                border: "1px solid rgba(255,255,255,0.06)",
                borderRadius: "14px",
                boxShadow: "0 12px 40px rgba(0,0,0,0.5)",
                backdropFilter: "blur(20px)",
                fontSize: "11px",
              }}
            />
            <Area type="monotone" dataKey="negative" stroke="#f87171" strokeWidth={1.5} fill="url(#gradNegative)" dot={false} />
            <Area type="monotone" dataKey="neutral" stroke="#a78bfa" strokeWidth={1.5} fill="url(#gradNeutral)" dot={false} />
            <Area type="monotone" dataKey="positive" stroke="#4ade80" strokeWidth={1.5} fill="url(#gradPositive)" dot={false} />
            <Legend
              verticalAlign="bottom"
              height={28}
              iconType="circle"
              iconSize={6}
              wrapperStyle={{ fontSize: "10px", color: "rgba(255,255,255,0.35)" }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </motion.div>
  );
}
