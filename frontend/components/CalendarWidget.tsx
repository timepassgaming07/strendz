"use client";

import { motion } from "framer-motion";
import { useMemo } from "react";

interface CalendarWidgetProps {
  postingDays: Set<number>;
}

export default function CalendarWidget({ postingDays }: CalendarWidgetProps) {
  const now = new Date();
  const year = now.getFullYear();
  const month = now.getMonth();

  const { monthName, daysInMonth, startDay, weeks } = useMemo(() => {
    const name = now.toLocaleString("default", { month: "long", year: "numeric" });
    const total = new Date(year, month + 1, 0).getDate();
    const start = new Date(year, month, 1).getDay();

    // Build week rows
    const rows: (number | null)[][] = [];
    let current = 1;
    for (let w = 0; w < 6; w++) {
      const week: (number | null)[] = [];
      for (let d = 0; d < 7; d++) {
        if ((w === 0 && d < start) || current > total) {
          week.push(null);
        } else {
          week.push(current);
          current++;
        }
      }
      rows.push(week);
      if (current > total) break;
    }

    return { monthName: name, daysInMonth: total, startDay: start, weeks: rows };
  }, [year, month]);

  const today = now.getDate();
  const dayLabels = ["S", "M", "T", "W", "T", "F", "S"];

  return (
    <div className="glass p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="section-title">{monthName}</h3>
      </div>

      {/* Day headers */}
      <div className="grid grid-cols-7 gap-1 mb-1">
        {dayLabels.map((d, i) => (
          <span
            key={i}
            className="text-center text-[9px] text-gray-600 font-medium"
          >
            {d}
          </span>
        ))}
      </div>

      {/* Calendar grid */}
      <div className="space-y-1">
        {weeks.map((week, wi) => (
          <div key={wi} className="grid grid-cols-7 gap-1">
            {week.map((day, di) => {
              if (day === null) {
                return <div key={di} className="w-full aspect-square" />;
              }

              const isToday = day === today;
              const isActive = postingDays.has(day);

              return (
                <motion.div
                  key={di}
                  whileHover={{ scale: 1.15 }}
                  className={`w-full aspect-square rounded-lg flex items-center justify-center text-[10px] font-medium cursor-default transition-colors relative ${
                    isToday
                      ? "bg-gradient-to-br from-purple-500/60 to-pink-500/60 text-white"
                      : isActive
                        ? "bg-white/[0.06] text-gray-300"
                        : "text-gray-600 hover:bg-white/[0.03]"
                  }`}
                >
                  {day}
                  {isActive && !isToday && (
                    <div className="absolute bottom-0.5 w-1 h-1 rounded-full bg-purple-400/60" />
                  )}
                </motion.div>
              );
            })}
          </div>
        ))}
      </div>

      {/* Legend */}
      <div className="flex items-center gap-3 mt-3 justify-center">
        <div className="flex items-center gap-1">
          <div className="w-1.5 h-1.5 rounded-full bg-purple-400/60" />
          <span className="text-[9px] text-gray-600">Active</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-1.5 h-1.5 rounded-full bg-gradient-to-r from-purple-500 to-pink-500" />
          <span className="text-[9px] text-gray-600">Today</span>
        </div>
      </div>
    </div>
  );
}
