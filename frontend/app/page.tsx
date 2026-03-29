"use client";

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
import ProfileSidebar from "@/components/ProfileSidebar";
import ConnectPanel from "@/components/ConnectPanel";
import ProfileExplorer from "@/components/ProfileExplorer";
import KeywordChart from "@/components/KeywordChart";
import CalendarWidget from "@/components/CalendarWidget";
import SentimentDonut from "@/components/SentimentDonut";
import PeakHoursChart from "@/components/PeakHoursChart";
import TopContent from "@/components/TopContent";
import CommentSentiment from "@/components/CommentSentiment";
import DownloadReport from "@/components/DownloadReport";
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
  const [postingCalendar, setPostingCalendar] = useState<{ year: number; month: number; days: Record<string, number> } | null>(null);
  const [peakHours, setPeakHours] = useState<{ hour: number; label: string; posts: number; engagement: number; avg_engagement: number }[] | null>(null);
  const [sentimentDist, setSentimentDist] = useState<{ distribution: { positive: number; negative: number; neutral: number }; polarity_histogram: { range: string; count: number }[]; avg_polarity: number; avg_subjectivity: number } | null>(null);
  const [topContent, setTopContent] = useState<{ top: { id: string; text: string; author: string; platform: string; sentiment: string; engagement: number; likes: number; comments: number; timestamp: string }[]; bottom: { id: string; text: string; author: string; platform: string; sentiment: string; engagement: number; likes: number; comments: number; timestamp: string }[] } | null>(null);
  const [commentSent, setCommentSent] = useState<{ posts: { positive: number; negative: number; neutral: number }; comments: { positive: number; negative: number; neutral: number }; post_total: number; comment_total: number } | null>(null);
  const [loading, setLoading] = useState(true);
  const [realProfile, setRealProfile] = useState<{
    name?: string;
    handle?: string;
    followers?: number;
    following?: number;
    description?: string;
    avatar_url?: string;
    karma?: number;
    link_karma?: number;
    comment_karma?: number;
  } | null>(null);

  const mood = useMemo(() => deriveMood(summary), [summary]);

  const fetchConnectionStatus = useCallback(async () => {
    try {
      const s = await api.getConnectionStatus();
      if (s.connected.length > 0 && s.profile?.name) {
        setRealProfile(s.profile);
      } else {
        setRealProfile(null);
      }
    } catch {
      /* backend may be down */
    }
  }, []);

  const fetchAll = useCallback(async () => {
    try {
      const [dataRes, summaryRes, trendsRes, alertsRes, timelineRes, platRes, engRes, insightRes, calRes, peakRes, sentDistRes, topRes, commentRes] =
        await Promise.all([
          api.getData(platform || undefined, 50),
          api.getSentimentSummary(platform || undefined),
          api.getTrends(10),
          api.getAlerts(),
          api.getSentimentTimeline(),
          api.getPlatformBreakdown(),
          api.getEngagement(),
          api.getAiInsight(),
          api.getPostingCalendar(),
          api.getPeakHours(),
          api.getSentimentDistribution(),
          api.getTopContent(5),
          api.getCommentSentiment(),
        ]);
      setPosts(dataRes.posts);
      setSummary(summaryRes);
      setKeywords(trendsRes.keywords);
      setAlerts(alertsRes.alerts);
      setTimeline(timelineRes.timeline);
      setPlatformData(platRes);
      setEngagement(engRes);
      setInsight(insightRes.insight);
      setPostingCalendar(calRes);
      setPeakHours(peakRes.hours);
      setSentimentDist(sentDistRes);
      setTopContent(topRes);
      setCommentSent(commentRes);
    } catch (err) {
      console.error("Fetch failed:", err);
    } finally {
      setLoading(false);
    }
  }, [platform]);

  useEffect(() => {
    setLoading(true);
    // Force refresh from APIs on page load to get latest data
    api.refresh().catch(() => {});
    fetchAll();
    fetchConnectionStatus();
  }, [fetchAll, fetchConnectionStatus]);

  const handleConnected = useCallback(() => {
    fetchConnectionStatus();
    fetchAll();
  }, [fetchConnectionStatus, fetchAll]);

  const handleSetActive = useCallback(async (identifier: string, mode: "subreddit" | "user") => {
    try {
      if (mode === "user") {
        await api.connect("reddit_user", { username: identifier });
      } else {
        await api.connect("reddit", { subreddit: identifier });
      }
      fetchConnectionStatus();
      fetchAll();
    } catch {
      /* ignore */
    }
  }, [fetchConnectionStatus, fetchAll]);

  useEffect(() => {
    // Only simulate new posts when NOT connected to real accounts
    if (realProfile) return;
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
  }, [platform, realProfile]);

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
          <motion.div key="app" initial="hidden" animate="visible" variants={stagger} className="flex min-h-screen">
            {/* ── MAIN CONTENT (LEFT) ─────────────────────────── */}
            <div className="flex-1 min-w-0">
            {/* ── STICKY TOP DASHBOARD ────────────────────────── */}
            <div className="sticky top-0 z-40 glass-sticky">
              <div className="max-w-[1200px] mx-auto px-6 py-4 space-y-3">
                {/* Title + Search */}
                <motion.div variants={fadeUp} className="flex items-center justify-between">
                  <div>
                    <h1 className="text-base font-semibold bg-gradient-to-r from-purple-300 via-pink-300 to-indigo-300 bg-clip-text text-transparent tracking-tight">
                      Strendz
                    </h1>
                    <p className="text-[9px] text-gray-500 mt-0.5 tracking-wide">Real-time sentiment analytics</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <ProfileExplorer onSetActive={handleSetActive} />
                    <ConnectPanel onConnected={handleConnected} />
                    <DownloadReport />
                    <FloatingSearch platform={platform} onPlatformChange={setPlatform} />
                  </div>
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
            <main className="max-w-[1200px] mx-auto px-6 py-6 space-y-5">
              {/* Sentiment Timeline — full width */}
              <motion.div variants={fadeUp}>
                <SentimentChart data={timeline} />
              </motion.div>

              {/* Two-column: Platform + Engagement */}
              <motion.div variants={fadeUp} className="grid grid-cols-1 lg:grid-cols-2 gap-5">
                <PlatformBreakdown data={platformData} />
                <EngagementMetrics data={engagement} />
              </motion.div>

              {/* Two-column: Sentiment Distribution + Keyword Frequency */}
              <motion.div variants={fadeUp} className="grid grid-cols-1 lg:grid-cols-2 gap-5">
                <SentimentDonut data={sentimentDist} />
                <KeywordChart data={keywords} />
              </motion.div>

              {/* Peak Hours — full width */}
              <motion.div variants={fadeUp}>
                <PeakHoursChart data={peakHours} />
              </motion.div>

              {/* Two-column: Comment Sentiment + Calendar */}
              <motion.div variants={fadeUp} className="grid grid-cols-1 lg:grid-cols-2 gap-5">
                <CommentSentiment data={commentSent} />
                <CalendarWidget
                  postingDays={new Set(
                    postingCalendar
                      ? Object.keys(postingCalendar.days).map(Number)
                      : []
                  )}
                />
              </motion.div>

              {/* Top Content — full width */}
              <motion.div variants={fadeUp}>
                <TopContent data={topContent} />
              </motion.div>

              {/* Alerts */}
              <motion.div variants={fadeUp}>
                <AlertsPanel alerts={alerts} mood={mood} />
              </motion.div>

              {/* Footer */}
              <div className="text-center text-[9px] text-gray-700/40 py-6 tracking-[0.2em] uppercase select-none">
                Strendz AI
              </div>
            </main>
            </div>

            {/* ── PROFILE SIDEBAR (RIGHT) ─────────────────────── */}
            <ProfileSidebar posts={posts} mood={mood} summary={summary} realProfile={realProfile} />
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
