#!/usr/bin/env python3
"""Complete UI refactor: premium minimal dashboard."""
import os

BASE = "/Users/akshjain/social/frontend"
files = {}

# ── globals.css ──────────────────────────────────────────────────────────────
files["app/globals.css"] = r"""@import "tailwindcss";

@theme {
  --color-primary-50: #fdf2f8;
  --color-primary-100: #fce7f3;
  --color-primary-200: #fbcfe8;
  --color-primary-300: #f9a8d4;
  --color-primary-400: #f472b6;
  --color-primary-500: #ec4899;
  --color-primary-600: #db2777;
  --color-primary-700: #be185d;

  --color-accent-50: #f5f3ff;
  --color-accent-100: #ede9fe;
  --color-accent-200: #ddd6fe;
  --color-accent-300: #c4b5fd;
  --color-accent-400: #a78bfa;
  --color-accent-500: #8b5cf6;
  --color-accent-600: #7c3aed;
  --color-accent-700: #6d28d9;
}

* {
  box-sizing: border-box;
}

body {
  background: #08080f;
  color: #e2e8f0;
  min-height: 100vh;
  font-feature-settings: "cv02", "cv03", "cv04", "cv11";
  letter-spacing: 0.01em;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  overflow-x: hidden;
}

/* Scrollbar */
::-webkit-scrollbar {
  width: 5px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: rgba(139, 92, 246, 0.12);
  border-radius: 10px;
}
::-webkit-scrollbar-thumb:hover {
  background: rgba(139, 92, 246, 0.25);
}

/* Premium glass card */
.glass {
  background: linear-gradient(
    135deg,
    rgba(255, 255, 255, 0.055) 0%,
    rgba(255, 255, 255, 0.02) 100%
  );
  backdrop-filter: blur(28px) saturate(1.4);
  -webkit-backdrop-filter: blur(28px) saturate(1.4);
  border: 1px solid rgba(255, 255, 255, 0.07);
  border-radius: 20px;
  box-shadow:
    0 8px 32px -4px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.06);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.glass-hover:hover {
  background: linear-gradient(
    135deg,
    rgba(255, 255, 255, 0.08) 0%,
    rgba(255, 255, 255, 0.035) 100%
  );
  border-color: rgba(139, 92, 246, 0.12);
  box-shadow:
    0 16px 48px -6px rgba(139, 92, 246, 0.08),
    0 8px 32px -4px rgba(0, 0, 0, 0.25),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  transform: translateY(-2px);
}

/* Sticky header glass */
.glass-sticky {
  background: linear-gradient(
    135deg,
    rgba(8, 8, 15, 0.75) 0%,
    rgba(15, 14, 23, 0.7) 100%
  );
  backdrop-filter: blur(40px) saturate(1.6);
  -webkit-backdrop-filter: blur(40px) saturate(1.6);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  box-shadow:
    0 8px 40px -8px rgba(0, 0, 0, 0.45),
    inset 0 -1px 0 rgba(255, 255, 255, 0.02);
}

/* Section heading */
.section-title {
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  color: rgba(203, 213, 225, 0.5);
  text-transform: uppercase;
}

/* Mood glow accents */
.mood-glow-positive {
  box-shadow:
    0 0 60px -15px rgba(74, 222, 128, 0.08),
    inset 0 1px 0 rgba(74, 222, 128, 0.04);
}
.mood-glow-negative {
  box-shadow:
    0 0 60px -15px rgba(248, 113, 113, 0.08),
    inset 0 1px 0 rgba(248, 113, 113, 0.04);
}
.mood-glow-neutral {
  box-shadow:
    0 0 60px -15px rgba(139, 92, 246, 0.08),
    inset 0 1px 0 rgba(139, 92, 246, 0.04);
}
"""

