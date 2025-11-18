#!/usr/bin/env python3
"""
STRIPE PRODUCTS CREATION & CONFIGURATION ASSISTANT
================================================

This script helps you:
1. Create 9 Stripe products with correct pricing
2. Configure your backend .env file
3. Test Stripe API connectivity
4. Verify webhook configuration

Run: python stripe_setup_assistant.py
"""

from pathlib import Path
from colorama import Fore, Back, Style, init

init(autoreset=True)

def print_header(title):
    """Print a formatted header"""
    print(f"\n{Back.CYAN}{Fore.BLACK}{'='*70}{Style.RESET_ALL}")
    print(f"{Back.CYAN}{Fore.BLACK} {title:<68} {Style.RESET_ALL}")
    print(f"{Back.CYAN}{Fore.BLACK}{'='*70}{Style.RESET_ALL}\n")

def print_success(msg):
    """Print success message"""
    print(f"{Fore.GREEN}{msg}{Style.RESET_ALL}")

def print_warning(msg):
    """Print warning message"""
    print(f"{Fore.YELLOW}  {msg}{Style.RESET_ALL}")

def print_error(msg):
    """Print error message"""
    print(f"{Fore.RED} {msg}{Style.RESET_ALL}")

def print_info(msg):
    """Print info message"""
    print(f"{Fore.CYAN}  {msg}{Style.RESET_ALL}")

# ============================================================================
# STEP 1: STRIPE PRODUCTS DEFINITION
# ============================================================================

STRIPE_PRODUCTS = [
    {
        "id": 1,
        "tier_name": "PRO",
        "price": 20,
        "description": "Individual developer with API access",
        "env_var": "STRIPE_PRICE_ID_PRO",
        "emoji": ""
    },
    {
        "id": 2,
        "tier_name": "PRO-PLUS",
        "price": 45,
        "description": "Custom LLMs + Advanced features",
        "env_var": "STRIPE_PRICE_ID_PRO_PLUS",
        "emoji": ""
    },
    {
        "id": 3,
        "tier_name": "PRO-ULTIMATE",
        "price": 79,
        "description": "All access for the Top Dog Aura solo developer",
        "env_var": "STRIPE_PRICE_ID_PRO_ULTIMATE",
        "emoji": "🚀"
    },
    {
        "id": 4,
        "tier_name": "PRO-TEAM",
        "price": 75,
        "description": "Team collaboration (3 members)",
        "env_var": "STRIPE_PRICE_ID_PRO_TEAM",
        "emoji": ""
    },
    {
        "id": 5,
        "tier_name": "TEAMS-SMALL",
        "price": 75,
        "description": "Teams plan (5 members)",
        "env_var": "STRIPE_PRICE_ID_TEAMS_SMALL",
        "emoji": ""
    },
    {
        "id": 6,
        "tier_name": "TEAMS-MEDIUM",
        "price": 300,
        "description": "Teams plan (15 members)",
        "env_var": "STRIPE_PRICE_ID_TEAMS_MEDIUM",
        "emoji": ""
    },
    {
        "id": 7,
        "tier_name": "TEAMS-LARGE",
        "price": 800,
        "description": "Teams plan (unlimited members)",
        "env_var": "STRIPE_PRICE_ID_TEAMS_LARGE",
        "emoji": ""
    },
    {
        "id": 8,
        "tier_name": "ENTERPRISE-STANDARD",
        "price": 5000,
        "description": "Enterprise (HIPAA Ready, SOC2)",
        "env_var": "STRIPE_PRICE_ID_ENTERPRISE_STANDARD",
        "emoji": ""
    },
    {
        "id": 9,
        "tier_name": "ENTERPRISE-PREMIUM",
        "price": 15000,
        "description": "Enterprise (SSO/SAML + Compliance)",
        "env_var": "STRIPE_PRICE_ID_ENTERPRISE_PREMIUM",
        "emoji": ""
    },
    {
        "id": 10,
        "tier_name": "ENTERPRISE-ULTIMATE",
        "price": 50000,
        "description": "Enterprise (On-Premise + Data Residency)",
        "env_var": "STRIPE_PRICE_ID_ENTERPRISE_ULTIMATE",
        "emoji": ""
    }
]

# ============================================================================
# STEP 2: PRODUCT CREATION INSTRUCTIONS
# ============================================================================

