#!/usr/bin/env python3
"""Write all refactored frontend component files."""
import os

BASE = "/Users/akshjain/social/frontend"

files = {}

# AnimatedBackground.tsx
files["components/AnimatedBackground.tsx"] = r'''"use client";

import { motion } from "framer-motion";
import { useMemo } from "react";

type Mood = "positive" | "neutral" | "negative";

interface AnimatedBackgroundProps {
  mood?: Mood;
}

const moodColors: Record<Mood, { blobs: string[]; base: string }> = {
  positive: {
    blobs: [
      "radial-gradient(circle, rgba(74,222,128,0.12) 0%, transparent 70%)",
      "radial-gradient(circle, rgba(56,189,248,0.10) 0%, transparent 70%)",
      "radial-gradient(circle, rgba(129,140,248,0.08) 0%, transparent 70%)",
      "radial-gradient(circle, rgba(52,211,153,0.06) 0%, transparent 70%)",
    ],
    base: "rgba(16, 28, 20, 0.3)",
  },
  neutral: {
    blobs: [
      "radial-gradient(circle, rgba(139,92,246,0.12) 0%, transparent 70%)",
      "radial-gradient(circle, rgba(236,72,153,0.08) 0%, transparent 70%)",
      "radial-gradient(circle, rgba(99,102,241,0.10) 0%, transparent 70%)",
      "radial-gradient(circle, rgba(168,85,247,0.06) 0%, transparent 70%)",
    ],
    base: "rgba(15, 14, 23, 0.3)",
  },
  negative: {
    blobs: [
      "radial-gradient(circle, rgba(248,113,113,0.10) 0%, transparent 70%)",
      "radial-gradient(circle, rgba(251,146,60,0.08) 0%, transparent 70%)",
      "radial-gradient(circle, rgba(168,85,247,0.06) 0%, transparent 70%)",
      "radial-gradient(circle, rgba(244,63,94,0.05) 0%, transparent 70%)",
    ],
    base: "rgba(28, 14, 14, 0.3)",
  },
};

const blobPositions = [
  { top: "5%", left: "10%", size: "45vw" },
  { top: "40%", right: "5%", size: "40vw" },
  { bottom: "10%", left: "35%", size: "35vw" },
  { top: "60%", left: "5%", size: "25vw" },
];

export default function AnimatedBackground({ mood = "neutral" }: AnimatedBackgroundProps) {
  const colors = moodColors[mood];

  const blobs = useMemo(
    () =>
      colors.blobs.map((gradient, i) => {
        const pos = blobPositions[i];
        return { gradient, pos, i };
      }),
    [colors.blobs],
  );

  return (
    <div className="fixed inset-0 -z-10 overflow-hidden">
      <motion.div
        className="absolute inset-0"
        animate={{
          background: [
            `linear-gradient(135deg, #0a0a12 0%, ${colors.base} 25%, #0f0e17 50%, #1a1032 100%)`,
            `linear-gradient(200deg, #0f0e17 0%, #1a1032 25%, ${colors.base} 50%, #0a0a12 100%)`,
            `linear-gradient(300deg, #1a1032 0%, ${colors.base} 25%, #0a0a12 50%, #0f0e17 100%)`,
            `linear-gradient(135deg, #0a0a12 0%, ${colors.base} 25%, #0f0e17 50%, #1a1032 100%)`,
          ],
        }}
        transition={{ duration: 25, repeat: Infinity, ease: "linear" }}
      />

      {blobs.map(({ gradient, pos, i }) => (
        <motion.div
          key={`${mood}-${i}`}
          className="absolute rounded-full"
          style={{
            width: pos.size,
            height: pos.size,
            background: gradient,
            top: pos.top,
            left: pos.left,
            right: (pos as Record<string, string>).right,
            bottom: (pos as Record<string, string>).bottom,
            filter: "blur(80px)",
          }}
          animate={{
            x: [0, 40, -30, 20, 0],
            y: [0, -35, 25, -15, 0],
            scale: [1, 1.06, 0.96, 1.04, 1],
          }}
          transition={{
            duration: 22 + i * 5,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />
      ))}

      <div
        className="absolute inset-0 opacity-[0.02]"
        style={{
          backgroundImage:
            "url(\"data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E\")",
        }}
      />
    </div>
  );
}
'''

