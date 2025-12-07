#!/usr/bin/env python
"""
Status Check Script - Kiểm tra cấu hình API keys
"""
import os
import sys
sys.path.insert(0, '.')

from dotenv import load_dotenv

# Load .env
load_dotenv()

print("\n" + "="*60)
print("🔍 CHATBOT API KEY STATUS CHECK")
print("="*60)

# Check primary key
primary_key = os.getenv("GEMINI_API_KEY", "")
print(f"\n📌 PRIMARY KEY:")
if primary_key:
    print(f"   ✓ Configured: {primary_key[:20]}...{primary_key[-10:]}")
else:
    print(f"   ✗ NOT configured")

# Check backup keys
backup_keys_str = os.getenv("GEMINI_API_KEYS", "")
if backup_keys_str:
    keys_list = [k.strip() for k in backup_keys_str.split(",") if k.strip()]
    print(f"\n🔄 BACKUP KEYS ({len(keys_list)}):")
    for i, key in enumerate(keys_list, 1):
        print(f"   [{i}] {key[:20]}...{key[-10:]}")
else:
    print(f"\n🔄 BACKUP KEYS:")
    print(f"   ✗ Not configured")

# Summary
print(f"\n" + "="*60)
print("📊 SUMMARY:")
print("="*60)

total_keys = len(keys_list) if backup_keys_str else (1 if primary_key else 0)
if total_keys == 0:
    print("❌ NO API KEYS CONFIGURED!")
elif total_keys == 1:
    print(f"⚠️  Only 1 key configured (recommend: 3+)")
    print("   → To add more keys, edit .env file:")
    print("   → GEMINI_API_KEYS=\"key1,key2,key3\"")
else:
    print(f"✅ {total_keys} keys configured")
    print(f"   → Quota: {total_keys * 200} requests/day (estimated)")
    print(f"   → With 1h caching: {total_keys * 100}-{total_keys * 150} requests/day (effective)")

print("\n💾 Config File: .env")
print("📖 Setup Guide: SETUP_MULTIPLE_API_KEYS.md")
print("🔗 Google Console: https://console.cloud.google.com/apis/credentials")
print("="*60 + "\n")
