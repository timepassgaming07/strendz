"use client";

import { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { api } from "@/lib/api";

type Platform = "twitter" | "instagram" | "linkedin" | "reddit" | "reddit_user";

interface ConnectionInfo {
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
}

interface ConnectPanelProps {
  onConnected?: () => void;
}

const platformMeta: Record<Platform, { label: string; emoji: string; fields: { key: string; label: string; placeholder: string; type?: string }[] }> = {
  reddit: {
    label: "Reddit",
    emoji: "🤖",
    fields: [
      { key: "subreddit", label: "Subreddit", placeholder: "technology, programming, apple…" },
    ],
  },
  reddit_user: {
    label: "Reddit User",
    emoji: "👤",
    fields: [
      { key: "username", label: "Username", placeholder: "spez, GallowBoob, any username…" },
    ],
  },
  twitter: {
    label: "Twitter / X",
    emoji: "𝕏",
    fields: [
      { key: "bearer_token", label: "Bearer Token", placeholder: "AAAA…your-bearer-token", type: "password" },
      { key: "handle", label: "Handle", placeholder: "@yourbrand" },
    ],
  },
  instagram: {
    label: "Instagram",
    emoji: "📸",
    fields: [],
  },
  linkedin: {
    label: "LinkedIn",
    emoji: "💼",
    fields: [
      { key: "access_token", label: "Access Token", placeholder: "AQV…your-access-token", type: "password" },
    ],
  },
};

export default function ConnectPanel({ onConnected }: ConnectPanelProps) {
  const [open, setOpen] = useState(false);
  const [activePlatform, setActivePlatform] = useState<Platform>("reddit");
  const [fields, setFields] = useState<Record<string, string>>({});
  const [status, setStatus] = useState<ConnectionInfo | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const fetchStatus = useCallback(async () => {
    try {
      const s = await api.getConnectionStatus();
      setStatus(s);
    } catch {
      /* backend may be down */
    }
  }, []);

  useEffect(() => {
    fetchStatus();
  }, [fetchStatus]);

  // Listen for OAuth popup completion
  useEffect(() => {
    const handler = (e: MessageEvent) => {
      if (e.data?.type === "instagram_connected") {
        fetchStatus();
        onConnected?.();
        setSuccess("Instagram connected! Posts, comments & everything loaded 🎉");
        setOpen(true);
      }
    };
    window.addEventListener("message", handler);
    return () => window.removeEventListener("message", handler);
  }, [fetchStatus, onConnected]);

  const handleInstagramLogin = () => {
    setError(null);
    setSuccess(null);
    window.open(
      "http://localhost:8000/auth/instagram/start",
      "instagram_oauth",
      "width=600,height=700,left=200,top=100",
    );
  };

  const handleConnect = async () => {
    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      const result = await api.connect(activePlatform, fields);
      if (result.ok) {
        setSuccess(result.message || `Connected to ${activePlatform}`);
        setFields({});
        await fetchStatus();
        onConnected?.();
      } else {
        setError(result.error || "Connection failed");
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Connection failed");
    } finally {
      setLoading(false);
    }
  };

  const handleDisconnect = async (platform: string) => {
    try {
      await api.disconnect(platform);
      await fetchStatus();
      onConnected?.();
    } catch {
      /* ignore */
    }
  };

  const connectedCount = status?.connected?.length ?? 0;
  const isInstagram = activePlatform === "instagram";
  const isInstagramConnected = status?.connected?.includes("instagram");

  return (
    <>
      {/* Trigger button */}
      <motion.button
        whileHover={{ scale: 1.04 }}
        whileTap={{ scale: 0.97 }}
        onClick={() => setOpen(true)}
        className="glass px-3.5 py-1.5 flex items-center gap-2 cursor-pointer"
      >
        <div className={`w-2 h-2 rounded-full ${connectedCount > 0 ? "bg-emerald-400" : "bg-gray-500"}`} />
        <span className="text-[10px] text-gray-300 tracking-wide">
          {connectedCount > 0 ? `${connectedCount} Connected` : "Connect"}
        </span>
      </motion.button>

      {/* Modal overlay */}
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-[100] flex items-center justify-center p-4"
            onClick={() => setOpen(false)}
          >
            {/* Backdrop */}
            <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" />

            {/* Panel */}
            <motion.div
              initial={{ scale: 0.92, opacity: 0, y: 20 }}
              animate={{ scale: 1, opacity: 1, y: 0 }}
              exit={{ scale: 0.92, opacity: 0, y: 20 }}
              transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] as [number, number, number, number] }}
              onClick={(e) => e.stopPropagation()}
              className="relative glass w-full max-w-md p-6 space-y-5"
            >
              {/* Header */}
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-sm font-semibold text-white/90 tracking-tight">
                    Connect Accounts
                  </h2>
                  <p className="text-[10px] text-gray-500 mt-0.5">
                    Link your social media for real-time analytics
                  </p>
                </div>
                <button
                  onClick={() => setOpen(false)}
                  className="w-7 h-7 rounded-lg bg-white/[0.05] flex items-center justify-center text-gray-500 hover:text-gray-300 transition-colors"
                >
                  ✕
                </button>
              </div>

              {/* Connected accounts */}
              {connectedCount > 0 && (
                <div className="space-y-2">
                  <p className="text-[9px] text-gray-600 uppercase tracking-widest">Active Connections</p>
                  {status!.connected.map((p) => (
                    <div
                      key={p}
                      className="flex items-center justify-between p-2.5 rounded-xl bg-white/[0.03] border border-white/[0.05]"
                    >
                      <div className="flex items-center gap-2.5">
                        <span className="text-sm">{platformMeta[p as Platform]?.emoji ?? "📱"}</span>
                        <div>
                          <p className="text-[11px] text-white/80 font-medium">
                            {platformMeta[p as Platform]?.label ?? p}
                          </p>
                          <p className="text-[9px] text-gray-500">
                            {status!.platforms[p]?.handle || "Connected"}
                          </p>
                        </div>
                      </div>
                      <button
                        onClick={() => handleDisconnect(p)}
                        className="text-[9px] text-rose-400/70 hover:text-rose-400 transition-colors px-2 py-1"
                      >
                        Disconnect
                      </button>
                    </div>
                  ))}
                </div>
              )}

              {/* Platform tabs */}
              <div className="flex gap-2">
                {(Object.keys(platformMeta) as Platform[]).map((p) => {
                  const isConnected = status?.connected?.includes(p);
                  return (
                    <button
                      key={p}
                      onClick={() => {
                        setActivePlatform(p);
                        setFields({});
                        setError(null);
                        setSuccess(null);
                      }}
                      className={`flex-1 py-2 rounded-xl text-[10px] tracking-wide transition-all ${
                        activePlatform === p
                          ? "bg-white/[0.08] text-white/90 border border-white/[0.1]"
                          : "text-gray-500 hover:text-gray-400"
                      } ${isConnected ? "opacity-50" : ""}`}
                    >
                      {platformMeta[p].emoji} {platformMeta[p].label}
                    </button>
                  );
                })}
              </div>

              {/* Instagram: one-click connect + token fallback */}
              {isInstagram && !isInstagramConnected && (
                <div className="space-y-3">
                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={handleInstagramLogin}
                    className="w-full py-3.5 rounded-xl bg-gradient-to-r from-fuchsia-600/30 via-purple-500/25 to-orange-500/20 border border-purple-500/30 text-[13px] text-white/90 font-semibold tracking-wide hover:border-purple-400/40 transition-all flex items-center justify-center gap-2.5"
                  >
                    <span className="text-lg">📸</span> Connect Instagram
                  </motion.button>

                  <div className="flex items-center gap-3">
                    <div className="flex-1 h-px bg-white/[0.06]" />
                    <span className="text-[9px] text-gray-600">or paste token</span>
                    <div className="flex-1 h-px bg-white/[0.06]" />
                  </div>

                  <div>
                    <input
                      type="password"
                      value={fields["access_token"] ?? ""}
                      onChange={(e) => setFields((prev) => ({ ...prev, access_token: e.target.value }))}
                      placeholder="IGAA… your Instagram token"
                      className="w-full px-3 py-2 rounded-xl bg-white/[0.04] border border-white/[0.06] text-[11px] text-white/80 placeholder:text-gray-600 focus:outline-none focus:border-purple-500/30 transition-colors"
                    />
                  </div>

                  {fields["access_token"] && (
                    <motion.button
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={handleConnect}
                      disabled={loading}
                      className="w-full py-2.5 rounded-xl bg-gradient-to-r from-purple-500/20 to-pink-500/20 border border-purple-500/20 text-[11px] text-white/80 font-medium tracking-wide hover:border-purple-500/30 transition-all disabled:opacity-50"
                    >
                      {loading ? "Connecting…" : "Connect with Token"}
                    </motion.button>
                  )}

                  {error && (
                    <p className="text-[10px] text-rose-400/80 bg-rose-500/[0.06] px-3 py-2 rounded-xl">
                      {error}
                    </p>
                  )}
                  {success && (
                    <p className="text-[10px] text-emerald-400/80 bg-emerald-500/[0.06] px-3 py-2 rounded-xl">
                      {success}
                    </p>
                  )}
                </div>
              )}

              {/* Other platforms: normal fields */}
              {!isInstagram && !status?.connected?.includes(activePlatform) && (
                <div className="space-y-3">
                  {platformMeta[activePlatform].fields.map((f) => (
                    <div key={f.key}>
                      <label className="text-[9px] text-gray-500 uppercase tracking-widest mb-1 block">
                        {f.label}
                      </label>
                      <input
                        type={f.type ?? "text"}
                        value={fields[f.key] ?? ""}
                        onChange={(e) => setFields((prev) => ({ ...prev, [f.key]: e.target.value }))}
                        placeholder={f.placeholder}
                        className="w-full px-3 py-2 rounded-xl bg-white/[0.04] border border-white/[0.06] text-[11px] text-white/80 placeholder:text-gray-600 focus:outline-none focus:border-purple-500/30 transition-colors"
                      />
                    </div>
                  ))}

                  {error && (
                    <p className="text-[10px] text-rose-400/80 bg-rose-500/[0.06] px-3 py-2 rounded-xl">
                      {error}
                    </p>
                  )}
                  {success && (
                    <p className="text-[10px] text-emerald-400/80 bg-emerald-500/[0.06] px-3 py-2 rounded-xl">
                      {success}
                    </p>
                  )}

                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={handleConnect}
                    disabled={loading}
                    className="w-full py-2.5 rounded-xl bg-gradient-to-r from-purple-500/20 to-pink-500/20 border border-purple-500/20 text-[11px] text-white/80 font-medium tracking-wide hover:border-purple-500/30 transition-all disabled:opacity-50"
                  >
                    {loading ? "Connecting…" : `Connect ${platformMeta[activePlatform].label}`}
                  </motion.button>

                  <div className="bg-white/[0.02] border border-white/[0.04] rounded-xl p-3">
                    <p className="text-[9px] text-gray-600 leading-relaxed">
                      <span className="text-gray-500 font-medium">Tip:</span>{" "}
                      {activePlatform === "reddit"
                        ? "Just enter a subreddit name — no API key needed! Try: technology, programming, apple, etc."
                        : activePlatform === "reddit_user"
                        ? "Enter any Reddit username to track their posts & comments — no API key needed!"
                        : activePlatform === "twitter"
                        ? "Get a Bearer Token from developer.x.com → Projects & Apps → Keys and Tokens."
                        : "Create an app at linkedin.com/developers and generate an access token."}
                    </p>
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
