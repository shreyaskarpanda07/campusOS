"use client";

import React, { useState } from "react";

export interface TagItem {
  name: string;
  proficiency?: string | null;
}

export interface TagInputProps {
  label: string;
  placeholder?: string;
  tags: TagItem[];
  onChange: (tags: TagItem[]) => void;
  showProficiency?: boolean;
}

export const TagInput: React.FC<TagInputProps> = ({
  label,
  placeholder = "Type and press Enter...",
  tags,
  onChange,
  showProficiency = false,
}) => {
  const [inputVal, setInputVal] = useState("");
  const [proficiencyVal, setProficiencyVal] = useState<string>("intermediate");

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" || e.key === ",") {
      e.preventDefault();
      addTag();
    }
  };

  const addTag = () => {
    const trimmed = inputVal.trim();
    if (!trimmed) return;

    // Check if tag already exists (case-insensitive)
    if (tags.some((t) => t.name.toLowerCase() === trimmed.toLowerCase())) {
      setInputVal("");
      return;
    }

    const newTag: TagItem = {
      name: trimmed,
      ...(showProficiency ? { proficiency: proficiencyVal } : {}),
    };

    onChange([...tags, newTag]);
    setInputVal("");
  };

  const removeTag = (indexToRemove: number) => {
    onChange(tags.filter((_, idx) => idx !== indexToRemove));
  };

  return (
    <div className="w-full space-y-2">
      <label className="block text-sm font-medium text-gray-700">
        {label}
      </label>

      {/* ── Input + Optional Proficiency Dropdown ── */}
      <div className="flex gap-2">
        <input
          type="text"
          value={inputVal}
          onChange={(e) => setInputVal(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          className="flex-1 rounded-lg border border-gray-300 px-3.5 py-2 text-sm text-gray-900 shadow-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
        />

        {showProficiency && (
          <select
            value={proficiencyVal}
            onChange={(e) => setProficiencyVal(e.target.value)}
            className="rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-700 shadow-sm bg-white focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
          >
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
          </select>
        )}

        <button
          type="button"
          onClick={addTag}
          className="rounded-lg bg-gray-100 hover:bg-gray-200 px-4 py-2 text-sm font-medium text-gray-700 transition-colors"
        >
          Add
        </button>
      </div>

      {/* ── Render Tag Pills ── */}
      {tags.length > 0 && (
        <div className="flex flex-wrap gap-2 pt-1">
          {tags.map((tag, idx) => (
            <span
              key={`${tag.name}-${idx}`}
              className="inline-flex items-center gap-1.5 rounded-full bg-primary-50 border border-primary-200 px-3 py-1 text-xs font-medium text-primary-800"
            >
              <span>{tag.name}</span>
              {tag.proficiency && (
                <span className="text-primary-500 text-[10px] font-normal uppercase tracking-wider">
                  ({tag.proficiency})
                </span>
              )}
              <button
                type="button"
                onClick={() => removeTag(idx)}
                className="text-primary-400 hover:text-primary-700 focus:outline-none"
                aria-label={`Remove ${tag.name}`}
              >
                &times;
              </button>
            </span>
          ))}
        </div>
      )}
    </div>
  );
};
