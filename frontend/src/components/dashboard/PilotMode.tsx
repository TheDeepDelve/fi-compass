import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  AlertTriangle, 
  CreditCard, 
  TrendingUp, 
  Target, 
  Eye,
  CheckCircle,
  Calendar,
  DollarSign
} from "lucide-react";
import FinanceCharts from "./FinanceCharts";

const PilotMode = () => {
  const insightCards = [
    {
      type: "alert",
      priority: "high",
      icon: AlertTriangle,
      title: "High-Interest Alert",
      description: "Your credit card balance is ₹45,000 at 36% APR while you have ₹60,000 in savings. Paying it off could save you ~₹1,200 in interest next month.",
      actions: ["Show me the math", "Simulate Impact in Navigator"],
      color: "border-destructive bg-destructive/5"
    },
    {
      type: "optimization",
      priority: "medium",
      icon: CreditCard,
      title: "Subscription Check",
      description: "We've noticed you haven't used your Disney+ Hotstar account in 6 weeks. Cancelling it could save ₹1,499 this year.",
      actions: ["Remind me in 1 week", "Mark as 'Keep'"],
      color: "border-warning bg-warning/5"
    },
    {
      type: "spending",
      priority: "medium",
      icon: TrendingUp,
      title: "Unusual Spending",
      description: "Your 'Dining Out' spending this month is ₹8,500, which is 40% higher than your 6-month average. Just a heads-up!",
      actions: ["View Transactions", "This was expected"],
      color: "border-info bg-info/5"
    },
    {
      type: "achievement",
      priority: "positive",
      icon: Target,
      title: "Milestone Unlocked!",
      description: "You've successfully saved for 3 consecutive months towards your 'Europe Trip' goal. You're now 25% of the way there!",
      actions: ["View Goal Progress"],
      color: "border-success bg-success/5"
    }
  ];

  const quickStats = [
    {
      title: "Current Wealth",
      value: "₹3.9K",
      change: "+₹240",
      trend: "up",
      icon: DollarSign
    },
    {
      title: "Monthly Savings",
      value: "₹12,500",
      change: "+15%",
      trend: "up", 
      icon: TrendingUp
    },
    {
      title: "Active Goals",
      value: "3",
      change: "1 new",
      trend: "neutral",
      icon: Target
    },
    {
      title: "Credit Score",
      value: "742",
      change: "+8",
      trend: "up",
      icon: CheckCircle
    }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-foreground">Pilot Mode</h2>
          <p className="text-muted-foreground">AI-powered insights tailored for you</p>
        </div>
        <Badge variant="outline" className="bg-primary/10 text-primary border-primary">
          <Eye className="w-3 h-3 mr-1" />
          Veda AI Active
        </Badge>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {quickStats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <Card key={index} className="finance-card">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">{stat.title}</p>
                    <p className="text-xl font-bold">{stat.value}</p>
                    <p className={`text-xs ${
                      stat.trend === 'up' ? 'text-success' : 
                      stat.trend === 'down' ? 'text-destructive' : 'text-muted-foreground'
                    }`}>
                      {stat.change}
                    </p>
                  </div>
                  <Icon className="w-8 h-8 text-primary opacity-60" />
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>
      {/* Financial Charts */}
      <FinanceCharts />
      {/* AI Insight Cards */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Today's Insights</h3>
        {Array.from({ length: Math.ceil(insightCards.length / 2) }).map((_, pairIdx) => (
          <Card key={pairIdx} className="finance-card border-border bg-background/60">
            <CardContent className="flex flex-col md:flex-row gap-4 p-4">
              {[0, 1].map((offset) => {
                const cardIdx = pairIdx * 2 + offset;
                if (cardIdx >= insightCards.length) return null;
                const card = insightCards[cardIdx];
                const Icon = card.icon;
                return (
                  <Card key={cardIdx} className={`flex-1 ${card.color} shadow-none border`}>
                    <CardHeader className="pb-3">
                      <div className="flex items-start gap-3">
                        <div className="p-2 rounded-lg bg-background/50">
                          <Icon className="w-5 h-5" />
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <CardTitle className="text-lg">{card.title}</CardTitle>
                            <Badge variant="secondary">
                              {card.priority}
                            </Badge>
                          </div>
                          <CardDescription className="text-foreground/80">
                            {card.description}
                          </CardDescription>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="flex flex-wrap gap-2">
                        {card.actions.map((action, actionIndex) => (
                          <Button 
                            key={actionIndex} 
                            variant="outline" 
                            size="sm"
                            className="text-xs"
                          >
                            {action}
                          </Button>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Weekly Summary */}
      <Card className="finance-card">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calendar className="w-5 h-5" />
            This Week's Summary
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4 bg-background/50 rounded-lg">
              <p className="text-2xl font-bold text-success">₹2,340</p>
              <p className="text-sm text-muted-foreground">Money Saved</p>
            </div>
            <div className="text-center p-4 bg-background/50 rounded-lg">
              <p className="text-2xl font-bold text-primary">5</p>
              <p className="text-sm text-muted-foreground">Smart Actions Taken</p>
            </div>
            <div className="text-center p-4 bg-background/50 rounded-lg">
              <p className="text-2xl font-bold text-info">12</p>
              <p className="text-sm text-muted-foreground">Insights Provided</p>
            </div>
          </div>
        </CardContent>
      </Card>

      
    </div>
  );
};

export default PilotMode;