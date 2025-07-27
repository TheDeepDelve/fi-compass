// import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
// import { Button } from "@/components/ui/button";
// import { Carousel, CarouselContent, CarouselItem, CarouselNext, CarouselPrevious } from "@/components/ui/carousel";
// import { 
//   Brain, 
//   Target, 
//   Shield, 
//   TrendingUp, 
//   Zap, 
//   BarChart3,
//   ArrowRight
// } from "lucide-react";
// import { Link } from "react-router-dom";

// const FeaturesSection = () => {
//   return (
//     <section className="py-24 bg-background">
//       <div className="max-w-6xl mx-auto px-6">
        
//         {/* Core Features */}
//         <div className="mb-32" id="features">
//           <div className="text-center mb-16">
//             <h2 className="text-4xl font-bold mb-6">
//               Powerful Features
//             </h2>
//             <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
//               Everything you need for complete financial control
//             </p>
//           </div>

//           <div className="relative">
//             <Carousel className="w-full max-w-5xl mx-auto">
//               <CarouselContent className="-ml-2 md:-ml-4">
//                 {[
//                   {
//                     icon: Brain,
//                     title: "AI-Powered Insights",
//                     description: "Get personalized recommendations based on your spending patterns and financial goals."
//                   },
//                   {
//                     icon: Shield,
//                     title: "Bank-Grade Security",
//                     description: "Your data is protected with 256-bit encryption and multi-factor authentication."
//                   },
//                   {
//                     icon: TrendingUp,
//                     title: "Investment Tracking",
//                     description: "Monitor portfolio performance with real-time data and professional analytics."
//                   },
//                   {
//                     icon: Target,
//                     title: "Goal Planning",
//                     description: "Set and track financial goals with intelligent projections and strategies."
//                   },
//                   {
//                     icon: Zap,
//                     title: "Smart Automation",
//                     description: "Automate savings, investments, and bill payments with intelligent rules."
//                   },
//                   {
//                     icon: BarChart3,
//                     title: "Advanced Analytics",
//                     description: "Deep insights into your spending, saving, and investment patterns."
//                   }
//                 ].map((feature, index) => {
//                   const Icon = feature.icon;
//                   return (
//                     <CarouselItem key={index} className="pl-2 md:pl-4 md:basis-1/2 lg:basis-1/3">
//                       <Card className="finance-card group hover:scale-105 transition-transform h-full">
//                         <CardHeader className="pb-4">
//                           <Icon className="w-8 h-8 text-primary mb-3" />
//                           <CardTitle className="text-lg">{feature.title}</CardTitle>
//                         </CardHeader>
//                         <CardContent className="pt-0">
//                           <CardDescription className="text-muted-foreground leading-relaxed text-sm">
//                             {feature.description}
//                           </CardDescription>
//                         </CardContent>
//                       </Card>
//                     </CarouselItem>
//                   );
//                 })}
//               </CarouselContent>
//               <CarouselPrevious className="hidden md:flex" />
//               <CarouselNext className="hidden md:flex" />
//             </Carousel>
//           </div>
//         </div>

//         {/* CTA Section */}
//         <div className="text-center">
//           <Card className="finance-card inline-block max-w-2xl">
//             <CardContent className="p-12">
//               <h3 className="text-2xl font-bold mb-4">Ready to Transform Your Finances?</h3>
//               <p className="text-muted-foreground mb-8">
//                 Join thousands of users who are already taking control of their financial future.
//               </p>
//               <Link to="/login">
//                 <Button variant="hero" size="lg">
//                   Get Started Free
//                   <ArrowRight className="w-5 h-5 ml-2" />
//                 </Button>
//               </Link>
//             </CardContent>
//           </Card>
//         </div>
//       </div>
//     </section>
//   );
// };

// export default FeaturesSection;

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Brain, Target, Shield, TrendingUp, Zap, BarChart3, ArrowRight } from "lucide-react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";

// Animation variant
const fadeUp = {
  hidden: { opacity: 0, y: 30 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.5,
      delay: i * 0.1,
    },
  }),
};

const FeaturesSection = () => {
  return (
    <section className="py-24 bg-background">
      <div className="max-w-6xl mx-auto px-6">
        
        {/* Core Features */}
        <div className="mb-32" id="features">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-6">
              Powerful Features
            </h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Everything you need for complete financial control
            </p>
          </div>

          {/* Animated Horizontal Scroll */}
          <motion.div
            className="overflow-x-auto no-scrollbar"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: false, amount: 0.2 }}
            variants={{
              visible: { transition: { staggerChildren: 0.1 } },
            }}
          >
            <div className="flex space-x-6 min-w-[100vw] px-4 md:px-0">
              {[
                {
                  icon: Brain,
                  title: "AI-Powered Insights",
                  description: "Get personalized recommendations based on your spending patterns and financial goals.",
                },
                {
                  icon: Shield,
                  title: "Bank-Grade Security",
                  description: "Your data is protected with 256-bit encryption and multi-factor authentication.",
                },
                {
                  icon: TrendingUp,
                  title: "Investment Tracking",
                  description: "Monitor portfolio performance with real-time data and professional analytics.",
                },
                {
                  icon: Target,
                  title: "Goal Planning",
                  description: "Set and track financial goals with intelligent projections and strategies.",
                },
                {
                  icon: Zap,
                  title: "Smart Automation",
                  description: "Automate savings, investments, and bill payments with intelligent rules.",
                },
                {
                  icon: BarChart3,
                  title: "Advanced Analytics",
                  description: "Deep insights into your spending, saving, and investment patterns.",
                }
              ].map((feature, index) => {
                const Icon = feature.icon;
                return (
                  <motion.div
                    key={index}
                    className="min-w-[280px] md:min-w-[320px]"
                    variants={fadeUp}
                    custom={index}
                  >
                    <Card className="finance-card group hover:scale-105 transition-transform h-full">
                      <CardHeader className="pb-4">
                        <Icon className="w-8 h-8 text-primary mb-3" />
                        <CardTitle className="text-lg">{feature.title}</CardTitle>
                      </CardHeader>
                      <CardContent className="pt-0">
                        <CardDescription className="text-muted-foreground leading-relaxed text-sm">
                          {feature.description}
                        </CardDescription>
                      </CardContent>
                    </Card>
                  </motion.div>
                );
              })}
            </div>
          </motion.div>
        </div>

        {/* CTA Section */}
        <div className="text-center">
          <Card className="finance-card inline-block max-w-2xl">
            <CardContent className="p-12">
              <h3 className="text-2xl font-bold mb-4">Ready to Transform Your Finances?</h3>
              <p className="text-muted-foreground mb-8">
                Join thousands of users who are already taking control of their financial future.
              </p>
              <Link to="/login">
                <Button variant="hero" size="lg">
                  Get Started Free
                  <ArrowRight className="w-5 h-5 ml-2" />
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>
      </div>
    </section>
  );
};

export default FeaturesSection;