# ── AnimatedBackground.tsx ───────────────────────────────────────────────────
files["components/AnimatedBackground.tsx"] = r""""use client";

import { motion, useScroll, useTransform } from "framer-motion";
import { useMemo, useRef, useEffect, useState } from "react";

type Mood = "positive" | "neutral" | "negative";

interface AnimatedBackgroundProps {
  mood?: Mood;
}

const moodColors: Record<Mood, { blobs: string[]; base: string }> = {
  positive: {
    blobs: [
      "radial-gradient(circle, rgba(74,222,128,0.14) 0%, transparent 70%)",
      "radial-gradient(circle, rgba(56,189,248,0.10) 0%, transparent 70%)",
      "radial-gradient(circle, rgba(129,140,248,0.08) 0%, transparent 70%)",
      "radial-gradient(circle, rgba(52,211,153,0.06) 0%, transparent 70%)",
    ],
    base: "rgba(16, 28, 20, 0.35)",
  },
  neutral: {
    blobs: [
      "radial-gradient(circle, rgba(139,92,246,0.14) 0%, transparent 70%)",
      "radial-gradient(circle, rgba(236,72,153,0.10) 0%, transparent 70%)",
      "radial-gradient(circle, rgba(99,102,241,0.10) 0%, transparent 70%)",
      "radial-gradient(circle, rgba(168,85,247,0.06) 0%, transparent 70%)",
    ],
    base: "rgba(15, 14, 23, 0.35)",
  },
  negative: {
    blobs: [
      "radial-gradient(circle, rgba(248,113,113,0.12) 0%, transparent 70%)",
      "radial-gradient(circle, rgba(251,146,60,0.08) 0%, transparent 70%)",
      "radial-gradient(circle, rgba(168,85,247,0.06) 0%, transparent 70%)",
      "radial-gradient(circle, rgba(244,63,94,0.05) 0%, transparent 70%)",
    ],
    base: "rgba(28, 14, 14, 0.35)",
  },
};

const blobConfigs = [
  { top: "0%", left: "5%", size: "50vw" },
  { top: "30%", left: "55%", size: "45vw" },
  { top: "65%", left: "25%", size: "40vw" },
  { top: "50%", left: "70%", size: "30vw" },
];

export default function AnimatedBackground({ mood = "neutral" }: AnimatedBackgroundProps) {
  const colors = moodColors[mood];
  const containerRef = useRef<HTMLDivElement>(null);
  const [scrollY, setScrollY] = useState(0);

  useEffect(() => {
    const handleScroll = () => setScrollY(window.scrollY);
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const parallaxOffset = scrollY * 0.15;

  return (
    <div ref={containerRef} className="fixed inset-0 -z-10 overflow-hidden">
      {/* Animated base gradient */}
      <motion.div
        className="absolute inset-0"
        animate={{
          background: [
            `linear-gradient(135deg, #08080f 0%, ${colors.base} 30%, #0f0e17 60%, #1a1032 100%)`,
            `linear-gradient(200deg, #0f0e17 0%, #1a1032 30%, ${colors.base} 60%, #08080f 100%)`,
            `linear-gradient(300deg, #1a1032 0%, ${colors.base} 30%, #08080f 60%, #0f0e17 100%)`,
            `linear-gradient(135deg, #08080f 0%, ${colors.base} 30%, #0f0e17 60%, #1a1032 100%)`,
          ],
        }}
        transition={{ duration: 25, repeat: Infinity, ease: "linear" }}
      />

      {/* Scroll-reactive blobs */}
      {colors.blobs.map((gradient, i) => {
        const cfg = blobConfigs[i];
        return (
          <motion.div
            key={`${mood}-${i}`}
            className="absolute rounded-full"
            style={{
              width: cfg.size,
              height: cfg.size,
              background: gradient,
              top: cfg.top,
              left: cfg.left,
              filter: "blur(80px)",
              transform: `translateY(${parallaxOffset * (i % 2 === 0 ? -1 : 1) * (0.5 + i * 0.2)}px)`,
            }}
            animate={{
              x: [0, 40 + i * 10, -30 - i * 5, 20, 0],
              y: [0, -35 + i * 8, 25, -15, 0],
              scale: [1, 1.05, 0.97, 1.03, 1],
            }}
            transition={{
              duration: 20 + i * 6,
              repeat: Infinity,
              ease: "easeInOut",
            }}
          />
        );
      })}

      {/* Noise texture */}
      <div
        className="absolute inset-0 opacity-[0.015]"
        style={{
          backgroundImage:
            "url(\"data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E\")",
        }}
      />
    </div>
  );
}
"""

