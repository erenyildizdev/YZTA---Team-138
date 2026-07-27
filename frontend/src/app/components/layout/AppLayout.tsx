import {
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";
import {
  BarChart3,
  Bot,
  FileText,
  History,
  LayoutDashboard,
  LogOut,
  Menu,
  Moon,
  Plus,
  Settings,
  Sparkles,
  X,
} from "lucide-react";
import {
  NavLink,
  Outlet,
  useNavigate,
} from "react-router";

import { useAuth } from "../../context/AuthContext";
import { useTheme } from "../../context/ThemeContext";
import { useIsMobile } from "../ui/use-mobile";

const navigation = [
  {
    to: "/",
    label: "Ana Sayfa",
    Icon: LayoutDashboard,
    end: true,
  },
  {
    to: "/mentor",
    label: "Mentor ile Görüş",
    Icon: Bot,
  },
  {
    to: "/analysis",
    label: "Fikir Analizi",
    Icon: BarChart3,
  },
  {
    to: "/report",
    label: "Doğrulama Raporu",
    Icon: FileText,
  },
  {
    to: "/history",
    label: "Geçmiş Fikirler",
    Icon: History,
  },
  {
    to: "/ideas/new",
    label: "Yeni Fikir Ekle",
    Icon: Plus,
  },
];

interface SidebarProps {
  onClose: () => void;
}

function Sidebar({ onClose }: SidebarProps) {
  const { user, logout } = useAuth();
  const { isDark, toggleTheme } = useTheme();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    onClose();
    navigate("/login", { replace: true });
  };

  const displayName = user
    ? `${user.first_name} ${user.last_name}`.trim() || user.email
    : "Kullanıcı";

  return (
    <aside className="flex h-full min-h-0 w-64 flex-col border-r border-sidebar-border bg-sidebar text-sidebar-foreground">
      <div className="flex shrink-0 items-center justify-between border-b border-sidebar-border px-5 py-5">
        <NavLink
          to="/"
          onClick={onClose}
          className="flex items-center gap-2.5"
        >
          <span className="flex h-8 w-8 items-center justify-center rounded-xl bg-primary text-primary-foreground">
            <Sparkles size={15} />
          </span>

          <span className="font-bold">FikirLab</span>
        </NavLink>

        <button
          type="button"
          onClick={onClose}
          aria-label="Menüyü kapat"
          className="rounded-lg p-2 text-muted-foreground transition-colors hover:bg-sidebar-accent hover:text-sidebar-foreground md:hidden"
        >
          <X size={18} />
        </button>
      </div>

      <nav
        aria-label="Ana navigasyon"
        className="min-h-0 flex-1 space-y-1 overflow-y-auto p-3"
      >
        {navigation.map(({ to, label, Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            onClick={onClose}
            className={({ isActive }) =>
              [
                "flex items-center gap-3 rounded-xl px-3 py-2.5",
                "text-sm transition-colors",
                isActive
                  ? "bg-sidebar-accent text-sidebar-accent-foreground"
                  : "text-sidebar-foreground/65 hover:bg-sidebar-accent hover:text-sidebar-foreground",
              ].join(" ")
            }
          >
            <Icon size={17} />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="shrink-0 border-t border-sidebar-border p-3">
        <button
          type="button"
          role="switch"
          aria-checked={isDark}
          aria-labelledby="sidebar-theme-label"
          onClick={toggleTheme}
          className="group flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm text-sidebar-foreground/65 transition-colors hover:bg-sidebar-accent hover:text-sidebar-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sidebar-ring focus-visible:ring-offset-2 focus-visible:ring-offset-sidebar"
        >
          <Moon size={17} />

          <span id="sidebar-theme-label">
            Koyu Tema
          </span>

          <span
            aria-hidden="true"
            className={[
              "relative ml-auto h-5 w-9 rounded-full",
              "border border-sidebar-foreground/55",
              "transition-colors",
              isDark
                ? "bg-primary"
                : "bg-switch-background",
            ].join(" ")}
          >
            <span
              className={[
                "absolute left-0.5 top-0.5 h-4 w-4 rounded-full",
                "shadow-sm transition-transform",
                isDark
                  ? "translate-x-4 bg-primary-foreground"
                  : "translate-x-0 bg-sidebar-foreground",
              ].join(" ")}
            />
          </span>
        </button>

        <button
          type="button"
          disabled
          title="Backend entegrasyonu sonrasında kullanılabilir"
          className="flex w-full cursor-not-allowed items-center gap-3 rounded-xl px-3 py-2.5 text-sm text-sidebar-foreground/30"
        >
          <Settings size={17} />
          Hesap Ayarları
        </button>

        <button
          type="button"
          onClick={handleLogout}
          className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm text-sidebar-foreground/65 transition-colors hover:bg-sidebar-accent hover:text-sidebar-foreground"
        >
          <LogOut size={17} />
          Çıkış Yap
        </button>

        <div className="mt-2 rounded-xl bg-sidebar-surface px-3 py-2.5 text-xs">
          <strong className="block text-sidebar-foreground">
            {displayName}
          </strong>

          <div className="mt-1 break-all text-sidebar-foreground/65">
            {user?.email ?? "Aktif Kullanıcı"}
          </div>
        </div>
      </div>
    </aside>
  );
}

export function AppLayout() {
  const [open, setOpen] = useState(false);
  const isMobile = useIsMobile();

  const menuButtonRef = useRef<HTMLButtonElement>(null);
  const sidebarPanelRef = useRef<HTMLDivElement>(null);

  const closeSidebar = useCallback(() => {
    setOpen(false);

    window.requestAnimationFrame(() => {
      menuButtonRef.current?.focus();
    });
  }, []);

  const mobileDialogOpen = isMobile && open;
  const sidebarIsHidden = isMobile && !open;

  useEffect(() => {
    if (!mobileDialogOpen) {
      return;
    }

    const focusFrame = window.requestAnimationFrame(() => {
      sidebarPanelRef.current
        ?.querySelector<HTMLElement>(
          '[aria-label="Menüyü kapat"]',
        )
        ?.focus();
    });

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        closeSidebar();
        return;
      }

      if (
        event.key !== "Tab" ||
        !sidebarPanelRef.current
      ) {
        return;
      }

      const focusableElements = Array.from(
        sidebarPanelRef.current.querySelectorAll<HTMLElement>(
          [
            "a[href]",
            "button:not([disabled])",
            '[tabindex]:not([tabindex="-1"])',
          ].join(","),
        ),
      );

      if (focusableElements.length === 0) {
        return;
      }

      const firstElement = focusableElements[0];
      const lastElement =
        focusableElements[focusableElements.length - 1];
      const activeElement = document.activeElement;

      if (
        event.shiftKey &&
        (
          activeElement === firstElement ||
          !sidebarPanelRef.current.contains(activeElement)
        )
      ) {
        event.preventDefault();
        lastElement.focus();
        return;
      }

      if (
        !event.shiftKey &&
        activeElement === lastElement
      ) {
        event.preventDefault();
        firstElement.focus();
      }
    };

    document.addEventListener(
      "keydown",
      handleKeyDown,
    );

    return () => {
      window.cancelAnimationFrame(focusFrame);
      document.removeEventListener(
        "keydown",
        handleKeyDown,
      );
    };
  }, [closeSidebar, mobileDialogOpen]);

  return (
    <div className="flex min-h-dvh w-full overflow-x-hidden bg-background md:h-dvh md:overflow-hidden">
      {mobileDialogOpen && (
        <button
          type="button"
          aria-label="Navigasyon menüsünü kapat"
          onClick={closeSidebar}
          className="fixed inset-0 z-40 bg-overlay md:hidden"
        />
      )}

      <div
        id="mobile-sidebar"
        ref={sidebarPanelRef}
        inert={sidebarIsHidden || undefined}
        aria-hidden={sidebarIsHidden || undefined}
        aria-modal={mobileDialogOpen || undefined}
        role={mobileDialogOpen ? "dialog" : undefined}
        aria-label={
          mobileDialogOpen
            ? "Navigasyon menüsü"
            : undefined
        }
        className={[
          "no-print",
          "fixed inset-y-0 left-0 z-50",
          "transform transition-transform duration-300",
          "md:relative md:inset-auto md:h-dvh md:shrink-0 md:translate-x-0",
          open
            ? "translate-x-0"
            : "-translate-x-full",
        ].join(" ")}
      >
        <Sidebar onClose={closeSidebar} />
      </div>

      <main className="flex min-h-dvh min-w-0 flex-1 flex-col overflow-x-hidden md:h-dvh md:min-h-0 md:overflow-hidden">
        <header className="no-print sticky top-0 z-30 flex shrink-0 items-center gap-3 border-b border-border bg-sidebar/95 px-4 py-3 backdrop-blur md:hidden">
          <button
            ref={menuButtonRef}
            type="button"
            onClick={() => setOpen(true)}
            aria-label="Menüyü aç"
            aria-expanded={open}
            aria-controls="mobile-sidebar"
            className="rounded-lg p-1 text-muted-foreground transition-colors hover:bg-sidebar-accent hover:text-sidebar-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          >
            <Menu size={20} />
          </button>

          <Sparkles
            size={14}
            className="text-primary"
          />

          <span className="flex-1 text-sm font-bold">
            FikirLab
          </span>
        </header>

        <Outlet />
      </main>
    </div>
  );
}
