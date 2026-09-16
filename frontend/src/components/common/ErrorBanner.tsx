export function ErrorBanner({ message }: { message: string }) {
  return (
    <div className="border-2 border-clay bg-rose/30 px-4 py-3 text-sm font-semibold text-ink">
      {message}
    </div>
  );
}
