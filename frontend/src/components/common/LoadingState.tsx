export function LoadingState({ label = "Loading..." }: { label?: string }) {
  return (
    <div className="flex items-center gap-3 py-10 font-mono text-sm text-ink/60">
      <span className="h-2 w-2 animate-ping rounded-full bg-moss" />
      {label}
    </div>
  );
}
