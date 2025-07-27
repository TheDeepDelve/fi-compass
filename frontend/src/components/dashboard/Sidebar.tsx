import React, { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  DollarSign,
  BarChart3,
  Target,
  Settings,
  HelpCircle,
  ChevronLeft,
  ChevronRight,
  Home,
  TrendingUp,
  PiggyBank,
  Shield,
  BookOpen,
  X,
  CreditCard,
  User,
  LogOut,
  Receipt
} from "lucide-react";

import { AnimatePresence, motion } from "framer-motion";

interface SidebarProps {
  onToggle: () => void;
  onShowProfile: () => void;
  onShowNetWorthCalculator: () => void;
  onShowAddSpending: () => void;
  onShowUpdates: () => void;
  onShowSubscriptionTracker: () => void;
  onShowInvestments: () => void;
}

const Sidebar = ({ onToggle, onShowProfile, onShowNetWorthCalculator, onShowAddSpending, onShowUpdates, onShowSubscriptionTracker, onShowInvestments }: SidebarProps) => {

  const menuItems = [
                     {
                   id: 'profile',
                   title: 'Profile',
                   description: 'Manage your account',
                   icon: User,
                   action: () => {
                     onToggle(); // Close the sidebar first
                     // Add a small delay to ensure sidebar closes before popup opens
                     setTimeout(() => {
                       onShowProfile();
                     }, 150);
                   }
                 },
    {
      id: 'net-worth',
      title: 'Know Your Worth',
      description: 'Track your net worth',
      icon: DollarSign,
      badge: 'New',
      action: () => {
        onToggle();
        setTimeout(() => {
          onShowNetWorthCalculator();
        }, 150);
      }
    },
    {
      id: 'add-spending',
      title: 'Add Spending',
      description: 'Track daily expenses',
      icon: Receipt,
      badge: 'New',
      action: () => {
        onToggle();
        setTimeout(() => {
          onShowAddSpending();
        }, 150);
      }
    },
    {
      id: 'updates',
      title: 'Updates',
      description: 'Important notifications',
      icon: BarChart3,
      action: () => {
        onToggle();
        setTimeout(() => {
          onShowUpdates();
        }, 150);
      }
    },
    {
      id: 'subscriptions',
      title: 'Subscriptions',
      description: 'Track your subscriptions',
      icon: CreditCard,
      action: () => {
        onToggle();
        setTimeout(() => {
          onShowSubscriptionTracker();
        }, 150);
      }
    },
    {
      id: 'investments',
      title: 'Investments',
      description: 'Portfolio management',
      icon: TrendingUp,
      action: () => {
        onToggle();
        setTimeout(() => {
          onShowInvestments();
        }, 150);
      }
    }
  ];

  return (
    <>
      {/* Backdrop Overlay */}
      <AnimatePresence>
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.2 }}
          className="fixed inset-0 bg-black/20 backdrop-blur-[2px] z-30"
          onClick={onToggle}
        />
      </AnimatePresence>

      {/* Sidebar */}
      <AnimatePresence>
        <motion.div
          initial={{ x: -100, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          exit={{ x: -100, opacity: 0 }}
          transition={{ duration: 0.3, ease: "easeInOut" }}
          className="fixed left-0 top-16 h-[calc(100vh-4rem)] w-64 bg-background border-r border-border transition-all duration-300 z-40"
          onClick={(e) => e.stopPropagation()}
        >
            {/* Close Button */}
            <div className="flex justify-end p-2 border-b border-border">
              <Button
                variant="ghost"
                size="sm"
                onClick={onToggle}
                className="h-8 w-8 p-0"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>

            {/* Menu Items */}
            <div className="p-2 space-y-2">
              {menuItems.map((item) => {
                const Icon = item.icon;
                return (
                  <Button
                    key={item.id}
                    variant="ghost"
                                 className="w-full justify-start h-auto p-3 flex-row space-x-3"
                    onClick={item.action}
                  >
                    <div className="relative">
                      <Icon className="h-5 w-5" />
                      {item.badge && (
                        <Badge 
                          variant="secondary" 
                          className="absolute -top-2 -right-2 text-xs px-1"
                        >
                          {item.badge}
                        </Badge>
                      )}
                    </div>
                                 <div className="flex-1 text-left">
                   <div className="font-medium">{item.title}</div>
                   <div className="text-xs text-muted-foreground">{item.description}</div>
                 </div>
              </Button>
            );
          })}
        </div>

                 {/* Bottom Section */}
         <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-border">
           <div className="space-y-2">
             <Button variant="ghost" className="w-full justify-start" size="sm">
               <Settings className="h-4 w-4 mr-2" />
               Settings
             </Button>
             <Button variant="ghost" className="w-full justify-start" size="sm">
               <HelpCircle className="h-4 w-4 mr-2" />
               Help
             </Button>
           </div>
         </div>
      </motion.div>
      </AnimatePresence>


    </>
  );
};

export default Sidebar; 