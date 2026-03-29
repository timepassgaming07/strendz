"use client";

import { motion, AnimatePresence } from "framer-motion";
import type { Alert } from "@/lib/api";

type Mood = "positive" | "neutral" | "negative";

interface AlertsPanelProps {
  alerts: Alert[];
  mood?: Mood;
}

const alertStyles: Record<string, { border: string; bg: string; text: string }> = {
  danger: { border: "border-rose-500/12", bg: "bg-rose-500/[0.04]", text: "text-rose-300" },
  warning: { border: "border-amber-500/12", bg: "bg-amber-500/[0.04]", text: "text-amber-300" },
  info: { border: "border-blue-400/12", bg: "bg-blue-400/[0.04]", text: "text-blue-300" },
  success: { border: "border-emerald-400/12", bg: "bg-emerald-400/[0.04]", text: "text-emerald-300" },
};

export default function AlertsPanel({ alerts }: AlertsPanelProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-40px" }}
      transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] as [number, number, number, number] }}
      className="glass p-5"
    >
      <div className="flex items-center gap-2 mb-4">
        <h3 className="section-title">Alerts</h3>
        {alerts.length > 0 && (
          <span className="w-5 h-5 rounded-full bg-purple-500/15 text-purple-300 text-[9px] flex items-center justify-center font-semibold">
            {alerts.length}
          </span>
        )}
      </div>
      <div className="space-y-2">
        <AnimatePresence>
          {alerts.length === 0 && (
            <motion.p
              animate={{ opacity: [0.3, 0.5, 0.3] }}
              transition={{ duration: 3, repeat: Infinity }}
              className="text-[11px] text-gray-600 text-center py-6"
            >
              All clear
            </motion.p>
          )}
          {alerts.map((alert, i) => {
            const s = alertStyles[alert.type] || alertStyles.info;
            return (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.35, delay: i * 0.06 }}
                className={`flex items-center gap-3 p-3 rounded-xl border ${s.border} ${s.bg}`}
              >
                <span className="text-sm shrink-0">{alert.icon}</span>
                <p className={`text-[11px] ${s.text} leading-relaxed`}>{alert.message}</p>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>
    </motion.div>
  );
}
