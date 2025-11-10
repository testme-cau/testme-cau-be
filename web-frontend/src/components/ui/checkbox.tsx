import * as React from "react";
import { cn } from "@/lib/utils";

export interface CheckboxProps {
  id?: string;
  checked?: boolean;
  onCheckedChange?: (checked: boolean) => void;
  disabled?: boolean;
  className?: string;
}

const Checkbox = React.forwardRef<HTMLInputElement, CheckboxProps>(
  ({ id, checked, onCheckedChange, disabled, className }, ref) => {
    return (
      <input
        ref={ref}
        type="checkbox"
        id={id}
        checked={checked}
        onChange={(e) => onCheckedChange?.(e.target.checked)}
        disabled={disabled}
        className={cn(
          "h-4 w-4 rounded border-gray-300 text-emerald-600 focus:ring-emerald-500 disabled:opacity-50",
          className
        )}
      />
    );
  }
);

Checkbox.displayName = "Checkbox";

export { Checkbox };