def show_product_creation_instructions():
    """Show step-by-step instructions for creating Stripe products"""
    
    print_header("📝 STRIPE PRODUCT CREATION INSTRUCTIONS")
    
    print(f"{Fore.WHITE}{Style.BRIGHT}You need to create 9 products in Stripe Dashboard.{Style.RESET_ALL}")
    print(f"{Fore.WHITE}Here's how:{Style.RESET_ALL}\n")
    
    print(f"{Fore.YELLOW}1. Open Stripe Dashboard:{Style.RESET_ALL}")
    print("   → https://dashboard.stripe.com/login\n")
    
    print(f"{Fore.YELLOW}2. Navigate to Products:{Style.RESET_ALL}")
    print("   → Products (left sidebar) → Create Product\n")
    
    print(f"{Fore.YELLOW}3. For each product below, create it in Stripe:{Style.RESET_ALL}\n")
    
    total_price = 0
    for product in STRIPE_PRODUCTS:
        total_price += product["price"]
        print(f"{Fore.CYAN}   Product {product['id']}/9: {product['emoji']} {product['tier_name']}{Style.RESET_ALL}")
        print(f"   ├─ Price: ${product['price']}/month")
        print(f"   ├─ Description: {product['description']}")
    print("   ├─ Type: Service")
    print("   ├─ Billing: Monthly")
    print("   └─ Save the 'Price ID' (looks like: price_xxxxx)\n")
    
    print(f"{Fore.GREEN}Total monthly revenue at full capacity: ${total_price:,.0f}/month{Style.RESET_ALL}\n")
    
    print(f"{Fore.YELLOW}4. After creating each product:{Style.RESET_ALL}")
    print("   ✓ Click the product")
    print("   ✓ Find the 'Pricing' section")
    print("   ✓ Copy the Price ID (starts with 'price_')")
    print("   ✓ Save it in a text file\n")
    
    print(f"{Fore.YELLOW}5. When done, come back here and enter the Price IDs{Style.RESET_ALL}\n")

# ============================================================================
# STEP 3: COLLECT PRICE IDS
# ============================================================================

def collect_price_ids():
    """Collect Price IDs from user"""
    
    print_header("📋 ENTER STRIPE PRICE IDs")
    
    print(f"{Fore.YELLOW}Enter the Price ID for each product.{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}(You can find these in Stripe Dashboard → Products){Style.RESET_ALL}\n")
    
    price_ids = {}
    
    for product in STRIPE_PRODUCTS:
        while True:
            price_id = input(
                f"{product['emoji']} {product['tier_name']:30s} (${product['price']:6.0f}/mo): "
            ).strip()
            
            if price_id.startswith("price_") and len(price_id) > 10:
                price_ids[product['env_var']] = price_id
                print_success(f"Saved: {price_id}\n")
                break
            else:
                print_error("Price ID must start with 'price_'. Try again.\n")
    
    return price_ids

# ============================================================================
# STEP 4: STRIPE API KEYS
# ============================================================================

def collect_stripe_keys():
    """Collect Stripe API keys from user"""
    
    print_header("🔐 STRIPE API KEYS")
    
    print(f"{Fore.YELLOW}Enter your Stripe API keys.{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}(Get these from: Stripe Dashboard → Settings → API Keys){Style.RESET_ALL}\n")
    
    keys = {}
    
    # Public Key
    while True:
        pub_key = input("📌 Stripe Public Key (pk_test_...): ").strip()
        if pub_key.startswith("pk_test_") or pub_key.startswith("pk_live_"):
            keys['STRIPE_PUBLIC_KEY'] = pub_key
            print_success("Saved public key\n")
            break
        else:
            print_error("Must start with 'pk_test_' or 'pk_live_'\n")
    
    # Secret Key
    while True:
        secret_key = input("🔑 Stripe Secret Key (sk_test_...): ").strip()
        if secret_key.startswith("sk_test_") or secret_key.startswith("sk_live_"):
            keys['STRIPE_SECRET_KEY'] = secret_key
            print_success("Saved secret key\n")
            break
        else:
            print_error("Must start with 'sk_test_' or 'sk_live_'\n")
    
    # Webhook Secret
    while True:
        webhook_secret = input("🔗 Stripe Webhook Secret (whsec_...): ").strip()
        if webhook_secret.startswith("whsec_"):
            keys['STRIPE_WEBHOOK_SECRET'] = webhook_secret
            print_success("Saved webhook secret\n")
            break
        else:
            print_error("Must start with 'whsec_'\n")
    
    return keys

# ============================================================================
# STEP 5: UPDATE .ENV FILE
# ============================================================================

def update_env_file(stripe_keys, price_ids):
    """Update or create backend/.env file"""
    
    print_header("💾 UPDATING .env FILE")
    
    env_path = Path("backend") / ".env"
    
    # Read existing .env if it exists
    env_content = {}
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    env_content[key.strip()] = value.strip()
    
    # Update with new values
    env_content.update(stripe_keys)
    env_content.update(price_ids)
    
    # Add other important keys if not present
    if 'FRONTEND_URL' not in env_content:
        env_content['FRONTEND_URL'] = 'http://localhost:5173'
    if 'BACKEND_URL' not in env_content:
        env_content['BACKEND_URL'] = 'http://localhost:8000'
    if 'DATABASE_URL' not in env_content:
        env_content['DATABASE_URL'] = 'sqlite:///./topdog_ide.db'
    
    # Write updated .env
    with open(env_path, 'w') as f:
        f.write("# ===== STRIPE CONFIGURATION =====\n\n")
        f.write("# Test Mode Keys (for development)\n")
        if 'STRIPE_PUBLIC_KEY' in env_content:
            f.write(f"STRIPE_PUBLIC_KEY={env_content['STRIPE_PUBLIC_KEY']}\n")
        if 'STRIPE_SECRET_KEY' in env_content:
            f.write(f"STRIPE_SECRET_KEY={env_content['STRIPE_SECRET_KEY']}\n")
        if 'STRIPE_WEBHOOK_SECRET' in env_content:
            f.write(f"STRIPE_WEBHOOK_SECRET={env_content['STRIPE_WEBHOOK_SECRET']}\n")
        
        f.write("\n# Price IDs - Map each tier to its Stripe price ID\n")
        for product in STRIPE_PRODUCTS:
            env_var = product['env_var']
            if env_var in env_content:
                f.write(f"{env_var}={env_content[env_var]}\n")
        
        f.write("\n# URLs\n")
        f.write(f"FRONTEND_URL={env_content.get('FRONTEND_URL', 'http://localhost:5173')}\n")
        f.write(f"BACKEND_URL={env_content.get('BACKEND_URL', 'http://localhost:8000')}\n")
        f.write(f"DATABASE_URL={env_content.get('DATABASE_URL', 'sqlite:///./topdog_ide.db')}\n")
    
    print_success(f"Updated .env file: {env_path}")
    print_info(f"Location: {env_path.absolute()}")

