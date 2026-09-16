interface ChipSelectProps {
  options: string[];
  selected: string[];
  onToggle: (value: string) => void;
}

export function ChipSelect({ options, selected, onToggle }: ChipSelectProps) {
  return (
    <div className="flex flex-wrap gap-2">
      {options.map((option) => {
        const isSelected = selected.includes(option);
        return (
          <button
            key={option}
            type="button"
            onClick={() => onToggle(option)}
            className={`chip ${isSelected ? "chip-selected" : "chip-idle"}`}
          >
            {isSelected && <span>&#10003;</span>}
            {option}
          </button>
        );
      })}
    </div>
  );
}
