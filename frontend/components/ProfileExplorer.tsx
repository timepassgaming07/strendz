"use client";

import { useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { api, type Post, type SentimentSummary, type TrendKeyword } from "@/lib/api";

type SearchMode = "subreddit" | "user";

interface ProfileData {
  name: string;
  handle: string;
  followers: number;
  active_users: number;
  description: string;
  avatar_url: string;
  created_utc: number;
  over18: boolean;
  is_user?: boolean;
  karma?: number;
  link_karma?: number;
  comment_karma?: number;
}

interface AnalysisResult {
  profile: ProfileData;
  sentiment: SentimentSummary;
  keywords: TrendKeyword[];
  engagement: {
    total_likes: number;
    total_shares: number;
    total_comments: number;
    avg_likes: number;
    avg_shares: number;
    avg_comments: number;
  };
  insight: string;
  posts: Post[];
  totalPosts: number;
  mode: SearchMode;
}

interface HistoryItem {
  name: string;
  mode: SearchMode;
}

interface ProfileExplorerProps {
  onSetActive?: (identifier: string, mode: SearchMode) => void;
}

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

const sentimentColor: Record<string, string> = {
  positive: "text-emerald-400",
  neutral: "text-gray-400",
  negative: "text-rose-400",
};

const sentimentBg: Record<string, string> = {
  positive: "bg-emerald-500",
  neutral: "bg-purple-500",
  negative: "bg-rose-500",
};

export default function ProfileExplorer({ onSetActive }: ProfileExplorerProps) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [activeTab, setActiveTab] = useState<"overview" | "posts" | "keywords">("overview");
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [mode, setMode] = useState<SearchMode>("subreddit");

  const analyze = useCallback(async (sub?: string, overrideMode?: SearchMode) => {
    const currentMode = overrideMode ?? mode;
    const raw = (sub ?? query).trim();
    const target = currentMode === "subreddit"
      ? raw.replace(/^r\//, "")
      : raw.replace(/^u\//, "").replace(/^\/u\//, "");
    if (!target) return;
    setLoading(true);
    setError(null);
    setResult(null);
    setActiveTab("overview");
    try {
      const res = currentMode === "user"
        ? await api.analyzeProfile("", target)
        : await api.analyzeProfile(target);
      if (!res.ok) {
        setError(res.error || "Analysis failed");
        return;
      }
      setResult({
        profile: res.profile!,
        sentiment: res.sentiment!,
        keywords: res.keywords!,
        engagement: res.engagement!,
        insight: res.insight!,
        posts: res.posts!,
        totalPosts: res.total_posts!,
        mode: currentMode,
      });
      setHistory((prev) => {
        const clean = prev.filter((h) => !(h.name === target && h.mode === currentMode));
        return [{ name: target, mode: currentMode }, ...clean].slice(0, 8);
      });
      setQuery(target);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Analysis failed");
    } finally {
      setLoading(false);
    }
  }, [query, mode]);

  const handleSetActive = useCallback(() => {
    if (!result) return;
    const currentMode = result.mode;
    const id = currentMode === "user"
      ? result.profile.handle.replace("u/", "")
      : result.profile.handle.replace("r/", "");
    onSetActive?.(id, currentMode);
    setOpen(false);
  }, [result, onSetActive]);

  return (
    <>
      {/* Trigger button */}
      <motion.button
        whileHover={{ scale: 1.04 }}
        whileTap={{ scale: 0.97 }}
        onClick={() => setOpen(true)}
        className="glass px-3.5 py-1.5 flex items-center gap-2 cursor-pointer"
      >
        <span className="text-[11px]">🔍</span>
        <span className="text-[10px] text-gray-300 tracking-wide">Explore</span>
      </motion.button>

      {/* Modal */}
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-[100] flex items-start justify-center pt-12 p-4 overflow-y-auto"
            onClick={() => setOpen(false)}
          >
            <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" />

            <motion.div
              initial={{ scale: 0.92, opacity: 0, y: 30 }}
              animate={{ scale: 1, opacity: 1, y: 0 }}
              exit={{ scale: 0.92, opacity: 0, y: 30 }}
              transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] as [number, number, number, number] }}
              onClick={(e) => e.stopPropagation()}
              className="relative glass w-full max-w-2xl p-6 space-y-5 mb-12"
            >
              {/* Header */}
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-sm font-semibold text-white/90 tracking-tight">
                    Explore Profile
                  </h2>
                  <p className="text-[10px] text-gray-500 mt-0.5">
                    Search any {mode === "subreddit" ? "subreddit" : "Reddit user"} for detailed analysis
                  </p>
                </div>
                <button
                  onClick={() => setOpen(false)}
                  className="w-7 h-7 rounded-lg bg-white/[0.05] flex items-center justify-center text-gray-500 hover:text-gray-300 transition-colors"
                >
                  ✕
                </button>
              </div>

              {/* Mode toggle */}
              <div className="flex gap-1 p-1 rounded-xl bg-white/[0.02]">
                <button
                  onClick={() => setMode("subreddit")}
                  className={`flex-1 py-1.5 rounded-lg text-[10px] tracking-wide transition-all ${
                    mode === "subreddit"
                      ? "bg-white/[0.07] text-white/90"
                      : "text-gray-500 hover:text-gray-400"
                  }`}
                >
                  🏠 Subreddit
                </button>
                <button
                  onClick={() => setMode("user")}
                  className={`flex-1 py-1.5 rounded-lg text-[10px] tracking-wide transition-all ${
                    mode === "user"
                      ? "bg-white/[0.07] text-white/90"
                      : "text-gray-500 hover:text-gray-400"
                  }`}
                >
                  👤 User
                </button>
              </div>

              {/* Search bar */}
              <div className="flex gap-2">
                <div className="flex-1 relative">
                  <span className="absolute left-3 top-1/2 -translate-y-1/2 text-[11px] text-gray-600">{mode === "subreddit" ? "r/" : "u/"}</span>
                  <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && analyze()}
                    placeholder={mode === "subreddit" ? "technology, programming, apple…" : "spez, GallowBoob, any username…"}
                    className="w-full pl-8 pr-3 py-2.5 rounded-xl bg-white/[0.04] border border-white/[0.06] text-[12px] text-white/80 placeholder:text-gray-600 focus:outline-none focus:border-purple-500/30 transition-colors"
                    autoFocus
                  />
                </div>
                <motion.button
                  whileHover={{ scale: 1.03 }}
                  whileTap={{ scale: 0.97 }}
                  onClick={() => analyze()}
                  disabled={loading || !query.trim()}
                  className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-purple-500/20 to-pink-500/20 border border-purple-500/20 text-[11px] text-white/80 font-medium tracking-wide hover:border-purple-500/30 transition-all disabled:opacity-40"
                >
                  {loading ? "Analyzing…" : "Analyze"}
                </motion.button>
              </div>

              {/* Recent searches */}
              {history.length > 0 && !result && (
                <div className="flex flex-wrap gap-1.5">
                  <span className="text-[9px] text-gray-600 uppercase tracking-widest self-center mr-1">Recent:</span>
                  {history.map((h) => (
                    <button
                      key={`${h.mode}-${h.name}`}
                      onClick={() => { setMode(h.mode); setQuery(h.name); analyze(h.name, h.mode); }}
                      className="px-2.5 py-1 rounded-lg bg-white/[0.04] border border-white/[0.05] text-[10px] text-gray-400 hover:text-white/70 hover:border-white/[0.1] transition-colors"
                    >
                      {h.mode === "user" ? "u/" : "r/"}{h.name}
                    </button>
                  ))}
                </div>
              )}

              {/* Error */}
              {error && (
                <p className="text-[10px] text-rose-400/80 bg-rose-500/[0.06] px-3 py-2 rounded-xl">{error}</p>
              )}

              {/* Loading state */}
              {loading && (
                <div className="flex items-center justify-center py-12">
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ repeat: Infinity, duration: 1.2, ease: "linear" }}
                    className="w-7 h-7 rounded-full border-2 border-purple-500/20 border-t-purple-400"
                  />
                </div>
              )}

              {/* Results */}
              {result && !loading && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="space-y-4"
                >
                  {/* Profile card */}
                  <div className="flex items-start gap-4 p-4 rounded-2xl bg-white/[0.03] border border-white/[0.05]">
                    {result.profile.avatar_url ? (
                      <img
                        src={result.profile.avatar_url}
                        alt={result.profile.name}
                        className="w-14 h-14 rounded-xl object-cover shrink-0"
                      />
                    ) : (
                      <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-purple-500/30 to-pink-500/30 flex items-center justify-center text-lg shrink-0">
                        🤖
                      </div>
                    )}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <h3 className="text-[13px] font-semibold text-white/90 truncate">
                          {result.profile.name}
                        </h3>
                        {result.profile.over18 && (
                          <span className="px-1.5 py-0.5 rounded text-[8px] bg-rose-500/20 text-rose-400">NSFW</span>
                        )}
                      </div>
                      <p className="text-[10px] text-gray-500">{result.profile.handle}</p>
                      {result.profile.description && (
                        <p className="text-[10px] text-gray-400 mt-1.5 leading-relaxed line-clamp-2">
                          {result.profile.description}
                        </p>
                      )}
                      <div className="flex items-center gap-4 mt-2.5">
                        {result.profile.is_user ? (
                          <>
                            <div>
                              <span className="text-[12px] font-semibold text-white/85">{formatNum(result.profile.karma || 0)}</span>
                              <span className="text-[9px] text-gray-600 ml-1">karma</span>
                            </div>
                            <div>
                              <span className="text-[12px] font-semibold text-white/85">{formatNum(result.profile.link_karma || 0)}</span>
                              <span className="text-[9px] text-gray-600 ml-1">post karma</span>
                            </div>
                            <div>
                              <span className="text-[12px] font-semibold text-white/85">{formatNum(result.profile.comment_karma || 0)}</span>
                              <span className="text-[9px] text-gray-600 ml-1">comment karma</span>
                            </div>
                          </>
                        ) : (
                          <>
                            <div>
                              <span className="text-[12px] font-semibold text-white/85">{formatNum(result.profile.followers)}</span>
                              <span className="text-[9px] text-gray-600 ml-1">members</span>
                            </div>
                            <div>
                              <span className="text-[12px] font-semibold text-white/85">{formatNum(result.profile.active_users)}</span>
                              <span className="text-[9px] text-gray-600 ml-1">online</span>
                            </div>
                          </>
                        )}
                        <div>
                          <span className="text-[12px] font-semibold text-white/85">{result.totalPosts}</span>
                          <span className="text-[9px] text-gray-600 ml-1">posts analyzed</span>
                        </div>
                      </div>
                    </div>
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={handleSetActive}
                      className="shrink-0 px-3 py-2 rounded-xl bg-emerald-500/15 border border-emerald-500/20 text-[10px] text-emerald-400 font-medium hover:border-emerald-500/40 transition-all"
                    >
                      Set Active ↗
                    </motion.button>
                  </div>

                  {/* AI Insight */}
                  <div className="p-3 rounded-xl bg-gradient-to-r from-purple-500/[0.06] to-pink-500/[0.06] border border-purple-500/10">
                    <p className="text-[10px] text-gray-300 leading-relaxed">
                      <span className="text-purple-400 font-medium">AI Insight: </span>
                      {result.insight}
                    </p>
                  </div>

                  {/* Tabs */}
                  <div className="flex gap-1 p-1 rounded-xl bg-white/[0.02]">
                    {(["overview", "posts", "keywords"] as const).map((tab) => (
                      <button
                        key={tab}
                        onClick={() => setActiveTab(tab)}
                        className={`flex-1 py-1.5 rounded-lg text-[10px] tracking-wide transition-all ${
                          activeTab === tab
                            ? "bg-white/[0.07] text-white/90"
                            : "text-gray-500 hover:text-gray-400"
                        }`}
                      >
                        {tab === "overview" ? "📊 Overview" : tab === "posts" ? "📝 Posts" : "🔑 Keywords"}
                      </button>
                    ))}
                  </div>

                  {/* Tab content */}
                  <AnimatePresence mode="wait">
                    {activeTab === "overview" && (
                      <motion.div
                        key="overview"
                        initial={{ opacity: 0, y: 6 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -6 }}
                        className="space-y-3"
                      >
                        {/* Sentiment breakdown */}
                        <div className="grid grid-cols-3 gap-2">
                          <div className="p-3 rounded-xl bg-white/[0.03] border border-white/[0.04] text-center">
                            <p className="text-lg font-bold text-emerald-400">{result.sentiment.positive_pct}%</p>
                            <p className="text-[8px] text-gray-600 uppercase tracking-widest mt-0.5">Positive</p>
                            <p className="text-[9px] text-gray-500 mt-0.5">{result.sentiment.positive_count} posts</p>
                          </div>
                          <div className="p-3 rounded-xl bg-white/[0.03] border border-white/[0.04] text-center">
                            <p className="text-lg font-bold text-purple-400">{result.sentiment.neutral_pct}%</p>
                            <p className="text-[8px] text-gray-600 uppercase tracking-widest mt-0.5">Neutral</p>
                            <p className="text-[9px] text-gray-500 mt-0.5">{result.sentiment.neutral_count} posts</p>
                          </div>
                          <div className="p-3 rounded-xl bg-white/[0.03] border border-white/[0.04] text-center">
                            <p className="text-lg font-bold text-rose-400">{result.sentiment.negative_pct}%</p>
                            <p className="text-[8px] text-gray-600 uppercase tracking-widest mt-0.5">Negative</p>
                            <p className="text-[9px] text-gray-500 mt-0.5">{result.sentiment.negative_count} posts</p>
                          </div>
                        </div>

                        {/* Sentiment bar */}
                        <div className="h-2.5 rounded-full overflow-hidden flex bg-white/[0.04]">
                          <div
                            className="bg-emerald-500/60 transition-all"
                            style={{ width: `${result.sentiment.positive_pct}%` }}
                          />
                          <div
                            className="bg-purple-500/40 transition-all"
                            style={{ width: `${result.sentiment.neutral_pct}%` }}
                          />
                          <div
                            className="bg-rose-500/60 transition-all"
                            style={{ width: `${result.sentiment.negative_pct}%` }}
                          />
                        </div>

                        {/* Engagement stats */}
                        <div className="grid grid-cols-3 gap-2">
                          <div className="p-3 rounded-xl bg-white/[0.03] border border-white/[0.04] text-center">
                            <p className="text-sm font-bold text-white/85">{formatNum(result.engagement.total_likes)}</p>
                            <p className="text-[8px] text-gray-600 uppercase tracking-widest mt-0.5">Upvotes</p>
                          </div>
                          <div className="p-3 rounded-xl bg-white/[0.03] border border-white/[0.04] text-center">
                            <p className="text-sm font-bold text-white/85">{formatNum(result.engagement.total_comments)}</p>
                            <p className="text-[8px] text-gray-600 uppercase tracking-widest mt-0.5">Comments</p>
                          </div>
                          <div className="p-3 rounded-xl bg-white/[0.03] border border-white/[0.04] text-center">
                            <p className="text-sm font-bold text-white/85">{result.engagement.avg_likes.toFixed(0)}</p>
                            <p className="text-[8px] text-gray-600 uppercase tracking-widest mt-0.5">Avg Upvotes</p>
                          </div>
                        </div>

                        {/* Top keywords preview */}
                        <div>
                          <p className="text-[9px] text-gray-600 uppercase tracking-widest mb-2">Top Keywords</p>
                          <div className="flex flex-wrap gap-1.5">
                            {result.keywords.slice(0, 8).map((kw) => (
                              <span
                                key={kw.keyword}
                                className="px-2.5 py-1 rounded-lg bg-white/[0.04] border border-white/[0.05] text-[10px] text-gray-300"
                              >
                                {kw.keyword} <span className="text-gray-600">{kw.count}</span>
                              </span>
                            ))}
                          </div>
                        </div>
                      </motion.div>
                    )}

                    {activeTab === "posts" && (
                      <motion.div
                        key="posts"
                        initial={{ opacity: 0, y: 6 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -6 }}
                        className="space-y-1.5 max-h-[340px] overflow-y-auto pr-1"
                      >
                        {result.posts.map((post, i) => (
                          <motion.div
                            key={post.id}
                            initial={{ opacity: 0, x: 8 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: i * 0.02 }}
                            className="flex items-start gap-3 p-3 rounded-xl bg-white/[0.02] hover:bg-white/[0.04] border border-white/[0.03] transition-colors"
                          >
                            <div className={`w-1.5 h-1.5 rounded-full mt-1.5 shrink-0 ${sentimentBg[post.sentiment?.label || "neutral"]}`} />
                            <div className="flex-1 min-w-0">
                              <p className="text-[11px] text-gray-300 leading-relaxed line-clamp-2">{post.text}</p>
                              <div className="flex items-center gap-3 mt-1.5">
                                <span className="text-[9px] text-gray-600">{post.author}</span>
                                <span className="text-[9px] text-gray-600">{timeAgo(post.timestamp)}</span>
                                <span className={`text-[9px] ${sentimentColor[post.sentiment?.label || "neutral"]}`}>
                                  {post.sentiment?.label}
                                </span>
                              </div>
                            </div>
                            <div className="text-right shrink-0">
                              <p className="text-[10px] text-gray-400">▲ {formatNum(post.engagement.likes)}</p>
                              <p className="text-[9px] text-gray-600">{post.engagement.comments} 💬</p>
                            </div>
                          </motion.div>
                        ))}
                      </motion.div>
                    )}

                    {activeTab === "keywords" && (
                      <motion.div
                        key="keywords"
                        initial={{ opacity: 0, y: 6 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -6 }}
                        className="space-y-1.5"
                      >
                        {result.keywords.map((kw, i) => {
                          const maxCount = result.keywords[0]?.count || 1;
                          const pct = (kw.count / maxCount) * 100;
                          return (
                            <div key={kw.keyword} className="flex items-center gap-3">
                              <span className="text-[9px] text-gray-600 w-4 text-right">{i + 1}</span>
                              <div className="flex-1">
                                <div className="flex items-center justify-between mb-0.5">
                                  <span className="text-[11px] text-gray-300 font-medium">{kw.keyword}</span>
                                  <span className="text-[10px] text-gray-500">{kw.count}</span>
                                </div>
                                <div className="h-1.5 rounded-full bg-white/[0.04] overflow-hidden">
                                  <motion.div
                                    initial={{ width: 0 }}
                                    animate={{ width: `${pct}%` }}
                                    transition={{ duration: 0.5, delay: i * 0.04 }}
                                    className="h-full rounded-full bg-gradient-to-r from-purple-500/50 to-pink-500/50"
                                  />
                                </div>
                              </div>
                            </div>
                          );
                        })}
                      </motion.div>
                    )}
                  </AnimatePresence>
                </motion.div>
              )}

              {/* Suggestion when empty */}
              {!result && !loading && !error && (
                <div className="text-center py-6 space-y-3">
                  <p className="text-2xl">🔍</p>
                  <p className="text-[11px] text-gray-500">
                    {mode === "subreddit" ? "Try exploring popular communities" : "Try exploring popular Reddit users"}
                  </p>
                  <div className="flex flex-wrap justify-center gap-1.5">
                    {mode === "subreddit"
                      ? ["technology", "programming", "apple", "science", "worldnews", "gaming", "movies"].map((s) => (
                          <button
                            key={s}
                            onClick={() => { setQuery(s); analyze(s); }}
                            className="px-3 py-1.5 rounded-lg bg-white/[0.04] border border-white/[0.05] text-[10px] text-gray-400 hover:text-white/70 hover:border-purple-500/20 transition-all"
                          >
                            r/{s}
                          </button>
                        ))
                      : ["spez", "GallowBoob", "Poem_for_your_sprog", "shittymorph", "AutoModerator"].map((u) => (
                          <button
                            key={u}
                            onClick={() => { setQuery(u); analyze(u); }}
                            className="px-3 py-1.5 rounded-lg bg-white/[0.04] border border-white/[0.05] text-[10px] text-gray-400 hover:text-white/70 hover:border-purple-500/20 transition-all"
                          >
                            u/{u}
                          </button>
                        ))
                    }
                  </div>
                </div>
              )}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
