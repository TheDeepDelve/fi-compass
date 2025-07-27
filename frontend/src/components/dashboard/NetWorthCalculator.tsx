import React, { useState } from 'react';
import {
  Chart as ChartJS,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Pie } from 'react-chartjs-2';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { 
  DollarSign,
  Home,
  Car,
  GraduationCap,
  Plane,
  X,
  Edit3,
  Save,
  Plus
} from "lucide-react";
import { AnimatePresence, motion } from "framer-motion";

ChartJS.register(
  ArcElement,
  Title,
  Tooltip,
  Legend
);

interface AssetCategory {
  id: string;
  name: string;
  value: number;
  color: string;
  icon: React.ComponentType<any>;
}

const NetWorthCalculator = ({ onClose }: { onClose: () => void }) => {
  const [assets, setAssets] = useState<AssetCategory[]>([
    {
      id: 'stocks',
      name: 'Stocks & Mutual Funds',
      value: 350000,
      color: 'rgba(34, 197, 94, 0.8)',
      icon: DollarSign
    },
    {
      id: 'real_estate',
      name: 'Real Estate',
      value: 200000,
      color: 'rgba(59, 130, 246, 0.8)',
      icon: Home
    },
    {
      id: 'gold',
      name: 'Gold & Precious Metals',
      value: 150000,
      color: 'rgba(245, 158, 11, 0.8)',
      icon: Car
    },
    {
      id: 'bonds',
      name: 'Bonds & Fixed Income',
      value: 100000,
      color: 'rgba(168, 85, 247, 0.8)',
      icon: GraduationCap
    },
    {
      id: 'cash',
      name: 'Cash & Savings',
      value: 50000,
      color: 'rgba(156, 163, 175, 0.8)',
      icon: Plane
    }
  ]);

  const [isEditing, setIsEditing] = useState(false);
  const [editingAsset, setEditingAsset] = useState<string | null>(null);
  const [showAddAsset, setShowAddAsset] = useState(false);
  const [newAsset, setNewAsset] = useState({
    name: '',
    value: 0,
    type: 'stocks'
  });

  const totalNetWorth = assets.reduce((sum, asset) => sum + asset.value, 0);

  const chartData = {
    labels: assets.map(asset => asset.name),
    datasets: [
      {
        data: assets.map(asset => asset.value),
        backgroundColor: assets.map(asset => asset.color),
        borderColor: assets.map(asset => asset.color.replace('0.8', '1')),
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
        text: 'Your Net Worth Breakdown',
      },
      tooltip: {
        callbacks: {
          label: function(context: any) {
            const label = context.label || '';
            const value = context.parsed;
            const percentage = ((value / totalNetWorth) * 100).toFixed(1);
            return `${label}: ₹${value.toLocaleString()} (${percentage}%)`;
          }
        }
      }
    }
  };

  const handleAssetUpdate = (assetId: string, newValue: number) => {
    setAssets(prev => prev.map(asset => 
      asset.id === assetId ? { ...asset, value: newValue } : asset
    ));
  };

  const handleEdit = (assetId: string) => {
    setEditingAsset(assetId);
    setIsEditing(true);
  };

  const handleSave = () => {
    setIsEditing(false);
    setEditingAsset(null);
  };

  const handleAddAsset = () => {
    if (newAsset.name && newAsset.value > 0) {
      const assetTypes = {
        stocks: { color: 'rgba(34, 197, 94, 0.8)', icon: DollarSign },
        real_estate: { color: 'rgba(59, 130, 246, 0.8)', icon: Home },
        gold: { color: 'rgba(245, 158, 11, 0.8)', icon: Car },
        bonds: { color: 'rgba(168, 85, 247, 0.8)', icon: GraduationCap },
        cash: { color: 'rgba(156, 163, 175, 0.8)', icon: Plane }
      };

      const selectedType = assetTypes[newAsset.type as keyof typeof assetTypes];
      
      const newAssetItem: AssetCategory = {
        id: `asset_${Date.now()}`,
        name: newAsset.name,
        value: newAsset.value,
        color: selectedType.color,
        icon: selectedType.icon
      };

      setAssets([...assets, newAssetItem]);
      setNewAsset({ name: '', value: 0, type: 'stocks' });
      setShowAddAsset(false);
    }
  };

  const handleCancelAdd = () => {
    setNewAsset({ name: '', value: 0, type: 'stocks' });
    setShowAddAsset(false);
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
                  <DollarSign className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
                    Know Your Worth
                  </h2>
                  <p className="text-sm text-muted-foreground">Track and visualize your financial assets</p>
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
            <div className="p-3">
              {/* Total Net Worth - Hero Section */}
              <div className="relative overflow-hidden rounded-lg bg-gradient-to-br from-success/10 via-success/5 to-transparent border border-success/20 p-3 mb-3">
                <div className="absolute top-0 right-0 w-16 h-16 bg-success/5 rounded-full -translate-y-8 translate-x-8"></div>
                <div className="relative text-center">
                  <h3 className="text-sm font-semibold text-success mb-1">Total Net Worth</h3>
                  <div className="text-2xl font-bold text-success mb-1">
                    ₹{totalNetWorth.toLocaleString()}
                  </div>
                  <p className="text-xs text-muted-foreground">Last updated: {new Date().toLocaleDateString()}</p>
                </div>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
              {/* Assets List - Modern Cards */}
                              <div className="space-y-2">
                  <h3 className="text-sm font-semibold flex items-center gap-2">
                    <div className="p-0.5 bg-primary/10 rounded-lg">
                      <DollarSign className="w-3 h-3 text-primary" />
                    </div>
                    Asset Management
                  </h3>
                  <div className="space-y-1.5 max-h-48 overflow-y-auto pr-2">
                  {assets.map((asset) => {
                    const Icon = asset.icon;
                    const percentage = ((asset.value / totalNetWorth) * 100).toFixed(1);
                    
                                          return (
                        <div key={asset.id} className="relative overflow-hidden rounded-md bg-gradient-to-br from-background via-background to-primary/5 border border-primary/20 p-2">
                          <div className="absolute top-0 right-0 w-6 h-6 bg-primary/5 rounded-full -translate-y-3 translate-x-3"></div>
                          <div className="relative flex items-center justify-between">
                            <div className="flex items-center gap-2">
                              <div className="p-1 rounded-lg" style={{ backgroundColor: asset.color.replace('0.8', '0.1') }}>
                                <Icon className="w-3 h-3" style={{ color: asset.color.replace('0.8', '1') }} />
                              </div>
                              <div>
                                <div className="font-medium text-xs">{asset.name}</div>
                                <div className="text-xs text-muted-foreground">{percentage}% of total</div>
                              </div>
                            </div>
                            <div className="text-right">
                              <div className="font-semibold text-xs">₹{asset.value.toLocaleString()}</div>
                              {isEditing && editingAsset === asset.id ? (
                                <div className="flex items-center gap-1 mt-1">
                                  <Input
                                    type="number"
                                    value={asset.value}
                                    onChange={(e) => handleAssetUpdate(asset.id, Number(e.target.value))}
                                    className="w-14 h-4 text-xs border-primary/30 focus:border-primary"
                                  />
                                  <Button
                                    size="sm"
                                    onClick={() => handleSave()}
                                    className="h-4 px-1 bg-success hover:bg-success/80"
                                  >
                                    <Save className="w-2 h-2" />
                                  </Button>
                                </div>
                              ) : (
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => handleEdit(asset.id)}
                                  className="h-4 px-1 hover:bg-primary/10"
                                >
                                  <Edit3 className="w-2 h-2" />
                                </Button>
                              )}
                            </div>
                          </div>
                        </div>
                      );
                  })}
                </div>
              </div>

                              {/* Chart - Modern Design */}
                <div className="relative overflow-hidden rounded-lg bg-gradient-to-br from-info/10 via-info/5 to-transparent border border-info/20 p-2">
                  <div className="absolute top-0 right-0 w-6 h-6 bg-info/5 rounded-full -translate-y-3 translate-x-3"></div>
                  <div className="relative">
                    <h3 className="text-sm font-semibold text-info mb-1 flex items-center gap-2">
                      <div className="p-0.5 bg-info/10 rounded-lg">
                        <DollarSign className="w-3 h-3 text-info" />
                      </div>
                      Asset Distribution
                    </h3>
                    <div className="flex justify-center">
                      <div className="w-40 h-40">
                        <Pie data={chartData} options={chartOptions} />
                      </div>
                    </div>
                  </div>
                </div>
            </div>

                                        {/* Quick Actions - Modern Design */}
              <div className="relative overflow-hidden rounded-lg bg-gradient-to-br from-warning/10 via-warning/5 to-transparent border border-warning/20 p-3 mt-3">
                <div className="absolute top-0 right-0 w-12 h-12 bg-warning/5 rounded-full -translate-y-6 translate-x-6"></div>
                <div className="relative">
                  <h3 className="text-sm font-semibold text-warning mb-2 flex items-center gap-2">
                    <div className="p-0.5 bg-warning/10 rounded-lg">
                      <DollarSign className="w-3 h-3 text-warning" />
                    </div>
                    Quick Actions
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                    <Button 
                      variant="outline" 
                      className="flex items-center gap-1 border-primary/30 hover:bg-primary/10 text-xs h-8"
                      onClick={() => setShowAddAsset(true)}
                    >
                      <Plus className="w-3 h-3" />
                      Add New Asset
                    </Button>
                    <Button variant="outline" className="flex items-center gap-1 border-primary/30 hover:bg-primary/10 text-xs h-8">
                      <Home className="w-3 h-3" />
                      Export Report
                    </Button>
                    <Button variant="outline" className="flex items-center gap-1 border-primary/30 hover:bg-primary/10 text-xs h-8">
                      <GraduationCap className="w-3 h-3" />
                      Set Goals
                    </Button>
                  </div>
                </div>
              </div>
          </div>

          {/* Add New Asset Modal */}
          {showAddAsset && (
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
                          Add New Asset
                        </h3>
                        <p className="text-sm text-muted-foreground">Add a new asset to your portfolio</p>
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
                    <label className="text-sm font-medium mb-2 block">Asset Name</label>
                    <Input
                      type="text"
                      placeholder="e.g., Cryptocurrency, Art Collection"
                      value={newAsset.name}
                      onChange={(e) => setNewAsset({ ...newAsset, name: e.target.value })}
                      className="w-full"
                    />
                  </div>

                  <div>
                    <label className="text-sm font-medium mb-2 block">Asset Type</label>
                    <select
                      value={newAsset.type}
                      onChange={(e) => setNewAsset({ ...newAsset, type: e.target.value })}
                      className="w-full p-2 border border-border rounded-md bg-background text-foreground"
                    >
                      <option value="stocks">Stocks & Mutual Funds</option>
                      <option value="real_estate">Real Estate</option>
                      <option value="gold">Gold & Precious Metals</option>
                      <option value="bonds">Bonds & Fixed Income</option>
                      <option value="cash">Cash & Savings</option>
                    </select>
                  </div>

                  <div>
                    <label className="text-sm font-medium mb-2 block">Value (₹)</label>
                    <Input
                      type="number"
                      placeholder="Enter asset value"
                      value={newAsset.value}
                      onChange={(e) => setNewAsset({ ...newAsset, value: Number(e.target.value) })}
                      className="w-full"
                    />
                  </div>

                  <div className="flex gap-2 pt-2">
                    <Button
                      onClick={handleAddAsset}
                      className="flex-1 bg-primary hover:bg-primary/80"
                      disabled={!newAsset.name || newAsset.value <= 0}
                    >
                      <Plus className="w-4 h-4 mr-2" />
                      Add Asset
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

export default NetWorthCalculator; 