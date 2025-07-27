import Navbar from "@/components/Navbar";
import HeroSection from "@/components/HeroSection";
import FeaturesSection from "@/components/FeaturesSection";
import Footer from "@/components/Footer";
import Chatbot from "@/components/Chatbot";

const Index = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#18181b] via-[#23272f] to-[#2e374a]">
      <Navbar />
      <div className="mt-10"> {/* Reduced margin-top for spacing */}
        <HeroSection />
      </div>
      <FeaturesSection />
      <Footer />
      <Chatbot />
    </div>
  );
};

export default Index;
