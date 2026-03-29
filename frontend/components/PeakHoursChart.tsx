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

interface PeakHoursChartProps {
  data: {
    hour: number;
    label: string;
    posts: number;
    engagement: number;
    avg_engagement: number;
  }[] | null;
}

export default function PeakHoursChart({ data }: PeakHoursChartProps) {
  if (!data) return null;

  const maxEng = Math.max(...data.map((d) => d.engagement), 1);
  const totalEng = data.reduce((a, d) => a + d.engagement, 0);
  const activePosts = data.reduce((a, d) => a + d.posts, 0);
  const activeHours = data.filter((d) => d.engagement > 0);
  const best = activeHours.length > 0 ? activeHours.reduce((a, b) => (a.engagement > b.engagement ? a : b)) : null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-40px" }}
      transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] as [number, number, number, number] }}
      className="glass p-5 relative overflow-hidden"
    >
      <div
        className="absolute bottom-0 left-0 w-1/2 h-1/2 rounded-full opacity-10 blur-3xl pointer-events-none"
        style={{ background: "radial-gradient(circle, rgba(96,165,250,0.15) 0%, transparent 70%)" }}
      />

      {/* Header with stats */}
      <div className="flex items-start justify-between mb-5 relative z-10">
        <div>
          <h3 className="text-sm font-semibold text-gray-200 tracking-tight">Peak Engagement Hours</h3>
          <p className="text-[11px] text-gray-500 mt-0.5">Discover when your audience is most active</p>
        </div>
        <div className="flex gap-4">
          <div className="text-right">
            <p className="text-lg font-bold text-white leading-none">{totalEng}</p>
            <p className="text-[9px] text-gray-500 mt-0.5 uppercase tracking-wider">Total Eng.</p>
          </div>
          <div className="text-right">
            <p className="text-lg font-bold text-white leading-none">{activePosts}</p>
            <p className="text-[9px] text-gray-500 mt-0.5 uppercase tracking-wider">Posts</p>
          </div>
        </div>
      </div>

      <div className="h-[200px] relative z-10">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} barCategoryGap="12%">
            <XAxis
              dataKey="label"
              fontSize={9}
              stroke="rgba(255,255,255,0.1)"
              tickLine={false}
              axisLine={false}
              interval={2}
              tick={{ fill: "rgba(255,255,255,0.35)" }}
            />
            <YAxis
              fontSize={9}
              stroke="rgba(255,255,255,0.06)"
              tickLine={false}
              axisLine={false}
              width={30}
              tick={{ fill: "rgba(255,255,255,0.25)" }}
            />
            <Tooltip
              cursor={{ fill: "rgba(255,255,255,0.03)" }}
              contentStyle={{
                background: "rgba(8, 8, 15, 0.95)",
                border: "1px solid rgba(255,255,255,0.08)",
                borderRadius: "12px",
                boxShadow: "0 8px 32px rgba(0,0,0,0.5)",
                backdropFilter: "blur(20px)",
                padding: "10px 14px",
              }}
              labelStyle={{ color: "rgba(255,255,255,0.5)", fontSize: "10px", marginBottom: "4px" }}
              itemStyle={{ color: "rgba(255,255,255,0.8)", fontSize: "11px" }}
              formatter={(value: unknown, name: unknown) => {
                const labels: Record<string, string> = {
                  engagement: "Engagements",
                  posts: "Posts",
                };
                return [Number(value), labels[String(name)] || String(name)];
              }}
            />
            <Bar dataKey="engagement" radius={[6, 6, 0, 0]} animationDuration={800}>
              {data.map((d, i) => {
                const intensity = d.engagement / maxEng;
                const color =
                  intensity > 0.7
                    ? "#4ade80"
                    : intensity > 0.3
                      ? "#60a5fa"
                      : "rgba(167,139,250,0.4)";
                return <Cell key={i} fill={color} fillOpacity={intensity > 0 ? 0.85 : 0.1} />;
              })}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Best time badge */}
      {best && (
        <div className="mt-4 flex items-center gap-3 p-3 rounded-xl bg-gradient-to-r from-green-500/[0.06] to-transparent border border-green-500/10 relative z-10">
          <div className="w-8 h-8 rounded-lg bg-green-500/15 flex items-center justify-center text-sm">🏆</div>
          <div>
            <p className="text-[11px] text-gray-300 font-medium">
              Best time to post: <span className="text-green-400 font-semibold">{best.label}</span>
            </p>
            <p className="text-[10px] text-gray-500">
              {best.engagement} engagements across {best.posts} post{best.posts !== 1 ? "s" : ""}
            </p>
          </div>
        </div>
      )}
    </motion.div>
  );
}
