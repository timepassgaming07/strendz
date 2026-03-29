"use client";

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