# OverviewCards.tsx
files["components/OverviewCards.tsx"] = r'''"use client";

import { motion } from "framer-motion";
import type { SentimentSummary, TrendKeyword } from "@/lib/api";

type Mood = "positive" | "neutral" | "negative";

interface OverviewCardsProps {
  summary: SentimentSummary | null;
  topKeyword: TrendKeyword | null;
  mood?: Mood;
}

const cardVariants = {
  hidden: { opacity: 0, y: 20, scale: 0.97 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    scale: 1,
    transition: { delay: i * 0.06, duration: 0.5, ease: [0.22, 1, 0.36, 1] as [number, number, number, number] },
  }),
};

export default function OverviewCards({ summary, topKeyword, mood = "neutral" }: OverviewCardsProps) {
  const cards = [
    {
      label: "Total Mentions",
      value: summary?.total_mentions ?? "\u2014",
      gradient: "from-indigo-500/70 to-purple-500/70",
      glow: "rgba(99, 102, 241, 0.2)",
      icon: "M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z",
    },
    {
      label: "Positive",
      value: summary ? `${summary.positive_pct}%` : "\u2014",
      gradient: "from-emerald-400/70 to-cyan-400/70",
      glow: "rgba(52, 211, 153, 0.2)",
      icon: "M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z",
    },
    {
      label: "Negative",
      value: summary ? `${summary.negative_pct}%` : "\u2014",
      gradient: "from-rose-400/70 to-pink-400/70",
      glow: "rgba(244, 63, 94, 0.15)",
      icon: "M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z",
    },
    {
      label: "Trending",
      value: topKeyword?.keyword ?? "\u2014",
      gradient: "from-amber-400/70 to-orange-400/70",
      glow: "rgba(251, 191, 36, 0.15)",
      icon: "M13 7h8m0 0v8m0-8l-8 8-4-4-6 6",
    },
  ];

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
      {cards.map((card, i) => (
        <motion.div
          key={card.label}
          custom={i}
          variants={cardVariants}
          initial="hidden"
          animate="visible"
          whileHover={{ y: -3, transition: { duration: 0.25 } }}
          className="glass glass-hover p-4 cursor-default relative overflow-hidden"
        >
          <div
            className="absolute -top-6 -right-6 w-20 h-20 rounded-full opacity-30 blur-2xl pointer-events-none"
            style={{ background: card.glow }}
          />
          <div className="relative z-10">
            <div className="flex items-center justify-between mb-2">
              <span className="text-[10px] text-gray-500 font-medium uppercase tracking-widest">
                {card.label}
              </span>
              <div
                className={`w-8 h-8 rounded-xl bg-gradient-to-br ${card.gradient} flex items-center justify-center`}
                style={{ boxShadow: `0 4px 12px -2px ${card.glow}` }}
              >
                <svg className="w-3.5 h-3.5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={card.icon} />
                </svg>
              </div>
            </div>
            <p className="text-xl font-bold text-white/90 tracking-tight">{card.value}</p>
          </div>
        </motion.div>
      ))}
    </div>
  );
}
'''

# AiInsightBox.tsx
files["components/AiInsightBox.tsx"] = r'''"use client";

import { motion } from "framer-motion";

type Mood = "positive" | "neutral" | "negative";

interface AiInsightBoxProps {
  insight: string | null;
  mood?: Mood;
}

const moodBorder: Record<Mood, string> = {
  positive: "rgba(52, 211, 153, 0.35)",
  neutral: "rgba(139, 92, 246, 0.35)",
  negative: "rgba(244, 63, 94, 0.35)",
};

const moodGlow: Record<Mood, string> = {
  positive: "0 0 24px -6px rgba(52, 211, 153, 0.2)",
  neutral: "0 0 24px -6px rgba(139, 92, 246, 0.2)",
  negative: "0 0 24px -6px rgba(244, 63, 94, 0.15)",
};

export default function AiInsightBox({ insight, mood = "neutral" }: AiInsightBoxProps) {
  if (!insight) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] as [number, number, number, number] }}
      className="glass p-4 relative overflow-hidden"
      style={{
        borderLeft: `2px solid ${moodBorder[mood]}`,
        boxShadow: moodGlow[mood],
      }}
    >
      <motion.div
        className="absolute -top-8 -left-8 w-24 h-24 rounded-full pointer-events-none"
        style={{
          background: `radial-gradient(circle, ${moodBorder[mood].replace("0.35", "0.08")} 0%, transparent 70%)`,
        }}
        animate={{ scale: [1, 1.2, 1], opacity: [0.4, 0.7, 0.4] }}
        transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
      />
      <div className="relative z-10 flex items-start gap-3">
        <motion.div
          animate={{ rotate: [0, 3, -3, 0] }}
          transition={{ duration: 6, repeat: Infinity, ease: "easeInOut" }}
          className="w-7 h-7 rounded-lg bg-gradient-to-br from-purple-500/50 to-pink-500/50 flex items-center justify-center shrink-0"
        >
          <span className="text-xs">{"\ud83e\udde0"}</span>
        </motion.div>
        <div>
          <h3 className="text-[10px] font-semibold text-gray-400 uppercase tracking-widest mb-1">AI Insight</h3>
          <p className="text-[12px] text-gray-300/80 leading-relaxed">{insight}</p>
        </div>
      </div>
    </motion.div>
  );
}
'''

