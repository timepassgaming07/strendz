const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchAPI<T>(
  endpoint: string,
  params?: Record<string, string>,
  options?: { method?: string; body?: string },
): Promise<T> {
  const url = new URL(endpoint, API_BASE);
  if (params) {
    Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v));
  }
  const res = await fetch(url.toString(), {
    method: options?.method ?? "GET",
    headers: options?.body ? { "Content-Type": "application/json" } : undefined,
    body: options?.body,
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export interface PostComment {
  author: string;
  body: string;
  ups: number;
  timestamp: string;
}

export interface Post {
  id: string;
  text: string;
  platform: string;
  timestamp: string;
  engagement: { likes: number; shares: number; comments: number };
  author: string;
  sentiment: { label: string; polarity: number; subjectivity: number };
  real?: boolean;
  permalink?: string;
  url?: string;
  flair?: string;
  top_comments?: PostComment[];
}

export interface SentimentSummary {
  total_mentions: number;
  positive_pct: number;
  negative_pct: number;
  neutral_pct: number;
  positive_count: number;
  negative_count: number;
  neutral_count: number;
}

export interface TrendKeyword {
  keyword: string;
  count: number;
}

export interface Alert {
  type: string;
  icon: string;
  message: string;
}

export interface TimelinePoint {
  time: string;
  positive: number;
  neutral: number;
  negative: number;
}

export interface PlatformData {
  total: number;
  positive: number;
  negative: number;
  neutral: number;
}

export const api = {
  getData: (platform?: string, limit = 50) =>
    fetchAPI<{ posts: Post[]; total: number }>("/data", {
      ...(platform ? { platform } : {}),
      limit: String(limit),
    }),

  getSentimentSummary: (platform?: string) =>
    fetchAPI<SentimentSummary>("/sentiment-summary", platform ? { platform } : {}),

  getTrends: (topN = 10) =>
    fetchAPI<{ keywords: TrendKeyword[] }>("/trends", { top_n: String(topN) }),

  getAlerts: () => fetchAPI<{ alerts: Alert[] }>("/alerts"),

  getPlatformBreakdown: () => fetchAPI<Record<string, PlatformData>>("/platform-breakdown"),

  getEngagement: () =>
    fetchAPI<{
      total_likes: number;
      total_shares: number;
      total_comments: number;
      avg_likes: number;
      avg_shares: number;
      avg_comments: number;
    }>("/engagement"),

  getAiInsight: () => fetchAPI<{ insight: string }>("/ai-insight"),

  simulate: () => fetchAPI<Post>("/simulate", undefined, { method: "POST" }),

  getSentimentTimeline: () =>
    fetchAPI<{ timeline: TimelinePoint[] }>("/sentiment-timeline"),

  // Social connection endpoints
  connect: (platform: string, credentials: Record<string, string>) =>
    fetchAPI<{ ok: boolean; error?: string; message?: string; profile?: Record<string, unknown> }>(
      "/connect",
      undefined,
      { method: "POST", body: JSON.stringify({ platform, credentials }) },
    ),

  disconnect: (platform: string) =>
    fetchAPI<{ ok: boolean }>("/disconnect", { platform }, { method: "POST" }),

  getConnectionStatus: () =>
    fetchAPI<{
      connected: string[];
      profile: {
        name?: string;
        handle?: string;
        followers?: number;
        following?: number;
        description?: string;
        avatar_url?: string;
      };
      total_real_posts: number;
      platforms: Record<string, { handle: string; connected: boolean }>;
    }>("/connection-status"),

  refresh: () =>
    fetchAPI<{ ok: boolean; count?: number }>("/refresh", undefined, { method: "POST" }),

  analyzeProfile: (subreddit: string, username?: string) =>
    fetchAPI<{
      ok: boolean;
      error?: string;
      profile?: {
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
      };
      sentiment?: SentimentSummary;
      keywords?: TrendKeyword[];
      engagement?: {
        total_likes: number;
        total_shares: number;
        total_comments: number;
        avg_likes: number;
        avg_shares: number;
        avg_comments: number;
      };
      insight?: string;
      posts?: Post[];
      total_posts?: number;
    }>("/analyze-profile", undefined, {
      method: "POST",
      body: JSON.stringify(username ? { username } : { subreddit }),
    }),
};
