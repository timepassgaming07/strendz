"use client";

import { motion } from "framer-motion";

interface TopContentProps {
  data: {
    top: {
      id: string;
      text: string;
      author: string;
      platform: string;
      sentiment: string;
      engagement: number;
      likes: number;
      comments: number;
      timestamp: string;
    }[];
    bottom: {
      id: string;
      text: string;
      author: string;
      platform: string;
      sentiment: string;
      engagement: number;
      likes: number;
      comments: number;
      timestamp: string;
    }[];
  } | null;
}

const sentimentColors: Record<string, string> = {
  positive: "text-green-400",
  neutral: "text-purple-400",
  negative: "text-red-400",
};

const sentimentDots: Record<string, string> = {
  positive: "bg-green-400",
  neutral: "bg-purple-400",
  negative: "bg-red-400",
};

function timeAgo(ts: string): string {
  const diff = Date.now() - new Date(ts).getTime();
  const hrs = Math.floor(diff / 3600000);
  if (hrs < 1) return `${Math.floor(diff / 60000)}m ago`;
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

export default function TopContent({ data }: TopContentProps) {
  if (!data) return null;

  const items = data.top.filter((t) => t.engagement > 0);
  if (items.length === 0) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-40px" }}
      transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] as [number, number, number, number] }}
      className="glass p-5 relative overflow-hidden"
    >
      <div
        className="absolute top-0 left-0 w-1/2 h-1/2 rounded-full opacity-10 blur-3xl pointer-events-none"
        style={{ background: "radial-gradient(circle, rgba(251,191,36,0.1) 0%, transparent 70%)" }}
      />
      <h3 className="section-title mb-4 relative z-10">Top Performing Content</h3>

      <div className="space-y-2.5 relative z-10">
        {items.map((item, i) => (
          <motion.div
            key={item.id}
            initial={{ opacity: 0, x: -12 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ delay: i * 0.05 }}
            className="p-3 rounded-xl bg-white/[0.02] border border-white/[0.04] hover:border-white/[0.08] transition-colors"
          >
            <div className="flex items-start justify-between gap-3">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-[10px] text-gray-500 font-medium">#{i + 1}</span>
                  <div className={`w-1.5 h-1.5 rounded-full ${sentimentDots[item.sentiment] || sentimentDots.neutral}`} />
                  <span className={`text-[9px] ${sentimentColors[item.sentiment] || sentimentColors.neutral}`}>
                    {item.sentiment}
                  </span>
                  <span className="text-[9px] text-gray-600">{timeAgo(item.timestamp)}</span>
                </div>
                <p className="text-[11px] text-gray-300 leading-relaxed line-clamp-2">
                  {item.text}
                </p>
                <p className="text-[9px] text-gray-600 mt-1">{item.author}</p>
              </div>
              <div className="flex-shrink-0 text-right">
                <div className="text-sm font-semibold text-white">{item.engagement}</div>
                <div className="text-[8px] text-gray-500 uppercase tracking-wider">engagements</div>
                <div className="flex gap-2 mt-1 justify-end">
                  <span className="text-[9px] text-pink-400/70">❤️ {item.likes}</span>
                  <span className="text-[9px] text-blue-400/70">💬 {item.comments}</span>
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}
