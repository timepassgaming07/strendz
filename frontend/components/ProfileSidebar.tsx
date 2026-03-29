"use client";

import { motion } from "framer-motion";
import { useMemo, useState } from "react";
import type { Post } from "@/lib/api";

type Mood = "positive" | "neutral" | "negative";

interface ProfileSidebarProps {
  posts: Post[];
  mood?: Mood;
  summary: {
    total_mentions: number;
    positive_pct: number;
    negative_pct: number;
  } | null;
  realProfile?: {
    name?: string;
    handle?: string;
    followers?: number;
    following?: number;
    description?: string;
    avatar_url?: string;
    karma?: number;
    link_karma?: number;
    comment_karma?: number;
  } | null;
}

const moodAccent: Record<Mood, string> = {
  positive: "from-emerald-400 to-cyan-400",
  neutral: "from-purple-400 to-pink-400",
  negative: "from-rose-400 to-orange-400",
};

const moodDot: Record<Mood, string> = {
  positive: "bg-emerald-400",
  neutral: "bg-purple-400",
  negative: "bg-rose-400",
};

const platformEmoji: Record<string, string> = {
  twitter: "\ud835\udd4f",
  instagram: "\ud83d\udcf8",
  linkedin: "\ud83d\udcbc",
  reddit: "\ud83e\udd16",
};

const sentimentDot: Record<string, string> = {
  positive: "bg-emerald-400/70",
  neutral: "bg-purple-400/50",
  negative: "bg-rose-400/60",
};

function formatNum(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return String(n);
}

function timeAgo(ts: string): string {
  const s = Math.floor((Date.now() - new Date(ts).getTime()) / 1000);
  if (s < 60) return "just now";
  if (s < 3600) return `${Math.floor(s / 60)}m`;
  if (s < 86400) return `${Math.floor(s / 3600)}h`;
  return `${Math.floor(s / 86400)}d`;
}

