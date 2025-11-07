import { Header } from "@/components/Layout/Header";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Download, Shield, Zap, Wifi } from "lucide-react";
import { useEffect, useState } from "react";

export default function Install() {
  const [deferredPrompt, setDeferredPrompt] = useState<any>(null);
  const [isInstallable, setIsInstallable] = useState(false);

  useEffect(() => {
    const handler = (e: Event) => {
      e.preventDefault();
      setDeferredPrompt(e);
      setIsInstallable(true);
    };

    window.addEventListener("beforeinstallprompt", handler);
    return () => window.removeEventListener("beforeinstallprompt", handler);
  }, []);

  const handleInstall = async () => {
    if (!deferredPrompt) {
      alert("App is already installed or cannot be installed on this device.");
      return;
    }

    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;
    
    if (outcome === "accepted") {
      setDeferredPrompt(null);
      setIsInstallable(false);
    }
  };

  return (
    <div className="min-h-screen bg-background pb-20">
      <Header title="Install App" />
      
      <main className="px-4 py-6 max-w-screen-xl mx-auto space-y-6">
        {/* Hero */}
        <div className="text-center py-8">
          <div className="bg-primary/10 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-4">
            <Shield className="h-10 w-10 text-primary" />
          </div>
          <h1 className="text-2xl font-bold text-foreground mb-2">
            Install Fraud Intelligence
          </h1>
          <p className="text-muted-foreground">
            Get instant access from your home screen
          </p>
        </div>

        {/* Benefits */}
        <div className="space-y-3">
          <Card className="p-4 flex items-start gap-4">
            <div className="bg-success/10 p-2 rounded-lg">
              <Zap className="h-5 w-5 text-success" />
            </div>
            <div>
              <h3 className="font-semibold text-foreground mb-1">Lightning Fast</h3>
              <p className="text-sm text-muted-foreground">
                Launch instantly from your home screen, no app store needed
              </p>
            </div>
          </Card>

          <Card className="p-4 flex items-start gap-4">
            <div className="bg-primary/10 p-2 rounded-lg">
              <Wifi className="h-5 w-5 text-primary" />
            </div>
            <div>
              <h3 className="font-semibold text-foreground mb-1">Works Offline</h3>
              <p className="text-sm text-muted-foreground">
                Access cached cases and data even without internet
              </p>
            </div>
          </Card>

          <Card className="p-4 flex items-start gap-4">
            <div className="bg-warning/10 p-2 rounded-lg">
              <Download className="h-5 w-5 text-warning" />
            </div>
            <div>
              <h3 className="font-semibold text-foreground mb-1">No Downloads</h3>
              <p className="text-sm text-muted-foreground">
                Small footprint, updates automatically in the background
              </p>
            </div>
          </Card>
        </div>

        {/* Install Button */}
        {isInstallable ? (
          <Button
            onClick={handleInstall}
            className="w-full bg-gradient-primary"
            size="lg"
          >
            <Download className="h-5 w-5 mr-2" />
            Install Now
          </Button>
        ) : (
          <Card className="p-4 text-center">
            <p className="text-sm text-muted-foreground mb-2">
              To install this app on your device:
            </p>
            <ol className="text-xs text-muted-foreground text-left space-y-1 max-w-sm mx-auto">
              <li>• <strong>iPhone:</strong> Tap Share → Add to Home Screen</li>
              <li>• <strong>Android:</strong> Tap Menu (⋮) → Install app</li>
              <li>• <strong>Desktop:</strong> Look for install icon in address bar</li>
            </ol>
          </Card>
        )}

        {/* Manual Instructions */}
        <Card className="p-4 bg-muted/30">
          <h3 className="font-semibold text-foreground mb-2 text-sm">Manual Installation</h3>
          <div className="space-y-2 text-xs text-muted-foreground">
            <p><strong>iOS Safari:</strong></p>
            <p>1. Tap the Share button (square with arrow)</p>
            <p>2. Scroll down and tap "Add to Home Screen"</p>
            <p>3. Tap "Add" in the top right</p>
            
            <p className="mt-3"><strong>Android Chrome:</strong></p>
            <p>1. Tap the Menu button (three dots)</p>
            <p>2. Tap "Install app" or "Add to Home screen"</p>
            <p>3. Tap "Install" when prompted</p>
          </div>
        </Card>
      </main>
    </div>
  );
}
