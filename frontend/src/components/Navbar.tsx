import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Menu, X, MessageCircle, Download, HelpCircle } from "lucide-react";
import { Link } from "react-router-dom";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Avatar, AvatarImage, AvatarFallback } from "@/components/ui/avatar";

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);

  const teamMembers = [
    {
      name: "Rakesh Roushan",
      email: "rakeshroushan6200@gmail.com",
      photo: "/lovable-uploads/f3a81e68-b8d5-4dff-a4b0-3a091634fb92.png"
    },
    {
      name: "Rakesh Roushan",
      email: "rakeshroushan6200@gmail.com",
      photo: "/lovable-uploads/f3a81e68-b8d5-4dff-a4b0-3a091634fb92.png"
    },
    {
      name: "Rakesh Roushan",
      email: "rakeshroushan6200@gmail.com",
      photo: "/lovable-uploads/f3a81e68-b8d5-4dff-a4b0-3a091634fb92.png"
    },
    {
      name: "Rakesh Roushan",
      email: "rakeshroushan6200@gmail.com",
      photo: "/lovable-uploads/f3a81e68-b8d5-4dff-a4b0-3a091634fb92.png"
    },
    {
      name: "Rakesh Roushan",
      email: "rakeshroushan6200@gmail.com",
      photo: "/lovable-uploads/f3a81e68-b8d5-4dff-a4b0-3a091634fb92.png"
    }
  ];

  return (
    <nav className="fixed top-0 w-full z-50 bg-background/80 backdrop-blur-lg border-b border-border">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center">
            <button onClick={() => window.location.reload()} className="text-2xl font-bold text-primary">
              Fi Compass
            </button>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            <a
              href="#features"
              className="text-foreground hover:text-primary transition-colors"
              onClick={(e) => {
                e.preventDefault();
                document.getElementById('features')?.scrollIntoView({
                  behavior: 'smooth'
                });
              }}
            >
              Features
            </a>
            <Link to="#about" className="text-foreground hover:text-primary transition-colors">
              About
            </Link>
            <Dialog>
              <DialogTrigger asChild>
                <Button variant="ghost" size="sm">
                  <HelpCircle className="w-4 h-4 mr-2" />
                  Help
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-2xl">
                <DialogHeader>
                  <DialogTitle>Meet Our Team</DialogTitle>
                </DialogHeader>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                  {teamMembers.map((member, index) => (
                    <div key={index} className="flex items-center space-x-3 p-4 border rounded-lg">
                      <Avatar className="h-12 w-12">
                        <AvatarImage src={member.photo} alt={member.name} />
                        <AvatarFallback>{member.name.split(' ').map(n => n[0]).join('')}</AvatarFallback>
                      </Avatar>
                      <div>
                        <h3 className="font-semibold">{member.name}</h3>
                        <p className="text-sm text-muted-foreground">{member.email}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </DialogContent>
            </Dialog>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => window.postMessage('openChatbot', '*')}
            >
              <MessageCircle className="w-4 h-4 mr-2" />
              Chat
            </Button>

            <Link to="/login">
              <Button variant="hero" size="sm">
                Login/Sign Up
              </Button>
            </Link>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsOpen(!isOpen)}
            >
              {isOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </Button>
          </div>
        </div>
      </div>

      {/* Mobile Navigation */}
      {isOpen && (
        <div className="md:hidden">
          <div className="px-2 pt-2 pb-3 space-y-1 bg-background border-b border-border">
            <a
              href="#features"
              className="block px-3 py-2 text-foreground hover:text-primary transition-colors"
              onClick={(e) => {
                e.preventDefault();
                setIsOpen(false);
                document.getElementById('features')?.scrollIntoView({
                  behavior: 'smooth'
                });
              }}
            >
              Features
            </a>
            <Link
              to="#about"
              className="block px-3 py-2 text-foreground hover:text-primary transition-colors"
              onClick={() => setIsOpen(false)}
            >
              About
            </Link>
            <div className="px-3 py-2">
              <Dialog>
                <DialogTrigger asChild>
                  <Button variant="ghost" size="sm" className="w-full justify-start">
                    <HelpCircle className="w-4 h-4 mr-2" />
                    Help
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-w-2xl">
                  <DialogHeader>
                    <DialogTitle>Meet Our Team</DialogTitle>
                  </DialogHeader>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                    {teamMembers.map((member, index) => (
                      <div key={index} className="flex items-center space-x-3 p-4 border rounded-lg">
                        <Avatar className="h-12 w-12">
                          <AvatarImage src={member.photo} alt={member.name} />
                          <AvatarFallback>{member.name.split(' ').map(n => n[0]).join('')}</AvatarFallback>
                        </Avatar>
                        <div>
                          <h3 className="font-semibold">{member.name}</h3>
                          <p className="text-sm text-muted-foreground">{member.email}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </DialogContent>
              </Dialog>
            </div>
            <div className="px-3 py-2">
              <Button
                variant="ghost"
                size="sm"
                className="w-full justify-start"
                onClick={() => window.dispatchEvent(new Event('message'))}
              >
                <MessageCircle className="w-4 h-4 mr-2" />
                Chat
              </Button>
            </div>
            <div className="px-3 py-2">
              <Link to="/login" onClick={() => setIsOpen(false)}>
                <Button variant="hero" size="sm" className="w-full">
                  Get Started
                </Button>
              </Link>
            </div>
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;