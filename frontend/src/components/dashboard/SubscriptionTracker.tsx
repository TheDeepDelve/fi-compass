import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { CreditCard, CheckCircle, AlertTriangle, XCircle, X, Plus, TrendingUp, DollarSign } from "lucide-react";
import { AnimatePresence, motion } from "framer-motion";

interface SubscriptionTrackerProps {
  onClose: () => void;
}

const dummySubscriptions = [
  {
    name: 'Spotify',
    status: 'Active',
    lastUsed: 'Today',
    cost: '₹199/mo',
    icon: <CreditCard className="w-5 h-5 text-green-500" />,
  },
  {
    name: 'Netflix',
    status: 'Inactive',
    lastUsed: '2 weeks ago',
    cost: '₹649/mo',
    icon: <CreditCard className="w-5 h-5 text-red-500" />,
  },
  {
    name: 'Disney+ Hotstar',
    status: 'Active',
    lastUsed: 'Yesterday',
    cost: '₹299/mo',
    icon: <CreditCard className="w-5 h-5 text-blue-500" />,
  },
  {
    name: 'Apple Music',
    status: 'Active',
    lastUsed: '3 days ago',
    cost: '₹99/mo',
    icon: <CreditCard className="w-5 h-5 text-pink-500" />,
  },
];

