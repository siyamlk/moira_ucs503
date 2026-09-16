import { forwardRef, type InputHTMLAttributes } from "react";

interface TextFieldProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  required?: boolean;
  helpText?: string;
}

export const TextField = forwardRef<HTMLInputElement, TextFieldProps>(
  ({ label, required, helpText, id, ...rest }, ref) => {
    const inputId = id ?? label.toLowerCase().replace(/\s+/g, "-");
    return (
      <div>
        <div className="mb-1.5 flex items-baseline justify-between">
          <label htmlFor={inputId} className="label-tag text-ink">
            {label}
          </label>
          {required && <span className="label-tag text-clay">Required</span>}
        </div>
        <input id={inputId} ref={ref} required={required} className="field-input" {...rest} />
        {helpText && <p className="mt-1 text-xs text-ink/50">{helpText}</p>}
      </div>
    );
  }
);
TextField.displayName = "TextField";
