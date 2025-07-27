import React, { useState, useRef } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  LineElement,
  PointElement,
  ArcElement,
} from 'chart.js';
import { Bar, Line, Pie, Doughnut } from 'react-chartjs-2';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ChevronLeft, ChevronRight, BarChart3, TrendingUp, PieChart } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

export const FinanceCharts = () => {
  const [currentSlide, setCurrentSlide] = useState(0);
  const carouselRef = useRef<HTMLDivElement>(null);

  // Monthly spending data
  const monthlySpendingData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [
      {
        label: 'Income',
        data: [45000, 48000, 52000, 49000, 55000, 58000],
        backgroundColor: 'rgba(34, 197, 94, 0.5)',
        borderColor: 'rgba(34, 197, 94, 1)',
        borderWidth: 2,
      },
      {
        label: 'Expenses',
        data: [32000, 35000, 38000, 36000, 42000, 41000],
        backgroundColor: 'rgba(239, 68, 68, 0.5)',
        borderColor: 'rgba(239, 68, 68, 1)',
        borderWidth: 2,
      },
      {
        label: 'Savings',
        data: [13000, 13000, 14000, 13000, 13000, 17000],
        backgroundColor: 'rgba(59, 130, 246, 0.5)',
        borderColor: 'rgba(59, 130, 246, 1)',
        borderWidth: 2,
      }
    ],
  };

  // Investment portfolio data
  const portfolioData = {
    labels: ['Stocks', 'Bonds', 'Real Estate', 'Gold', 'Cash'],
    datasets: [
      {
        data: [35, 25, 20, 15, 5],
        backgroundColor: [
          'rgba(34, 197, 94, 0.8)',
          'rgba(59, 130, 246, 0.8)',
          'rgba(168, 85, 247, 0.8)',
          'rgba(245, 158, 11, 0.8)',
          'rgba(156, 163, 175, 0.8)',
        ],
        borderColor: [
          'rgba(34, 197, 94, 1)',
          'rgba(59, 130, 246, 1)',
          'rgba(168, 85, 247, 1)',
          'rgba(245, 158, 11, 1)',
          'rgba(156, 163, 175, 1)',
        ],
        borderWidth: 2,
      },
    ],
  };

  // Net worth trend data
  const netWorthData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
    datasets: [
      {
        label: 'Net Worth',
        data: [250000, 265000, 280000, 275000, 290000, 310000, 305000, 320000, 335000, 350000, 365000, 380000],
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
        borderColor: 'rgba(34, 197, 94, 1)',
        borderWidth: 3,
        tension: 0.4,
        fill: true,
      },
      {
        label: 'Investments',
        data: [150000, 165000, 180000, 175000, 190000, 210000, 205000, 220000, 235000, 250000, 265000, 280000],
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        borderColor: 'rgba(59, 130, 246, 1)',
        borderWidth: 2,
        tension: 0.4,
        fill: false,
      }
    ],
  };

  const barOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Monthly Income vs Expenses',
      },
      tooltip: {
        callbacks: {
          label: function(context: any) {
            return `${context.dataset.label}: ₹${context.parsed.y.toLocaleString()}`;
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Amount (₹)'
        }
      }
    }
  };

  const lineOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Net Worth & Investment Growth',
      },
      tooltip: {
        callbacks: {
          label: function(context: any) {
            return `${context.dataset.label}: ₹${context.parsed.y.toLocaleString()}`;
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Amount (₹)'
        }
      }
    }
  };

  const pieOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Investment Portfolio Allocation',
      },
      tooltip: {
        callbacks: {
          label: function(context: any) {
            const label = context.label || '';
            const value = context.parsed;
            const total = context.dataset.data.reduce((a: number, b: number) => a + b, 0);
            const percentage = ((value / total) * 100).toFixed(1);
            return `${label}: ${percentage}% (₹${(value * 1000).toLocaleString()})`;
          }
        }
      }
    }
  };

  // Carousel slides data
  const slides = [
    {
      id: 'overview',
      title: 'Overview',
      icon: BarChart3,
      description: 'Financial overview and cash flow',
      content: (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card className="finance-card">
            <CardHeader>
              <CardTitle>Monthly Income vs Expenses</CardTitle>
              <CardDescription>Track your monthly cash flow</CardDescription>
            </CardHeader>
            <CardContent>
              <Bar options={barOptions} data={monthlySpendingData} />
            </CardContent>
          </Card>

          <Card className="finance-card">
            <CardHeader>
              <CardTitle>Net Worth Growth</CardTitle>
              <CardDescription>Your financial journey over time</CardDescription>
            </CardHeader>
            <CardContent>
              <Line options={lineOptions} data={netWorthData} />
            </CardContent>
          </Card>
        </div>
      )
    },
    {
      id: 'spending',
      title: 'Spending',
      icon: TrendingUp,
      description: 'Expense tracking and analysis',
      content: (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card className="finance-card">
            <CardHeader>
              <CardTitle>Spending by Category</CardTitle>
              <CardDescription>Breakdown of your monthly expenses</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex justify-center">
                <div className="w-90 h-90">
                  <Doughnut options={pieOptions} data={{
                    labels: ['Housing', 'Food', 'Transport', 'Entertainment', 'Healthcare', 'Shopping'],
                    datasets: [{
                      data: [12000, 8000, 6000, 4000, 3000, 5000],
                      backgroundColor: [
                        'rgba(239, 68, 68, 0.8)',
                        'rgba(34, 197, 94, 0.8)',
                        'rgba(59, 130, 246, 0.8)',
                        'rgba(245, 158, 11, 0.8)',
                        'rgba(168, 85, 247, 0.8)',
                        'rgba(156, 163, 175, 0.8)',
                      ],
                      borderColor: [
                        'rgba(239, 68, 68, 1)',
                        'rgba(34, 197, 94, 1)',
                        'rgba(59, 130, 246, 1)',
                        'rgba(245, 158, 11, 1)',
                        'rgba(168, 85, 247, 1)',
                        'rgba(156, 163, 175, 1)',
                      ],
                      borderWidth: 2,
                    }],
                  }} />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="finance-card">
            <CardHeader>
              <CardTitle>Monthly Spending Trend</CardTitle>
              <CardDescription>Track your spending patterns</CardDescription>
            </CardHeader>
            <CardContent>
              <Bar options={barOptions} data={monthlySpendingData} />
            </CardContent>
          </Card>
        </div>
      )
    },
    {
      id: 'investments',
      title: 'Investments',
      icon: PieChart,
      description: 'Portfolio and investment analysis',
      content: (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card className="finance-card">
            <CardHeader>
              <CardTitle>Portfolio Allocation</CardTitle>
              <CardDescription>Your current investment distribution</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex justify-center">
                <div className="w-90 h-90">
                  <Pie options={pieOptions} data={portfolioData} />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="finance-card">
            <CardHeader>
              <CardTitle>Investment Growth</CardTitle>
              <CardDescription>Performance of your investment portfolio</CardDescription>
            </CardHeader>
            <CardContent>
              <Line options={lineOptions} data={netWorthData} />
            </CardContent>
          </Card>
        </div>
      )
    }
  ];

  const nextSlide = () => {
    setCurrentSlide((prev) => (prev + 1) % slides.length);
  };

  const prevSlide = () => {
    setCurrentSlide((prev) => (prev - 1 + slides.length) % slides.length);
  };

  const goToSlide = (index: number) => {
    setCurrentSlide(index);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-foreground">Financial Analytics</h2>
          <p className="text-muted-foreground">Track your financial health with detailed charts and insights</p>
        </div>
      </div>

      {/* Navigation Dots */}
      <div className="flex justify-center space-x-2">
        {slides.map((slide, index) => {
          const Icon = slide.icon;
          return (
            <Button
              key={slide.id}
              variant={currentSlide === index ? "default" : "outline"}
              size="sm"
              onClick={() => goToSlide(index)}
              className="flex items-center gap-2 px-4 py-2"
            >
              <Icon className="w-4 h-4" />
              {slide.title}
            </Button>
          );
        })}
      </div>

      {/* Carousel Container */}
      <div className="relative">
        {/* Navigation Arrows */}
        <Button
          variant="outline"
          size="icon"
          onClick={prevSlide}
          className="absolute left-4 top-1/2 transform -translate-y-1/2 z-10 bg-background/80 backdrop-blur-sm hover:bg-background"
        >
          <ChevronLeft className="w-5 h-5" />
        </Button>

        <Button
          variant="outline"
          size="icon"
          onClick={nextSlide}
          className="absolute right-4 top-1/2 transform -translate-y-1/2 z-10 bg-background/80 backdrop-blur-sm hover:bg-background"
        >
          <ChevronRight className="w-5 h-5" />
        </Button>

        {/* Carousel Content */}
        <div 
          ref={carouselRef}
          className="overflow-hidden rounded-lg"
        >
          <div 
            className="flex transition-transform duration-500 ease-in-out"
            style={{ transform: `translateX(-${currentSlide * 100}%)` }}
          >
            {slides.map((slide, index) => (
              <div
                key={slide.id}
                className="w-full flex-shrink-0"
                style={{ width: '100%' }}
              >
                <AnimatePresence mode="wait">
                  <motion.div
                    key={slide.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ duration: 0.3 }}
                    className="space-y-6"
                  >
                    {/* Slide Header */}
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-primary/10 rounded-lg">
                        <slide.icon className="w-6 h-6 text-primary" />
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold">{slide.title}</h3>
                        <p className="text-sm text-muted-foreground">{slide.description}</p>
                      </div>
                      <Badge variant="secondary" className="ml-auto">
                        {index + 1} of {slides.length}
                      </Badge>
                    </div>

                    {/* Slide Content */}
                    {slide.content}
                  </motion.div>
                </AnimatePresence>
              </div>
            ))}
          </div>
        </div>

        {/* Progress Indicator */}
        <div className="flex justify-center mt-4 space-x-2">
          {slides.map((_, index) => (
            <div
              key={index}
              className={`h-2 rounded-full transition-all duration-300 ${
                index === currentSlide 
                  ? 'bg-primary w-8' 
                  : 'bg-muted w-2'
              }`}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

export default FinanceCharts; 