# Fi Compass - AI-Powered Financial Management Platform

[![React](https://img.shields.io/badge/React-18.3.1-blue.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.5.3-blue.svg)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/Vite-5.4.1-purple.svg)](https://vitejs.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4.11-38B2AC.svg)](https://tailwindcss.com/)

Fi Compass is a comprehensive financial management platform that combines AI-powered insights with traditional financial tools to help users take control of their finances. Built with modern web technologies, it offers a seamless experience for tracking investments, analyzing spending patterns, and receiving personalized financial guidance.

## Features

### Core Features
- **AI-Powered Financial Assistant** - Chat with an intelligent financial advisor
- **Dual Dashboard Modes** - Pilot Mode for overview and Navigator Mode for detailed analysis
- **Real-time Market Data** - Live stock prices, charts, and market alerts
- **Investment Tracking** - Monitor stocks, mutual funds, and other investments
- **Spending Analysis** - Track and categorize expenses with AI insights
- **Net Worth Calculator** - Comprehensive asset and liability tracking
- **Subscription Tracker** - Monitor recurring payments and subscriptions

### AI & Analytics
- **Smart Chatbot** - Financial advice with markdown-free responses
- **Spending Pattern Analysis** - AI-powered insights into spending habits
- **Financial Insights** - Personalized recommendations and analysis
- **Knowledge Base (RAG)** - Document upload and intelligent search
- **Market Alerts** - Custom alerts for price movements and news

### User Experience
- **Responsive Design** - Works seamlessly on desktop and mobile
- **Dark/Light Theme** - Modern UI with smooth animations
- **Real-time Updates** - Live data synchronization
- **Demo Mode** - Try features without real data
- **Toast Notifications** - User-friendly feedback system

## Technology Stack

### Frontend
- **React 18** - Modern UI library with hooks
- **TypeScript** - Type-safe development
- **Vite** - Fast build tool and dev server
- **React Router** - Client-side routing
- **Framer Motion** - Smooth animations and transitions

### UI Components
- **Shadcn/ui** - High-quality, accessible components
- **Radix UI** - Unstyled, accessible primitives
- **Tailwind CSS** - Utility-first CSS framework
- **Lucide React** - Beautiful, customizable icons

### State Management & Data
- **TanStack Query** - Server state management
- **React Hook Form** - Form handling and validation
- **Zod** - Schema validation

### Charts & Visualization
- **Chart.js** - Flexible charting library
- **React Chart.js 2** - React wrapper for Chart.js
- **Recharts** - Composable charting library

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── ui/             # Shadcn/ui components
│   ├── dashboard/      # Dashboard-specific components
│   ├── Chatbot.tsx     # AI chat interface
│   ├── HeroSection.tsx # Landing page hero
│   └── ...
├── hooks/              # Custom React hooks
│   ├── useApi.ts       # API integration hooks
│   └── use-toast.ts    # Toast notification hook
├── lib/                # Utility functions
│   ├── api.ts          # API client functions
│   ├── utils.ts        # General utilities
│   └── gemini-test.ts  # AI integration
├── pages/              # Route components
│   ├── Dashboard.tsx   # Main dashboard
│   ├── Index.tsx       # Landing page
│   └── Login.tsx       # Authentication
└── assets/             # Static assets
```

## Getting Started

### Prerequisites
- Node.js 18+ 
- npm or yarn package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd fi-compass
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```

4. **Open your browser**
   Navigate to `http://localhost:5173`

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run build:dev` - Build for development
- `npm run lint` - Run ESLint
- `npm run preview` - Preview production build

## Architecture

### Component Architecture
The application follows a modular component architecture:

- **Pages** - Top-level route components
- **Components** - Reusable UI components
- **Hooks** - Custom logic and API integration
- **Utils** - Helper functions and utilities

### State Management
- **TanStack Query** - Server state and caching
- **React State** - Local component state
- **Local Storage** - User preferences and session data

### API Integration
The application integrates with multiple financial APIs:

- **Authentication** - User login/logout
- **Financial Data** - Net worth, transactions, investments
- **Market Data** - Real-time stock prices and charts
- **AI Services** - Chatbot and financial insights
- **Knowledge Base** - Document management and search

## UI/UX Features

### Design System
- **Consistent Theming** - Dark/light mode support
- **Responsive Design** - Mobile-first approach
- **Accessibility** - WCAG compliant components
- **Smooth Animations** - Framer Motion integration

### Key Components
- **Chatbot** - AI assistant with markdown-free responses
- **Dashboard** - Dual-mode financial overview
- **Charts** - Interactive financial visualizations
- **Modals** - Feature-rich overlay components
- **Forms** - Validated input components

## AI Integration

### Chatbot Features
- **Markdown Removal** - Clean, readable responses
- **Financial Context** - Personalized advice based on user data
- **Conversation History** - Persistent chat sessions
- **Real-time Responses** - Instant AI assistance

### AI Capabilities
- **Financial Analysis** - Spending pattern insights
- **Investment Advice** - Personalized recommendations
- **Document Processing** - Knowledge base integration
- **Market Analysis** - Real-time market insights

## Dashboard Modes

### Pilot Mode
- **Overview Dashboard** - Key financial metrics
- **Quick Actions** - Common financial tasks
- **Recent Activity** - Latest transactions and updates
- **AI Insights** - Personalized recommendations

### Navigator Mode
- **Detailed Analysis** - Comprehensive financial data
- **Advanced Charts** - Interactive visualizations
- **Custom Reports** - Tailored financial reports
- **Deep Insights** - In-depth financial analysis

## Configuration

### Environment Variables
Create a `.env` file in the root directory:

```env
VITE_API_BASE_URL=your_api_base_url
VITE_AI_SERVICE_URL=your_ai_service_url
VITE_MARKET_DATA_URL=your_market_data_url
```

### API Integration
The application is designed to work with various financial APIs:

- **Authentication APIs** - User management
- **Financial Data APIs** - Transaction and investment data
- **Market Data APIs** - Real-time stock information
- **AI Service APIs** - Chatbot and analysis services

## Testing

### Development Testing
- **ESLint** - Code quality and consistency
- **TypeScript** - Type safety and error checking
- **Hot Reload** - Instant development feedback

### Manual Testing
- **Demo Mode** - Test features without real data
- **Responsive Testing** - Cross-device compatibility
- **Browser Testing** - Cross-browser compatibility

## Mobile Support

The application is fully responsive and optimized for mobile devices:

- **Touch-friendly Interface** - Optimized for touch interactions
- **Mobile Navigation** - Collapsible sidebar and menus
- **Responsive Charts** - Touch-enabled visualizations
- **Mobile Chatbot** - Optimized chat interface

## Security

### Data Protection
- **Local Storage** - Secure session management
- **API Security** - Authenticated API calls
- **Input Validation** - Form validation and sanitization
- **Error Handling** - Graceful error management

### Privacy
- **Demo Mode** - Test without real financial data
- **Data Encryption** - Secure data transmission
- **Session Management** - Secure user sessions

## Deployment

### Build for Production
```bash
npm run build
```

### Deploy Options
- **Vercel** - Recommended for React applications
- **Netlify** - Static site hosting
- **AWS S3** - Static website hosting
- **Docker** - Containerized deployment

## Contributing

### Development Guidelines
1. **Fork the repository**
2. **Create a feature branch** - `git checkout -b feature/amazing-feature`
3. **Commit your changes** - `git commit -m 'Add amazing feature'`
4. **Push to the branch** - `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### Code Standards
- **TypeScript** - Strict type checking
- **ESLint** - Code quality enforcement
- **Prettier** - Code formatting
- **Conventional Commits** - Standard commit messages

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Shadcn/ui** - Beautiful, accessible components
- **Framer Motion** - Smooth animations
- **TanStack Query** - Powerful data fetching
- **Tailwind CSS** - Utility-first styling
- **Lucide** - Beautiful icons

## Support

For support and questions:
- **Documentation** - Check the API integration docs
- **Issues** - Report bugs and feature requests
- **Discussions** - Community discussions and help

---

**Fi Compass** - Your Smart Financial Companion 🚀
