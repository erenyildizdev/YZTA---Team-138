import { useEffect, useRef, useState } from "react";
import { Menu, Sparkles, X } from "lucide-react";
import { NavLink, Outlet } from "react-router";
import { BarChart3, Bot, FileText, History, LayoutDashboard, Settings } from "lucide-react";

const navigation = [
  { to: "/", label: "Ana Sayfa", Icon: LayoutDashboard, end: true },
  { to: "/mentor", label: "Mentor ile Görüş", Icon: Bot },
  { to: "/analysis", label: "Fikir Analizi", Icon: BarChart3 },
  { to: "/report", label: "Doğrulama Raporu", Icon: FileText },
  { to: "/history", label: "Geçmiş Fikirler", Icon: History },
];

function Sidebar({ onClose }: { onClose: () => void }) {
  return (
    <aside className="flex h-full w-64 flex-col border-r border-sidebar-border bg-sidebar text-sidebar-foreground">
      <div className="flex items-center justify-between border-b border-sidebar-border px-5 py-5">
        <NavLink to="/" onClick={onClose} className="flex items-center gap-2.5">
          <span className="flex h-8 w-8 items-center justify-center rounded-xl bg-primary"><Sparkles size={15} /></span>
          <span className="font-bold">FikirLab</span>
        </NavLink>
        <button type="button" onClick={onClose} aria-label="Menüyü kapat" className="rounded-lg p-2 text-muted-foreground hover:bg-white/5 md:hidden"><X size={18} /></button>
      </div>
      <nav aria-label="Ana navigasyon" className="flex-1 space-y-1 p-3">
        {navigation.map(({ to, label, Icon, end }) => (
          <NavLink key={to} to={to} end={end} onClick={onClose} className={({ isActive }) => `flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm transition-colors ${isActive ? "bg-sidebar-accent text-blue-300" : "text-sidebar-foreground/55 hover:bg-white/5 hover:text-sidebar-foreground"}`}>
            <Icon size={17} /><span>{label}</span>
          </NavLink>
        ))}
      </nav>
      <div className="border-t border-sidebar-border p-3">
        <button type="button" disabled title="Backend entegrasyonu sonrasında kullanılabilir" className="flex w-full cursor-not-allowed items-center gap-3 rounded-xl px-3 py-2.5 text-sm text-sidebar-foreground/30"><Settings size={17} />Hesap Ayarları</button>
        <div className="mt-2 rounded-xl bg-white/5 px-3 py-2.5 text-xs"><strong>Ahmet Yılmaz</strong><div className="mt-1 text-sidebar-foreground/35">Aktif Kullanıcı</div></div>
      </div>
    </aside>
  );
}

export function AppLayout() {
  const [open, setOpen] = useState(false);
  const menuButton = useRef<HTMLButtonElement>(null);
  const close = () => { setOpen(false); menuButton.current?.focus(); };

  useEffect(() => {
    if (!open) return;
    const onKeyDown = (event: KeyboardEvent) => { if (event.key === "Escape") close(); };
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [open]);

  return (
    <div className="flex min-h-dvh w-full overflow-x-hidden bg-background">
      {open && <button type="button" aria-label="Menüyü kapat" onClick={close} className="fixed inset-0 z-40 bg-black/60 md:hidden" />}
      <div aria-modal={open || undefined} role={open ? "dialog" : undefined} aria-label={open ? "Navigasyon menüsü" : undefined} className={`fixed inset-y-0 left-0 z-50 transform transition-transform duration-300 md:sticky md:top-0 md:h-dvh md:translate-x-0 ${open ? "translate-x-0" : "-translate-x-full"}`}>
        <Sidebar onClose={close} />
      </div>
      <main className="flex min-h-dvh min-w-0 flex-1 flex-col overflow-x-hidden">
        <header className="sticky top-0 z-30 flex items-center gap-3 border-b border-border bg-sidebar/95 px-4 py-3 backdrop-blur md:hidden">
          <button ref={menuButton} type="button" onClick={() => setOpen(true)} aria-label="Menüyü aç" aria-expanded={open} className="rounded-lg p-1 text-muted-foreground"><Menu size={20} /></button>
          <Sparkles size={14} className="text-primary" /><span className="text-sm font-bold">FikirLab</span>
        </header>
        <Outlet />
      </main>
    </div>
  );
}
