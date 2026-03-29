"use client";

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
