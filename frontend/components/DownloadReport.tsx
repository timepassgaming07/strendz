"use client";

import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const formats = [
  { id: "csv", label: "CSV Spreadsheet", ext: ".csv", icon: "📊", desc: "Open in Excel, Google Sheets" },
  { id: "json", label: "JSON Data", ext: ".json", icon: "🔧", desc: "For developers & APIs" },
  { id: "md", label: "Markdown Report", ext: ".md", icon: "📝", desc: "Formatted documentation" },
  { id: "txt", label: "Plain Text", ext: ".txt", icon: "📄", desc: "Simple text summary" },
];

export default function DownloadReport() {
  const [open, setOpen] = useState(false);
  const [downloading, setDownloading] = useState<string | null>(null);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    if (open) document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, [open]);

  const handleDownload = async (format: string) => {
    setDownloading(format);
    try {
      const res = await fetch(`${API_BASE}/report/download?format=${format}`);
      if (!res.ok) throw new Error("Download failed");
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      const disposition = res.headers.get("content-disposition") || "";
      const match = disposition.match(/filename="(.+?)"/);
      a.href = url;
      a.download = match ? match[1] : `strendz-report.${format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      setOpen(false);
    } catch {
      /* ignore */
    } finally {
      setDownloading(null);
    }
  };

  return (
    <div ref={ref} className="relative">
      <motion.button
        whileHover={{ scale: 1.04 }}
        whileTap={{ scale: 0.96 }}
        onClick={() => setOpen(!open)}
        className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-gradient-to-r from-purple-500/20 to-pink-500/20 border border-purple-500/20 hover:border-purple-400/40 text-[11px] text-gray-300 font-medium transition-all"
      >
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
          <polyline points="7 10 12 15 17 10" />
          <line x1="12" y1="15" x2="12" y2="3" />
        </svg>
        Report
      </motion.button>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: -8, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -8, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            className="absolute right-0 top-full mt-2 w-[260px] rounded-2xl border border-white/[0.08] bg-[rgba(10,10,18,0.96)] backdrop-blur-xl shadow-2xl shadow-black/40 z-50 overflow-hidden"
          >
            <div className="p-3 border-b border-white/[0.06]">
              <p className="text-[11px] text-gray-300 font-semibold">Download Report</p>
              <p className="text-[9px] text-gray-500 mt-0.5">Export your analytics data</p>
            </div>

            <div className="p-1.5">
              {formats.map((f) => (
                <motion.button
                  key={f.id}
                  whileHover={{ x: 2 }}
                  onClick={() => handleDownload(f.id)}
                  disabled={downloading !== null}
                  className="w-full flex items-center gap-3 p-2.5 rounded-xl hover:bg-white/[0.04] transition-colors text-left disabled:opacity-50"
                >
                  <span className="text-base w-7 text-center flex-shrink-0">{f.icon}</span>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-[11px] text-gray-300 font-medium">{f.label}</span>
                      {downloading === f.id && (
                        <motion.div
                          animate={{ rotate: 360 }}
                          transition={{ repeat: Infinity, duration: 0.8, ease: "linear" }}
                          className="w-3 h-3 rounded-full border border-purple-400/30 border-t-purple-400"
                        />
                      )}
                    </div>
                    <p className="text-[9px] text-gray-500">{f.desc}</p>
                  </div>
                  <span className="text-[9px] text-gray-600 font-mono">{f.ext}</span>
                </motion.button>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
