import { useEffect } from "react";

interface ConfirmDialogProps {
  title: string;
  message: string;
  confirmLabel?: string;
  isDangerous?: boolean;
  isBusy?: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

export function ConfirmDialog({
  title,
  message,
  confirmLabel = "Confirm",
  isDangerous = true,
  isBusy = false,
  onConfirm,
  onCancel,
}: ConfirmDialogProps) {
  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") onCancel();
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onCancel]);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-ink/50 p-4" onClick={onCancel}>
      <div
        className="card-plate w-full max-w-md bg-parchment p-6"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
      >
        <h2 className="font-serif text-xl font-bold text-ink">{title}</h2>
        <p className="mt-2 text-sm text-ink/70">{message}</p>
        <div className="mt-6 flex justify-end gap-3">
          <button type="button" className="btn-outline" onClick={onCancel} disabled={isBusy}>
            Cancel
          </button>
          <button
            type="button"
            className={`btn-primary ${isDangerous ? "!bg-clay !border-clay" : ""}`}
            onClick={onConfirm}
            disabled={isBusy}
          >
            {isBusy ? "Working..." : confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
