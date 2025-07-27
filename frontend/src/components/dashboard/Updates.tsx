import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  TrendingUp,
  TrendingDown,
  Home,
  DollarSign,
  AlertTriangle,
  CheckCircle,
  Info,
  Clock,
  ArrowRight,
  Settings,
  X,
  Bell
} from "lucide-react";
import { AnimatePresence, motion } from "framer-motion";

interface Update {
  id: string;
  title: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
  type: 'growth' | 'loss' | 'property' | 'proposal' | 'achievement' | 'alert';
  timestamp: string;
  action?: string;
  value?: string;
  change?: string;
  subtext?: string;
}

interface UpdatesProps {
  onClose: () => void;
}

const Updates = ({ onClose }: UpdatesProps) => {
  const updates: Update[] = [
    {
      id: '1',
      title: 'Portfolio Growth',
      description: 'Your investment portfolio has grown by 12.5% this month',
      priority: 'high',
      type: 'growth',
      timestamp: '2 hours ago',
      value: '+₹45,000',
      change: '+12.5%',
      subtext: 'Check calculations behind'
    },
    {
      id: '2',
      title: 'New Property Listed',
      description: 'A new property matching your criteria is available in Mumbai',
      priority: 'medium',
      type: 'property',
      timestamp: '4 hours ago',
      action: 'View Details',
      subtext: 'Read more about this property'
    },
    {
      id: '3',
      title: 'Market Alert',
      description: 'Gold prices have dropped 3.2% - consider rebalancing',
      priority: 'high',
      type: 'alert',
      timestamp: '6 hours ago',
      value: '-₹8,500',
      change: '-3.2%',
      subtext: 'View market analysis'
    },
    {
      id: '4',
      title: 'Goal Achievement',
      description: 'You\'ve reached 75% of your emergency fund goal',
      priority: 'medium',
      type: 'achievement',
      timestamp: '1 day ago',
      value: '₹75,000',
      change: '75%',
      subtext: 'Track your progress'
    },
    {
      id: '5',
      title: 'Investment Proposal',
      description: 'AI suggests increasing your equity allocation by 5%',
      priority: 'low',
      type: 'proposal',
      timestamp: '2 days ago',
      action: 'Review Proposal',
      subtext: 'See AI reasoning'
    },
    {
      id: '6',
      title: 'Expense Alert',
      description: 'Your dining out expenses are 40% higher than usual',
      priority: 'medium',
      type: 'alert',
      timestamp: '3 days ago',
      value: '₹12,500',
      change: '+40%',
      subtext: 'View detailed breakdown'
    }
  ];

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'border-l-destructive';
      case 'medium':
        return 'border-l-warning';
      case 'low':
        return 'border-l-success';
      default:
        return 'border-l-primary';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'growth':
        return TrendingUp;
      case 'loss':
        return TrendingDown;
      case 'property':
        return Home;
      case 'proposal':
        return DollarSign;
      case 'achievement':
        return CheckCircle;
      case 'alert':
        return AlertTriangle;
      default:
        return Info;
    }
  };

  const getPriorityText = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'High Priority';
      case 'medium':
        return 'Medium Priority';
      case 'low':
        return 'Low Priority';
      default:
        return 'Normal Priority';
    }
  };

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.95, opacity: 0 }}
          transition={{ duration: 0.2 }}
          className="w-full max-w-3xl bg-background rounded-2xl border shadow-2xl"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Modern Header with Gradient */}
          <div className="relative p-6 border-b border-border bg-gradient-to-r from-primary/10 via-primary/5 to-transparent">
            <div className="absolute inset-0 bg-gradient-to-r from-primary/5 to-transparent opacity-50 rounded-t-2xl"></div>
            <div className="relative flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="p-3 bg-gradient-to-br from-primary to-primary/80 rounded-xl shadow-lg">
                  <Bell className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
                    Updates & Notifications
                  </h2>
                  <p className="text-sm text-muted-foreground">Important notifications and insights</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <Badge variant="outline" className="bg-primary/10 text-primary border-primary">
                  <Clock className="w-3 h-3 mr-1" />
                  {updates.length} Updates
                </Badge>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={onClose}
                  className="h-8 w-8 hover:bg-primary/10"
                >
                  <X className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </div>

                                {/* Content */}
                      <div className="p-3 max-h-[70vh] overflow-y-auto">
                                    <div className="space-y-3">
              {updates.map((update) => {
                const Icon = getTypeIcon(update.type);
                return (
                  <div 
                    key={update.id} 
                    className="relative overflow-hidden rounded-xl bg-gradient-to-br from-background via-background to-primary/5 border border-primary/20 p-4 cursor-pointer hover:shadow-md transition-all duration-200 hover:scale-[1.02]"
                    onClick={() => window.postMessage('openChatbot', '*')}
                  >
                    <div className="absolute top-0 right-0 w-12 h-12 bg-primary/5 rounded-full -translate-y-6 translate-x-6"></div>
                    <div className="relative flex items-start gap-4">
                      {/* Icon */}
                      <div className="p-2 rounded-lg bg-background/50">
                        <Icon className="w-5 h-5" />
                      </div>

                      {/* Content */}
                      <div className="flex-1">
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex-1">
                            <h3 className="font-semibold text-lg">{update.title}</h3>
                            <p className="text-sm text-muted-foreground mt-1">{update.description}</p>
                          </div>
                          
                          {/* Value and Change */}
                          {update.value && (
                            <div className="text-right">
                              <p className="font-bold text-lg">{update.value}</p>
                              {update.change && (
                                <p className="text-sm text-muted-foreground">{update.change}</p>
                              )}
                            </div>
                          )}
                        </div>

                        {/* Bottom Row */}
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <Badge variant="secondary" className="text-xs">
                              {getPriorityText(update.priority)}
                            </Badge>
                            <span className="text-xs text-muted-foreground">{update.timestamp}</span>
                          </div>
                          
                          {update.action && (
                            <Button 
                              variant="ghost" 
                              size="sm" 
                              className="text-xs hover:bg-primary/10"
                              onClick={(e) => {
                                e.stopPropagation();
                                console.log(`Action clicked: ${update.action}`);
                              }}
                            >
                              {update.action}
                              <ArrowRight className="w-3 h-3 ml-1" />
                            </Button>
                          )}
                        </div>

                        {/* Subtext */}
                        {update.subtext && (
                          <div className="mt-2 pt-2 border-t border-border/50">
                            <p className="text-xs text-muted-foreground italic">
                              {update.subtext}
                            </p>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Quick Actions */}
            <div className="relative overflow-hidden rounded-xl bg-gradient-to-br from-warning/10 via-warning/5 to-transparent border border-warning/20 p-6 mt-6">
              <div className="absolute top-0 right-0 w-20 h-20 bg-warning/5 rounded-full -translate-y-10 translate-x-10"></div>
              <div className="relative">
                <h3 className="text-lg font-semibold text-warning mb-4 flex items-center gap-2">
                  <div className="p-1.5 bg-warning/10 rounded-lg">
                    <Settings className="w-4 h-4 text-warning" />
                  </div>
                  Quick Actions
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <Button variant="outline" className="flex items-center gap-2 border-primary/30 hover:bg-primary/10">
                    <Bell className="w-4 h-4" />
                    Mark All Read
                  </Button>
                  <Button variant="outline" className="flex items-center gap-2 border-primary/30 hover:bg-primary/10">
                    <Settings className="w-4 h-4" />
                    Notification Settings
                  </Button>
                  <Button variant="outline" className="flex items-center gap-2 border-primary/30 hover:bg-primary/10">
                    <Info className="w-4 h-4" />
                    View Archive
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default Updates; 