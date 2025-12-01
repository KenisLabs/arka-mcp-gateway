import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Copy, CheckCircle, AlertCircle } from "lucide-react";
import api from "@/lib/api";

export function MCPConfigModal({ open, onOpenChange, clientType }) {
  const [generatedToken, setGeneratedToken] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);

  const handleGenerateToken = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await api.post("/api/mcp-tokens/", {});

      setGeneratedToken(response.data);
    } catch (err) {
      console.error("Failed to generate token:", err);
      setError(err.response?.data?.detail || "Failed to generate token");
    } finally {
      setLoading(false);
    }
  };

  const handleCopyConfig = () => {
    const config = getConfigForClient();
    navigator.clipboard.writeText(config);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const getConfigForClient = () => {
    if (!generatedToken) return "";

    // Use backend URL from environment variable or derive from current origin
    const backendUrl = import.meta.env.VITE_API_URL || window.location.origin;

    // Configuration for VS Code and Cursor (http type with headers)
    const httpConfig = {
      type: "http",
      url: `${backendUrl}/mcp`,
      headers: {
        Authorization: `Bearer ${generatedToken.token}`,
      },
    };

    // Configuration for Claude Desktop (streamable-http transport)
    const claudeConfig = {
      type: "http",
      command: "npx",
      args: [
        "mcp-remote",
        `${backendUrl}/mcp`,
        "--header",
        "Authorization: Bearer ${AUTH_TOKEN}",
      ],
      env: {
        AUTH_TOKEN: generatedToken.token,
      },
    };

    if (clientType === "vscode") {
      // Protocol-based install: compact JSON for VS Code MCP install
      return JSON.stringify({
        servers: {
          "arka-mcp-gateway": httpConfig,
        },
      });
    } else if (clientType === "cursor") {
      return JSON.stringify(
        {
          mcpServers: {
            "arka-mcp-gateway": httpConfig,
          },
        },
        null,
        2
      );
    } else if (clientType === "claude") {
      return JSON.stringify(
        {
          mcpServers: {
            "arka-mcp-gateway": claudeConfig,
          },
        },
        null,
        2
      );
    }

    return JSON.stringify(httpConfig, null, 2);
 };

  const getInstructions = () => {
    if (clientType === "vscode") {
      return {
        title: "VS Code Setup",
        steps: [
          "Open VS Code Settings (Cmd/Ctrl + ,)",
          'Search for "MCP Servers"',
          'Click "Edit in settings.json"',
          "Paste the configuration below",
          "Reload VS Code",
        ],
        configPath: "~/.vscode/mcp-servers.json or in your settings.json",
      };
    } else if (clientType === "claude") {
      return {
        title: "Claude Desktop Setup",
        steps: [
          "Open Claude Desktop settings",
          "Navigate to Developer settings",
          "Add MCP server configuration",
          "Paste the configuration below",
          "Restart Claude Desktop",
        ],
        configPath:
          "~/Library/Application Support/Claude/claude_desktop_config.json (macOS)",
      };
    } else if (clientType === "cursor") {
      return {
        title: "Cursor Setup",
        steps: [
          "Open Cursor Settings",
          "Navigate to MCP Servers",
          'Click "Add Server"',
          "Paste the configuration below",
          "Restart Cursor",
        ],
        configPath: "~/.cursor/mcp-servers.json",
      };
    }

    // Default fallback
    return {
      title: "MCP Client Setup",
      steps: ["Configure your MCP client with the settings below"],
      configPath: "Client-specific configuration file",
    };
  };
  /**
   * Build protocol link for direct MCP install (VS Code)
   */
  const getProtocolLink = () => {
    if (clientType !== "vscode" || !generatedToken) return "";
    const backendUrl = import.meta.env.VITE_API_URL || window.location.origin;
    const payload = { name: "arka-mcp-gateway", type: "http", url: `${backendUrl}/mcp`, headers: { Authorization: `Bearer ${generatedToken.token}` } };
    return `vscode:mcp/install?${JSON.stringify(payload)}`;
  };
  /**
   * Build protocol link for direct MCP install (Cursor)
   */
  const getCursorProtocolLink = () => {
    if (clientType !== "cursor" || !generatedToken) return "";
    // Build base payload for Cursor install and encode as Base64
    const backendUrl = import.meta.env.VITE_API_URL || window.location.origin;
    const payload = { name: "arka-mcp-gateway", type: "http", url: `${backendUrl}/mcp`, headers: { Authorization: `Bearer ${generatedToken.token}` } };
    const json = JSON.stringify(payload);
    // btoa for Base64 encoding; use encodeURIComponent in case of URL issues
    const configBase64 = encodeURIComponent(btoa(json));
    // Cursor deeplink format
    return `cursor://anysphere.cursor-deeplink/mcp/install?name=${payload.name}&config=${configBase64}`;
  };

  const instructions = getInstructions();

  const handleClose = () => {
    setGeneratedToken(null);
    setError(null);
    setCopied(false);
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{instructions.title}</DialogTitle>
          <DialogDescription>
            Generate an access token and configure your {clientType} to connect
            to Arka MCP Gateway
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {!generatedToken ? (
            <>
              {/* Token Generation Form */}
              <div className="space-y-4">
                <p className="text-sm text-muted-foreground">
                  Generate a new MCP access token for your {clientType}. This
                  will automatically revoke any existing token.
                </p>

                {error && (
                  <Alert variant="destructive">
                    <AlertCircle className="size-4" />
                    <AlertDescription>{error}</AlertDescription>
                  </Alert>
                )}

                <Button
                  onClick={handleGenerateToken}
                  disabled={loading}
                  className="w-full"
                >
                  {loading ? "Generating..." : "Generate Token"}
                </Button>
              </div>
            </>
          ) : (
            <>
              {/* Success Message */}
              <Alert>
                <CheckCircle className="size-4 text-green-600" />
                <AlertDescription>
                  Token generated successfully! Copy the configuration below and
                  save it securely.
                  <strong className="block mt-2 text-orange-600">
                    ⚠️ This token will only be shown once. Make sure to save it
                    now!
                  </strong>
                </AlertDescription>
              </Alert>

              {clientType === "vscode" ? (
                <div className="space-y-4">
                  <Button
                    onClick={() => window.location.href = getProtocolLink()}
                    className="w-full bg-[#e4e4e7] text-black hover:bg-[#e4e4e7]"
                  >
                    Install Arka MCP Gateway in VS Code
                  </Button>
                </div>
              ) : clientType === "cursor" ? (
                <div className="space-y-4">
                  <Button
                    onClick={() => window.location.href = getCursorProtocolLink()}
                    className="w-full bg-[#e4e4e7] text-black hover:bg-[#e4e4e7]"
                  >
                    Install Arka MCP Gateway in Cursor
                  </Button>
                </div>
              ) : (
                <>
                  {/* Instructions */}
                  <div className="space-y-3">
                    <h4 className="font-semibold text-sm">Setup Instructions:</h4>
                    <ol className="space-y-2 text-sm text-muted-foreground list-decimal list-inside">
                      {instructions.steps.map((step, i) => (
                        <li key={i}>{step}</li>
                      ))}
                    </ol>
                    <p className="text-xs text-muted-foreground mt-2 break-words">
                      Config file location:{" "}
                      <code className="bg-muted px-1 py-0.5 rounded break-all">
                        {instructions.configPath}
                      </code>
                    </p>
                  </div>

                  {/* Configuration */}
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <Label>Configuration</Label>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={handleCopyConfig}
                        className="gap-2"
                      >
                        {copied ? (
                          <>
                            <CheckCircle className="size-4" />
                            Copied!
                          </>
                        ) : (
                          <>
                            <Copy className="size-4" />
                            Copy
                          </>
                        )}
                      </Button>
                    </div>
                    <pre className="bg-muted p-4 rounded-lg text-xs overflow-x-auto whitespace-pre-wrap break-all">
                      <code className="break-all">{getConfigForClient()}</code>
                    </pre>
                  </div>

                  {/* Token Info */}
                  <div className="space-y-2 p-4 border rounded-lg bg-muted/50">
                    <h4 className="font-semibold text-sm">Token Details</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex flex-col sm:flex-row sm:justify-between gap-1">
                        <span className="text-muted-foreground">Token Name:</span>
                        <span className="font-medium break-words">
                          {generatedToken.token_name}
                        </span>
                      </div>
                      <div className="flex flex-col sm:flex-row sm:justify-between gap-1">
                        <span className="text-muted-foreground">Token ID:</span>
                        <span className="font-mono text-xs break-all">
                          {generatedToken.token_id}
                        </span>
                      </div>
                      <div className="flex flex-col sm:flex-row sm:justify-between gap-1">
                        <span className="text-muted-foreground">Created:</span>
                        <span className="break-words">
                          {new Date(generatedToken.created_at).toLocaleString()}
                        </span>
                      </div>
                    </div>
                  </div>
                </>
              )}

              {/* Action Buttons */}
              <div className="flex gap-2">
                <Button onClick={handleClose} className="flex-1">
                  Done
                </Button>
              </div>
            </>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