const SubscriptionTracker = ({ onClose }: SubscriptionTrackerProps) => {
  const [subscriptions, setSubscriptions] = useState(dummySubscriptions);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newSubscription, setNewSubscription] = useState({
    name: '',
    cost: '',
    status: 'Active'
  });

  const totalMonthlyCost = subscriptions
    .filter(sub => sub.status === 'Active')
    .reduce((sum, sub) => sum + parseInt(sub.cost.replace('₹', '').replace('/mo', '')), 0);

  const activeSubscriptions = subscriptions.filter(sub => sub.status === 'Active').length;

  const handleAddSubscription = () => {
    if (newSubscription.name && newSubscription.cost) {
      const newSub = {
        name: newSubscription.name,
        icon: <span>🎵</span>,
        status: newSubscription.status as 'Active' | 'Inactive',
        lastUsed: 'Today',
        cost: `₹${newSubscription.cost}/mo`
      };
      setSubscriptions([...subscriptions, newSub]);
      setNewSubscription({ name: '', cost: '', status: 'Active' });
      setShowAddForm(false);
    }
  };

  const handleCancelInactive = () => {
    setSubscriptions(subscriptions.filter(sub => sub.status === 'Active'));
  };

  const handleCancelAdd = () => {
    setNewSubscription({ name: '', cost: '', status: 'Active' });
    setShowAddForm(false);
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
          className="w-full max-w-2xl bg-background rounded-2xl border shadow-2xl"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Modern Header with Gradient */}
          <div className="relative p-6 border-b border-border bg-gradient-to-r from-primary/10 via-primary/5 to-transparent">
            <div className="absolute inset-0 bg-gradient-to-r from-primary/5 to-transparent opacity-50 rounded-t-2xl"></div>
            <div className="relative flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="p-3 bg-gradient-to-br from-primary to-primary/80 rounded-xl shadow-lg">
                  <CreditCard className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
                    Subscription Tracker
                  </h2>
                  <p className="text-sm text-muted-foreground">Monitor your active and inactive subscriptions</p>
                </div>
              </div>
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

          {/* Content */}
          <div className="p-2">
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-2 mb-3">
                              <div className="relative overflow-hidden rounded-lg bg-gradient-to-br from-success/10 via-success/5 to-transparent border border-success/20 p-3">
                  <div className="absolute top-0 right-0 w-12 h-12 bg-success/5 rounded-full -translate-y-6 translate-x-6"></div>
                  <div className="relative">
                    <div className="flex items-center gap-2 mb-1">
                      <div className="p-1 bg-success/20 rounded-lg">
                        <CheckCircle className="w-3 h-3 text-success" />
                      </div>
                      <span className="text-xs font-medium text-success">Active Subscriptions</span>
                    </div>
                    <div className="text-xl font-bold text-success">{activeSubscriptions}</div>
                  </div>
                </div>

              <div className="relative overflow-hidden rounded-lg bg-gradient-to-br from-info/10 via-info/5 to-transparent border border-info/20 p-3">
                <div className="absolute top-0 right-0 w-10 h-10 bg-info/5 rounded-full -translate-y-5 translate-x-5"></div>
                <div className="relative">
                  <div className="flex items-center gap-2 mb-1">
                    <div className="p-1 bg-info/20 rounded-lg">
                      <DollarSign className="w-3 h-3 text-info" />
                    </div>
                    <span className="text-xs font-medium text-info">Monthly Cost</span>
                  </div>
                  <div className="text-xl font-bold text-info">₹{totalMonthlyCost}</div>
                </div>
              </div>

              <div className="relative overflow-hidden rounded-lg bg-gradient-to-br from-warning/10 via-warning/5 to-transparent border border-warning/20 p-3">
                <div className="absolute top-0 right-0 w-8 h-8 bg-warning/5 rounded-full -translate-y-4 translate-x-4"></div>
                <div className="relative">
                  <div className="flex items-center gap-2 mb-1">
                    <div className="p-1 bg-warning/20 rounded-lg">
                      <TrendingUp className="w-3 h-3 text-warning" />
                    </div>
                    <span className="text-xs font-medium text-warning">Total Services</span>
                  </div>
                  <div className="text-xl font-bold text-warning">{subscriptions.length}</div>
                </div>
              </div>
            </div>

                                                            {/* Subscriptions Table */}
                        <div className="relative overflow-hidden rounded-lg bg-gradient-to-br from-background via-background to-primary/5 border border-primary/20 p-3">
                          <div className="absolute top-0 right-0 w-16 h-16 bg-primary/5 rounded-full -translate-y-8 translate-x-8"></div>
                          <div className="relative">
                            <div className="flex items-center justify-between mb-3">
                              <h3 className="text-base font-semibold flex items-center gap-2">
                                <div className="p-1 bg-primary/10 rounded-lg">
                                  <CreditCard className="w-3 h-3 text-primary" />
                                </div>
                                Tracked Subscriptions
                              </h3>
                              <Button 
                                className="bg-primary hover:bg-primary/80 text-xs h-8"
                                onClick={() => setShowAddForm(true)}
                              >
                                <Plus className="w-3 h-3 mr-1" />
                                Add Subscription
                              </Button>
                            </div>
                
                                            <div className="overflow-x-auto max-h-48 overflow-y-auto">
                              <table className="min-w-full divide-y divide-border">
                    <thead>
                      <tr>
                        <th className="px-4 py-2 text-left text-xs font-medium text-muted-foreground">Service</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-muted-foreground">Status</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-muted-foreground">Last Used</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-muted-foreground">Cost</th>
                        <th className="px-4 py-2"></th>
                      </tr>
                    </thead>
                                                    <tbody className="bg-background/50 divide-y divide-border">
                                  {subscriptions.map((sub, idx) => (
                                    <tr key={idx} className="hover:bg-background/80 transition-colors">
                                      <td className="px-3 py-2 flex items-center gap-2 font-medium text-sm">
                                        {sub.icon}
                                        {sub.name}
                                      </td>
                                      <td className="px-3 py-2">
                                        {sub.status === 'Active' ? (
                                          <Badge variant="secondary" className="text-xs bg-success/20 text-success border-success/30">Active</Badge>
                                        ) : (
                                          <Badge variant="destructive" className="text-xs">Inactive</Badge>
                                        )}
                                      </td>
                                      <td className="px-3 py-2 text-xs text-muted-foreground">{sub.lastUsed}</td>
                                      <td className="px-3 py-2 text-xs font-medium">{sub.cost}</td>
                                      <td className="px-3 py-2">
                                        <Button size="sm" variant="outline" className="text-xs border-primary/30 hover:bg-primary/10 h-6">Manage</Button>
                                      </td>
                                    </tr>
                                  ))}
                                </tbody>
                  </table>
                </div>
              </div>
            </div>

                                                            {/* Quick Actions */}
                        <div className="relative overflow-hidden rounded-lg bg-gradient-to-br from-warning/10 via-warning/5 to-transparent border border-warning/20 p-3 mt-3">
                          <div className="absolute top-0 right-0 w-12 h-12 bg-warning/5 rounded-full -translate-y-6 translate-x-6"></div>
                          <div className="relative">
                            <h3 className="text-base font-semibold text-warning mb-3 flex items-center gap-2">
                              <div className="p-1 bg-warning/10 rounded-lg">
                                <TrendingUp className="w-3 h-3 text-warning" />
                              </div>
                              Quick Actions
                            </h3>
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                                                <Button 
                                variant="outline" 
                                className="flex items-center gap-1 border-primary/30 hover:bg-primary/10 text-xs h-8"
                                onClick={() => setShowAddForm(true)}
                              >
                                <Plus className="w-3 h-3" />
                                Add New Subscription
                              </Button>
                              <Button variant="outline" className="flex items-center gap-1 border-primary/30 hover:bg-primary/10 text-xs h-8">
                                <DollarSign className="w-3 h-3" />
                                Cost Analysis
                              </Button>
                              <Button 
                                variant="outline" 
                                className="flex items-center gap-1 border-primary/30 hover:bg-primary/10 text-xs h-8"
                                onClick={handleCancelInactive}
                              >
                                <AlertTriangle className="w-3 h-3" />
                                Cancel Inactive
                              </Button>
                </div>
              </div>
            </div>
          </div>

          {/* Add New Subscription Modal */}
          {showAddForm && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/50 flex items-center justify-center z-[60] p-4"
              onClick={handleCancelAdd}
            >
              <motion.div
                initial={{ scale: 0.95, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.95, opacity: 0 }}
                transition={{ duration: 0.2 }}
                className="w-full max-w-md bg-background rounded-xl border shadow-2xl"
                onClick={(e) => e.stopPropagation()}
              >
                <div className="relative p-4 border-b border-border bg-gradient-to-r from-primary/10 via-primary/5 to-transparent">
                  <div className="absolute inset-0 bg-gradient-to-r from-primary/5 to-transparent opacity-50 rounded-t-xl"></div>
                  <div className="relative flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-gradient-to-br from-primary to-primary/80 rounded-lg shadow-lg">
                        <Plus className="w-5 h-5 text-white" />
                      </div>
                      <div>
                        <h3 className="text-lg font-bold bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
                          Add New Subscription
                        </h3>
                        <p className="text-sm text-muted-foreground">Add a new subscription to track</p>
                      </div>
                    </div>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={handleCancelAdd}
                      className="h-8 w-8 hover:bg-primary/10"
                    >
                      <X className="w-4 h-4" />
                    </Button>
                  </div>
                </div>

                <div className="p-4 space-y-4">
                  <div>
                    <label className="text-sm font-medium mb-2 block">Service Name</label>
                    <Input
                      type="text"
                      placeholder="e.g., Netflix, Spotify, Disney+"
                      value={newSubscription.name}
                      onChange={(e) => setNewSubscription({ ...newSubscription, name: e.target.value })}
                      className="w-full"
                    />
                  </div>

                  <div>
                    <label className="text-sm font-medium mb-2 block">Monthly Cost (₹)</label>
                    <Input
                      type="number"
                      placeholder="Enter monthly cost"
                      value={newSubscription.cost}
                      onChange={(e) => setNewSubscription({ ...newSubscription, cost: e.target.value })}
                      className="w-full"
                    />
                  </div>

                  <div>
                    <label className="text-sm font-medium mb-2 block">Status</label>
                    <select
                      value={newSubscription.status}
                      onChange={(e) => setNewSubscription({ ...newSubscription, status: e.target.value })}
                      className="w-full p-2 border border-border rounded-md bg-background text-foreground"
                    >
                      <option value="Active">Active</option>
                      <option value="Inactive">Inactive</option>
                    </select>
                  </div>

                  <div className="flex gap-2 pt-2">
                    <Button
                      onClick={handleAddSubscription}
                      className="flex-1 bg-primary hover:bg-primary/80"
                      disabled={!newSubscription.name || !newSubscription.cost}
                    >
                      <Plus className="w-4 h-4 mr-2" />
                      Add Subscription
                    </Button>
                    <Button
                      variant="outline"
                      onClick={handleCancelAdd}
                      className="flex-1"
                    >
                      Cancel
                    </Button>
                  </div>
                </div>
              </motion.div>
            </motion.div>
          )}
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default SubscriptionTracker; 