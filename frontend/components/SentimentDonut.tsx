"use client";

import { motion } from "framer-motion";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
} from "recharts";

interface SentimentDonutProps {
  data: {
    distribution: { positive: number; negative: number; neutral: number };
    polarity_histogram: { range: string; count: number }[];
    avg_polarity: number;
    avg_subjectivity: number;
  } | null;
}

const COLORS = { positive: "#4ade80", neutral: "#a78bfa", negative: "#f87171" };

export default function SentimentDonut({ data }: SentimentDonutProps) {
  if (!data) return null;

  const donutData = [
    { name: "Positive", value: data.distribution.positive, color: COLORS.positive },
    { name: "Neutral", value: data.distribution.neutral, color: COLORS.neutral },
    { name: "Negative", value: data.distribution.negative, color: COLORS.negative },
  ].filter((d) => d.value > 0);

  const total = donutData.reduce((a, d) => a + d.value, 0);

  const histData = data.polarity_histogram.map((b) => ({
    range: b.range.replace(" to ", "→"),
    count: b.count,
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
        className="absolute top-0 right-0 w-1/2 h-1/2 rounded-full opacity-10 blur-3xl pointer-events-none"
        style={{ background: "radial-gradient(circle, rgba(74,222,128,0.15) 0%, transparent 70%)" }}
      />
      <h3 className="section-title mb-4 relative z-10">Sentiment Distribution</h3>

      <div className="flex items-center gap-4 relative z-10">
        {/* Donut */}
        <div className="w-[140px] h-[140px] relative flex-shrink-0">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={donutData}
                innerRadius={40}
                outerRadius={65}
                paddingAngle={3}
                dataKey="value"
                stroke="none"
              >
                {donutData.map((d, i) => (
                  <Cell key={i} fill={d.color} fillOpacity={0.85} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  background: "rgba(8, 8, 15, 0.95)",
                  border: "1px solid rgba(255,255,255,0.06)",
                  borderRadius: "10px",
                  fontSize: "11px",
                }}
                formatter={(value: unknown, name: unknown) => [
                  `${value} (${((Number(value) / total) * 100).toFixed(1)}%)`,
                  String(name),
                ]}
              />
            </PieChart>
          </ResponsiveContainer>
          <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
            <span className="text-lg font-bold text-white">{total}</span>
            <span className="text-[9px] text-gray-500">total</span>
          </div>
        </div>

        {/* Stats */}
        <div className="flex-1 space-y-2">
          {donutData.map((d) => (
            <div key={d.name} className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full flex-shrink-0" style={{ background: d.color }} />
              <span className="text-[11px] text-gray-400 flex-1">{d.name}</span>
              <span className="text-[11px] text-gray-300 font-medium">{d.value}</span>
              <span className="text-[10px] text-gray-500">
                {((d.value / total) * 100).toFixed(0)}%
              </span>
            </div>
          ))}
          <div className="pt-2 border-t border-white/[0.04] space-y-1">
            <div className="flex justify-between">
              <span className="text-[10px] text-gray-500">Avg Polarity</span>
              <span
                className={`text-[10px] font-medium ${data.avg_polarity > 0 ? "text-green-400" : data.avg_polarity < 0 ? "text-red-400" : "text-gray-400"}`}
              >
                {data.avg_polarity > 0 ? "+" : ""}
                {data.avg_polarity.toFixed(3)}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-[10px] text-gray-500">Avg Subjectivity</span>
              <span className="text-[10px] text-gray-400 font-medium">
                {(data.avg_subjectivity * 100).toFixed(0)}%
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Polarity Histogram */}
      <div className="mt-4 relative z-10">
        <p className="text-[10px] text-gray-500 mb-2">Polarity Distribution</p>
        <div className="h-[80px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={histData}>
              <XAxis dataKey="range" fontSize={8} stroke="rgba(255,255,255,0.08)" tickLine={false} axisLine={false} />
              <YAxis fontSize={8} stroke="rgba(255,255,255,0.08)" tickLine={false} axisLine={false} width={20} />
              <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                {histData.map((_, i) => {
                  const colors = ["#f87171", "#fb923c", "#a78bfa", "#60a5fa", "#4ade80"];
                  return <Cell key={i} fill={colors[i]} fillOpacity={0.7} />;
                })}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </motion.div>
  );
}
