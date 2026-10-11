import { NavLink } from "react-router-dom";
import { cn } from "../../lib/utils";
import { NAV_ITEMS } from "./navItems";

export function MobileNav() {
  return (
    <nav className="fixed bottom-0 left-0 right-0 z-40 flex items-stretch justify-between border-t border-border bg-card/95 backdrop-blur md:hidden">
      {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
        <NavLink
          key={to}
          to={to}
          end={to === "/"}
          className={({ isActive }) =>
            cn(
              "flex flex-1 flex-col items-center gap-0.5 py-2 text-[10px] font-medium transition-colors",
              isActive ? "text-violet-700" : "text-muted"
            )
          }
        >
          <Icon size={18} />
          <span className="truncate">{label.split(" ")[0]}</span>
        </NavLink>
      ))}
    </nav>
  );
}
