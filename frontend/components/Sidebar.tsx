"use client";

import { motion } from "framer-motion";

type Mood = "positive" | "neutral" | "negative";

const icons = [
  { label: "Dashboard", path: "M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" },
  { label: "Analytics", path: "M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" },
  { label: "Mentions", path: "M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" },
  { label: "Trends", path: "M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" },
  { label: "Settings", path: "M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" },
];

const moodAccent: Record<Mood, string> = {
  positive: "from-emerald-400 to-cyan-400",
  neutral: "from-purple-400 to-pink-400",
  negative: "from-rose-400 to-orange-400",
};

interface SidebarProps {
  mood?: Mood;
}

export default function Sidebar({ mood = "neutral" }: SidebarProps) {
  return (
    <motion.aside
      initial={{ x: -80, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
      className="fixed left-0 top-0 h-screen w-[72px] flex flex-col items-center py-6 gap-2 z-50"
      style={{
        background: "rgba(255, 255, 255, 0.03)",
        backdropFilter: "blur(24px)",
        WebkitBackdropFilter: "blur(24px)",
        borderRight: "1px solid rgba(255, 255, 255, 0.06)",
      }}
    >
      {/* Logo */}
      <motion.div
        whileHover={{ scale: 1.1, rotate: 5 }}
        transition={{ type: "spring", stiffness: 400, damping: 15 }}
        className={`w-10 h-10 rounded-2xl bg-gradient-to-br ${moodAccent[mood]} flex items-center justify-center mb-8 shadow-lg`}
        style={{ boxShadow: "0 4px 20px -4px rgba(139, 92, 246, 0.4)" }}
      >
        <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      </motion.div>

      {/* Nav Icons */}
      {icons.map((icon, i) => (
        <motion.button
          key={icon.label}
          whileHover={{ scale: 1.12 }}
          whileTap={{ scale: 0.92 }}
          className="w-10 h-10 rounded-2xl flex items-center justify-center transition-all duration-300 group relative"
          style={
            i === 0
              ? {
                  background: "rgba(139, 92, 246, 0.15)",
                  boxShadow: "0 0 20px -4px rgba(139, 92, 246, 0.3), inset 0 1px 0 rgba(255,255,255,0.05)",
                }
              : undefined
          }
        >
          <svg
            className={`w-[18px] h-[18px] transition-colors duration-300 ${
              i === 0 ? "text-purple-300" : "text-gray-600 group-hover:text-purple-300"
            }`}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d={icon.path} />
          </svg>
          <span className="absolute left-16 bg-gray-900/95 backdrop-blur-md text-gray-200 text-[11px] px-3 py-1.5 rounded-xl opacity-0 group-hover:opacity-100 transition-all duration-200 whitespace-nowrap pointer-events-none shadow-xl border border-white/5 -translate-x-1 group-hover:translate-x-0">
            {icon.label}
          </span>
        </motion.button>
      ))}

      {/* Bottom mood dot */}
      <div className="mt-auto">
        <motion.div
          animate={{ scale: [1, 1.3, 1], opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
          className={`w-2 h-2 rounded-full bg-gradient-to-br ${moodAccent[mood]}`}
        />
      </div>
    </motion.aside>
  );
}
