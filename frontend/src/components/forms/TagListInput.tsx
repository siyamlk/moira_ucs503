import { useState, type KeyboardEvent } from "react";

interface TagListInputProps {
  label: string;
  values: string[];
  onChange: (values: string[]) => void;
  placeholder?: string;
  helpText?: string;
}

export function TagListInput({ label, values, onChange, placeholder, helpText }: TagListInputProps) {
  const [draft, setDraft] = useState("");
  // Defensive: a caller's data source (e.g. a profile fetched before this
  // field existed) can hand us undefined/null instead of []. Never crash
  // on that — treat it as empty.
  const safeValues = values ?? [];

  function commitDraft() {
    const value = draft.trim();
    if (value && !safeValues.includes(value)) {
      onChange([...safeValues, value]);
    }
    setDraft("");
  }

  function handleKeyDown(e: KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter" || e.key === ",") {
      e.preventDefault();
      commitDraft();
    } else if (e.key === "Backspace" && draft === "" && safeValues.length > 0) {
      onChange(safeValues.slice(0, -1));
    }
  }

  function removeAt(index: number) {
    onChange(safeValues.filter((_, i) => i !== index));
  }

  return (
    <div>
      <label className="label-tag mb-1.5 block text-ink">{label}</label>
      <div className="field-input flex flex-wrap items-center gap-1.5 py-2">
        {safeValues.map((v, i) => (
          <span
            key={`${v}-${i}`}
            className="chip chip-selected inline-flex items-center gap-1 !py-1 !px-2 text-xs"
          >
            {v}
            <button
              type="button"
              onClick={() => removeAt(i)}
              className="ml-0.5 leading-none opacity-70 hover:opacity-100"
              aria-label={`Remove ${v}`}
            >
              &times;
            </button>
          </span>
        ))}
        <input
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={handleKeyDown}
          onBlur={commitDraft}
          placeholder={safeValues.length === 0 ? placeholder : ""}
          className="min-w-[120px] flex-1 border-none bg-transparent p-1 text-sm outline-none"
        />
      </div>
      {helpText && <p className="mt-1 text-xs text-ink/50">{helpText}</p>}
    </div>
  );
}
