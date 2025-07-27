import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Menu } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import PilotMode from "@/components/dashboard/PilotMode";
import NavigatorMode from "@/components/dashboard/NavigatorMode";
import Sidebar from "@/components/dashboard/Sidebar";
import Profile from "@/components/dashboard/Profile";
import NetWorthCalculator from "@/components/dashboard/NetWorthCalculator";
import AddSpending from "@/components/dashboard/AddSpending";
import Updates from "@/components/dashboard/Updates";
import SubscriptionTracker from "@/components/dashboard/SubscriptionTracker";
import Investments from "@/components/dashboard/Investments";
import Chatbot from "@/components/Chatbot";
import { AnimatePresence, motion } from "framer-motion";

const Dashboard = () => {
  const [activeMode, setActiveMode] = useState("pilot");
  const [sidebarVisible, setSidebarVisible] = useState(false);
  const [showProfile, setShowProfile] = useState(false);
  const [showNetWorthCalculator, setShowNetWorthCalculator] = useState(false);
  const [showAddSpending, setShowAddSpending] = useState(false);
  const [showUpdates, setShowUpdates] = useState(false);
  const [showSubscriptionTracker, setShowSubscriptionTracker] = useState(false);
  const [showInvestments, setShowInvestments] = useState(false);
  const navigate = useNavigate();

  const handleSignOut = () => {
    navigate("/");
  };

  return (
    <div className="min-h-screen bg-gradient-dark">
      {/* Header */}
      <header className="fixed top-0 w-full z-50 border-b border-border bg-background/80 backdrop-blur-lg">
        <div className="flex items-center justify-between p-4">
          <div className="flex items-center gap-2">
            {/* Sidebar Toggle */}
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setSidebarVisible(!sidebarVisible)}
              className="h-10 w-10"
            >
              <Menu className="h-5 w-5" />
            </Button>
            <Link to="/" className="text-2xl font-bold text-primary">
              Fi Compass
            </Link>
          </div>
          {/* Header Actions */}
          <div className="flex items-center gap-4">
            {/* Right side space for future elements */}
          </div>
        </div>
      </header>

      {/* Sidebar */}
      {sidebarVisible && (
        <Sidebar 
          onToggle={() => setSidebarVisible(false)}
          onShowProfile={() => setShowProfile(true)}
          onShowNetWorthCalculator={() => setShowNetWorthCalculator(true)}
          onShowAddSpending={() => setShowAddSpending(true)}
          onShowUpdates={() => setShowUpdates(true)}
          onShowSubscriptionTracker={() => setShowSubscriptionTracker(true)}
          onShowInvestments={() => setShowInvestments(true)}
        />
      )}

      <div className="transition-all duration-300">
        <div className="container mx-auto p-6 mt-16">
          {/* Mode Toggle */}
          <div className="flex items-center justify-center space-x-4 mb-8">
            <span className={`text-lg font-medium transition-colors ${activeMode === "pilot" ? "text-primary" : "text-muted-foreground"}`}>
              Pilot Mode
            </span>
            <Switch 
              checked={activeMode === "navigator"} 
              onCheckedChange={(checked) => setActiveMode(checked ? "navigator" : "pilot")}
              className="data-[state=checked]:bg-blue-500"
            />
            <span className={`text-lg font-medium transition-colors ${activeMode === "navigator" ? "text-primary" : "text-muted-foreground"}`}>
              Navigator Mode
            </span>
          </div>

          {/* Content */}
          <div className="space-y-6 min-h-[60vh]">
            <AnimatePresence mode="wait">
              {activeMode === "pilot" && (
                <motion.div
                  key="pilot"
                  initial={{ opacity: 0, x: -40 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 40 }}
                  transition={{ duration: 0.4, ease: "easeInOut" }}
                >
                  <PilotMode />
                </motion.div>
              )}
              {activeMode === "navigator" && (
                <motion.div
                  key="navigator"
                  initial={{ opacity: 0, x: 40 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -40 }}
                  transition={{ duration: 0.4, ease: "easeInOut" }}
                >
                  <NavigatorMode />
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>

      {/* Profile Modal */}
      {showProfile && (
        <Profile onClose={() => setShowProfile(false)} />
      )}

      {/* Net Worth Calculator Modal */}
      {showNetWorthCalculator && (
        <NetWorthCalculator onClose={() => setShowNetWorthCalculator(false)} />
      )}

      {/* Add Spending Modal */}
      {showAddSpending && (
        <AddSpending onClose={() => setShowAddSpending(false)} />
      )}

      {/* Updates Modal */}
      {showUpdates && (
        <Updates onClose={() => setShowUpdates(false)} />
      )}

      {/* Subscription Tracker Modal */}
      {showSubscriptionTracker && (
        <SubscriptionTracker onClose={() => setShowSubscriptionTracker(false)} />
      )}

      {/* Investments Modal */}
      {showInvestments && (
        <Investments onClose={() => setShowInvestments(false)} />
      )}

      {/* AI Chatbot */}
      <Chatbot buttonPosition="bottom-4 right-4" />

    </div>
  );
};

export default Dashboard;