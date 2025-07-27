#!/usr/bin/env python3
"""
Environment Setup Script
Helps configure the .env file with your actual API keys
"""

import os
import re

def update_env_file():
    """Update the .env file with user input"""
    
    print("🔧 Alpha Vantage Environment Setup")
    print("=" * 40)
    
    # Check if .env exists
    if not os.path.exists('.env'):
        print("❌ .env file not found. Please run 'copy env_template.txt .env' first.")
        return False
    
    # Read current .env content
    with open('.env', 'r') as f:
        content = f.read()
    
    # Get Alpha Vantage API key
    print("\n📝 Please enter your Alpha Vantage API key:")
    print("   Get it from: https://www.alphavantage.co/support/#api-key")
    api_key = input("   API Key: ").strip()
    
    if not api_key:
        print("❌ API key is required!")
        return False
    
    # Update the API key in .env content
    content = re.sub(
        r'ALPHA_VANTAGE_API_KEY=.*',
        f'ALPHA_VANTAGE_API_KEY={api_key}',
        content
    )
    
    # Also set some basic values for testing
    content = re.sub(
        r'GCP_PROJECT_ID=.*',
        'GCP_PROJECT_ID=test-project',
        content
    )
    
    content = re.sub(
        r'JWT_SECRET_KEY=.*',
        'JWT_SECRET_KEY=test-secret-key-for-development',
        content
    )
    
    # Write updated content
    with open('.env', 'w') as f:
        f.write(content)
    
    print(f"\n✅ Updated .env file with your API key: {api_key[:8]}...")
    return True

def test_configuration():
    """Test if the configuration is working"""
    
    print("\n🧪 Testing configuration...")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    
    if api_key and api_key != 'your-alpha-vantage-api-key':
        print(f"✅ API Key found: {api_key[:8]}...")
        return True
    else:
        print("❌ API Key not properly configured")
        return False

def main():
    """Main setup function"""
    
    print("🚀 Welcome to the Alpha Vantage Setup!")
    print("This will help you configure your environment for testing.")
    
    # Update .env file
    if update_env_file():
        # Test configuration
        if test_configuration():
            print("\n🎉 Setup completed successfully!")
            print("\nNext steps:")
            print("1. Run: python test_alpha_vantage.py")
            print("2. If tests pass, you can start using the market data features")
        else:
            print("\n⚠️  Configuration test failed. Please check your .env file.")
    else:
        print("\n❌ Setup failed. Please try again.")

if __name__ == "__main__":
    main() 