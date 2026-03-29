"use client";

import { motion } from "framer-motion";

type Mood = "positive" | "neutral" | "negative";

interface NavbarProps {
  platform: string;
  onPlatformChange: (p: string) => void;
  mood?: Mood;
}

const moodDot: Record<Mood, string> = {
  positive: "bg-emerald-400",
  neutral: "bg-purple-400",
  negative: "bg-rose-400",
};

export default function Navbar({ platform, onPlatformChange, mood = "neutral" }: NavbarProps) {
  const platforms = [
    { value: "", label: "All Platforms" },
    { value: "twitter", label: "Twitter" },
    { value: "instagram", label: "Instagram" },
    { value: "linkedin", label: "LinkedIn" },
  ];

  return (
    <motion.header
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
      className="glass px-6 py-4 flex items-center justify-between"
    >
      <div className="flex items-center gap-3">
        <div>
          <h1 className="text-xl font-semibold bg-gradient-to-r from-purple-300 via-pink-300 to-indigo-300 bg-clip-text text-transparent tracking-tight">
            Strendz
          </h1>
          <div className="flex items-center gap-2 mt-0.5">
            <motion.div
              animate={{ scale: [1, 1.4, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
              className={`w-1.5 h-1.5 rounded-full ${moodDot[mood]}`}
            />
            <p className="text-[11px] text-gray-500 tracking-wide">Live sentiment analytics</p>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-3">
        {/* Platform Filter — pill style */}
        <div className="flex items-center gap-1 bg-white/[0.04] rounded-2xl p-1 border border-white/[0.05]">
          {platforms.map((p) => (
            <button
              key={p.value}
              onClick={() => onPlatformChange(p.value)}
              className={`px-4 py-1.5 rounded-xl text-[11px] font-medium transition-all duration-300 ${
                platform === p.value
                  ? "bg-gradient-to-r from-purple-500/80 to-pink-500/80 text-white shadow-lg shadow-purple-500/20"
                  : "text-gray-500 hover:text-gray-300 hover:bg-white/[0.04]"
              }`}
            >
              {p.label}
            </button>
          ))}
        </div>

        {/* Search */}
        <div className="relative">
          <svg className="w-3.5 h-3.5 text-gray-600 absolute left-3 top-1/2 -translate-y-1/2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            type="text"
            placeholder="Search..."
            className="bg-white/[0.04] border border-white/[0.06] rounded-2xl pl-9 pr-4 py-2 text-[12px] text-gray-400 placeholder-gray-600 focus:outline-none focus:border-purple-500/30 focus:bg-white/[0.06] w-44 transition-all duration-300"
          />
        </div>

        {/* Profile */}
        <motion.div
          whileHover={{ scale: 1.08 }}
          className="w-9 h-9 rounded-2xl bg-gradient-to-br from-purple-500/80 to-pink-500/80 flex items-center justify-center text-white text-[11px] font-semibold shadow-lg shadow-purple-500/20 cursor-pointer"
        >
          SR
        </motion.div>
      </div>
    </motion.header>
  );
}
