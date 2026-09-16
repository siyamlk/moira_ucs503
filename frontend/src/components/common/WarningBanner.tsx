export function WarningBanner({ message }: { message: string }) {
  return (
    <div className="border-2 border-clay bg-sticky/60 px-4 py-3 text-sm font-semibold text-ink">
      &#9888; {message}
    </div>
  );
}
