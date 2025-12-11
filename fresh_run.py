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
    
    # Create human-readable summary
    print("\n" + "=" * 60)
    print("📊 PARKING BOT SUMMARY")
    print("=" * 60)
    
    # Save summary to file for email
    summary_lines = []
    summary_lines.append("=" * 60)
    summary_lines.append("🚗 ELIA PARKING BOT - RUN SUMMARY")
    summary_lines.append("=" * 60)
    summary_lines.append("")
    
    # Executive booking
    if results.get('executive_today'):
        exec_result = results['executive_today']
        summary_lines.append("✅ EXECUTIVE SPOT (Tomorrow)")
        summary_lines.append(f"   Date: {exec_result.get('date', 'N/A')}")
        summary_lines.append(f"   Spot: {exec_result.get('spot_name', 'N/A')}")
        summary_lines.append(f"   Time: {exec_result.get('time', 'N/A')}")
        print("✅ Executive spot booked for tomorrow")
    else:
        summary_lines.append("⏭️  EXECUTIVE SPOT (Tomorrow)")
        summary_lines.append("   Status: Skipped or already booked")
        print("⏭️  Executive spot skipped")
    
    summary_lines.append("")
    
    # Regular bookings
    regular = results.get('regular_ahead', {})
    if regular:
        summary_lines.append(f"✅ REGULAR SPOTS (14 days ahead): {len(regular)} booked")
        print(f"✅ Regular spots booked: {len(regular)}")
        for date, booking in regular.items():
            summary_lines.append(f"   • {date}: {booking.get('spot_name', 'N/A')}")
            print(f"   • {date}: {booking.get('spot_name', 'N/A')}")
    else:
        summary_lines.append("⏭️  REGULAR SPOTS (14 days ahead)")
        summary_lines.append("   Status: None booked (already have bookings or vacation)")
        print("⏭️  No regular spots booked")
    
    summary_lines.append("")
    
    # Skipped dates
    skipped = results.get('skipped', [])
    if skipped:
        summary_lines.append(f"⏭️  SKIPPED DATES: {len(skipped)}")
        print(f"⏭️  Skipped dates: {len(skipped)}")
        for date in skipped:
            summary_lines.append(f"   • {date}")
            print(f"   • {date}")
    
    summary_lines.append("")
    
    # Errors
    errors = results.get('errors', [])
    if errors:
        summary_lines.append(f"❌ ERRORS: {len(errors)}")
        print(f"❌ Errors: {len(errors)}")
        for error in errors:
            summary_lines.append(f"   • {error}")
            print(f"   • {error}")
    else:
        summary_lines.append("✅ NO ERRORS")
        print("✅ No errors")
    
    summary_lines.append("")
    summary_lines.append("=" * 60)
    
    # Save to file for GitHub Actions to read
    with open('run_summary.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(summary_lines))
    
    print("\n" + "=" * 60)
    print("Summary saved to run_summary.txt")
