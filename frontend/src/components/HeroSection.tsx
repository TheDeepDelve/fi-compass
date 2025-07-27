// import { Button } from "@/components/ui/button";
// import { ArrowRight, Play, Smartphone, Apple } from "lucide-react";
// import { Link } from "react-router-dom";
// import heroImage from "@/assets/hero-finance.jpg";

// const HeroSection = () => {
//   return (
//     <section className="relative min-h-screen flex items-center justify-center py-20">
//       {/* Clean Background */}
//       <div className="absolute inset-0 bg-gradient-to-br from-background via-background to-primary/5"></div>

//       {/* Content */}
//       <div className="relative z-10 max-w-6xl mx-auto px-6">
//         <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
          
//           {/* Left Column - Text Content */}
//           <div className="space-y-8">
//             <div className="space-y-6">
//               <h1 className="text-5xl lg:text-6xl font-bold leading-tight">
//                 Your Smart
//                 <br />
//                 <span className="bg-gradient-to-r from-primary to-primary-glow bg-clip-text text-transparent">
//                   Financial
//                 </span>
//                 <br />
//                 Companion
//               </h1>
              
//               <p className="text-xl text-muted-foreground leading-relaxed max-w-lg">
//                 Take control of your finances with AI-powered insights, 
//                 smart planning tools, and personalized guidance.
//               </p>
//             </div>

//             {/* Action Buttons */}
//             <div className="flex flex-col sm:flex-row gap-4">
//               <Link to="/login">
//                 <Button variant="hero" size="xl" className="w-full sm:w-auto">
//                   Get Started Free
//                   <ArrowRight className="w-5 h-5 ml-2" />
//                 </Button>
//               </Link>
//               <Button variant="outline" size="xl" className="w-full sm:w-auto">
//                 <Play className="w-5 h-5 mr-2" />
//                 Watch Demo
//               </Button>
//             </div>

//             {/* Download Options */}
//             <div className="space-y-4">
//               <p className="text-sm text-muted-foreground">Download our mobile app:</p>
//               <div className="flex flex-col sm:flex-row gap-3">
//                 <Button variant="finance" className="justify-start">
//                   <Apple className="w-5 h-5 mr-3" />
//                   <div className="text-left">
//                     <div className="text-xs text-muted-foreground">Download on</div>
//                     <div className="font-semibold">App Store</div>
//                   </div>
//                 </Button>
//                 <Button variant="finance" className="justify-start">
//                   <Smartphone className="w-5 h-5 mr-3" />
//                   <div className="text-left">
//                     <div className="text-xs text-muted-foreground">Get it on</div>
//                     <div className="font-semibold">Google Play</div>
//                   </div>
//                 </Button>
//               </div>
//             </div>
//           </div>

//           {/* Right Column - Hero Image */}
//           <div className="flex justify-center lg:justify-end">
//             <div className="relative max-w-md w-full">
//               <div className="absolute inset-0 bg-gradient-to-br from-primary/20 to-primary-glow/20 rounded-3xl blur-3xl"></div>
//               <img
//                 src={heroImage}
//                 alt="Financial Dashboard"
//                 className="relative z-10 w-full h-auto rounded-2xl shadow-2xl"
//               />
//             </div>
//           </div>
//         </div>

//         {/* Stats Row */}
//         <div className="mt-20 pt-12 border-t border-border">
//           <div className="grid grid-cols-2 lg:grid-cols-4 gap-8 text-center">
//             <div>
//               <div className="text-3xl font-bold text-primary mb-2">10K+</div>
//               <div className="text-muted-foreground">Active Users</div>
//             </div>
//             <div>
//               <div className="text-3xl font-bold text-primary mb-2">₹100Cr+</div>
//               <div className="text-muted-foreground">Assets Managed</div>
//             </div>
//             <div>
//               <div className="text-3xl font-bold text-primary mb-2">95%</div>
//               <div className="text-muted-foreground">Success Rate</div>
//             </div>
//             <div>
//               <div className="text-3xl font-bold text-primary mb-2">24/7</div>
//               <div className="text-muted-foreground">AI Support</div>
//             </div>
//           </div>
//         </div>
//       </div>
//     </section>
//   );
// };

