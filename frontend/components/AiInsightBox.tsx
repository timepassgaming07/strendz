"use client";

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
