"use client";

import { motion } from "framer-motion";

interface CommentSentimentProps {
  data: {
    posts: { positive: number; negative: number; neutral: number };
    comments: { positive: number; negative: number; neutral: number };
    post_total: number;
    comment_total: number;
  } | null;
}

const COLORS = {
  positive: { bg: "bg-green-400", bar: "#4ade80", text: "text-green-400" },
  neutral: { bg: "bg-purple-400", bar: "#a78bfa", text: "text-purple-400" },
  negative: { bg: "bg-red-400", bar: "#f87171", text: "text-red-400" },
};

function SentimentBar({ label, data, total }: { label: string; data: Record<string, number>; total: number }) {
  const pcts = {
    positive: total > 0 ? (data.positive / total) * 100 : 0,
    neutral: total > 0 ? (data.neutral / total) * 100 : 0,
    negative: total > 0 ? (data.negative / total) * 100 : 0,
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-1.5">
        <span className="text-[11px] text-gray-300 font-medium">{label}</span>
        <span className="text-[10px] text-gray-500">{total} total</span>
      </div>
      <div className="h-5 rounded-full overflow-hidden flex bg-white/[0.03]">
        {(["positive", "neutral", "negative"] as const).map((key) =>
          pcts[key] > 0 ? (
            <motion.div
              key={key}
              initial={{ width: 0 }}
              whileInView={{ width: `${pcts[key]}%` }}
              viewport={{ once: true }}
              transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] as [number, number, number, number] }}
              className="h-full flex items-center justify-center"
              style={{ background: COLORS[key].bar, opacity: 0.8 }}
            >
              {pcts[key] > 12 && (
                <span className="text-[8px] text-black/60 font-bold">
                  {pcts[key].toFixed(0)}%
                </span>
              )}
            </motion.div>
          ) : null,
        )}
      </div>
      <div className="flex gap-3 mt-1.5">
        {(["positive", "neutral", "negative"] as const).map((key) => (
          <div key={key} className="flex items-center gap-1">
            <div className={`w-1.5 h-1.5 rounded-full ${COLORS[key].bg}`} />
            <span className={`text-[9px] ${COLORS[key].text}`}>
              {data[key]} {key}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function CommentSentiment({ data }: CommentSentimentProps) {
  if (!data) return null;

  // Determine if comments are more negative than posts
  const postNegPct = data.post_total > 0 ? (data.posts.negative / data.post_total) * 100 : 0;
  const commentNegPct = data.comment_total > 0 ? (data.comments.negative / data.comment_total) * 100 : 0;
  const commentPosPct = data.comment_total > 0 ? (data.comments.positive / data.comment_total) * 100 : 0;

  let insight = "";
  if (data.comment_total === 0) {
    insight = "No comments to analyze yet.";
  } else if (commentNegPct > postNegPct + 10) {
    insight = "⚠️ Comments are significantly more negative than posts. Consider moderating.";
  } else if (commentPosPct > 60) {
    insight = "✅ Comments are overwhelmingly positive — strong community engagement!";
  } else {
    insight = "💬 Comment sentiment is balanced with the overall post mood.";
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-40px" }}
      transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] as [number, number, number, number] }}
      className="glass p-5 relative overflow-hidden"
    >
      <div
        className="absolute bottom-0 right-0 w-1/2 h-1/2 rounded-full opacity-10 blur-3xl pointer-events-none"
        style={{ background: "radial-gradient(circle, rgba(167,139,250,0.12) 0%, transparent 70%)" }}
      />
      <h3 className="section-title mb-4 relative z-10">Posts vs Comments Sentiment</h3>

      <div className="space-y-4 relative z-10">
        <SentimentBar label="Posts" data={data.posts} total={data.post_total} />
        <SentimentBar label="Comments" data={data.comments} total={data.comment_total} />
      </div>

      {insight && (
        <p className="text-[10px] text-gray-400 mt-4 p-2.5 rounded-lg bg-white/[0.02] border border-white/[0.04] relative z-10">
          {insight}
        </p>
      )}
    </motion.div>
  );
}