# ── FloatingSearch.tsx ───────────────────────────────────────────────────────
files["components/FloatingSearch.tsx"] = r""""use client";

import { motion } from "framer-motion";
import { useState } from "react";

interface FloatingSearchProps {
  platform: string;
  onPlatformChange: (p: string) => void;
}

const platforms = [
  { value: "", label: "All" },
  { value: "twitter", label: "Twitter" },
  { value: "instagram", label: "Instagram" },
  { value: "linkedin", label: "LinkedIn" },
];

export default function FloatingSearch({ platform, onPlatformChange }: FloatingSearchProps) {
  const [focused, setFocused] = useState(false);

  return (
    <motion.div
      initial={{ y: -12, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5, delay: 0.1, ease: [0.22, 1, 0.36, 1] as [number, number, number, number] }}
      className="flex items-center gap-2.5"
    >
      {/* Platform pills */}
      <div className="hidden sm:flex items-center gap-1 bg-white/[0.04] rounded-full p-1 border border-white/[0.05]">
        {platforms.map((p) => (
          <button
            key={p.value}
            onClick={() => onPlatformChange(p.value)}
            className={`px-3.5 py-1.5 rounded-full text-[10px] font-medium transition-all duration-300 ${
              platform === p.value
                ? "bg-gradient-to-r from-purple-500/60 to-pink-500/60 text-white shadow-lg shadow-purple-500/10"
                : "text-gray-500 hover:text-gray-300 hover:bg-white/[0.04]"
            }`}
          >
            {p.label}
          </button>
        ))}
      </div>

      {/* Pill search bar */}
      <motion.div
        animate={{ width: focused ? 220 : 170 }}
        transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] as [number, number, number, number] }}
        className="relative"
      >
        <svg
          className="w-3.5 h-3.5 text-gray-600 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <input
          type="text"
          placeholder="Search..."
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          className="w-full bg-white/[0.04] border border-white/[0.06] rounded-full pl-10 pr-4 py-2 text-[11px] text-gray-400 placeholder-gray-600 focus:outline-none focus:border-purple-500/20 focus:bg-white/[0.06] transition-all duration-300"
        />
      </motion.div>
    </motion.div>
  );
}
"""

# ── OverviewCards.tsx (inline for sticky bar) ────────────────────────────────
files["components/OverviewCards.tsx"] = r""""use client";

import { motion } from "framer-motion";
import type { SentimentSummary, TrendKeyword } from "@/lib/api";

type Mood = "positive" | "neutral" | "negative";

interface OverviewCardsProps {
  summary: SentimentSummary | null;
  topKeyword: TrendKeyword | null;
  mood?: Mood;
}

const cardVariants = {
  hidden: { opacity: 0, y: 14, scale: 0.97 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    scale: 1,
    transition: { delay: i * 0.05, duration: 0.45, ease: [0.22, 1, 0.36, 1] as [number, number, number, number] },
  }),
};

export default function OverviewCards({ summary, topKeyword }: OverviewCardsProps) {
  const cards = [
    {
      label: "Total Mentions",
      value: summary?.total_mentions ?? "\u2014",
      gradient: "from-indigo-500/60 to-purple-500/60",
      glow: "rgba(99, 102, 241, 0.15)",
      icon: "M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z",
    },
    {
      label: "Positive",
      value: summary ? `${summary.positive_pct}%` : "\u2014",
      gradient: "from-emerald-400/60 to-cyan-400/60",
      glow: "rgba(52, 211, 153, 0.15)",
      icon: "M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z",
    },
    {
      label: "Negative",
      value: summary ? `${summary.negative_pct}%` : "\u2014",
      gradient: "from-rose-400/60 to-pink-400/60",
      glow: "rgba(244, 63, 94, 0.12)",
      icon: "M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z",
    },
    {
      label: "Trending",
      value: topKeyword?.keyword ?? "\u2014",
      gradient: "from-amber-400/60 to-orange-400/60",
      glow: "rgba(251, 191, 36, 0.12)",
      icon: "M13 7h8m0 0v8m0-8l-8 8-4-4-6 6",
    },
  ];

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-2.5">
      {cards.map((card, i) => (
        <motion.div
          key={card.label}
          custom={i}
          variants={cardVariants}
          initial="hidden"
          animate="visible"
          whileHover={{ y: -2, transition: { duration: 0.2 } }}
          className="glass glass-hover px-4 py-3 cursor-default relative overflow-hidden"
        >
          <div
            className="absolute -top-5 -right-5 w-16 h-16 rounded-full opacity-25 blur-2xl pointer-events-none"
            style={{ background: card.glow }}
          />
          <div className="relative z-10">
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-[9px] text-gray-500 font-medium uppercase tracking-widest">
                {card.label}
              </span>
              <div
                className={`w-7 h-7 rounded-lg bg-gradient-to-br ${card.gradient} flex items-center justify-center`}
                style={{ boxShadow: `0 4px 12px -4px ${card.glow}` }}
              >
                <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={card.icon} />
                </svg>
              </div>
            </div>
            <p className="text-lg font-bold text-white/90 tracking-tight">{card.value}</p>
          </div>
        </motion.div>
      ))}
    </div>
  );
}
"""