# SentimentChart.tsx
files["components/SentimentChart.tsx"] = r'''"use client";

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
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] as [number, number, number, number] }}
      className="glass p-4 relative overflow-hidden"
    >
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-3/4 h-3/4 rounded-full opacity-15 blur-3xl pointer-events-none"
        style={{ background: "radial-gradient(circle, rgba(139,92,246,0.12) 0%, transparent 70%)" }}
      />
      <h3 className="section-title mb-3 relative z-10">Sentiment Timeline</h3>
      <div className="h-[220px] relative z-10">
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
            <XAxis dataKey="time" stroke="rgba(255,255,255,0.1)" fontSize={9} tickLine={false} axisLine={false} />
            <YAxis stroke="rgba(255,255,255,0.1)" fontSize={9} tickLine={false} axisLine={false} />
            <Tooltip
              contentStyle={{
                background: "rgba(10, 10, 18, 0.95)",
                border: "1px solid rgba(255,255,255,0.06)",
                borderRadius: "14px",
                boxShadow: "0 8px 32px rgba(0,0,0,0.5)",
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
              wrapperStyle={{ fontSize: "10px", color: "rgba(255,255,255,0.4)" }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </motion.div>
  );
}
'''

# KeywordChart.tsx
files["components/KeywordChart.tsx"] = r'''"use client";

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
'''

# PlatformBreakdown.tsx
files["components/PlatformBreakdown.tsx"] = r'''"use client";

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

  const chartData = Object.entries(data).map(([name, d]) => ({
    name: name.charAt(0).toUpperCase() + name.slice(1),
    positive: d.positive,
    neutral: d.neutral,
    negative: d.negative,
    total: d.total,
    key: name,
  }));

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] as [number, number, number, number] }}
      className="glass p-4"
    >
      <h3 className="section-title mb-3">Platform Breakdown</h3>
      <div className="space-y-3">
        {chartData.map((p) => {
          const config = PLATFORM_CONFIG[p.key] || { color: "#888", icon: "?" };
          return (
            <motion.div
              key={p.key}
              whileHover={{ x: 3 }}
              transition={{ duration: 0.2 }}
              className="flex items-center gap-3"
            >
              <div
                className="w-8 h-8 rounded-xl flex items-center justify-center text-xs font-bold"
                style={{ backgroundColor: config.color + "20", color: config.color }}
              >
                {config.icon}
              </div>
              <div className="flex-1">
                <div className="flex justify-between text-[10px] mb-1">
                  <span className="text-gray-300 font-medium">{p.name}</span>
                  <span className="text-gray-600">{p.total}</span>
                </div>
                <div className="h-1.5 bg-white/[0.04] rounded-full overflow-hidden flex">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${(p.positive / p.total) * 100}%` }}
                    transition={{ duration: 0.8, ease: "easeOut" }}
                    className="h-full bg-emerald-400/60 rounded-l-full"
                  />
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${(p.neutral / p.total) * 100}%` }}
                    transition={{ duration: 0.8, ease: "easeOut", delay: 0.1 }}
                    className="h-full bg-purple-400/40"
                  />
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${(p.negative / p.total) * 100}%` }}
                    transition={{ duration: 0.8, ease: "easeOut", delay: 0.2 }}
                    className="h-full bg-rose-400/50 rounded-r-full"
                  />
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>
    </motion.div>
  );
}
'''

