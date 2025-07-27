import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { Badge } from "@/components/ui/badge";
import { 
  Target,
  Calendar,
  TrendingUp,
  DollarSign,
  Home,
  Car,
  GraduationCap,
  Plane,
  Settings,
  BarChart3
} from "lucide-react";

const NavigatorMode = () => {
  const [selectedGoal, setSelectedGoal] = useState<string | null>(null);
  const [investmentAmount, setInvestmentAmount] = useState([5000]);
  const [riskAppetite, setRiskAppetite] = useState([60]);
  const [timeline, setTimeline] = useState([36]);

  const goals = [
    {
      id: "house",
      title: "Buy House",
      target: "₹50,00,000",
      current: "₹8,50,000",
      progress: 17,
      timeline: "5 years",
      icon: Home,
      status: "on-track",
      color: "bg-success/10 border-success"
    },
    {
      id: "car",
      title: "Car Purchase",
      target: "₹10,00,000",
      current: "₹2,50,000",
      progress: 25,
      timeline: "3 years",
      icon: Car,
      status: "behind",
      color: "bg-warning/10 border-warning"
    },
    {
      id: "education",
      title: "Child's Education",
      target: "₹25,00,000",
      current: "₹3,00,000",
      progress: 12,
      timeline: "15 years",
      icon: GraduationCap,
      status: "on-track",
      color: "bg-info/10 border-info"
    },
    {
      id: "vacation",
      title: "Europe Trip",
      target: "₹3,00,000",
      current: "₹75,000",
      progress: 25,
      timeline: "1 year",
      icon: Plane,
      status: "ahead",
      color: "bg-primary/10 border-primary"
    }
  ];

  const tradeOffPaths = [
    {
      type: "Optimizer",
      description: "I've identified you spend an average of ₹7,000/month on dining out. Reducing this by ₹4,000/month will get you to your goal.",
      impact: "₹48,000/year saved",
      effort: "Medium"
    },
    {
      type: "Investor", 
      description: "Shifting your goal's investment portfolio from a 60/40 to a 40/60 debt-to-equity split could get you there, but with higher risk.",
      impact: "12-15% higher returns",
      effort: "Low"
    },
    {
      type: "Side Hustle",
      description: "You would need to generate an additional income of ~₹4,000/month to reach your goal.",
      impact: "₹48,000/year income",
      effort: "High"
    }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-foreground">Navigator Mode</h2>
          <p className="text-muted-foreground">Plan, dream, and simulate your financial future</p>
        </div>
      </div>
      {/* Goal Timeline */}
      <Card className="finance-card">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="w-5 h-5" />
            Your Goal Timeline
          </CardTitle>
          <CardDescription>
            Track progress and visualize your path to financial goals
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {goals.map((goal) => {
              const Icon = goal.icon;
              return (
                <Card 
                  key={goal.id} 
                  className={`p-4 cursor-pointer transition-all hover:scale-105 ${
                    selectedGoal === goal.id ? 'ring-2 ring-primary' : ''
                  } ${goal.color}`}
                  onClick={() => setSelectedGoal(goal.id)}
                >
                  <div className="flex items-start gap-3">
                    <Icon className="w-6 h-6 text-primary mt-1" />
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-semibold">{goal.title}</h4>
                        <Badge variant={
                          goal.status === 'on-track' ? 'default' :
                          goal.status === 'ahead' ? 'default' : 'secondary'
                        }>
                          {goal.status}
                        </Badge>
                      </div>
                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span>{goal.current}</span>
                          <span>{goal.target}</span>
                        </div>
                        <div className="w-full bg-muted rounded-full h-2">
                          <div 
                            className="bg-primary h-2 rounded-full transition-all" 
                            style={{ width: `${goal.progress}%` }}
                          ></div>
                        </div>
                        <div className="flex justify-between text-xs text-muted-foreground">
                          <span>{goal.progress}% complete</span>
                          <span>{goal.timeline} left</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </Card>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Interactive Simulation Engine */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="finance-card">
          <CardHeader>
            <CardTitle>Goal Simulator</CardTitle>
            <CardDescription>
              Adjust parameters to see how they affect your goals
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Monthly Investment */}
            <div className="space-y-2">
              <Label>Monthly Investment: ₹{investmentAmount[0].toLocaleString()}</Label>
              <Slider
                value={investmentAmount}
                onValueChange={setInvestmentAmount}
                max={50000}
                min={1000}
                step={500}
                className="w-full"
              />
            </div>

            {/* Risk Appetite */}
            <div className="space-y-2">
              <Label>Risk Appetite: {riskAppetite[0]}% Equity</Label>
              <Slider
                value={riskAppetite}
                onValueChange={setRiskAppetite}
                max={100}
                min={0}
                step={10}
                className="w-full"
              />
            </div>

            {/* Timeline */}
            <div className="space-y-2">
              <Label>Timeline: {timeline[0]} months</Label>
              <Slider
                value={timeline}
                onValueChange={setTimeline}
                max={240}
                min={12}
                step={6}
                className="w-full"
              />
            </div>

            <Button variant="hero" className="w-full">
              <BarChart3 className="w-4 h-4 mr-2" />
              Update Projections
            </Button>
          </CardContent>
        </Card>

        {/* Projection Results */}
        <Card className="finance-card">
          <CardHeader>
            <CardTitle>Projection Results</CardTitle>
            <CardDescription>
              Based on your current settings
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="p-4 bg-primary/5 rounded-lg border border-primary/20">
                <h4 className="font-semibold text-primary mb-2">Expected Value</h4>
                <p className="text-2xl font-bold">₹{(investmentAmount[0] * timeline[0] * (1 + riskAppetite[0]/1000)).toLocaleString()}</p>
                <p className="text-sm text-muted-foreground">
                  With {riskAppetite[0]}% equity allocation over {timeline[0]} months
                </p>
              </div>

              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Total Investment</span>
                  <span className="font-semibold">₹{(investmentAmount[0] * timeline[0]).toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Expected Returns</span>
                  <span className="font-semibold text-success">
                    ₹{(investmentAmount[0] * timeline[0] * riskAppetite[0]/1000).toLocaleString()}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Risk Level</span>
                  <Badge variant={riskAppetite[0] > 70 ? "destructive" : riskAppetite[0] > 40 ? "default" : "secondary"}>
                    {riskAppetite[0] > 70 ? "High" : riskAppetite[0] > 40 ? "Medium" : "Low"}
                  </Badge>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Trade-off Engine */}
      {selectedGoal && (
        <Card className="finance-card border-warning bg-warning/5">
          <CardHeader>
            <CardTitle className="text-warning">Trade-off Analysis</CardTitle>
            <CardDescription>
              You're ₹1.5 Lakh short of your car purchase goal. Here are your options:
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {tradeOffPaths.map((path, index) => (
                <Card key={index} className="p-4 bg-background/50">
                  <h4 className="font-semibold text-primary mb-2">The '{path.type}' Path</h4>
                  <p className="text-sm text-muted-foreground mb-3">{path.description}</p>
                  <div className="space-y-2 text-xs">
                    <div className="flex justify-between">
                      <span>Impact:</span>
                      <span className="font-semibold">{path.impact}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Effort:</span>
                      <Badge variant="outline">
                        {path.effort}
                      </Badge>
                    </div>
                  </div>
                  <Button variant="outline" size="sm" className="w-full mt-3">
                    Learn More
                  </Button>
                </Card>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default NavigatorMode;