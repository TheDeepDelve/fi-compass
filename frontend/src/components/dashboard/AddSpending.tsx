import React, { useState } from 'react';
import {
  Chart as ChartJS,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
} from 'chart.js';
import { Pie, Bar } from 'react-chartjs-2';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { 
  DollarSign,
  ShoppingCart,
  Utensils,
  Car,
  Home,
  Plane,
  GraduationCap,
  Heart,
  Gamepad2,
  Coffee,
  X,
  Plus,
  Calendar,
  TrendingUp,
  Receipt
} from "lucide-react";
import { AnimatePresence, motion } from "framer-motion";

ChartJS.register(
  ArcElement,
  Title,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement
);

interface SpendingEntry {
  id: string;
  amount: number;
  category: string;
  description: string;
  date: string;
  time: string;
}

interface SpendingCategory {
  id: string;
  name: string;
  icon: React.ComponentType<any>;
  color: string;
  total: number;
}

const AddSpending = ({ onClose }: { onClose: () => void }) => {
  const [spendingEntries, setSpendingEntries] = useState<SpendingEntry[]>([
    {
      id: '1',
      amount: 2500,
      category: 'food',
      description: 'Grocery shopping at Reliance Fresh',
      date: '2024-01-15',
      time: '14:30'
    },
    {
      id: '2',
      amount: 800,
      category: 'transport',
      description: 'Fuel for car',
      date: '2024-01-15',
      time: '09:15'
    },
    {
      id: '3',
      amount: 1500,
      category: 'shopping',
      description: 'Clothes from Myntra',
      date: '2024-01-14',
      time: '16:45'
    }
  ]);

  const [showAddForm, setShowAddForm] = useState(false);
  const [newEntry, setNewEntry] = useState<Omit<SpendingEntry, 'id'>>({
    amount: 0,
    category: '',
    description: '',
    date: new Date().toISOString().split('T')[0],
    time: new Date().toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' })
  });

  const categories = [
    { id: 'food', name: 'Food & Dining', icon: Utensils, color: 'rgba(239, 68, 68, 0.8)' },
    { id: 'transport', name: 'Transportation', icon: Car, color: 'rgba(59, 130, 246, 0.8)' },
    { id: 'shopping', name: 'Shopping', icon: ShoppingCart, color: 'rgba(168, 85, 247, 0.8)' },
    { id: 'entertainment', name: 'Entertainment', icon: Gamepad2, color: 'rgba(245, 158, 11, 0.8)' },
    { id: 'health', name: 'Healthcare', icon: Heart, color: 'rgba(34, 197, 94, 0.8)' },
    { id: 'education', name: 'Education', icon: GraduationCap, color: 'rgba(14, 165, 233, 0.8)' },
    { id: 'travel', name: 'Travel', icon: Plane, color: 'rgba(236, 72, 153, 0.8)' },
    { id: 'utilities', name: 'Utilities', icon: Home, color: 'rgba(156, 163, 175, 0.8)' },
    { id: 'coffee', name: 'Coffee & Snacks', icon: Coffee, color: 'rgba(120, 53, 15, 0.8)' }
  ];

  // Calculate category totals
  const categoryTotals = categories.map(category => ({
    ...category,
    total: spendingEntries
      .filter(entry => entry.category === category.id)
      .reduce((sum, entry) => sum + entry.amount, 0)
  })).filter(cat => cat.total > 0);

  const totalSpending = spendingEntries.reduce((sum, entry) => sum + entry.amount, 0);

  // Chart data for spending by category
  const chartData = {
    labels: categoryTotals.map(cat => cat.name),
    datasets: [
      {
        data: categoryTotals.map(cat => cat.total),
        backgroundColor: categoryTotals.map(cat => cat.color),
        borderColor: categoryTotals.map(cat => cat.color.replace('0.8', '1')),
        borderWidth: 2,
      },
    ],
  };

  // Weekly spending data for bar chart
  const weeklyData = {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: [
      {
        label: 'Daily Spending',
        data: [1200, 800, 1500, 900, 2000, 1800, 1100],
        backgroundColor: 'rgba(239, 68, 68, 0.6)',
        borderColor: 'rgba(239, 68, 68, 1)',
        borderWidth: 2,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'bottom' as const,
        labels: {
          padding: 20,
          usePointStyle: true,
        }
      },
      title: {
        display: true,
        text: 'Spending by Category',
      },
      tooltip: {
        callbacks: {
          label: function(context: any) {
            const label = context.label || '';
            const value = context.parsed;
            const percentage = ((value / totalSpending) * 100).toFixed(1);
            return `${label}: ₹${value.toLocaleString()} (${percentage}%)`;
          }
        }
      }
    }
  };

  const barOptions = {
    responsive: true,
    plugins: {
      legend: {
        display: false,
      },
      title: {
        display: true,
        text: 'Weekly Spending Trend',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          callback: function(value: any) {
            return '₹' + value.toLocaleString();
          }
        }
      }
    }
  };

  const handleAddSpending = () => {
    if (newEntry.amount > 0 && newEntry.category && newEntry.description) {
      const entry: SpendingEntry = {
        ...newEntry,
        id: Date.now().toString()
      };
      setSpendingEntries(prev => [entry, ...prev]);
      setNewEntry({
        amount: 0,
        category: '',
        description: '',
        date: new Date().toISOString().split('T')[0],
        time: new Date().toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' })
      });
      setShowAddForm(false);
    }
  };

  const handleDeleteEntry = (id: string) => {
    setSpendingEntries(prev => prev.filter(entry => entry.id !== id));
  };

  const getCategoryIcon = (categoryId: string) => {
    const category = categories.find(cat => cat.id === categoryId);
    return category ? category.icon : ShoppingCart;
  };

  const getCategoryName = (categoryId: string) => {
    const category = categories.find(cat => cat.id === categoryId);
    return category ? category.name : 'Other';
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-IN', {
      weekday: 'short',
      month: 'short',
      day: 'numeric'
    });
  };

  return (
    <AnimatePresence>
      <motion.div
        key="add-spending-modal"
        initial={{ y: 40, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        exit={{ y: 40, opacity: 0 }}
        transition={{ duration: 0.3, ease: "easeInOut" }}
        className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
      >
        <motion.div
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.95, opacity: 0 }}
          transition={{ duration: 0.2 }}
          className="w-full max-w-3xl max-h-[90vh] overflow-y-auto bg-background rounded-xl border shadow-lg"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-border">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-primary/10 rounded-lg">
                <DollarSign className="w-6 h-6 text-primary" />
              </div>
              <div>
                <CardTitle className="text-xl">Add Spending</CardTitle>
                <CardDescription>Track your daily and weekly expenses</CardDescription>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="default"
                size="sm"
                onClick={() => setShowAddForm(true)}
                className="flex items-center gap-2"
              >
                <Plus className="w-4 h-4" />
                Add Spending
              </Button>
              <Button
                variant="ghost"
                size="icon"
                onClick={onClose}
                className="h-8 w-8"
              >
                <X className="w-4 h-4" />
              </Button>
            </div>
          </div>

          {/* Content */}
                      <div className="p-3 space-y-4">
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Card className="finance-card">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">Total Spending</p>
                      <p className="text-2xl font-bold">₹{totalSpending.toLocaleString()}</p>
                    </div>
                    <DollarSign className="w-8 h-8 text-primary opacity-60" />
                  </div>
                </CardContent>
              </Card>
              <Card className="finance-card">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">This Week</p>
                      <p className="text-2xl font-bold">₹9,300</p>
                    </div>
                    <Calendar className="w-8 h-8 text-primary opacity-60" />
                  </div>
                </CardContent>
              </Card>
              <Card className="finance-card">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">Categories</p>
                      <p className="text-2xl font-bold">{categoryTotals.length}</p>
                    </div>
                    <TrendingUp className="w-8 h-8 text-primary opacity-60" />
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Charts Section */}
                          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <Card className="finance-card">
                <CardHeader>
                  <CardTitle>Spending by Category</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="h-64">
                    <Pie options={chartOptions} data={chartData} />
                  </div>
                </CardContent>
              </Card>
              <Card className="finance-card">
                <CardHeader>
                  <CardTitle>Weekly Spending Trend</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="h-64">
                    <Bar options={barOptions} data={weeklyData} />
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Recent Spending Entries */}
            <Card className="finance-card">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Receipt className="w-5 h-5" />
                  Recent Spending Entries
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {spendingEntries.map((entry) => {
                    const Icon = getCategoryIcon(entry.category);
                    return (
                      <div key={entry.id} className="flex items-center justify-between p-3 bg-muted/30 rounded-lg">
                        <div className="flex items-center gap-3">
                          <div className="p-2 bg-primary/10 rounded-lg">
                            <Icon className="w-4 h-4 text-primary" />
                          </div>
                          <div>
                            <p className="font-medium">{entry.description}</p>
                            <div className="flex items-center gap-2 text-sm text-muted-foreground">
                              <span>{getCategoryName(entry.category)}</span>
                              <span>•</span>
                              <span>{formatDate(entry.date)}</span>
                              <span>•</span>
                              <span>{entry.time}</span>
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <p className="font-semibold">₹{entry.amount.toLocaleString()}</p>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDeleteEntry(entry.id)}
                            className="h-6 w-6 p-0 text-muted-foreground hover:text-destructive"
                          >
                            <X className="w-3 h-3" />
                          </Button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Add Spending Form Modal */}
          {showAddForm && (
            <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
              <motion.div
                initial={{ scale: 0.95, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.95, opacity: 0 }}
                transition={{ duration: 0.2 }}
                className="w-full max-w-md bg-background rounded-xl border shadow-lg p-6"
                onClick={(e) => e.stopPropagation()}
              >
                <div className="flex items-center justify-between mb-4">
                  <CardTitle>Add New Spending</CardTitle>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => setShowAddForm(false)}
                    className="h-6 w-6"
                  >
                    <X className="w-4 h-4" />
                  </Button>
                </div>
                
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="amount">Amount (₹)</Label>
                    <Input
                      id="amount"
                      type="number"
                      value={newEntry.amount}
                      onChange={(e) => setNewEntry(prev => ({ ...prev, amount: Number(e.target.value) }))}
                      placeholder="Enter amount"
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="category">Category</Label>
                    <Select value={newEntry.category} onValueChange={(value) => setNewEntry(prev => ({ ...prev, category: value }))}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select category" />
                      </SelectTrigger>
                      <SelectContent>
                        {categories.map((category) => {
                          const Icon = category.icon;
                          return (
                            <SelectItem key={category.id} value={category.id}>
                              <div className="flex items-center gap-2">
                                <Icon className="w-4 h-4" />
                                {category.name}
                              </div>
                            </SelectItem>
                          );
                        })}
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="description">Description</Label>
                    <Textarea
                      id="description"
                      value={newEntry.description}
                      onChange={(e) => setNewEntry(prev => ({ ...prev, description: e.target.value }))}
                      placeholder="What did you spend on?"
                      rows={3}
                    />
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="date">Date</Label>
                      <Input
                        id="date"
                        type="date"
                        value={newEntry.date}
                        onChange={(e) => setNewEntry(prev => ({ ...prev, date: e.target.value }))}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="time">Time</Label>
                      <Input
                        id="time"
                        type="time"
                        value={newEntry.time}
                        onChange={(e) => setNewEntry(prev => ({ ...prev, time: e.target.value }))}
                      />
                    </div>
                  </div>
                  
                  <div className="flex gap-2 pt-4">
                    <Button
                      variant="outline"
                      onClick={() => setShowAddForm(false)}
                      className="flex-1"
                    >
                      Cancel
                    </Button>
                    <Button
                      onClick={handleAddSpending}
                      className="flex-1"
                      disabled={!newEntry.amount || !newEntry.category || !newEntry.description}
                    >
                      Add Spending
                    </Button>
                  </div>
                </div>
              </motion.div>
            </div>
          )}
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default AddSpending; 