# EngagementMetrics.tsx
files["components/EngagementMetrics.tsx"] = r'''"use client";

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
    { label: "Likes", total: data.total_likes, avg: data.avg_likes, icon: "\u2764\ufe0f", glow: "rgba(244, 114, 182, 0.12)" },
    { label: "Shares", total: data.total_shares, avg: data.avg_shares, icon: "\ud83d\udd01", glow: "rgba(96, 165, 250, 0.12)" },
    { label: "Comments", total: data.total_comments, avg: data.avg_comments, icon: "\ud83d\udcac", glow: "rgba(167, 139, 250, 0.12)" },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] as [number, number, number, number] }}
      className="glass p-4"
    >
      <h3 className="section-title mb-3">Engagement</h3>
      <div className="grid grid-cols-3 gap-2">
        {metrics.map((m) => (
          <motion.div
            key={m.label}
            whileHover={{ y: -3, transition: { duration: 0.2 } }}
            className="text-center p-3 rounded-xl bg-white/[0.02] border border-white/[0.03] relative overflow-hidden"
          >
            <span className="text-lg relative z-10">{m.icon}</span>
            <p className="text-lg font-bold text-white/90 mt-1 tracking-tight relative z-10">
              {m.total >= 1000 ? `${(m.total / 1000).toFixed(1)}k` : m.total}
            </p>
            <p className="text-[9px] text-gray-500 uppercase tracking-widest mt-0.5 relative z-10">{m.label}</p>
            <p className="text-[10px] text-gray-600 mt-1 relative z-10">avg {m.avg}/post</p>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}
'''

# AlertsPanel.tsx
files["components/AlertsPanel.tsx"] = r'''"use client";

import { motion, AnimatePresence } from "framer-motion";
import type { Alert } from "@/lib/api";

type Mood = "positive" | "neutral" | "negative";

interface AlertsPanelProps {
  alerts: Alert[];
  mood?: Mood;
}

const alertStyles: Record<string, { border: string; bg: string; text: string; glow: string }> = {
  danger: { border: "border-rose-500/15", bg: "bg-rose-500/[0.04]", text: "text-rose-300", glow: "rgba(244, 63, 94, 0.08)" },
  warning: { border: "border-amber-500/15", bg: "bg-amber-500/[0.04]", text: "text-amber-300", glow: "rgba(245, 158, 11, 0.08)" },
  info: { border: "border-blue-400/15", bg: "bg-blue-400/[0.04]", text: "text-blue-300", glow: "rgba(96, 165, 250, 0.08)" },
  success: { border: "border-emerald-400/15", bg: "bg-emerald-400/[0.04]", text: "text-emerald-300", glow: "rgba(52, 211, 153, 0.08)" },
};

export default function AlertsPanel({ alerts, mood = "neutral" }: AlertsPanelProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] as [number, number, number, number] }}
      className="glass p-4"
    >
      <div className="flex items-center gap-2 mb-3">
        <h3 className="section-title">Alerts</h3>
        {alerts.length > 0 && (
          <span className="w-4 h-4 rounded-full bg-purple-500/20 text-purple-300 text-[9px] flex items-center justify-center font-semibold">
            {alerts.length}
          </span>
        )}
      </div>
      <div className="space-y-1.5">
        <AnimatePresence>
          {alerts.length === 0 && (
            <motion.p
              animate={{ opacity: [0.3, 0.5, 0.3] }}
              transition={{ duration: 3, repeat: Infinity }}
              className="text-[11px] text-gray-600 text-center py-4"
            >
              All clear
            </motion.p>
          )}
          {alerts.map((alert, i) => {
            const style = alertStyles[alert.type] || alertStyles.info;
            return (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: 16 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -16 }}
                transition={{ duration: 0.35, delay: i * 0.06 }}
                className={`flex items-center gap-2.5 p-2.5 rounded-xl border ${style.border} ${style.bg}`}
              >
                <span className="text-sm">{alert.icon}</span>
                <p className={`text-[11px] ${style.text} leading-relaxed`}>{alert.message}</p>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>
    </motion.div>
  );
}
'''

