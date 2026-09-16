interface EmptyStateProps {
  title: string;
  description?: string;
  action?: React.ReactNode;
}

export function EmptyState({ title, description, action }: EmptyStateProps) {
  return (
    <div className="card-plate flex flex-col items-center gap-3 px-6 py-12 text-center">
      <p className="font-serif text-xl font-bold text-ink">{title}</p>
      {description && <p className="max-w-sm text-sm text-ink/60">{description}</p>}
      {action}
    </div>
  );
}
