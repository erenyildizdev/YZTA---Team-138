import { useEffect, useState, type ComponentPropsWithoutRef } from "react";
import { Eye, EyeOff } from "lucide-react";

import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { cn } from "../ui/utils";

type PasswordInputProps = Omit<
  ComponentPropsWithoutRef<"input">,
  "type"
>;

export function PasswordInput({
  className,
  disabled,
  id,
  ...props
}: PasswordInputProps) {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    if (disabled) {
      setIsVisible(false);
    }
  }, [disabled]);

  const toggleLabel = isVisible
    ? "Parolayı gizle"
    : "Parolayı göster";
  const VisibilityIcon = isVisible ? EyeOff : Eye;

  return (
    <div className="relative min-w-0">
      <Input
        {...props}
        id={id}
        type={isVisible ? "text" : "password"}
        disabled={disabled}
        className={cn(
          "h-auto rounded-xl border-border bg-muted px-3.5 py-2.5 text-sm text-foreground placeholder:text-muted-foreground focus-visible:border-primary/50 focus-visible:ring-1 focus-visible:ring-primary/20 dark:bg-muted",
          className,
          "pr-11",
        )}
      />

      <Button
        type="button"
        variant="ghost"
        size="icon"
        disabled={disabled}
        aria-label={toggleLabel}
        aria-pressed={isVisible}
        aria-controls={id}
        onClick={() => setIsVisible((visible) => !visible)}
        className="absolute right-1.5 top-1/2 h-8 w-8 -translate-y-1/2 rounded-lg text-muted-foreground hover:bg-background/70 hover:text-foreground focus-visible:ring-2 focus-visible:ring-ring"
      >
        <VisibilityIcon aria-hidden="true" size={16} />
      </Button>
    </div>
  );
}