# ── AiInsightBox.tsx (compact for sticky) ────────────────────────────────────
files["components/AiInsightBox.tsx"] = r""""use client";

import { motion } from "framer-motion";

type Mood = "positive" | "neutral" | "negative";

interface AiInsightBoxProps {
  insight: string | null;
  mood?: Mood;
}

const moodBorder: Record<Mood, string> = {
  positive: "rgba(52, 211, 153, 0.3)",
  neutral: "rgba(139, 92, 246, 0.3)",
  negative: "rgba(244, 63, 94, 0.3)",
};

export default function AiInsightBox({ insight, mood = "neutral" }: AiInsightBoxProps) {
  if (!insight) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1] as [number, number, number, number] }}
      className="flex items-center gap-3 px-4 py-3 rounded-2xl"
      style={{
        background: "linear-gradient(135deg, rgba(255,255,255,0.04) 0%, rgba(255,255,255,0.015) 100%)",
        border: `1px solid ${moodBorder[mood].replace("0.3", "0.12")}`,
        borderLeft: `2px solid ${moodBorder[mood]}`,
      }}
    >
      <motion.div
        animate={{ rotate: [0, 3, -3, 0] }}
        transition={{ duration: 6, repeat: Infinity, ease: "easeInOut" }}
        className="w-7 h-7 rounded-lg bg-gradient-to-br from-purple-500/40 to-pink-500/40 flex items-center justify-center shrink-0"
      >
        <span className="text-xs">{"\ud83e\udde0"}</span>
      </motion.div>
      <p className="text-[11px] text-gray-300/80 leading-relaxed line-clamp-2 flex-1">{insight}</p>
    </motion.div>
  );
}
"""

# ── SentimentChart.tsx ───────────────────────────────────────────────────────
files["components/SentimentChart.tsx"] = r""""use client";

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
"""

# ── PlatformBreakdown.tsx ────────────────────────────────────────────────────
files["components/PlatformBreakdown.tsx"] = r""""use client";

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
"""

# ── EngagementMetrics.tsx ────────────────────────────────────────────────────
files["components/EngagementMetrics.tsx"] = r""""use client";

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
"""

# ── AlertsPanel.tsx ──────────────────────────────────────────────────────────
files["components/AlertsPanel.tsx"] = r""""use client";

import { motion, AnimatePresence } from "framer-motion";
import type { Alert } from "@/lib/api";

type Mood = "positive" | "neutral" | "negative";

interface AlertsPanelProps {
  alerts: Alert[];
  mood?: Mood;
}

const alertStyles: Record<string, { border: string; bg: string; text: string }> = {
  danger: { border: "border-rose-500/12", bg: "bg-rose-500/[0.04]", text: "text-rose-300" },
  warning: { border: "border-amber-500/12", bg: "bg-amber-500/[0.04]", text: "text-amber-300" },
  info: { border: "border-blue-400/12", bg: "bg-blue-400/[0.04]", text: "text-blue-300" },
  success: { border: "border-emerald-400/12", bg: "bg-emerald-400/[0.04]", text: "text-emerald-300" },
};

export default function AlertsPanel({ alerts }: AlertsPanelProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-40px" }}
      transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] as [number, number, number, number] }}
      className="glass p-5"
    >
      <div className="flex items-center gap-2 mb-4">
        <h3 className="section-title">Alerts</h3>
        {alerts.length > 0 && (
          <span className="w-5 h-5 rounded-full bg-purple-500/15 text-purple-300 text-[9px] flex items-center justify-center font-semibold">
            {alerts.length}
          </span>
        )}
      </div>
      <div className="space-y-2">
        <AnimatePresence>
          {alerts.length === 0 && (
            <motion.p
              animate={{ opacity: [0.3, 0.5, 0.3] }}
              transition={{ duration: 3, repeat: Infinity }}
              className="text-[11px] text-gray-600 text-center py-6"
            >
              All clear
            </motion.p>
          )}
          {alerts.map((alert, i) => {
            const s = alertStyles[alert.type] || alertStyles.info;
            return (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.35, delay: i * 0.06 }}
                className={`flex items-center gap-3 p-3 rounded-xl border ${s.border} ${s.bg}`}
              >
                <span className="text-sm shrink-0">{alert.icon}</span>
                <p className={`text-[11px] ${s.text} leading-relaxed`}>{alert.message}</p>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>
    </motion.div>
  );
}
"""

