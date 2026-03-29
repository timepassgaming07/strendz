"use client";

import { motion, useScroll, useTransform } from "framer-motion";
import { useMemo, useRef, useEffect, useState } from "react";

type Mood = "positive" | "neutral" | "negative";

interface AnimatedBackgroundProps {
  mood?: Mood;
}

const moodColors: Record<Mood, { blobs: string[]; base: string }> = {
  positive: {
    blobs: [
      "radial-gradient(circle, rgba(74,222,128,0.14) 0%, transparent 70%)",
      "radial-gradient(circle, rgba(56,189,248,0.10) 0%, transparent 70%)",
      "radial-gradient(circle, rgba(129,140,248,0.08) 0%, transparent 70%)",
      "radial-gradient(circle, rgba(52,211,153,0.06) 0%, transparent 70%)",
    ],
    base: "rgba(16, 28, 20, 0.35)",
  },
  neutral: {
    blobs: [
      "radial-gradient(circle, rgba(139,92,246,0.14) 0%, transparent 70%)",
      "radial-gradient(circle, rgba(236,72,153,0.10) 0%, transparent 70%)",
      "radial-gradient(circle, rgba(99,102,241,0.10) 0%, transparent 70%)",
      "radial-gradient(circle, rgba(168,85,247,0.06) 0%, transparent 70%)",
    ],
    base: "rgba(15, 14, 23, 0.35)",
  },
  negative: {
    blobs: [
      "radial-gradient(circle, rgba(248,113,113,0.12) 0%, transparent 70%)",
      "radial-gradient(circle, rgba(251,146,60,0.08) 0%, transparent 70%)",
      "radial-gradient(circle, rgba(168,85,247,0.06) 0%, transparent 70%)",
      "radial-gradient(circle, rgba(244,63,94,0.05) 0%, transparent 70%)",
    ],
    base: "rgba(28, 14, 14, 0.35)",
  },
};

const blobConfigs = [
  { top: "0%", left: "5%", size: "50vw" },
  { top: "30%", left: "55%", size: "45vw" },
  { top: "65%", left: "25%", size: "40vw" },
  { top: "50%", left: "70%", size: "30vw" },
];

export default function AnimatedBackground({ mood = "neutral" }: AnimatedBackgroundProps) {
  const colors = moodColors[mood];
  const containerRef = useRef<HTMLDivElement>(null);
  const [scrollY, setScrollY] = useState(0);

  useEffect(() => {
    const handleScroll = () => setScrollY(window.scrollY);
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const parallaxOffset = scrollY * 0.15;

  return (
    <div ref={containerRef} className="fixed inset-0 -z-10 overflow-hidden">
      {/* Background video */}
      <video
        autoPlay
        loop
        muted
        playsInline
        className="absolute inset-0 w-full h-full object-cover opacity-[0.07]"
        style={{ filter: "blur(2px) saturate(1.2)" }}
        src="https://cdn.pixabay.com/video/2020/07/30/45442-445028332_large.mp4"
      />

      {/* Color overlay that reacts to mood */}
      <div className="absolute inset-0" style={{ background: "rgba(8, 8, 15, 0.88)" }} />

      {/* Animated base gradient */}
      <motion.div
        className="absolute inset-0"
        animate={{
          background: [
            `linear-gradient(135deg, transparent 0%, ${colors.base} 30%, transparent 60%, rgba(26,16,50,0.4) 100%)`,
            `linear-gradient(200deg, transparent 0%, rgba(26,16,50,0.4) 30%, ${colors.base} 60%, transparent 100%)`,
            `linear-gradient(300deg, rgba(26,16,50,0.4) 0%, ${colors.base} 30%, transparent 60%, transparent 100%)`,
            `linear-gradient(135deg, transparent 0%, ${colors.base} 30%, transparent 60%, rgba(26,16,50,0.4) 100%)`,
          ],
        }}
        transition={{ duration: 25, repeat: Infinity, ease: "linear" }}
      />

      {/* Scroll-reactive blobs */}
      {colors.blobs.map((gradient, i) => {
        const cfg = blobConfigs[i];
        return (
          <motion.div
            key={`${mood}-${i}`}
            className="absolute rounded-full"
            style={{
              width: cfg.size,
              height: cfg.size,
              background: gradient,
              top: cfg.top,
              left: cfg.left,
              filter: "blur(80px)",
              transform: `translateY(${parallaxOffset * (i % 2 === 0 ? -1 : 1) * (0.5 + i * 0.2)}px)`,
            }}
            animate={{
              x: [0, 40 + i * 10, -30 - i * 5, 20, 0],
              y: [0, -35 + i * 8, 25, -15, 0],
              scale: [1, 1.05, 0.97, 1.03, 1],
            }}
            transition={{
              duration: 20 + i * 6,
              repeat: Infinity,
              ease: "easeInOut",
            }}
          />
        );
      })}

      {/* Noise texture */}
      <div
        className="absolute inset-0 opacity-[0.015]"
        style={{
          backgroundImage:
            "url(\"data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E\")",
        }}
      />
    </div>
  );
}
