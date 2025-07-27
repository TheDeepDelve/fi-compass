// import { Link } from "react-router-dom";
// import { 
//   Facebook, 
//   Twitter, 
//   Instagram, 
//   Linkedin, 
//   Mail, 
//   Phone, 
//   MapPin,
//   Smartphone,
//   Download
// } from "lucide-react";

// const Footer = () => {
//   const currentYear = new Date().getFullYear();

//   const footerSections = [
//     {
//       title: "Features",
//       links: [
//         { name: "Smart Analytics", href: "#features" },
//         { name: "Goal Tracking", href: "#features" },
//         { name: "Investment Tools", href: "#features" },
//         { name: "AI Assistant", href: "#chatbot" }
//       ]
//     },
//     {
//       title: "Support",
//       links: [
//         { name: "Help Center", href: "#help" },
//         { name: "Contact Us", href: "#contact" },
//         { name: "Community", href: "#community" },
//         { name: "Status", href: "#status" }
//       ]
//     },
//     {
//       title: "About",
//       links: [
//         { name: "About Us", href: "#about" },
//         { name: "Privacy Policy", href: "#privacy" },
//         { name: "Terms of Service", href: "#terms" },
//         { name: "Security", href: "#security" }
//       ]
//     }
//   ];

//   return (
//     <footer className="bg-background border-t border-border">
//       <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
//         {/* Main Footer Content */}
//         <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
//           {/* Brand Section */}
//           <div>
//             <Link to="/" className="text-2xl font-bold text-primary mb-4 block">
//               Fi Compass
//             </Link>
//             <p className="text-muted-foreground mb-6 max-w-md">
//               Your intelligent financial companion that helps you navigate investments, 
//               track expenses, and achieve your financial goals with AI-powered insights.
//             </p>
            
//             {/* Download Section */}
//             {/* <div className="mb-6">
//               <h4 className="font-semibold text-foreground mb-3">Download Our App</h4>
//               <div className="flex flex-col sm:flex-row gap-3">
//                 <a 
//                   href="#ios-download" 
//                   className="flex items-center gap-3 bg-card hover:bg-accent transition-colors p-3 rounded-lg border border-border"
//                 >
//                   <Smartphone className="w-6 h-6 text-primary" />
//                   <div>
//                     <div className="text-xs text-muted-foreground">Download on</div>
//                     <div className="font-semibold">App Store</div>
//                   </div>
//                 </a>
//                 <a 
//                   href="#android-download" 
//                   className="flex items-center gap-3 bg-card hover:bg-accent transition-colors p-3 rounded-lg border border-border"
//                 >
//                   <Download className="w-6 h-6 text-primary" />
//                   <div>
//                     <div className="text-xs text-muted-foreground">Get it on</div>
//                     <div className="font-semibold">Google Play</div>
//                   </div>
//                 </a>
//               </div>
//             </div> */}

//             {/* Contact Info */}
//             <div className="space-y-2 text-sm text-muted-foreground">
//               <div className="flex items-center gap-2">
//                 <Mail className="w-4 h-4" />
//                 <span>support@ficompass.com</span>
//               </div>
//               <div className="flex items-center gap-2">
//                 <Phone className="w-4 h-4" />
//                 <span>+91 1800-123-4567</span>
//               </div>
//               <div className="flex items-center gap-2">
//                 <MapPin className="w-4 h-4" />
//                 <span>Bengaluru, Karnatka, India</span>
//               </div>
//             </div>
//           </div>

//           {/* Footer Links in Three Columns */}
//           <div className="lg:col-span-3">
//             <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
//               {footerSections.map((section, index) => (
//                 <div key={index}>
//                   <h4 className="font-semibold text-foreground mb-4">{section.title}</h4>
//                   <ul className="space-y-3">
//                     {section.links.map((link, linkIndex) => (
//                       <li key={linkIndex}>
//                         {link.name === "AI Assistant" ? (
//                           <button 
//                             onClick={() => window.postMessage('openChatbot', '*')} 
//                             className="text-muted-foreground hover:text-primary transition-colors text-sm text-left"
//                           >
//                             {link.name}
//                           </button>
//                         ) : (
//                           <a 
//                             href={link.href} 
//                             className="text-muted-foreground hover:text-primary transition-colors text-sm"
//                           >
//                             {link.name}
//                           </a>
//                         )}
//                       </li>
//                     ))}
//                   </ul>
//                 </div>
//               ))}
//             </div>
//           </div>
//         </div>

//         <div className="border-t border-border mt-12 pt-8">
//           <div className="flex flex-col md:flex-row justify-between items-center gap-4">
//             {/* Copyright */}
//             <div className="text-sm text-muted-foreground">
//               © {currentYear} Fi Compass. All rights reserved. | Built with for better financial health.
//             </div>