# ── page.tsx (COMPLETE REWRITE — no sidebar, sticky top, scroll content) ─────
files["app/page.tsx"] = r""""use client";

import { useState, useEffect, useCallback, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import AnimatedBackground from "@/components/AnimatedBackground";
import FloatingSearch from "@/components/FloatingSearch";
import OverviewCards from "@/components/OverviewCards";
import SentimentChart from "@/components/SentimentChart";
import PlatformBreakdown from "@/components/PlatformBreakdown";
import AlertsPanel from "@/components/AlertsPanel";
import EngagementMetrics from "@/components/EngagementMetrics";
import AiInsightBox from "@/components/AiInsightBox";
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

const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.55, ease: [0.22, 1, 0.36, 1] as [number, number, number, number] },
  },
};

const stagger = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.08, delayChildren: 0.05 },
  },
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
      console.error("Fetch failed:", err);
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
        /* backend may be down */
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
            exit={{ opacity: 0, transition: { duration: 0.3 } }}
            className="flex flex-col items-center justify-center min-h-screen gap-4"
          >
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ repeat: Infinity, duration: 1.2, ease: "linear" }}
              className="w-10 h-10 rounded-full border-2 border-purple-500/20 border-t-purple-400"
            />
            <p className="text-[11px] text-gray-600 tracking-widest uppercase">Loading analytics</p>
          </motion.div>
        ) : (
          <motion.div key="app" initial="hidden" animate="visible" variants={stagger}>
            {/* ── STICKY TOP DASHBOARD ────────────────────────── */}
            <div className="sticky top-0 z-40 glass-sticky">
              <div className="max-w-[1400px] mx-auto px-6 py-4 space-y-3">
                {/* Title + Search */}
                <motion.div variants={fadeUp} className="flex items-center justify-between">
                  <div>
                    <h1 className="text-base font-semibold bg-gradient-to-r from-purple-300 via-pink-300 to-indigo-300 bg-clip-text text-transparent tracking-tight">
                      Social Radar
                    </h1>
                    <p className="text-[9px] text-gray-500 mt-0.5 tracking-wide">Real-time sentiment analytics</p>
                  </div>
                  <FloatingSearch platform={platform} onPlatformChange={setPlatform} />
                </motion.div>

                {/* AI Insight */}
                <motion.div variants={fadeUp}>
                  <AiInsightBox insight={insight} mood={mood} />
                </motion.div>

                {/* Metric Cards */}
                <motion.div variants={fadeUp}>
                  <OverviewCards summary={summary} topKeyword={topKeyword} mood={mood} />
                </motion.div>
              </div>
            </div>

            {/* ── SCROLLABLE CONTENT ──────────────────────────── */}
            <main className="max-w-[1400px] mx-auto px-6 py-6 space-y-5">
              {/* Sentiment Timeline — full width */}
              <motion.div variants={fadeUp}>
                <SentimentChart data={timeline} />
              </motion.div>

              {/* Two-column: Platform + Engagement */}
              <motion.div variants={fadeUp} className="grid grid-cols-1 lg:grid-cols-2 gap-5">
                <PlatformBreakdown data={platformData} />
                <EngagementMetrics data={engagement} />
              </motion.div>

              {/* Alerts */}
              <motion.div variants={fadeUp}>
                <AlertsPanel alerts={alerts} mood={mood} />
              </motion.div>

              {/* Footer */}
              <div className="text-center text-[9px] text-gray-700/40 py-6 tracking-[0.2em] uppercase select-none">
                Social Radar AI
              </div>
            </main>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
"""

# ── Write all files ──────────────────────────────────────────────────────────
for rel, content in files.items():
    path = os.path.join(BASE, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    print(f"  OK  {rel}")

print("\nAll files written.")
