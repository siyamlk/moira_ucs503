const PRIORITY_STYLES: Record<string, string> = {
  CRITICAL: "bg-rose text-ink border-clay",
  HIGH: "bg-sticky text-ink border-ink",
  MODERATE: "bg-mossLight text-ink border-moss",
};

export function PriorityBadge({ label }: { label: string }) {
  const style = PRIORITY_STYLES[label] ?? "bg-parchmentDark text-ink border-ink";
  return (
    <span className={`label-tag border-2 px-2.5 py-1 ${style}`}>{label}</span>
  );
}

export function MatchBadge({ percent }: { percent: number }) {
  return (
    <span className="inline-flex items-center gap-1.5 font-mono text-xs font-bold text-moss">
      <span className="h-1.5 w-1.5 rounded-full bg-moss" />
      {percent}% MATCH
    </span>
  );
}