# ActivityFeed.tsx - keep for the profile panel's internal use but remove the standalone version
files["components/ActivityFeed.tsx"] = r'''"use client";

import { motion, AnimatePresence } from "framer-motion";
import type { Post } from "@/lib/api";

interface ActivityFeedProps {
  posts: Post[];
}

const sentimentConfig: Record<string, { color: string; bg: string; border: string; label: string }> = {
  positive: { color: "text-emerald-300", bg: "bg-emerald-400/10", border: "border-emerald-400/15", label: "Positive" },
  neutral: { color: "text-purple-300", bg: "bg-purple-400/10", border: "border-purple-400/15", label: "Neutral" },
  negative: { color: "text-rose-300", bg: "bg-rose-400/10", border: "border-rose-400/15", label: "Negative" },
};

const platformEmoji: Record<string, string> = {
  twitter: "\U0001d54f",
  instagram: "\ud83d\udcf8",
  linkedin: "\ud83d\udcbc",
};

export default function ActivityFeed({ posts }: ActivityFeedProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] as [number, number, number, number] }}
      className="glass p-4"
    >
      <h3 className="section-title mb-3">Recent Activity</h3>
      <div className="space-y-1.5 max-h-[300px] overflow-y-auto pr-1">
        <AnimatePresence>
          {posts.slice(0, 12).map((post, i) => {
            const s = sentimentConfig[post.sentiment?.label] || sentimentConfig.neutral;
            const timeAgo = getTimeAgo(post.timestamp);
            return (
              <motion.div
                key={post.id}
                initial={{ opacity: 0, x: 12 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -12 }}
                transition={{ duration: 0.3, delay: i * 0.02 }}
                className="flex items-start gap-2.5 p-2 rounded-xl hover:bg-white/[0.03] transition-colors"
              >
                <div className="w-7 h-7 rounded-lg bg-white/[0.05] flex items-center justify-center text-[11px] shrink-0">
                  {platformEmoji[post.platform] || "\ud83d\udcf1"}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-[11px] text-gray-300/80 leading-relaxed line-clamp-2">{post.text}</p>
                  <div className="flex items-center gap-1.5 mt-1">
                    <span className={`text-[9px] px-1.5 py-0.5 rounded-full ${s.bg} ${s.color} ${s.border} border font-medium`}>
                      {s.label}
                    </span>
                    <span className="text-[9px] text-gray-600">{timeAgo}</span>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>
    </motion.div>
  );
}

function getTimeAgo(timestamp: string): string {
  const seconds = Math.floor((Date.now() - new Date(timestamp).getTime()) / 1000);
  if (seconds < 60) return "just now";
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  return `${Math.floor(seconds / 86400)}d ago`;
}
'''

