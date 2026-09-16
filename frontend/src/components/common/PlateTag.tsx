interface PlateTagProps {
  children: React.ReactNode;
  tone?: "dark" | "light";
}

export function PlateTag({ children, tone = "dark" }: PlateTagProps) {
  return (
    <span
      className={`label-tag inline-block border-2 border-ink px-2 py-1 ${
        tone === "dark" ? "bg-ink text-parchment" : "bg-parchmentDark text-ink"
      }`}
    >
      {children}
    </span>
  );
}
