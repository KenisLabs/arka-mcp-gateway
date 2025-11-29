import * as React from "react";
import {
  ChevronsUpDown,
  CreditCard,
  Key,
  LayoutGrid,
  Search,
  Tag,
  TrendingUp,
  User,
  Users,
  Zap,
  Shield,
  UsersRound,
  Lock,
  Palette,
  BarChart3,
  FileText,
  Globe,
  Activity,
  Sparkles,
} from "lucide-react";
import { Link, useLocation } from "react-router-dom";

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarInput,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarMenuSub,
  SidebarMenuSubButton,
  SidebarMenuSubItem,
} from "@/components/ui/sidebar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

const applicationItems = [
  { title: "MCP Servers", icon: Zap, url: "/dashboard", enabled: true },
  {
    title: "Documentation",
    icon: LayoutGrid,
    url: "/documentation",
    enabled: true,
  },
  {
    title: "API Keys",
    icon: Key,
    url: "/api-keys",
    enabled: false,
    comingSoon: true,
  },
  {
    title: "Usage",
    icon: TrendingUp,
    url: "/usage",
    enabled: false,
    comingSoon: true,
  },
];

const enterpriseItems = [
  {
    title: "Enterprise SSO",
    icon: Shield,
    url: "/enterprise/sso",
    description: "Azure AD, SAML, LDAP integration",
  },
  {
    title: "Teams & Groups",
    icon: UsersRound,
    url: "/enterprise/teams",
    description: "Team-based permissions and collaboration",
  },
  {
    title: "AI Guardrails",
    icon: Sparkles,
    url: "/enterprise/guardrails",
    description: "Content filtering, PII detection, DLP",
  },
  {
    title: "Whitelabeling",
    icon: Palette,
    url: "/enterprise/whitelabel",
    description: "Custom branding and themes",
  },
  {
    title: "Audit Logs",
    icon: FileText,
    url: "/enterprise/audit",
    description: "Comprehensive audit trail and compliance",
  },
  {
    title: "Custom MCP Servers",
    icon: Zap,
    url: "/enterprise/custom-servers",
    description: "Build and deploy your own MCP servers",
  },
  {
    title: "Monitoring",
    icon: Activity,
    url: "/enterprise/monitoring",
    description: "Real-time monitoring and alerts",
  },
];

const settingsItems = [
  { title: "Profile", icon: User, url: "/profile" },
  { title: "Billing", icon: CreditCard, url: "/billing" },
];

export function AppSidebar({ user, onLogout }) {
  const location = useLocation();
  const pathname = location.pathname;

  // Check if user is admin
  const isAdmin = user?.role === "admin";

  return (
    <Sidebar>
      <SidebarHeader className="border-b border-sidebar-border">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="ghost"
              className="w-full justify-between px-2 h-12"
            >
              <div className="flex items-center gap-2">
                <Avatar className="size-6 rounded-md bg-gradient-to-br from-pink-500 via-purple-500 to-orange-500">
                  <AvatarFallback className="rounded-md bg-gradient-to-br from-pink-500 via-purple-500 to-orange-500 text-white text-xs">
                    A
                  </AvatarFallback>
                </Avatar>
                <span className="text-sm font-medium">Personal Account</span>
              </div>
              <ChevronsUpDown className="size-4 opacity-50" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent
            align="start"
            className="w-[--radix-dropdown-menu-trigger-width]"
          >
            <DropdownMenuItem>Personal Account</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
        <div className="px-2 pb-2">
          <div className="relative">
            <Search className="absolute left-2 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
            <SidebarInput placeholder="Search Account..." className="pl-8" />
          </div>
        </div>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Application</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {applicationItems.map((item) => (
                <SidebarMenuItem key={item.title}>
                  {item.enabled ? (
                    <SidebarMenuButton asChild isActive={pathname === item.url}>
                      <Link to={item.url}>
                        <item.icon />
                        <span>{item.title}</span>
                      </Link>
                    </SidebarMenuButton>
                  ) : (
                    <SidebarMenuButton
                      disabled
                      className="cursor-not-allowed opacity-50"
                    >
                      <item.icon />
                      <span>{item.title}</span>
                      {item.comingSoon && (
                        <Badge variant="secondary" className="ml-auto text-xs">
                          Coming Soon
                        </Badge>
                      )}
                    </SidebarMenuButton>
                  )}
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
        {/* Admin Section - Only visible to admins */}
        {isAdmin && (
          <SidebarGroup>
            <SidebarGroupLabel>Administration</SidebarGroupLabel>
            <SidebarGroupContent>
              <SidebarMenu>
                <SidebarMenuItem>
                  <SidebarMenuButton
                    asChild
                    isActive={pathname === "/admin/users"}
                  >
                    <Link to="/admin/users">
                      <Users />
                      <span>Users</span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        )}
        <SidebarGroup>
          <SidebarGroupLabel>Settings</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {settingsItems.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild isActive={pathname === item.url}>
                    <Link to={item.url}>
                      <item.icon />
                      <span>{item.title}</span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        {/* Enterprise Section */}
        <SidebarGroup>
          <SidebarGroupLabel>
            <div className="flex items-center gap-2">
              <span>Enterprise Features</span>
              <Badge
                variant="secondary"
                className="text-xs bg-gradient-to-r from-purple-500 to-pink-500 text-white border-0"
              >
                ⭐
              </Badge>
            </div>
          </SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {enterpriseItems.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild isActive={pathname === item.url}>
                    <Link to={item.url}>
                      <item.icon />
                      <span>{item.title}</span>
                      <Lock className="ml-auto size-3 opacity-50" />
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
      <SidebarFooter className="border-t border-sidebar-border">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="w-full justify-start gap-2 px-2">
              <Avatar className="size-8 rounded-md bg-gradient-to-br from-pink-500 via-purple-500 to-orange-500">
                <AvatarFallback className="rounded-md bg-gradient-to-br from-pink-500 via-purple-500 to-orange-500 text-white text-sm">
                  {user?.name?.charAt(0)?.toUpperCase() || "A"}
                </AvatarFallback>
              </Avatar>
              <div className="flex flex-col items-start text-left">
                <span className="text-sm font-medium">
                  {user?.name
                    ? user.name.length > 12
                      ? user.name.substring(0, 12) + "..."
                      : user.name
                    : "User"}
                </span>
                <span className="text-xs text-muted-foreground">
                  {user?.email
                    ? user.email.length > 15
                      ? user.email.substring(0, 15) + "..."
                      : user.email
                    : ""}
                </span>
              </div>
              <ChevronsUpDown className="ml-auto size-4 opacity-50" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-56">
            <DropdownMenuItem asChild>
              <Link to="/profile">Profile</Link>
            </DropdownMenuItem>
            <DropdownMenuItem asChild>
              <Link to="/billing">Billing</Link>
            </DropdownMenuItem>
            <DropdownMenuItem onClick={onLogout}>Sign Out</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </SidebarFooter>
    </Sidebar>
  );
}
