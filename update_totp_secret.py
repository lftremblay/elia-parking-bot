#!/usr/bin/env python3
"""
🔧 TOTP SECRET UPDATER
Updates your TOTP secret in config.json and .env files
"""

import json
import os
from pathlib import Path

def update_totp_secret(new_secret):
    """Update TOTP secret in both config.json and .env files"""
    
    print("🔧 UPDATING TOTP SECRET")
    print("=" * 40)
    
    # Update config.json
    config_path = Path("config.json")
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        if 'mfa' not in config:
            config['mfa'] = {}
        
        config['mfa']['totp_secret'] = new_secret
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Updated config.json with secret: {new_secret[:8]}...{new_secret[-8:]}")
    
    # Update .env file
    env_path = Path(".env")
    if env_path.exists():
        with open(env_path, 'r') as f:
            env_content = f.read()
        
        # Replace or add TOTP_SECRET
        lines = env_content.split('\n')
        updated_lines = []
        secret_updated = False
        
        for line in lines:
            if line.startswith('TOTP_SECRET='):
                updated_lines.append(f'TOTP_SECRET={new_secret}')
                secret_updated = True
            else:
                updated_lines.append(line)
        
        if not secret_updated:
            updated_lines.append(f'TOTP_SECRET={new_secret}')
        
        with open(env_path, 'w') as f:
            f.write('\n'.join(updated_lines))
        
        print(f"✅ Updated .env with secret: {new_secret[:8]}...{new_secret[-8:]}")
    
    print()
    print("🎯 NEXT STEPS:")
    print("1. Test locally: python debug_totp_secret.py")
    print("2. Commit changes: git add . && git commit -m 'Update TOTP secret'")
    print("3. Push to GitHub: git push origin main")
    print("4. Monitor GitHub Actions for success!")

if __name__ == "__main__":
    # Get the new secret from user input
    new_secret = input("Enter your new TOTP secret: ").strip()
    if new_secret:
        update_totp_secret(new_secret)
    else:
        print("❌ No secret provided. Please run again with the correct secret.")
