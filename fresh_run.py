#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fresh run script to bypass Python module caching
"""
import sys
import os

# Remove any cached modules
modules_to_remove = [k for k in sys.modules.keys() if k.startswith('production_api_bot') or k.startswith('fixed_graphql_client')]
for module in modules_to_remove:
    del sys.modules[module]

# Force environment reload
from dotenv import load_dotenv
load_dotenv(override=True)

# Now import fresh
import asyncio
from production_api_bot import ProductionEliaBot

async def main():
    print("FRESH RUN - bypassing module cache")
    print("=" * 50)
    
    # Create fresh bot instance
    bot = ProductionEliaBot()
    
    # Test time calculation
    start_time, end_time = bot._calculate_booking_times(6)
    print(f"Time calculation test: {start_time} to {end_time}")
    
    # Run smart booking
    results = await bot.smart_weekday_booking()
    return results

if __name__ == "__main__":
    results = asyncio.run(main())
    print("\nFinal Results:")
    print(results)
