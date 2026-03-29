"use client";

import { motion } from "framer-motion";
import type { PlatformData } from "@/lib/api";

interface PlatformBreakdownProps {
  data: Record<string, PlatformData> | null;
}

const PLATFORM_CONFIG: Record<string, { color: string; icon: string }> = {
  twitter: { color: "#60a5fa", icon: "\U0001d54f" },
  instagram: { color: "#f472b6", icon: "\ud83d\udcf8" },
  linkedin: { color: "#38bdf8", icon: "in" },
};

export default function PlatformBreakdown({ data }: PlatformBreakdownProps) {
  if (!data) return null;

  const items = Object.entries(data).map(([name, d]) => ({
    name: name.charAt(0).toUpperCase() + name.slice(1),
    key: name,
    ...d,
  }));

  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-40px" }}
      transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] as [number, number, number, number] }}
      className="glass p-5"
    >
      <h3 className="section-title mb-4">Platform Breakdown</h3>
      <div className="space-y-4">
        {items.map((p) => {
          const cfg = PLATFORM_CONFIG[p.key] || { color: "#888", icon: "?" };
          return (
            <motion.div
              key={p.key}
              whileHover={{ x: 2, transition: { duration: 0.15 } }}
              className="flex items-center gap-3"
            >
              <div
                className="w-9 h-9 rounded-xl flex items-center justify-center text-xs font-bold shrink-0"
                style={{ backgroundColor: cfg.color + "18", color: cfg.color }}
              >
                {cfg.icon}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex justify-between text-[10px] mb-1.5">
                  <span className="text-gray-300 font-medium">{p.name}</span>
                  <span className="text-gray-600">{p.total} posts</span>
                </div>
                <div className="h-2 bg-white/[0.04] rounded-full overflow-hidden flex">
                  <motion.div
                    initial={{ width: 0 }}
                    whileInView={{ width: `${(p.positive / p.total) * 100}%` }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.9, ease: "easeOut" }}
                    className="h-full bg-emerald-400/60 rounded-l-full"
                  />
                  <motion.div
                    initial={{ width: 0 }}
                    whileInView={{ width: `${(p.neutral / p.total) * 100}%` }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.9, ease: "easeOut", delay: 0.1 }}
                    className="h-full bg-purple-400/40"
                  />
                  <motion.div
                    initial={{ width: 0 }}
                    whileInView={{ width: `${(p.negative / p.total) * 100}%` }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.9, ease: "easeOut", delay: 0.2 }}
                    className="h-full bg-rose-400/50 rounded-r-full"
                  />
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>
      <div className="flex items-center gap-4 mt-4 pt-3 border-t border-white/[0.04]">
        <span className="flex items-center gap-1.5 text-[9px] text-gray-500">
          <span className="w-2 h-2 rounded-full bg-emerald-400/60" /> Positive
        </span>
        <span className="flex items-center gap-1.5 text-[9px] text-gray-500">
          <span className="w-2 h-2 rounded-full bg-purple-400/40" /> Neutral
        </span>
        <span className="flex items-center gap-1.5 text-[9px] text-gray-500">
          <span className="w-2 h-2 rounded-full bg-rose-400/50" /> Negative
        </span>
      </div>
    </motion.div>
  );
}
