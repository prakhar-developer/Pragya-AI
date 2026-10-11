import {
  Home,
  MessagesSquare,
  AlertTriangle,
  Share2,
  FileText,
  UserRoundPen,
  LayoutDashboard,
  Gauge,
  type LucideIcon,
} from "lucide-react";

export interface NavItem {
  to: string;
  label: string;
  icon: LucideIcon;
}

export const NAV_ITEMS: NavItem[] = [
  { to: "/", label: "Home", icon: Home },
  { to: "/copilot", label: "Copilot", icon: MessagesSquare },
  { to: "/conflicts", label: "Conflicts", icon: AlertTriangle },
  { to: "/graph", label: "Graph Explorer", icon: Share2 },
  { to: "/documents", label: "Documents", icon: FileText },
  { to: "/expert", label: "Expert Capture", icon: UserRoundPen },
  { to: "/benchmarks", label: "Benchmarks", icon: Gauge },
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
];