// export default HeroSection;

import { Button } from "@/components/ui/button";
import { ArrowRight, Play, Smartphone, Apple } from "lucide-react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import heroImage from "@/assets/hero-finance.jpg";

// Animation variants
const fadeUp = {
  hidden: { opacity: 0, y: 40 },
  visible: (delay = 0) => ({
    opacity: 1,
    y: 0,
    transition: { delay, duration: 0.6, ease: "easeOut" },
  }),
};

const HeroSection = () => {
  return (
    <section className="relative min-h-screen flex items-center justify-center py-20 overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-background via-background to-primary/5"></div>

      {/* Content */}
      <div className="relative z-10 max-w-6xl mx-auto px-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
          
          {/* Text Content */}
          <motion.div
            className="space-y-8"
            initial="hidden"
            animate="visible"
          >
            <motion.div className="space-y-6">
              <motion.h1
                className="text-5xl lg:text-6xl font-bold leading-tight"
                variants={fadeUp}
                custom={0.1}
              >
                Your Smart <br />
                <span className="bg-gradient-to-r from-primary to-primary-glow bg-clip-text text-transparent">
                  Financial
                </span>
                <br />
                Companion
              </motion.h1>

              <motion.p
                className="text-xl text-muted-foreground leading-relaxed max-w-lg"
                variants={fadeUp}
                custom={0.3}
              >
                Take control of your finances with AI-powered insights, 
                smart planning tools, and personalized guidance.
              </motion.p>
            </motion.div>

            {/* Action Buttons */}
            <motion.div
              className="flex flex-col sm:flex-row gap-4"
              variants={fadeUp}
              custom={0.5}
            >
              <Link to="/login">
                <Button variant="hero" size="xl" className="w-full sm:w-auto">
                  Get Started Free
                  <ArrowRight className="w-5 h-5 ml-2" />
                </Button>
              </Link>
              <Button variant="outline" size="xl" className="w-full sm:w-auto">
                <Play className="w-5 h-5 mr-2" />
                Watch Demo
              </Button>
            </motion.div>

            {/* App Download */}
            <motion.div
              className="space-y-4"
              variants={fadeUp}
              custom={0.6}
            >
              <p className="text-sm text-muted-foreground">Download our mobile app:</p>
              <div className="flex flex-col sm:flex-row gap-3">
                <Button variant="finance" className="justify-start">
                  <Apple className="w-5 h-5 mr-3" />
                  <div className="text-left">
                    <div className="text-xs text-muted-foreground">Download on</div>
                    <div className="font-semibold">App Store</div>
                  </div>
                </Button>
                <Button variant="finance" className="justify-start">
                  <Smartphone className="w-5 h-5 mr-3" />
                  <div className="text-left">
                    <div className="text-xs text-muted-foreground">Get it on</div>
                    <div className="font-semibold">Google Play</div>
                  </div>
                </Button>
              </div>
            </motion.div>
          </motion.div>

          {/* Hero Image */}
          <motion.div
            className="flex justify-center lg:justify-end"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.4, duration: 0.8 }}
          >
            <div className="relative max-w-md w-full">
              <div className="absolute inset-0 bg-gradient-to-br from-primary/20 to-primary-glow/20 rounded-3xl blur-3xl"></div>
              <img
                src={heroImage}
                alt="Financial Dashboard"
                className="relative z-10 w-full h-auto rounded-2xl shadow-2xl"
              />
            </div>
          </motion.div>
        </div>

        {/* Stats Row */}
        <motion.div
          className="mt-20 pt-12 border-t border-border"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={{
            hidden: {},
            visible: {
              transition: {
                staggerChildren: 0.2,
              },
            },
          }}
        >
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-8 text-center">
            {[
              ["10K+", "Active Users"],
              ["₹100Cr+", "Assets Managed"],
              ["95%", "Success Rate"],
              ["24/7", "AI Support"],
            ].map(([value, label], index) => (
              <motion.div key={index} variants={fadeUp}>
                <div className="text-3xl font-bold text-primary mb-2">{value}</div>
                <div className="text-muted-foreground">{label}</div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default HeroSection;