# page.tsx - complete refactored layout
files["app/page.tsx"] = r'''"use client";

import { useState, useEffect, useCallback, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import AnimatedBackground from "@/components/AnimatedBackground";
import Sidebar from "@/components/Sidebar";
import ProfilePanel from "@/components/ProfilePanel";
import FloatingSearch from "@/components/FloatingSearch";
import OverviewCards from "@/components/OverviewCards";
import SentimentChart from "@/components/SentimentChart";
import KeywordChart from "@/components/KeywordChart";
import PlatformBreakdown from "@/components/PlatformBreakdown";
import AlertsPanel from "@/components/AlertsPanel";
import EngagementMetrics from "@/components/EngagementMetrics";
import AiInsightBox from "@/components/AiInsightBox";
import ActivityFeed from "@/components/ActivityFeed";
import {
  api,
  type Post,
  type SentimentSummary,
  type TrendKeyword,
  type Alert,
  type TimelinePoint,
  type PlatformData,
} from "@/lib/api";

type Mood = "positive" | "neutral" | "negative";

function deriveMood(summary: SentimentSummary | null): Mood {
  if (!summary) return "neutral";
  if (summary.positive_pct > 50) return "positive";
  if (summary.negative_pct > 35) return "negative";
  return "neutral";
}

const staggerContainer = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.06, delayChildren: 0.1 },
  },
};

const fadeUp = {
  hidden: { opacity: 0, y: 18 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.5, ease: [0.22, 1, 0.36, 1] as [number, number, number, number] } },
};

export default function DashboardPage() {
  const [platform, setPlatform] = useState("");
  const [posts, setPosts] = useState<Post[]>([]);
  const [summary, setSummary] = useState<SentimentSummary | null>(null);
  const [keywords, setKeywords] = useState<TrendKeyword[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [timeline, setTimeline] = useState<TimelinePoint[]>([]);
  const [platformData, setPlatformData] = useState<Record<string, PlatformData> | null>(null);
  const [engagement, setEngagement] = useState<{
    total_likes: number;
    total_shares: number;
    total_comments: number;
    avg_likes: number;
    avg_shares: number;
    avg_comments: number;
  } | null>(null);
  const [insight, setInsight] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const mood = useMemo(() => deriveMood(summary), [summary]);

  const fetchAll = useCallback(async () => {
    try {
      const [dataRes, summaryRes, trendsRes, alertsRes, timelineRes, platRes, engRes, insightRes] =
        await Promise.all([
          api.getData(platform || undefined, 50),
          api.getSentimentSummary(platform || undefined),
          api.getTrends(10),
          api.getAlerts(),
          api.getSentimentTimeline(),
          api.getPlatformBreakdown(),
          api.getEngagement(),
          api.getAiInsight(),
        ]);

      setPosts(dataRes.posts);
      setSummary(summaryRes);
      setKeywords(trendsRes.keywords);
      setAlerts(alertsRes.alerts);
      setTimeline(timelineRes.timeline);
      setPlatformData(platRes);
      setEngagement(engRes);
      setInsight(insightRes.insight);
    } catch (err) {
      console.error("Failed to fetch data:", err);
    } finally {
      setLoading(false);
    }
  }, [platform]);

  useEffect(() => {
    setLoading(true);
    fetchAll();
  }, [fetchAll]);

  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const newPost = await api.simulate();
        setPosts((prev) => [newPost, ...prev.slice(0, 49)]);
        const [summaryRes, alertsRes] = await Promise.all([
          api.getSentimentSummary(platform || undefined),
          api.getAlerts(),
        ]);
        setSummary(summaryRes);
        setAlerts(alertsRes.alerts);
      } catch {
        // Silently ignore if backend is down
      }
    }, 3000);
    return () => clearInterval(interval);
  }, [platform]);

  const topKeyword = keywords.length > 0 ? keywords[0] : null;

  return (
    <>
      <AnimatedBackground mood={mood} />

      <AnimatePresence mode="wait">
        {loading ? (
          <motion.div
            key="loader"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="flex flex-col items-center justify-center min-h-screen gap-3"
          >
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ repeat: Infinity, duration: 1.2, ease: "linear" }}
              className="w-10 h-10 rounded-full border-2 border-purple-500/30 border-t-purple-400"
            />
            <p className="text-xs text-gray-500 tracking-wide">Loading analytics...</p>
          </motion.div>
        ) : (
          <motion.div
            key="dashboard"
            className="flex min-h-screen"
            initial="hidden"
            animate="visible"
            variants={staggerContainer}
          >
            {/* Icon Sidebar */}
            <Sidebar mood={mood} />

            {/* Profile Panel (Left) */}
            <ProfilePanel posts={posts} mood={mood} />

            {/* Main Dashboard (Right) */}
            <main className="flex-1 min-w-0 p-5 space-y-4 overflow-y-auto">
              {/* Top bar: floating search */}
              <motion.div variants={fadeUp} className="flex items-center justify-between">
                <div>
                  <h1 className="text-lg font-semibold bg-gradient-to-r from-purple-300 via-pink-300 to-indigo-300 bg-clip-text text-transparent tracking-tight">
                    Dashboard
                  </h1>
                  <p className="text-[10px] text-gray-500 mt-0.5">Real-time sentiment analytics</p>
                </div>
                <FloatingSearch platform={platform} onPlatformChange={setPlatform} />
              </motion.div>

              {/* AI Insight */}
              <motion.div variants={fadeUp}>
                <AiInsightBox insight={insight} mood={mood} />
              </motion.div>

              {/* Overview Cards */}
              <motion.div variants={fadeUp}>
                <OverviewCards summary={summary} topKeyword={topKeyword} mood={mood} />
              </motion.div>

              {/* Charts Row */}
              <motion.div variants={fadeUp} className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                <SentimentChart data={timeline} />
                <KeywordChart data={keywords} />
              </motion.div>

              {/* Bottom Row */}
              <motion.div variants={fadeUp} className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                <PlatformBreakdown data={platformData} />
                <EngagementMetrics data={engagement} />
                <AlertsPanel alerts={alerts} mood={mood} />
              </motion.div>

              {/* Activity Feed */}
              <motion.div variants={fadeUp}>
                <ActivityFeed posts={posts} />
              </motion.div>

              <motion.div variants={fadeUp} className="text-center text-[10px] text-gray-600/40 py-4 tracking-widest uppercase">
                Social Radar AI
              </motion.div>
            </main>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
'''

for rel_path, content in files.items():
    full_path = os.path.join(BASE, rel_path)
    with open(full_path, 'w') as f:
        f.write(content)
    print(f"OK: {rel_path}")

print("\nAll files written successfully!")
