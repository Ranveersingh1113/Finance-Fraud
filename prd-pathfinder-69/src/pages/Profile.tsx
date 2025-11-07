import { Header } from "@/components/Layout/Header";
import { Card } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { ChevronRight, Bell, Lock, Moon, Download, HelpCircle, LogOut, Loader2 } from "lucide-react";
import { useSystemStats } from "@/hooks/useStats";
import { useUserProfile } from "@/hooks/useUser";
import { useAuth } from "@/context/AuthContext";
import { useNavigate } from "react-router-dom";

export default function Profile() {
  const navigate = useNavigate();
  const { data: stats, isLoading: statsLoading } = useSystemStats();
  const { data: userProfile, isLoading: userLoading } = useUserProfile();
  const { user: authUser, logout } = useAuth();
  const user = userProfile || authUser;
  
  const caseStats = stats?.rag_engine_stats?.case_statistics;
  const totalCases = caseStats?.total_cases || 0;
  const totalQueries = caseStats?.total_queries || 0;
  const totalSARs = caseStats?.sar_reports || 0;

  // Generate initials from user name
  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const isLoading = userLoading || statsLoading;

  return (
    <div className="min-h-screen bg-background pb-20">
      <Header title="Profile" />
      
      <main className="px-4 py-6 max-w-screen-xl mx-auto space-y-6">
        {/* User Profile */}
        <Card className="p-6">
          {isLoading ? (
            <div className="flex items-center gap-4">
              <div className="h-16 w-16 rounded-full bg-muted animate-pulse" />
              <div className="flex-1 space-y-2">
                <div className="h-6 w-48 bg-muted rounded animate-pulse" />
                <div className="h-4 w-32 bg-muted rounded animate-pulse" />
                <div className="h-3 w-56 bg-muted rounded animate-pulse" />
              </div>
            </div>
          ) : user ? (
            <div className="flex items-center gap-4">
              <Avatar className="h-16 w-16">
                <AvatarImage src={user.avatar_url || undefined} />
                <AvatarFallback className="bg-primary text-primary-foreground text-xl">
                  {getInitials(user.name)}
                </AvatarFallback>
              </Avatar>
              <div className="flex-1">
                <h2 className="text-xl font-bold text-foreground">{user.name}</h2>
                <p className="text-sm text-muted-foreground">{user.role}</p>
                <p className="text-xs text-muted-foreground mt-1">{user.email}</p>
                {user.department && (
                  <p className="text-xs text-muted-foreground mt-1">{user.department}</p>
                )}
              </div>
            </div>
          ) : (
            <div className="text-center py-4 text-muted-foreground">
              Failed to load user profile
            </div>
          )}
        </Card>

        {/* Quick Stats */}
        {statsLoading ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        ) : (
          <div className="grid grid-cols-3 gap-3">
            <Card className="p-4 text-center">
              <p className="text-2xl font-bold text-primary">{totalCases}</p>
              <p className="text-xs text-muted-foreground">Cases</p>
            </Card>
            <Card className="p-4 text-center">
              <p className="text-2xl font-bold text-success">{totalQueries}</p>
              <p className="text-xs text-muted-foreground">Queries</p>
            </Card>
            <Card className="p-4 text-center">
              <p className="text-2xl font-bold text-warning">{totalSARs}</p>
              <p className="text-xs text-muted-foreground">SARs</p>
            </Card>
          </div>
        )}

        {/* Settings */}
        <section>
          <h3 className="text-sm font-semibold text-muted-foreground mb-3">SETTINGS</h3>
          <Card className="divide-y divide-border">
            <div className="p-4 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Bell className="h-5 w-5 text-muted-foreground" />
                <span className="text-sm font-medium">Push Notifications</span>
              </div>
              <Switch defaultChecked />
            </div>
            <div className="p-4 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Lock className="h-5 w-5 text-muted-foreground" />
                <span className="text-sm font-medium">Biometric Login</span>
              </div>
              <Switch defaultChecked />
            </div>
            <div className="p-4 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Moon className="h-5 w-5 text-muted-foreground" />
                <span className="text-sm font-medium">Dark Mode</span>
              </div>
              <Switch />
            </div>
          </Card>
        </section>

        {/* Actions */}
        <section>
          <h3 className="text-sm font-semibold text-muted-foreground mb-3">ACTIONS</h3>
          <Card className="divide-y divide-border">
            <button className="w-full p-4 flex items-center justify-between hover:bg-muted/50 transition-colors">
              <div className="flex items-center gap-3">
                <Download className="h-5 w-5 text-muted-foreground" />
                <span className="text-sm font-medium">Install App</span>
              </div>
              <ChevronRight className="h-5 w-5 text-muted-foreground" />
            </button>
            <button className="w-full p-4 flex items-center justify-between hover:bg-muted/50 transition-colors">
              <div className="flex items-center gap-3">
                <HelpCircle className="h-5 w-5 text-muted-foreground" />
                <span className="text-sm font-medium">Help & Support</span>
              </div>
              <ChevronRight className="h-5 w-5 text-muted-foreground" />
            </button>
          </Card>
        </section>

        {/* Logout */}
        <Button
          variant="destructive"
          className="w-full"
          size="lg"
          onClick={() => {
            logout();
            navigate("/login", { replace: true });
          }}
        >
          <LogOut className="h-5 w-5 mr-2" />
          Logout
        </Button>

        <p className="text-xs text-center text-muted-foreground">
          Version 1.0.0 • © 2025 Fraud Intelligence Platform
        </p>
      </main>
    </div>
  );
}
