"use client";

import { useState, useRef, useEffect } from "react";
import { searchUniversities, UniversityResult } from "@/lib/api";

interface Props {
  value: string;
  onChange: (val: string) => void;
  onSelect?: (name: string) => void;
  placeholder?: string;
  onKeyDown?: (e: React.KeyboardEvent) => void;
  className?: string;
}

export default function UniversityInput({ value, onChange, onSelect, placeholder = "输入大学名称...", onKeyDown, className = "" }: Props) {
  const [suggestions, setSuggestions] = useState<UniversityResult[]>([]);
  const [open, setOpen] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const wrapperRef = useRef<HTMLDivElement>(null);
  const timerRef = useRef<ReturnType<typeof setTimeout>>();

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  const handleChange = (val: string) => {
    onChange(val);
    setSelectedIndex(-1);
    if (timerRef.current) clearTimeout(timerRef.current);
    if (val.trim().length < 1) { setSuggestions([]); setOpen(false); return; }
    timerRef.current = setTimeout(async () => {
      const results = await searchUniversities(val);
      setSuggestions(results);
      setOpen(results.length > 0);
    }, 200);
  };

  const select = (name: string) => {
    onChange("");
    setOpen(false);
    setSuggestions([]);
    if (onSelect) onSelect(name);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (open) {
      if (e.key === "ArrowDown") { e.preventDefault(); setSelectedIndex(i => Math.min(i + 1, suggestions.length - 1)); }
      else if (e.key === "ArrowUp") { e.preventDefault(); setSelectedIndex(i => Math.max(i - 1, -1)); }
      else if (e.key === "Enter") {
        if (selectedIndex >= 0) { e.preventDefault(); select(suggestions[selectedIndex].name); return; }
      }
      else if (e.key === "Escape") { setOpen(false); }
    }
    if (!open && onKeyDown) onKeyDown(e);
  };

  return (
    <div ref={wrapperRef} className={`relative ${className}`}>
      <input
        value={value}
        onChange={(e) => handleChange(e.target.value)}
        onKeyDown={handleKeyDown}
        onFocus={() => { if (suggestions.length > 0) setOpen(true); }}
        placeholder={placeholder}
        autoComplete="off"
      />
      {open && suggestions.length > 0 && (
        <div className="absolute z-50 mt-1 w-full bg-white border border-slate-200 rounded-lg shadow-lg max-h-60 overflow-y-auto">
          {suggestions.map((s, i) => (
            <div
              key={s.name}
              className={`px-4 py-2.5 cursor-pointer flex items-center justify-between hover:bg-blue-50 transition-colors ${i === selectedIndex ? "bg-blue-50" : ""}`}
              onMouseDown={(e) => { e.preventDefault(); select(s.name); }}
              onMouseEnter={() => setSelectedIndex(i)}
            >
              <div>
                <span className="font-semibold text-slate-700">{s.name}</span>
                <span className="ml-2 text-xs text-slate-400">{s.province}</span>
              </div>
              <div className="flex gap-1">
                {s.tags.map(t => <span key={t} className="px-1.5 py-0.5 bg-blue-100 text-blue-600 text-xs rounded font-medium">{t}</span>)}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
