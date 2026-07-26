import { Moon, Sun } from "lucide-react";
import { useTheme } from "../../context/ThemeContext";

export function ThemeToggle({ className }: { className?: string }) {
  const { theme, toggleTheme } = useTheme();
  const isDark = theme === "dark";

  return (
    <button
      type="button"
      onClick={toggleTheme}
      aria-label={isDark ? "Aydınlık moda geç" : "Karanlık moda geç"}
      title={isDark ? "Aydınlık mod" : "Karanlık mod"}
      className={`inline-flex items-center justify-center rounded-lg p-2 text-muted-foreground hover:bg-white/5 hover:text-foreground transition-colors ${className ?? ""}`}
    >
      {isDark ? <Sun size={17} /> : <Moon size={17} />}
    </button>
  );
}
