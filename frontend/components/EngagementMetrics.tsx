"use client";

import { motion } from "framer-motion";

interface EngagementMetricsProps {
  data: {
    total_likes: number;
    total_shares: number;
    total_comments: number;
    avg_likes: number;
    avg_shares: number;
    avg_comments: number;
  } | null;
}

export default function EngagementMetrics({ data }: EngagementMetricsProps) {
  if (!data) return null;

  const metrics = [
    { label: "Likes", total: data.total_likes, avg: data.avg_likes, icon: "\u2764\ufe0f", color: "rgba(244, 114, 182, 0.15)" },
    { label: "Shares", total: data.total_shares, avg: data.avg_shares, icon: "\ud83d\udd01", color: "rgba(96, 165, 250, 0.15)" },
    { label: "Comments", total: data.total_comments, avg: data.avg_comments, icon: "\ud83d\udcac", color: "rgba(167, 139, 250, 0.15)" },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-40px" }}
      transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] as [number, number, number, number] }}
      className="glass p-5"
    >
      <h3 className="section-title mb-4">Engagement</h3>
      <div className="space-y-3">
        {metrics.map((m, i) => (
          <motion.div
            key={m.label}
            initial={{ opacity: 0, x: -12 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ delay: i * 0.08, duration: 0.4 }}
            whileHover={{ x: 2, transition: { duration: 0.15 } }}
            className="flex items-center gap-3 p-3 rounded-xl bg-white/[0.02] border border-white/[0.03]"
          >
            <div
              className="w-10 h-10 rounded-xl flex items-center justify-center text-lg shrink-0"
              style={{ background: m.color }}
            >
              {m.icon}
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-baseline justify-between">
                <span className="text-[10px] text-gray-500 uppercase tracking-widest">{m.label}</span>
                <span className="text-[10px] text-gray-600">avg {m.avg}/post</span>
              </div>
              <p className="text-lg font-bold text-white/90 tracking-tight mt-0.5">
                {m.total >= 1000 ? `${(m.total / 1000).toFixed(1)}k` : m.total}
              </p>
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}
