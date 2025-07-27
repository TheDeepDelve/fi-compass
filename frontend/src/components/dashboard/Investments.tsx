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
  LineElement,
  PointElement,
} from 'chart.js';
import { Pie, Bar, Line } from 'react-chartjs-2';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  TrendingUp,
  TrendingDown,
  DollarSign,
  PieChart,
  BarChart3,
  LineChart,
  X,
  Plus,
  Target,
  AlertTriangle,
  CheckCircle,
  ArrowUpRight,
  ArrowDownRight
} from "lucide-react";
import { AnimatePresence, motion } from "framer-motion";

ChartJS.register(
  ArcElement,
  Title,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement
);

interface Investment {
  id: string;
  name: string;
  type: string;
  value: number;
  change: number;
  changePercent: number;
  allocation: number;
  color: string;
}

interface InvestmentsProps {
  onClose: () => void;
}

const Investments = ({ onClose }: InvestmentsProps) => {
  const [selectedTimeframe, setSelectedTimeframe] = useState('1M');

  const investments: Investment[] = [
    {
      id: '1',
      name: 'Equity Mutual Funds',
      type: 'Equity',
      value: 450000,
      change: 25000,
      changePercent: 5.88,
      allocation: 45,
      color: 'rgba(34, 197, 94, 0.8)'
    },
    {
      id: '2',
      name: 'Fixed Deposits',
      type: 'Fixed Income',
      value: 300000,
      change: 15000,
      changePercent: 5.26,
      allocation: 30,
      color: 'rgba(59, 130, 246, 0.8)'
    },
    {
      id: '3',
      name: 'Gold ETFs',
      type: 'Commodity',
      value: 150000,
      change: -5000,
      changePercent: -3.23,
      allocation: 15,
      color: 'rgba(245, 158, 11, 0.8)'
    },
    {
      id: '4',
      name: 'Real Estate',
      type: 'Property',
      value: 100000,
      change: 8000,
      changePercent: 8.70,
      allocation: 10,
      color: 'rgba(168, 85, 247, 0.8)'
    }
  ];

  const totalPortfolio = investments.reduce((sum, inv) => sum + inv.value, 0);
  const totalChange = investments.reduce((sum, inv) => sum + inv.change, 0);
  const totalChangePercent = ((totalChange / (totalPortfolio - totalChange)) * 100).toFixed(2);

  const portfolioData = {
    labels: investments.map(inv => inv.name),
    datasets: [{
      data: investments.map(inv => inv.value),
      backgroundColor: investments.map(inv => inv.color),
      borderColor: investments.map(inv => inv.color.replace('0.8', '1')),
      borderWidth: 2,
    }],
  };

  const performanceData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [{
      label: 'Portfolio Value',
      data: [850000, 870000, 890000, 920000, 950000, 1000000],
      borderColor: 'rgba(34, 197, 94, 1)',
      backgroundColor: 'rgba(34, 197, 94, 0.1)',
      tension: 0.4,
    }],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'bottom' as const,
      },
    },
  };

  const lineOptions = {
    responsive: true,
    plugins: {
      legend: {
        display: false,
      },
    },
    scales: {
      y: {
        beginAtZero: false,
      },
    },
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
          <div className="relative p-4 border-b border-border bg-gradient-to-r from-primary/10 via-primary/5 to-transparent">
            <div className="absolute inset-0 bg-gradient-to-r from-primary/5 to-transparent opacity-50 rounded-t-2xl"></div>
            <div className="relative flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="p-3 bg-gradient-to-br from-primary to-primary/80 rounded-xl shadow-lg">
                  <TrendingUp className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h2 className="text-xl font-bold bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
                    Investment Portfolio
                  </h2>
                  <p className="text-xs text-muted-foreground">Track and manage your investment portfolio</p>
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
            {/* Portfolio Summary */}
            <div className="relative overflow-hidden rounded-lg bg-gradient-to-br from-success/10 via-success/5 to-transparent border border-success/20 p-3 mb-3">
              <div className="absolute top-0 right-0 w-24 h-24 bg-success/5 rounded-full -translate-y-12 translate-x-12"></div>
              <div className="relative grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center">
                  <h3 className="text-base font-semibold text-success mb-1">Total Portfolio</h3>
                  <div className="text-2xl font-bold text-success mb-1">
                    ₹{totalPortfolio.toLocaleString()}
                  </div>
                  <p className="text-sm text-muted-foreground">Current Value</p>
                </div>
                <div className="text-center">
                  <h3 className="text-base font-semibold text-success mb-1">Total Return</h3>
                  <div className="text-2xl font-bold text-success mb-1">
                    ₹{totalChange.toLocaleString()}
                  </div>
                  <div className="flex items-center justify-center gap-1">
                    {totalChange >= 0 ? (
                      <ArrowUpRight className="w-4 h-4 text-success" />
                    ) : (
                      <ArrowDownRight className="w-4 h-4 text-destructive" />
                    )}
                    <span className={`text-sm ${totalChange >= 0 ? 'text-success' : 'text-destructive'}`}>
                      {totalChangePercent}%
                    </span>
                  </div>
                </div>
                <div className="text-center">
                  <h3 className="text-base font-semibold text-success mb-1">Active Investments</h3>
                  <div className="text-2xl font-bold text-success mb-1">
                    {investments.length}
                  </div>
                  <p className="text-sm text-muted-foreground">Diversified Portfolio</p>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
                              {/* Portfolio Allocation */}
                <div className="relative overflow-hidden rounded-lg bg-gradient-to-br from-info/10 via-info/5 to-transparent border border-info/20 p-3">
                <div className="absolute top-0 right-0 w-16 h-16 bg-info/5 rounded-full -translate-y-8 translate-x-8"></div>
                <div className="relative">
                  <h3 className="text-base font-semibold text-info mb-3 flex items-center gap-2">
                    <div className="p-1.5 bg-info/10 rounded-lg">
                      <PieChart className="w-4 h-4 text-info" />
                    </div>
                    Portfolio Allocation
                  </h3>
                  <div className="flex justify-center mb-3">
                    <div className="w-40 h-40">
                      <Pie data={portfolioData} options={chartOptions} />
                    </div>
                  </div>
                  <div className="space-y-2">
                    {investments.map((investment) => (
                      <div key={investment.id} className="flex items-center justify-between p-2 bg-background/50 rounded-lg">
                        <div className="flex items-center gap-2">
                          <div 
                            className="w-3 h-3 rounded-full" 
                            style={{ backgroundColor: investment.color }}
                          ></div>
                          <span className="text-sm font-medium">{investment.name}</span>
                        </div>
                        <span className="text-sm text-muted-foreground">{investment.allocation}%</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

                              {/* Performance Chart */}
                <div className="relative overflow-hidden rounded-lg bg-gradient-to-br from-warning/10 via-warning/5 to-transparent border border-warning/20 p-3">
                <div className="absolute top-0 right-0 w-14 h-14 bg-warning/5 rounded-full -translate-y-7 translate-x-7"></div>
                <div className="relative">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-warning flex items-center gap-2">
                      <div className="p-1.5 bg-warning/10 rounded-lg">
                        <LineChart className="w-4 h-4 text-warning" />
                      </div>
                      Performance Trend
                    </h3>
                    <div className="flex gap-1">
                      {['1M', '3M', '6M', '1Y'].map((timeframe) => (
                        <Button
                          key={timeframe}
                          variant={selectedTimeframe === timeframe ? "default" : "outline"}
                          size="sm"
                          onClick={() => setSelectedTimeframe(timeframe)}
                          className="text-xs"
                        >
                          {timeframe}
                        </Button>
                      ))}
                    </div>
                  </div>
                  <div className="h-64">
                    <Line data={performanceData} options={lineOptions} />
                  </div>
                </div>
              </div>
            </div>

            {/* Investment Details */}
            <div className="relative overflow-hidden rounded-lg bg-gradient-to-br from-background via-background to-primary/5 border border-primary/20 p-3 mt-3">
              <div className="absolute top-0 right-0 w-20 h-20 bg-primary/5 rounded-full -translate-y-10 translate-x-10"></div>
              <div className="relative">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-base font-semibold flex items-center gap-2">
                    <div className="p-1.5 bg-primary/10 rounded-lg">
                      <BarChart3 className="w-4 h-4 text-primary" />
                    </div>
                    Investment Details
                  </h3>
                  <Button className="bg-primary hover:bg-primary/80">
                    <Plus className="w-4 h-4 mr-2" />
                    Add Investment
                  </Button>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-48 overflow-y-auto">
                  {investments.map((investment) => (
                                          <div key={investment.id} className="relative overflow-hidden rounded-lg bg-gradient-to-br from-background via-background to-primary/5 border border-primary/20 p-3">
                      <div className="absolute top-0 right-0 w-12 h-12 bg-primary/5 rounded-full -translate-y-6 translate-x-6"></div>
                      <div className="relative">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-semibold">{investment.name}</h4>
                          <Badge variant="outline" className="text-xs">
                            {investment.type}
                          </Badge>
                        </div>
                        <div className="space-y-2">
                          <div className="flex justify-between">
                            <span className="text-sm text-muted-foreground">Value:</span>
                            <span className="font-medium">₹{investment.value.toLocaleString()}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-sm text-muted-foreground">Change:</span>
                            <div className="flex items-center gap-1">
                              {investment.change >= 0 ? (
                                <ArrowUpRight className="w-3 h-3 text-success" />
                              ) : (
                                <ArrowDownRight className="w-3 h-3 text-destructive" />
                              )}
                              <span className={`font-medium ${investment.change >= 0 ? 'text-success' : 'text-destructive'}`}>
                                ₹{Math.abs(investment.change).toLocaleString()} ({investment.changePercent}%)
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="relative overflow-hidden rounded-lg bg-gradient-to-br from-warning/10 via-warning/5 to-transparent border border-warning/20 p-3 mt-3">
              <div className="absolute top-0 right-0 w-16 h-16 bg-warning/5 rounded-full -translate-y-8 translate-x-8"></div>
              <div className="relative">
                                  <h3 className="text-base font-semibold text-warning mb-3 flex items-center gap-2">
                  <div className="p-1.5 bg-warning/10 rounded-lg">
                    <Target className="w-4 h-4 text-warning" />
                  </div>
                  Quick Actions
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <Button variant="outline" className="flex items-center gap-2 border-primary/30 hover:bg-primary/10">
                    <Plus className="w-4 h-4" />
                    Add Investment
                  </Button>
                  <Button variant="outline" className="flex items-center gap-2 border-primary/30 hover:bg-primary/10">
                    <TrendingUp className="w-4 h-4" />
                    Rebalance
                  </Button>
                  <Button variant="outline" className="flex items-center gap-2 border-primary/30 hover:bg-primary/10">
                    <BarChart3 className="w-4 h-4" />
                    Performance Report
                  </Button>
                  <Button variant="outline" className="flex items-center gap-2 border-primary/30 hover:bg-primary/10">
                    <AlertTriangle className="w-4 h-4" />
                    Risk Analysis
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

export default Investments; 