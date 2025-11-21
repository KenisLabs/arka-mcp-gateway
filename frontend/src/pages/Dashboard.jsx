import { useState, useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import api from "@/lib/api";
import {
  Search,
  Shield,
  ShieldCheck,
  Lock,
  CheckCircle,
  XCircle,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  SidebarProvider,
  SidebarInset,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/app-sidebar";
import { Separator } from "@/components/ui/separator";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";
import { MCPConfigModal } from "@/components/MCPConfigModal";

const floatingIcons = [
  {
    icon: "https://api.iconify.design/logos:slack-icon.svg",
    position: "top-[10%] left-[15%]",
    size: 40,
  },
  {
    icon: "https://api.iconify.design/logos:dropbox.svg",
    position: "top-[15%] right-[20%]",
    size: 50,
  },
  {
    icon: "https://api.iconify.design/logos:trello.svg",
    position: "top-[25%] right-[10%]",
    size: 35,
  },
  {
    icon: "https://api.iconify.design/logos:google-calendar.svg",
    position: "top-[35%] right-[25%]",
    size: 40,
  },
  {
    icon: "https://api.iconify.design/logos:google-gmail.svg",
    position: "bottom-[35%] left-[10%]",
    size: 50,
  },
  {
    icon: "https://api.iconify.design/logos:figma.svg",
    position: "bottom-[25%] right-[15%]",
    size: 30,
  },
  {
    icon: "https://api.iconify.design/logos:notion-icon.svg",
    position: "bottom-[40%] right-[30%]",
    size: 40,
  },
  {
    icon: "https://api.iconify.design/logos:supabase-icon.svg",
    position: "bottom-[30%] left-[25%]",
    size: 40,
  },
  {
    icon: "https://api.iconify.design/logos:linkedin-icon.svg",
    position: "bottom-[20%] right-[8%]",
    size: 45,
  },
  {
    icon: "https://api.iconify.design/logos:airtable.svg",
    position: "bottom-[15%] left-[20%]",
    size: 38,
  },
  {
    icon: "https://api.iconify.design/logos:google-drive.svg",
    position: "top-[20%] right-[35%]",
    size: 48,
  },
  {
    icon: "https://api.iconify.design/devicon:jira.svg",
    position: "bottom-[35%] left-[35%]",
    size: 36,
  },
];

function Dashboard() {
  const [user, setUser] = useState(null);
  const [mcpServers, setMcpServers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [notification, setNotification] = useState(null);
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const [mcpConfigOpen, setMcpConfigOpen] = useState(false);
  const [selectedClient, setSelectedClient] = useState(null);

  useEffect(() => {
    checkAuth();

    // Check for OAuth callback results
    const authSuccess = searchParams.get("auth_success");
    const authError = searchParams.get("auth_error");
    const errorDescription = searchParams.get("description");

    if (authSuccess === "true") {
      setNotification({
        type: "success",
        message: "Successfully authorized! Your MCP server is now connected.",
      });
      // Clear query params
      setSearchParams({});
      // Refresh server list to show updated authorization status
      fetchMcpServers();
    } else if (authError) {
      setNotification({
        type: "error",
        message: `Authorization failed: ${errorDescription || authError}`,
      });
      // Clear query params
      setSearchParams({});
    }
  }, []);

  const checkAuth = async () => {
    try {
      const response = await api.get("/api/auth/me");
      setUser(response.data);
      await fetchMcpServers();
      setLoading(false);
    } catch (error) {
      console.error("Not authenticated:", error);
      setLoading(false);
      navigate("/login");
    }
  };

  const fetchMcpServers = async () => {
    try {
      const response = await api.get("/api/servers/me");
      setMcpServers(response.data);
    } catch (error) {
      console.error("Failed to fetch MCP servers:", error);
      // Fallback to public endpoint if authenticated endpoint fails
      try {
        const fallbackResponse = await api.get("/api/servers");
        // Map to include default values
        setMcpServers(
          fallbackResponse.data.map((server) => ({
            ...server,
            is_authorized: false,
            is_enabled:
              server.default_enabled !== undefined
                ? server.default_enabled
                : true,
            authorized_at: null,
          }))
        );
      } catch (fallbackError) {
        console.error("Failed to fetch from fallback:", fallbackError);
      }
    }
  };

  const handleToggleEnabled = async (serverId, currentEnabled) => {
    try {
      await api.put(`/api/servers/${serverId}/toggle`, {
        enabled: !currentEnabled,
      });
      // Update local state
      setMcpServers((prevServers) =>
        prevServers.map((server) =>
          server.id === serverId
            ? { ...server, is_enabled: !currentEnabled }
            : server
        )
      );
    } catch (error) {
      console.error("Failed to toggle MCP:", error);
    }
  };

  const handleAuthorize = async (serverId) => {
    try {
      // Get OAuth authorization URL from backend
      const response = await api.get(`/api/servers/${serverId}/auth-url`);

      // Redirect user to OAuth provider
      window.location.href = response.data.auth_url;
    } catch (error) {
      console.error("Failed to initiate OAuth:", error);
      setNotification({
        type: "error",
        message: `Failed to start authorization: ${
          error.response?.data?.detail || error.message
        }`,
      });
    }
  };

  const handleDisconnect = async (serverId) => {
    try {
      await api.delete(`/api/servers/${serverId}/disconnect`);

      // Update local state to reflect disconnected status
      setMcpServers((prevServers) =>
        prevServers.map((server) =>
          server.id === serverId
            ? { ...server, is_authorized: false, authorized_at: null }
            : server
        )
      );

      setNotification({
        type: "success",
        message: "Successfully disconnected from server",
      });
    } catch (error) {
      console.error("Failed to disconnect:", error);
      setNotification({
        type: "error",
        message: `Failed to disconnect: ${
          error.response?.data?.detail || error.message
        }`,
      });
    }
  };

  const handleConnect = (server) => {
    if (!server.is_authorized && server.requires_auth) {
      handleAuthorize(server.id);
    } else {
      // TODO: Implement actual connection logic
      console.log("Connect to MCP:", server.id);
      alert(
        `Connecting to ${server.name}... (Connection logic will be implemented in the next phase)`
      );
    }
  };

  const handleLogout = async () => {
    try {
      await api.post("/api/auth/logout", {});
      navigate("/login");
    } catch (error) {
      console.error("Logout failed:", error);
      navigate("/login");
    }
  };

  const handleOpenMCPConfig = (clientType) => {
    setSelectedClient(clientType);
    setMcpConfigOpen(true);
  };

  const filteredServers = mcpServers.filter(
    (server) =>
      server.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      server.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <div className="text-sm text-muted-foreground">Loading...</div>
      </div>
    );
  }

  return (
    <SidebarProvider>
      <AppSidebar user={user} onLogout={handleLogout} />
      <SidebarInset>
        <header className="sticky top-0 z-10 flex h-14 shrink-0 items-center gap-2 border-b bg-background px-4">
          <SidebarTrigger />
          <Separator orientation="vertical" className="h-6" />
          <div className="flex items-center gap-2">
            <div className="flex size-6 items-center justify-center rounded-lg bg-gradient-to-br from-pink-500 via-purple-500 to-orange-500">
              <span className="text-sm font-bold text-white">A</span>
            </div>
            <span className="font-semibold text-sm">Arka MCP Gateway</span>
          </div>
        </header>
        <div className="flex flex-1 flex-col">
          {/* Notification Banner */}
          {notification && (
            <div
              className={`mx-6 mt-4 rounded-lg border p-4 ${
                notification.type === "success"
                  ? "border-green-500 bg-green-50 dark:bg-green-950/20"
                  : "border-red-500 bg-red-50 dark:bg-red-950/20"
              }`}
            >
              <div className="flex items-center gap-3">
                {notification.type === "success" ? (
                  <CheckCircle className="size-5 text-black-600 dark:text-green-400" />
                ) : (
                  <XCircle className="size-5 text-black-600 dark:text-red-400" />
                )}
                <p className="text-sm font-medium text-gray-900 dark:text-gray-900">
                  {notification.message}
                </p>
                <button
                  onClick={() => setNotification(null)}
                  className="ml-auto text-sm underline text-gray-900 dark:text-gray-900"
                >
                  Dismiss
                </button>
              </div>
            </div>
          )}

          {/* Hero Section */}
          <div className="relative overflow-hidden bg-gradient-to-b from-background to-muted/20 py-24">
            {/* Floating Icons */}
            {floatingIcons.map((item, i) => (
              <div
                key={i}
                className={`absolute ${item.position} opacity-30 animate-pulse`}
                style={{ width: item.size, height: item.size }}
              >
                <img src={item.icon} alt="" className="size-full" />
              </div>
            ))}

            {/* Hero Content */}
            <div className="relative z-10 mx-auto max-w-4xl space-y-8 px-6 text-center">
              <h1 className="bg-gradient-to-r from-pink-500 via-red-500 to-orange-500 bg-clip-text text-7xl font-bold text-transparent">
                Arka
              </h1>
              <p className="text-2xl font-semibold text-foreground">
                ✨ One MCP server that handles any tools progressively at scale
              </p>

              {/* Action Buttons */}
              <div className="flex flex-wrap items-center justify-center gap-4">
                <div className="relative flex-1 min-w-[200px] max-w-[300px]">
                  <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    placeholder="Search integrations..."
                    className="pl-10"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                </div>
                <Button variant="outline" size="sm">
                  📖 Documentation
                </Button>
                <Button
                  size="sm"
                  className="bg-black text-white hover:bg-black/90"
                  onClick={() => handleOpenMCPConfig("cursor")}
                >
                  🐱 Add to Cursor
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleOpenMCPConfig("vscode")}
                >
                  💎 Add to VS Code
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleOpenMCPConfig("claude")}
                >
                  🌟 Add to Claude
                </Button>
              </div>
            </div>
          </div>

          {/* MCP Server Cards */}
          <div className="mx-auto max-w-7xl px-6 py-12">
            <div className="mb-8 flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-semibold mb-2">
                  Available MCP Servers
                </h2>
                <p className="text-muted-foreground">
                  {filteredServers.length} of {mcpServers.length} servers shown
                </p>
              </div>
            </div>

            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {filteredServers.map((server) => (
                <Card key={server.id} className="relative">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-3 flex-1">
                        <div className="size-10 rounded-lg bg-muted p-2 flex-shrink-0">
                          <img
                            src={
                              server.icon
                                ? `https://api.iconify.design/${server.icon}.svg`
                                : "https://api.iconify.design/mdi:server.svg?color=%23888888"
                            }
                            alt={server.name}
                            className="size-full"
                          />
                        </div>
                        <div className="flex-1 min-w-0">
                          <CardTitle className="text-base truncate">
                            {server.name}
                          </CardTitle>
                          <div className="flex items-center gap-2 mt-1">
                            {server.is_authorized ? (
                              <Badge
                                variant="success"
                                className="flex items-center gap-1"
                              >
                                <ShieldCheck className="size-3" />
                                Authorized
                              </Badge>
                            ) : server.requires_auth ? (
                              <Badge
                                variant="warning"
                                className="flex items-center gap-1"
                              >
                                <Shield className="size-3" />
                                Not Authorized
                              </Badge>
                            ) : (
                              <Badge
                                variant="secondary"
                                className="flex items-center gap-1"
                              >
                                <Lock className="size-3" />
                                No Auth Required
                              </Badge>
                            )}
                          </div>
                        </div>
                      </div>
                      <div className="flex flex-col items-end gap-2">
                        <Switch
                          checked={server.is_enabled}
                          onCheckedChange={() =>
                            handleToggleEnabled(server.id, server.is_enabled)
                          }
                        />
                      </div>
                    </div>
                    <CardDescription className="mt-2">
                      {server.description}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    {(() => {
                      // Check if token is expired
                      const isTokenExpired =
                        server.expires_at &&
                        new Date(server.expires_at) <= new Date();

                      // Show "Authorize" if:
                      // 1. Server requires auth and not authorized yet
                      // 2. Server is authorized but token is expired
                      if (
                        (!server.is_authorized && server.requires_auth) ||
                        (server.is_authorized && isTokenExpired)
                      ) {
                        return (
                          <Button
                            className="w-full"
                            variant="outline"
                            onClick={() => handleAuthorize(server.id)}
                          >
                            Authorize
                          </Button>
                        );
                      }

                      // Show "Disconnect" if authorized and token not expired
                      if (server.is_authorized) {
                        return (
                          <Button
                            className="w-full"
                            variant="destructive"
                            onClick={() => handleDisconnect(server.id)}
                          >
                            Disconnect
                          </Button>
                        );
                      }

                      // Show "Connect" for non-auth servers
                      return (
                        <Button
                          className="w-full"
                          onClick={() => handleConnect(server)}
                        >
                          Connect
                        </Button>
                      );
                    })()}
                  </CardContent>
                </Card>
              ))}
            </div>

            {filteredServers.length === 0 && (
              <div className="text-center py-12">
                <p className="text-muted-foreground">
                  No servers match your search.
                </p>
              </div>
            )}
          </div>
        </div>
      </SidebarInset>

      {/* MCP Config Modal */}
      <MCPConfigModal
        open={mcpConfigOpen}
        onOpenChange={setMcpConfigOpen}
        clientType={selectedClient}
      />
    </SidebarProvider>
  );
}

export default Dashboard;
