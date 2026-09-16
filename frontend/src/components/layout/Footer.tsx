export function Footer() {
  return (
    <footer className="border-t-2 border-ink bg-parchmentDark">
      <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-2 px-6 py-6 text-center sm:flex-row sm:text-left">
        <div className="flex items-center gap-2">
          <span className="flex h-6 w-6 items-center justify-center border border-ink bg-ink font-serif text-xs font-bold text-parchment">
            M
          </span>
          <span className="font-hand text-lg text-ink/80">Find your way forward.</span>
        </div>
        <p className="label-tag text-ink/50">&copy; 2026 MOIRA &middot; Academic Advisory Platform</p>
      </div>
    </footer>
  );
}
