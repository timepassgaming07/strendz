"use client";

import { motion } from "framer-motion";
import { useMemo } from "react";
import type { Post } from "@/lib/api";
import CalendarWidget from "./CalendarWidget";

type Mood = "positive" | "neutral" | "negative";

interface ProfilePanelProps {
  posts: Post[];
  mood?: Mood;
}

const moodAccent: Record<Mood, string> = {
  positive: "from-emerald-400 to-cyan-400",
  neutral: "from-purple-400 to-pink-400",
  negative: "from-rose-400 to-orange-400",
};

export default function ProfilePanel({ posts, mood = "neutral" }: ProfilePanelProps) {
  const recentActivity = useMemo(() => {
    return posts.slice(0, 6).map((post) => ({
      id: post.id,
      platform: post.platform,
      text: post.text,
      time: getTimeAgo(post.timestamp),
      type: post.engagement.likes > post.engagement.comments ? "like" : "comment",
      author: post.author,
    }));
  }, [posts]);

  const postingDays = useMemo(() => {
    const days = new Set<number>();
    posts.forEach((p) => {
      const d = new Date(p.timestamp).getDate();
      days.add(d);
    });
    return days;
  }, [posts]);

  const platformEmoji: Record<string, string> = {
    twitter: "𝕏",
    instagram: "📸",
    linkedin: "💼",
  };

  const actionVerb: Record<string, string> = {
    like: "liked a post",
    comment: "commented on a post",
  };

  return (
    <motion.aside
      initial={{ x: -40, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] as [number, number, number, number] }}
      className="w-[300px] shrink-0 h-screen sticky top-0 overflow-y-auto p-4 pr-2 flex flex-col gap-4"
    >
      {/* Profile Card */}
      <div className="glass p-6 text-center relative overflow-hidden">
        {/* Top gradient glow */}
        <div
          className="absolute top-0 left-0 right-0 h-24 opacity-30 pointer-events-none"
          style={{
            background:
              "linear-gradient(180deg, rgba(139,92,246,0.15) 0%, transparent 100%)",
          }}
        />

        {/* Avatar */}
        <motion.div
          whileHover={{ scale: 1.05 }}
          className="relative z-10 mx-auto w-20 h-20 rounded-full p-[2px] bg-gradient-to-br from-purple-500 via-pink-500 to-indigo-500"
        >
          <div className="w-full h-full rounded-full bg-[#12121e] flex items-center justify-center">
            <span className="text-2xl font-bold bg-gradient-to-r from-purple-300 to-pink-300 bg-clip-text text-transparent">
              SR
            </span>
          </div>
        </motion.div>

        <h2 className="mt-3 text-base font-semibold text-white/90 tracking-tight relative z-10">
          Social Radar
        </h2>
        <p className="text-[11px] text-gray-500 mt-0.5 relative z-10">
          @socialradar_ai
        </p>

        {/* Mood indicator */}
        <div className="flex items-center justify-center gap-1.5 mt-3 relative z-10">
          <motion.div
            animate={{ scale: [1, 1.3, 1] }}
            transition={{ duration: 2, repeat: Infinity }}
            className={`w-2 h-2 rounded-full bg-gradient-to-r ${moodAccent[mood]}`}
          />
          <span className="text-[10px] text-gray-500 uppercase tracking-widest">
            {mood} sentiment
          </span>
        </div>
      </div>

      {/* Activity Feed */}
      <div className="glass p-4 flex-1 min-h-0">
        <h3 className="section-title mb-3">Activity</h3>
        <div className="space-y-1 overflow-y-auto max-h-[260px] pr-1">
          {recentActivity.map((item, i) => (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, x: -12 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.05, duration: 0.3 }}
              className="flex items-start gap-2.5 p-2 rounded-xl hover:bg-white/[0.03] transition-colors cursor-default"
            >
              <div className="w-7 h-7 rounded-lg bg-white/[0.05] flex items-center justify-center text-[11px] shrink-0 mt-0.5">
                {platformEmoji[item.platform] || "📱"}
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-[11px] text-gray-400 leading-relaxed truncate">
                  <span className="text-gray-300 font-medium">{item.author}</span>{" "}
                  {actionVerb[item.type]}
                </p>
                <p className="text-[10px] text-gray-600 mt-0.5">{item.time}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Calendar */}
      <CalendarWidget postingDays={postingDays} />
    </motion.aside>
  );
}

function getTimeAgo(timestamp: string): string {
  const seconds = Math.floor(
    (Date.now() - new Date(timestamp).getTime()) / 1000
  );
  if (seconds < 60) return "just now";
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  return `${Math.floor(seconds / 86400)}d ago`;
}
