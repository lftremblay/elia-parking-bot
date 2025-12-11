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
from datetime import datetime, timedelta
from production_api_bot import ProductionEliaBot

async def main():
    print("FRESH RUN - bypassing module cache")
    print("=" * 50)
    
    # Create fresh bot instance
    bot = ProductionEliaBot()
    
    # Test time calculation
    start_time, end_time = bot._calculate_booking_times(12)
    print(f"Time calculation test: {start_time} to {end_time}")
    
    # Run smart booking
    results = await bot.smart_weekday_booking()
    return results

if __name__ == "__main__":
    results = asyncio.run(main())
    
    # Create human-readable summary
    print("\n" + "=" * 60)
    print("📊 COMPREHENSIVE PARKING BOT SUMMARY")
    print("=" * 60)
    
    # Save summary to file for email
    summary_lines = []
    summary_lines.append("=" * 60)
    summary_lines.append("🚗 ELIA PARKING BOT - COMPREHENSIVE RUN SUMMARY")
    summary_lines.append("=" * 60)
    summary_lines.append("")
    
    # Today's booking (executive or regular)
    today_date = datetime.now().strftime('%Y-%m-%d')
    today_booked = False
    
    if results.get('executive_today'):
        exec_result = results['executive_today']
        summary_lines.append("✅ EXECUTIVE SPOT (Today)")
        summary_lines.append(f"   Date: {exec_result.get('date', 'N/A')}")
        summary_lines.append(f"   Status: Booked")
        print("✅ Executive spot booked for today")
        today_booked = True
    
    # Check if regular spot was booked for today (fallback)
    if today_date in results.get('regular_ahead', {}):
        if not today_booked:
            summary_lines.append("✅ REGULAR SPOT (Today - fallback)")
            summary_lines.append(f"   Date: {today_date}")
            summary_lines.append(f"   Status: Booked (executive unavailable)")
            print("✅ Regular spot booked for today (fallback)")
            today_booked = True
    
    if not today_booked and not results.get('executive_today'):
        summary_lines.append("⏭️  TODAY'S SPOT")
        summary_lines.append("   Status: Skipped or already booked")
        print("⏭️  Today's spot skipped")
    
    summary_lines.append("")
    
    # All regular bookings (days 1-15, excluding today which was already shown)
    regular = results.get('regular_ahead', {})
    regular_future = {k: v for k, v in regular.items() if k != today_date}
    
    if regular_future:
        successful = sum(1 for v in regular_future.values() if v.get('success', False))
        summary_lines.append(f"✅ REGULAR SPOTS (Days 1-15): {successful}/{len(regular_future)} booked")
        print(f"✅ Regular spots: {successful}/{len(regular_future)} successful")
        for date in sorted(regular_future.keys()):
            booking = regular_future[date]
            status = "✅" if booking.get('success', False) else "❌"
            days = booking.get('days_ahead', '?')
            summary_lines.append(f"   {status} {date} (day {days})")
            print(f"   {status} {date} (day {days})")
    else:
        summary_lines.append("⏭️  REGULAR SPOTS (Days 1-15)")
        summary_lines.append("   Status: None attempted (all already booked or vacation)")
        print("⏭️  No regular spots attempted")
    
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
