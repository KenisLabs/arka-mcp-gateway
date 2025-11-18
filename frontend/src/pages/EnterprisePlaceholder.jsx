import { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api from "@/lib/api";
import { Lock, Mail, ExternalLink, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
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
import { Badge } from "@/components/ui/badge";

// Map feature keys to their details
const featureDetails = {
  sso: {
    title: "Enterprise SSO",
    icon: "🔐",
    description:
      "Secure single sign-on with industry-leading identity providers",
    features: [
      "Azure AD / Entra ID integration",
      "SAML 2.0 (Okta, OneLogin, Auth0)",
      "LDAP/Active Directory support",
      "Google Workspace SSO",
      "Multi-factor Authentication (MFA)",
      "SCIM-based user provisioning",
    ],
  },
  teams: {
    title: "Teams & Groups",
    icon: "👥",
    description: "Organize users into teams with hierarchical permissions",
    features: [
      "Create and manage teams/groups",
      "Team-based tool permissions",
      "Role hierarchies and inheritance",
      "Dedicated team dashboards",
      "Cross-team collaboration controls",
      "Team activity monitoring",
    ],
  },
  guardrails: {
    title: "AI Guardrails & Compliance",
    icon: "🛡️",
    description: "Advanced security controls for AI interactions",
    features: [
      "Content filtering and moderation",
      "PII detection & automatic redaction",
      "Prompt injection protection",
      "Data Loss Prevention (DLP)",
      "Approval workflows for sensitive operations",
      "Advanced threat detection",
    ],
  },
  whitelabel: {
    title: "Whitelabeling & Customization",
    icon: "🎨",
    description: "Make the platform your own with complete branding control",
    features: [
      "Custom branding (logo, colors, theme)",
      "Custom domain (gateway.yourcompany.com)",
      "Branded login and signup pages",
      "Custom email templates",
      'Remove "Powered by Arka" branding',
      "Full theme customization",
    ],
  },
  audit: {
    title: "Audit Logs & Compliance",
    icon: "📊",
    description: "Comprehensive audit trail for security and compliance",
    features: [
      "Comprehensive audit logs",
      "Searchable audit trail with filters",
      "Compliance reports (SOC 2, GDPR, HIPAA)",
      "SIEM integration (Splunk, Datadog)",
      "Data retention policies",
      "Tamper-proof log storage",
    ],
  },
  "custom-servers": {
    title: "Custom MCP Servers",
    icon: "⚡",
    description: "Build and deploy your own custom MCP servers",
    features: [
      "Custom MCP server development support",
      "Private server registry",
      "API key management for custom servers",
      "Webhook support for integrations",
      "Custom server plugins and extensions",
      "Secrets management integration",
    ],
  },
  monitoring: {
    title: "Monitoring & Observability",
    icon: "📡",
    description: "Real-time monitoring and alerting for your platform",
    features: [
      "Real-time monitoring dashboard",
      "Custom alerts and notifications",
      "Anomaly detection with ML",
      "Distributed tracing",
      "Performance analytics",
      "99.9% uptime SLA",
    ],
  },
};

function EnterprisePlaceholder() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const { feature } = useParams();

  const details = featureDetails[feature] || {
    title: "Enterprise Feature",
    icon: "⭐",
    description: "This is an Enterprise Edition feature",
    features: [
      "Enhanced capabilities",
      "Priority support",
      "Advanced security",
    ],
  };

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const response = await api.get("/api/auth/me");
      setUser(response.data);
      setLoading(false);
    } catch (error) {
      console.error("Not authenticated:", error);
      setLoading(false);
      navigate("/login");
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

  const handleContactSales = () => {
    window.open("https://calendly.com/ayushshivani12345/", "_blank");
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
      </div>
    );
  }

  return (
    <SidebarProvider>
      <AppSidebar user={user} onLogout={handleLogout} />
      <SidebarInset>
        <header className="flex h-16 shrink-0 items-center gap-2 border-b px-4">
          <SidebarTrigger className="-ml-1" />
          <Separator orientation="vertical" className="mr-2 h-4" />
          <div className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-purple-600" />
            <h1 className="text-xl font-semibold">{details.title}</h1>
          </div>
          <div className="ml-auto flex items-center gap-2">
            <Badge
              variant="secondary"
              className="bg-gradient-to-r from-purple-500 to-pink-500 text-white border-0"
            >
              ⭐ Enterprise
            </Badge>
          </div>
        </header>

        <div className="flex flex-1 flex-col gap-6 p-8">
          {/* Hero Section */}
          <div className="relative overflow-hidden rounded-xl border-2 border-purple-200 dark:border-purple-800 p-12">
            <div className="absolute top-4 right-4 text-6xl opacity-20">
              {details.icon}
            </div>
            <div className="relative z-10 max-w-2xl">
              <div className="flex items-center gap-2 mb-4">
                <Lock className="h-8 w-8 text-purple-600" />
                <Badge
                  variant="secondary"
                  className="bg-gradient-to-r from-purple-500 to-pink-500 text-white border-0 text-sm"
                >
                  Enterprise Edition Only
                </Badge>
              </div>
              <h2 className="text-4xl font-bold mb-4 bg-gradient-to-r from-purple-600 via-pink-600 to-orange-600 bg-clip-text text-transparent">
                {details.title}
              </h2>
              <p className="text-xl text-muted-foreground mb-6">
                {details.description}
              </p>
              <div className="flex gap-4">
                <Button
                  size="lg"
                  className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white"
                  onClick={handleContactSales}
                >
                  <ExternalLink className="mr-2 h-4 w-4" />
                  Schedule Demo
                </Button>
                <Button
                  size="lg"
                  variant="outline"
                  onClick={() =>
                    window.open(
                      "mailto:support@kenislabs.com?subject=Enterprise Edition Inquiry",
                      "_blank"
                    )
                  }
                >
                  <Mail className="mr-2 h-4 w-4" />
                  Email Us
                </Button>
              </div>
            </div>
          </div>

          {/* Features Grid */}
          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Key Features</CardTitle>
                <CardDescription>
                  What's included in this Enterprise feature
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3">
                  {details.features.map((feature, index) => (
                    <li key={index} className="flex items-start gap-3">
                      <div className="rounded-full bg-purple-100 dark:bg-purple-900/20 p-1 mt-0.5">
                        <Sparkles className="h-3 w-3 text-purple-600" />
                      </div>
                      <span className="text-sm text-muted-foreground">
                        {feature}
                      </span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Why Enterprise?</CardTitle>
                <CardDescription>
                  Benefits of upgrading to Enterprise Edition
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3">
                  <li className="flex items-start gap-3">
                    <div className="rounded-full bg-green-100 dark:bg-green-900/20 p-1 mt-0.5">
                      <Sparkles className="h-3 w-3 text-green-600" />
                    </div>
                    <span className="text-sm text-muted-foreground">
                      24/7 priority support with dedicated customer success
                      manager
                    </span>
                  </li>
                  <li className="flex items-start gap-3">
                    <div className="rounded-full bg-green-100 dark:bg-green-900/20 p-1 mt-0.5">
                      <Sparkles className="h-3 w-3 text-green-600" />
                    </div>
                    <span className="text-sm text-muted-foreground">
                      99.9% uptime SLA with guaranteed response times
                    </span>
                  </li>
                  <li className="flex items-start gap-3">
                    <div className="rounded-full bg-green-100 dark:bg-green-900/20 p-1 mt-0.5">
                      <Sparkles className="h-3 w-3 text-green-600" />
                    </div>
                    <span className="text-sm text-muted-foreground">
                      Custom feature development and integrations
                    </span>
                  </li>
                  <li className="flex items-start gap-3">
                    <div className="rounded-full bg-green-100 dark:bg-green-900/20 p-1 mt-0.5">
                      <Sparkles className="h-3 w-3 text-green-600" />
                    </div>
                    <span className="text-sm text-muted-foreground">
                      Quarterly business reviews and strategic planning
                    </span>
                  </li>
                  <li className="flex items-start gap-3">
                    <div className="rounded-full bg-green-100 dark:bg-green-900/20 p-1 mt-0.5">
                      <Sparkles className="h-3 w-3 text-green-600" />
                    </div>
                    <span className="text-sm text-muted-foreground">
                      Private Slack channel for instant support
                    </span>
                  </li>
                </ul>
              </CardContent>
            </Card>
          </div>
        </div>
      </SidebarInset>
    </SidebarProvider>
  );
}

export default EnterprisePlaceholder;
