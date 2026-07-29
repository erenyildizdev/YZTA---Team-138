import type { ReactNode } from "react";
import { Sparkles } from "lucide-react";

import { ThemeToggle } from "../common/ThemeToggle";

interface AuthPageShellProps {
  subtitle: string;
  children: ReactNode;
  footer?: ReactNode;
}

export function AuthPageShell({
  subtitle,
  children,
  footer,
}: AuthPageShellProps) {
  return (
    <main className="relative flex min-h-dvh w-full animate-[page-in_0.3s_ease-out] items-center justify-center bg-background px-4 py-10">
      <ThemeToggle className="absolute right-4 top-4" />

      <div className="w-full max-w-sm">
        <div className="mb-7 flex flex-col items-center">
          <span className="mb-3 flex h-11 w-11 items-center justify-center rounded-xl bg-primary">
            <Sparkles
              aria-hidden="true"
              size={20}
              className="text-primary-foreground"
            />
          </span>
          <h1 className="text-lg font-bold text-foreground">FikirLab</h1>
          <p className="mt-1 text-center text-sm text-muted-foreground">
            {subtitle}
          </p>
        </div>

        {children}
        {footer}
      </div>
    </main>
  );
}
