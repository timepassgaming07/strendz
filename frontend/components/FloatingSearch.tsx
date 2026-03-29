"use client";

import { motion } from "framer-motion";
import { useState } from "react";

interface FloatingSearchProps {
  platform: string;
  onPlatformChange: (p: string) => void;
}

const platforms = [
  { value: "", label: "All" },
  { value: "twitter", label: "Twitter" },
  { value: "reddit", label: "Reddit" },
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
