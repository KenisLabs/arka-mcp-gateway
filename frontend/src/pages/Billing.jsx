import {
  SidebarProvider,
  SidebarInset,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/app-sidebar";
import { Separator } from "@/components/ui/separator";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Check } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";

function Billing() {
  const { user, loading, logout } = useAuth();

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <div className="text-sm text-muted-foreground">Loading...</div>
      </div>
    );
  }

  return (
    <SidebarProvider>
      <AppSidebar user={user} onLogout={logout} />
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
        <div className="flex flex-1 flex-col gap-4 p-4 pt-0">
          <div className="mt-4">
            <h1 className="text-3xl font-bold">Billing</h1>
            <p className="text-muted-foreground mt-2">
              Manage your subscription and billing information
            </p>
          </div>

          <Card className="mb-4">
            <CardHeader>
              <CardTitle>Current Plan</CardTitle>
              <CardDescription>
                You are currently on the Free plan
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Check className="h-4 w-4 text-green-600" />
                  <span className="text-sm">
                    1,000 MCP tool calls per month
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <Check className="h-4 w-4 text-green-600" />
                  <span className="text-sm">Basic MCP server integrations</span>
                </div>
                <div className="flex items-center gap-2">
                  <Check className="h-4 w-4 text-green-600" />
                  <span className="text-sm">Community support</span>
                </div>
              </div>
              <Button className="mt-4">Upgrade Plan</Button>
            </CardContent>
          </Card>

          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Free</CardTitle>
                <CardDescription>Perfect for trying out</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">$0</div>
                <p className="text-sm text-muted-foreground">per month</p>
                <ul className="mt-4 space-y-2 text-sm">
                  <li className="flex items-center gap-2">
                    <Check className="h-4 w-4" />
                    1,000 MCP tool calls/month
                  </li>
                  <li className="flex items-center gap-2">
                    <Check className="h-4 w-4" />
                    Basic integrations
                  </li>
                </ul>
                <Button variant="outline" className="mt-4 w-full" disabled>
                  Current Plan
                </Button>
              </CardContent>
            </Card>

            {/* Pro Plan - Commented out for now */}
            {/* <Card className="border-primary">
              <CardHeader>
                <CardTitle>Pro</CardTitle>
                <CardDescription>For growing teams</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">$49</div>
                <p className="text-sm text-muted-foreground">per month</p>
                <ul className="mt-4 space-y-2 text-sm">
                  <li className="flex items-center gap-2">
                    <Check className="h-4 w-4" />
                    100,000 requests/month
                  </li>
                  <li className="flex items-center gap-2">
                    <Check className="h-4 w-4" />
                    All integrations
                  </li>
                  <li className="flex items-center gap-2">
                    <Check className="h-4 w-4" />
                    Priority support
                  </li>
                </ul>
                <Button className="mt-4 w-full">Upgrade</Button>
              </CardContent>
            </Card> */}

            <Card>
              <CardHeader>
                <CardTitle>Enterprise</CardTitle>
                <CardDescription>For large organizations</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">Custom</div>
                <p className="text-sm text-muted-foreground">Contact us</p>
                <ul className="mt-4 space-y-2 text-sm">
                  <li className="flex items-center gap-2">
                    <Check className="h-4 w-4" />
                    Unlimited requests
                  </li>
                  <li className="flex items-center gap-2">
                    <Check className="h-4 w-4" />
                    Custom integrations
                  </li>
                  <li className="flex items-center gap-2">
                    <Check className="h-4 w-4" />
                    24/7 support
                  </li>
                </ul>
                <Button
                  variant="outline"
                  className="mt-4 w-full"
                  onClick={() =>
                    window.open(
                      "https://calendly.com/ayushshivani12345/",
                      "_blank"
                    )
                  }
                >
                  Contact Sales
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </SidebarInset>
    </SidebarProvider>
  );
}

export default Billing;