//             {/* Social Links */}
//             <div className="flex items-center gap-4">
//               <span className="text-sm text-muted-foreground mr-2">Follow us:</span>
//               <a href="#facebook" className="text-muted-foreground hover:text-primary transition-colors">
//                 <Facebook className="w-5 h-5" />
//               </a>
//               <a href="#twitter" className="text-muted-foreground hover:text-primary transition-colors">
//                 <Twitter className="w-5 h-5" />
//               </a>
//               <a href="#instagram" className="text-muted-foreground hover:text-primary transition-colors">
//                 <Instagram className="w-5 h-5" />
//               </a>
//               <a href="#linkedin" className="text-muted-foreground hover:text-primary transition-colors">
//                 <Linkedin className="w-5 h-5" />
//               </a>
//             </div>
//           </div>
//         </div>
//       </div>
//     </footer>
//   );
// };

// export default Footer;

import { Link } from "react-router-dom";
import { 
  Facebook, 
  Twitter, 
  Instagram, 
  Linkedin, 
  Mail, 
  Phone, 
  MapPin,
  Smartphone,
  Download
} from "lucide-react";

const Footer = () => {
  const currentYear = new Date().getFullYear();

  const footerSections = [
    {
      title: "Features",
      links: [
        { name: "Smart Analytics", href: "#features" },
        { name: "Goal Tracking", href: "#features" },
        { name: "Investment Tools", href: "#features" },
        { name: "AI Assistant", href: "#chatbot" } // Will trigger button below
      ]
    },    
    {
      title: "About",
      links: [
        { name: "About Us", href: "#about" },
        { name: "Privacy Policy", href: "#privacy" },
        { name: "Terms of Service", href: "#terms" },
        { name: "Security", href: "#security" }
      ]
    },
    {
      title: "Support",
      links: [
        { name: "Help Center", href: "#help" },
        { name: "Contact Us", href: "#contact" }
      ]
    }
  ];

  return (
    <footer className="bg-background border-t border-border">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Main Footer Content */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Brand Section */}
          <div>
            <Link to="/" className="text-2xl font-bold text-primary mb-4 block">
              Fi Compass
            </Link>
            <p className="text-muted-foreground mb-6 max-w-md">
              Your intelligent financial companion that helps you navigate investments, 
              track expenses, and achieve your financial goals with AI-powered insights.
            </p>

            {/* Contact Info */}
            <div className="space-y-2 text-sm text-muted-foreground">
              <div className="flex items-center gap-2">
                <Mail className="w-4 h-4" />
                <span>support@ficompass.com</span>
              </div>
              <div className="flex items-center gap-2">
                <Phone className="w-4 h-4" />
                <span>+91 1800-123-4567</span>
              </div>
              <div className="flex items-center gap-2">
                <MapPin className="w-4 h-4" />
                <span>Bengaluru, Karnatka, India</span>
              </div>
            </div>
          </div>

          {/* Footer Links in Three Columns */}
          <div className="lg:col-span-3">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {footerSections.map((section, index) => (
                <div key={index}>
                  <h4 className="font-semibold text-foreground mb-4">{section.title}</h4>
                  <ul className="space-y-3">
                    {section.links.map((link, linkIndex) => (
                      <li key={linkIndex}>
                        {link.name === "AI Assistant" ? (
                          <button 
                            onClick={() => window.postMessage('openChatbot', '*')} 
                            className="text-muted-foreground hover:text-primary transition-colors text-sm text-left"
                          >
                            {link.name}
                          </button>
                        ) : (
                          <a 
                            href={link.href} 
                            className="text-muted-foreground hover:text-primary transition-colors text-sm"
                          >
                            {link.name}
                          </a>
                        )}
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="border-t border-border mt-12 pt-8">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            {/* Copyright */}
            <div className="text-sm text-muted-foreground">
              © {currentYear} Fi Compass. All rights reserved. | Built with for better financial health.
            </div>

            {/* Social Links */}
            <div className="flex items-center gap-4">
              <span className="text-sm text-muted-foreground mr-2">Follow us:</span>
              <a href="#facebook" className="text-muted-foreground hover:text-primary transition-colors">
                <Facebook className="w-5 h-5" />
              </a>
              <a href="#twitter" className="text-muted-foreground hover:text-primary transition-colors">
                <Twitter className="w-5 h-5" />
              </a>
              <a href="#instagram" className="text-muted-foreground hover:text-primary transition-colors">
                <Instagram className="w-5 h-5" />
              </a>
              <a href="#linkedin" className="text-muted-foreground hover:text-primary transition-colors">
                <Linkedin className="w-5 h-5" />
              </a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