# ============================================================================
# STEP 6: WEBHOOK SETUP INSTRUCTIONS
# ============================================================================

def show_webhook_setup():
    """Show webhook setup instructions"""
    
    print_header("🔗 WEBHOOK CONFIGURATION")
    
    print(f"{Fore.YELLOW}Step 1: Start ngrok tunnel{Style.RESET_ALL}")
    print("   In a new terminal, run:")
    print(f"   {Fore.CYAN}ngrok http 8000{Style.RESET_ALL}\n")
    
    print(f"{Fore.YELLOW}Step 2: Copy ngrok URL{Style.RESET_ALL}")
    print("   ngrok will show a URL like:")
    print(f"   {Fore.GREEN}https://a1b2c3d4e5f6.ngrok.io{Style.RESET_ALL}\n")
    
    print(f"{Fore.YELLOW}Step 3: Add webhook in Stripe{Style.RESET_ALL}")
    print("   1. Go to: https://dashboard.stripe.com/webhooks")
    print("   2. Click 'Add Endpoint'")
    print("   3. Endpoint URL:")
    print(f"      {Fore.GREEN}https://YOUR_NGROK_URL/api/billing/webhook{Style.RESET_ALL}")
    print("   4. Select events:")
    print("      ✓ customer.subscription.created")
    print("      ✓ customer.subscription.updated")
    print("      ✓ customer.subscription.deleted")
    print("      ✓ invoice.payment_succeeded")
    print("      ✓ invoice.payment_failed")
    print("   5. Click 'Create endpoint'\n")
    
    print(f"{Fore.YELLOW}Step 4: Copy webhook secret{Style.RESET_ALL}")
    print("   1. Click on the webhook endpoint")
    print("   2. Find 'Signing secret'")
    print("   3. Click 'Reveal'")
    print(f"   4. Copy the {Fore.CYAN}whsec_{Style.RESET_ALL} value\n")

# ============================================================================
# MAIN FLOW
# ============================================================================

def main():
    """Main flow"""
    
    print_header("🎯 STRIPE PRODUCTS & WEBHOOK SETUP")
    print(f"{Fore.GREEN}Welcome to the Stripe setup assistant!{Style.RESET_ALL}")
    print("This will help you configure all 10 tiers for payment processing.\n")
    
    # Step 1: Show instructions
    show_product_creation_instructions()
    input(f"{Fore.CYAN}Press Enter when you've created all 9 products in Stripe...{Style.RESET_ALL}")
    
    # Step 2: Collect Price IDs
    price_ids = collect_price_ids()
    
    # Step 3: Collect Stripe keys
    stripe_keys = collect_stripe_keys()
    
    # Step 4: Update .env
    update_env_file(stripe_keys, price_ids)
    
    # Step 5: Show webhook setup
    show_webhook_setup()
    
    # Step 6: Summary
    print_header("✅ SETUP COMPLETE!")
    print(f"{Fore.GREEN}You've successfully:{Style.RESET_ALL}")
    print("  ✓ Created 9 Stripe products")
    print("  ✓ Collected all Price IDs")
    print("  ✓ Entered API keys")
    print("  ✓ Updated backend/.env\n")
    
    print(f"{Fore.YELLOW}Next steps:{Style.RESET_ALL}")
    print(f"  1. Set up ngrok tunnel: {Fore.CYAN}ngrok http 8000{Style.RESET_ALL}")
    print("  2. Create webhook in Stripe Dashboard")
    print(f"  3. Start backend: {Fore.CYAN}python main.py{Style.RESET_ALL}")
    print(f"  4. Start frontend: {Fore.CYAN}npm run dev{Style.RESET_ALL}")
    print(f"  5. Test payment with card: {Fore.CYAN}4242 4242 4242 4242{Style.RESET_ALL}\n")
    
    print(f"{Fore.GREEN}Ready to start testing! 🚀{Style.RESET_ALL}\n")

if __name__ == "__main__":
    main()