export default function ProfileSidebar({ posts, mood = "neutral", summary, realProfile }: ProfileSidebarProps) {
  const isReal = !!realProfile?.name;
  const isRedditSub = realProfile?.handle?.startsWith("r/");
  const isRedditUser = realProfile?.handle?.startsWith("u/");
  const isReddit = isRedditSub || isRedditUser;
  const [expandedPost, setExpandedPost] = useState<string | null>(null);

  const stats = useMemo(() => {
    if (isReal && realProfile) {
      const totalEng = posts.reduce((a, p) => a + p.engagement.likes + p.engagement.shares + p.engagement.comments, 0);
      const f = realProfile.followers ?? 0;
      return {
        followers: isRedditUser ? formatNum(realProfile.karma ?? 0) : formatNum(f),
        followersLabel: isRedditUser ? "Karma" : isRedditSub ? "Members" : "Followers",
        following: isRedditUser
          ? formatNum(realProfile.comment_karma ?? 0)
          : realProfile.following ? formatNum(realProfile.following) : "—",
        followingLabel: isRedditUser ? "Comment Karma" : isRedditSub ? "Online" : "Following",
        engRate: isRedditUser
          ? formatNum(realProfile.link_karma ?? 0)
          : f > 0 ? `${((totalEng / Math.max(posts.length, 1) / f) * 100).toFixed(2)}%` : "—",
        engRateLabel: isRedditUser ? "Post Karma" : "Eng. Rate",
        totalPosts: summary?.total_mentions ?? posts.length,
      };
    }
    const authors = new Set(posts.map((p) => p.author));
    const totalEng = posts.reduce((a, p) => a + p.engagement.likes + p.engagement.shares + p.engagement.comments, 0);
    return {
      followers: `${(12.4 + (summary?.total_mentions ?? 0) * 0.01).toFixed(1)}K`,
      followersLabel: "Followers",
      following: `${(1.2 + authors.size * 0.05).toFixed(1)}K`,
      followingLabel: "Following",
      engRate: totalEng > 0 ? `${((totalEng / Math.max(posts.length, 1) / 100) * 2.5).toFixed(1)}%` : "—",
      engRateLabel: "Eng. Rate",
      totalPosts: summary?.total_mentions ?? posts.length,
    };
  }, [posts, summary, isReal, isRedditSub, isRedditUser, realProfile]);

  const activity = useMemo(
    () =>
      posts.slice(0, 12).map((p) => ({
        id: p.id,
        platform: p.platform,
        text: p.text,
        author: p.author,
        time: timeAgo(p.timestamp),
        sentiment: p.sentiment?.label || "neutral",
        likes: p.engagement.likes,
        comments: p.engagement.comments,
        flair: (p as Post & { flair?: string }).flair,
        top_comments: p.top_comments,
        real: p.real,
      })),
    [posts],
  );

  return (
    <motion.aside
      initial={{ x: 40, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] as [number, number, number, number] }}
      className="w-[300px] shrink-0 h-screen sticky top-0 overflow-y-auto flex flex-col gap-3 p-4 pl-0"
    >
      {/* ── Brand Profile Card ──────────────────── */}
      <div className="glass p-5 text-center relative overflow-hidden">
        <div
          className="absolute top-0 left-0 right-0 h-20 opacity-25 pointer-events-none"
          style={{ background: "linear-gradient(180deg, rgba(139,92,246,0.18) 0%, transparent 100%)" }}
        />

        <motion.div
          whileHover={{ scale: 1.06 }}
          transition={{ type: "spring", stiffness: 400, damping: 15 }}
          className="relative z-10 mx-auto w-[72px] h-[72px] rounded-full p-[2px] bg-gradient-to-br from-purple-500 via-pink-500 to-indigo-500"
        >
          {realProfile?.avatar_url ? (
            <img
              src={realProfile.avatar_url}
              alt={realProfile.name || "Profile"}
              className="w-full h-full rounded-full object-cover"
            />
          ) : (
            <div className="w-full h-full rounded-full bg-[#0c0c18] flex items-center justify-center">
              <span className="text-xl font-bold bg-gradient-to-r from-purple-300 to-pink-300 bg-clip-text text-transparent">
                SR
              </span>
            </div>
          )}
        </motion.div>

        <h2 className="mt-2.5 text-sm font-semibold text-white/90 tracking-tight relative z-10">
          {realProfile?.name || "Strendz"}
        </h2>
        <p className="text-[10px] text-gray-500 relative z-10">
          {realProfile?.handle || "@socialradar_ai"}
        </p>
        {realProfile?.description && (
          <p className="text-[9px] text-gray-500 mt-1.5 leading-relaxed line-clamp-2 relative z-10 px-2">
            {realProfile.description}
          </p>
        )}

        {isReal && (
          <div className="flex items-center justify-center gap-1.5 mt-2 relative z-10">
            <div className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
            <span className="text-[9px] text-emerald-400/80 tracking-widest uppercase">Live</span>
          </div>
        )}

        {!isReal && (
          <div className="flex items-center justify-center gap-1.5 mt-2 relative z-10">
            <motion.div
              animate={{ scale: [1, 1.4, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
              className={`w-1.5 h-1.5 rounded-full ${moodDot[mood]}`}
            />
            <span className="text-[9px] text-gray-600 uppercase tracking-widest">{mood}</span>
          </div>
        )}

        <div className="flex items-center justify-center gap-5 mt-4 pt-3 border-t border-white/[0.05] relative z-10">
          <div className="text-center">
            <p className="text-sm font-bold text-white/85">{stats.followers}</p>
            <p className="text-[8px] text-gray-600 uppercase tracking-widest mt-0.5">{stats.followersLabel}</p>
          </div>
          <div className="w-px h-7 bg-white/[0.06]" />
          <div className="text-center">
            <p className="text-sm font-bold text-white/85">{stats.following}</p>
            <p className="text-[8px] text-gray-600 uppercase tracking-widest mt-0.5">{stats.followingLabel}</p>
          </div>
          <div className="w-px h-7 bg-white/[0.06]" />
          <div className="text-center">
            <p className="text-sm font-bold text-white/85">{stats.engRate}</p>
            <p className="text-[8px] text-gray-600 uppercase tracking-widest mt-0.5">{stats.engRateLabel}</p>
          </div>
        </div>
      </div>

      {/* ── Quick Stats Chips ───────────────────── */}
      <div className="grid grid-cols-2 gap-2">
        <div className="glass px-3 py-2.5 text-center">
          <p className="text-base font-bold text-white/85">{stats.totalPosts}</p>
          <p className="text-[8px] text-gray-600 uppercase tracking-widest mt-0.5">Total Posts</p>
        </div>
        <div className="glass px-3 py-2.5 text-center">
          <p className={`text-base font-bold bg-gradient-to-r ${moodAccent[mood]} bg-clip-text text-transparent`}>
            {summary ? `${summary.positive_pct}%` : "—"}
          </p>
          <p className="text-[8px] text-gray-600 uppercase tracking-widest mt-0.5">Positive</p>
        </div>
      </div>

      {/* ── Activity Feed ───────────────────────── */}
      <div className="glass p-4 flex-1 min-h-0 flex flex-col">
        <div className="flex items-center justify-between mb-3">
          <h3 className="section-title">Recent Activity</h3>
          {isReal && (
            <span className="text-[8px] text-emerald-400/60 uppercase tracking-widest">Real Data</span>
          )}
        </div>
        <div className="space-y-1 overflow-y-auto flex-1 pr-1">
          {activity.map((item, i) => (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, x: 10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.04, duration: 0.3 }}
              className="rounded-xl hover:bg-white/[0.025] transition-colors"
            >
              <div
                className="flex items-start gap-2.5 p-2 cursor-pointer"
                onClick={() => setExpandedPost(expandedPost === item.id ? null : item.id)}
              >
                <div className="w-7 h-7 rounded-lg bg-white/[0.04] flex items-center justify-center text-[10px] shrink-0 mt-0.5">
                  {platformEmoji[item.platform] || "\ud83d\udcf1"}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-1.5">
                    <span className="text-[10px] text-gray-300 font-medium truncate">{item.author}</span>
                    <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${sentimentDot[item.sentiment]}`} />
                    {item.flair && (
                      <span className="text-[8px] text-purple-400/60 bg-purple-500/10 px-1.5 py-0.5 rounded truncate">
                        {item.flair}
                      </span>
                    )}
                  </div>
                  <p className="text-[10px] text-gray-500 leading-relaxed line-clamp-2 mt-0.5">{item.text}</p>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-[9px] text-gray-600">{item.time}</span>
                    {item.likes > 0 && (
                      <span className="text-[9px] text-gray-600">▲ {item.likes}</span>
                    )}
                    {item.comments > 0 && (
                      <span className="text-[9px] text-gray-600">💬 {item.comments}</span>
                    )}
                    {item.top_comments && item.top_comments.length > 0 && (
                      <span className="text-[8px] text-purple-400/60">
                        {expandedPost === item.id ? "▾" : "▸"} {item.top_comments.length} replies
                      </span>
                    )}
                  </div>
                </div>
              </div>

              {/* Expanded comments */}
              {expandedPost === item.id && item.top_comments && item.top_comments.length > 0 && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  exit={{ opacity: 0, height: 0 }}
                  className="ml-9 mr-2 mb-2 space-y-1"
                >
                  {item.top_comments.map((c, ci) => (
                    <div
                      key={ci}
                      className="p-2 rounded-lg bg-white/[0.02] border-l-2 border-purple-500/20"
                    >
                      <div className="flex items-center gap-1.5">
                        <span className="text-[9px] text-gray-400 font-medium">{c.author}</span>
                        {c.ups > 0 && <span className="text-[8px] text-gray-600">▲{c.ups}</span>}
                      </div>
                      <p className="text-[9px] text-gray-500 leading-relaxed mt-0.5 line-clamp-3">{c.body}</p>
                    </div>
                  ))}
                </motion.div>
              )}
            </motion.div>
          ))}
        </div>
      </div>
    </motion.aside>
  );
}
