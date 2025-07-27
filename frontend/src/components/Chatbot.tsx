import { useEffect, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { MessageCircle, X, Send } from "lucide-react";
import { Input } from "@/components/ui/input";
import { AnimatePresence, motion } from "framer-motion";

interface ChatbotProps {
  buttonPosition?: string;
}

const Chatbot = ({ buttonPosition = "bottom-4 right-4" }: ChatbotProps) => {
  const [isOpen, setIsOpen] = useState(false);
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([
    {
      type: "bot",
      content: "Hi! I'm your Fi Guru AI assistant. How can I help you with your finances today?",
    },
  ]);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const handleSendMessage = () => {
    if (!message.trim()) return;

    setMessages((prev) => [...prev, { type: "user", content: message }]);
    setMessage("");

    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        {
          type: "bot",
          content: "Thanks for your message! I'm here to help with any financial questions you have.",
        },
      ]);
    }, 1000);
  };

  // Listener for footer button trigger
  useEffect(() => {
    const handleMessage = (event: MessageEvent) => {
      if (event.data === "openChatbot") {
        setIsOpen(true);
      }
    };

    window.addEventListener("message", handleMessage);
    return () => window.removeEventListener("message", handleMessage);
  }, []);

  // 👇 Scroll to bottom when messages update
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <>
      {/* Right-side Chatbot Panel */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ x: 100, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: 100, opacity: 0 }}
            transition={{ duration: 0.3, ease: "easeInOut" }}
            className="fixed top-0 right-0 bottom-0 w-96 max-w-full bg-background border-l border-border shadow-2xl z-50 flex flex-col"
          >
            <div className="flex items-center justify-between p-4 border-b">
              <CardTitle className="text-lg">FI Guru</CardTitle>
              <Button variant="ghost" size="icon" onClick={() => setIsOpen(false)}>
                <X className="w-5 h-5" />
              </Button>
            </div>
            <div className="flex-1 flex flex-col overflow-hidden">
              <div className="flex-1 overflow-y-auto p-4 space-y-3">
                {messages.map((msg, index) => (
                  <div
                    key={index}
                    className={`flex ${msg.type === "user" ? "justify-end" : "justify-start"}`}
                  >
                    <div
                      className={`max-w-[80%] p-3 rounded-lg text-sm ${
                        msg.type === "user"
                          ? "bg-primary text-primary-foreground"
                          : "bg-muted text-muted-foreground"
                      }`}
                    >
                      {msg.content}
                    </div>
                  </div>
                ))}
                <div ref={messagesEndRef} />
              </div>
              <div className="p-4 border-t bg-background">
                <div className="flex gap-2">
                  <Input
                    placeholder="Ask me anything..."
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleSendMessage()}
                    className="flex-1"
                  />
                  <Button size="sm" onClick={handleSendMessage}>
                    <Send className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Chat Bubble Button */}
      <Button
        className={`fixed ${buttonPosition} w-14 h-14 rounded-full shadow-lg z-40`}
        variant="hero"
        onClick={() => setIsOpen(!isOpen)}
      >
        <MessageCircle className="w-6 h-6" />
      </Button>
    </>
  );
};

export default Chatbot;
