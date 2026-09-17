export interface AdminTableColumn<T> {
  header: string;
  render: (row: T) => React.ReactNode;
  className?: string;
}

interface AdminTableProps<T> {
  columns: AdminTableColumn<T>[];
  rows: T[];
  getRowKey: (row: T) => string | number;
  onEdit?: (row: T) => void;
  onDelete?: (row: T) => void;
}

export function AdminTable<T>({ columns, rows, getRowKey, onEdit, onDelete }: AdminTableProps<T>) {
  const showActions = Boolean(onEdit || onDelete);

  return (
    <div className="card-plate overflow-x-auto">
      <table className="w-full min-w-[640px] border-collapse text-left text-sm">
        <thead>
          <tr className="border-b-2 border-ink">
            {columns.map((col) => (
              <th key={col.header} className="label-tag whitespace-nowrap px-4 py-3 text-ink/60">
                {col.header}
              </th>
            ))}
            {showActions && <th className="label-tag px-4 py-3 text-right text-ink/60">Actions</th>}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={getRowKey(row)} className="border-b border-ink/15 last:border-b-0 hover:bg-parchmentDark/60">
              {columns.map((col) => (
                <td key={col.header} className={`px-4 py-3 align-top text-ink/80 ${col.className ?? ""}`}>
                  {col.render(row)}
                </td>
              ))}
              {showActions && (
                <td className="px-4 py-3 text-right align-top">
                  <div className="flex justify-end gap-2">
                    {onEdit && (
                      <button
                        type="button"
                        className="label-tag border-2 border-ink/30 px-2 py-1 text-ink/70 hover:border-ink hover:text-ink"
                        onClick={() => onEdit(row)}
                      >
                        Edit
                      </button>
                    )}
                    {onDelete && (
                      <button
                        type="button"
                        className="label-tag border-2 border-clay/50 px-2 py-1 text-clay hover:border-clay hover:bg-clay hover:text-parchment"
                        onClick={() => onDelete(row)}
                      >
                        Delete
                      </button>
                    )}
                  </div>
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
