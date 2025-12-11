#!/usr/bin/env python3
"""
Test script for the robust booking detector
"""

import asyncio
import logging
from datetime import datetime, timedelta
from booking_detector import RobustBookingDetector
from fixed_graphql_client import FixedEliaGraphQLClient
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s:%(lineno)d - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

async def test_detector():
    """Test the robust booking detector"""
    print("Testing Robust Booking Detector")
    print("=" * 50)
    
    # Initialize client
    client = FixedEliaGraphQLClient()
    await client.test_auth()
    
    # Get configuration
    user_email = os.getenv('ELIA_EMAIL', '')
    floor_id = os.getenv('FLOOR_ID', 'sp_Mkddt7JNKkLPhqTc')
    
    print(f"User: {user_email}")
    print(f"Floor: {floor_id}")
    print()
    
    # Create detector
    detector = RobustBookingDetector(client, user_email, floor_id)
    
    # Test dates
    today = datetime.now()
    test_dates = [
        (today - timedelta(days=1)).strftime('%Y-%m-%d'),  # Yesterday
        today.strftime('%Y-%m-%d'),                        # Today
        (today + timedelta(days=1)).strftime('%Y-%m-%d'),  # Tomorrow
        (today + timedelta(days=7)).strftime('%Y-%m-%d'),  # Next week
        (today + timedelta(days=14)).strftime('%Y-%m-%d'), # 2 weeks
    ]
    
    print("Testing individual dates:")
    results = {}
    for date in test_dates:
        print(f"  Checking {date}...")
        has_booking = await detector.has_booking_for_date(date)
        results[date] = has_booking
        status = "BOOKED" if has_booking else "AVAILABLE"
        print(f"     {status}")
    
    print()
    print("Getting all bookings for next 30 days:")
    
    # Get all bookings
    end_date = (today + timedelta(days=30)).strftime('%Y-%m-%d')
    bookings = await detector.get_all_user_bookings(
        today.strftime('%Y-%m-%d'),
        end_date
    )
    
    if bookings:
        print(f"   Found {len(bookings)} parking bookings:")
        for booking in bookings:
            print(f"     {booking.date}: {booking.space_name}")
            print(f"        {booking.start_time} - {booking.end_time}")
            print(f"        ID: {booking.booking_id}")
            print()
    else:
        print("   No parking bookings found in next 30 days")
    
    print()
    print("Summary:")
    for date, has_booking in results.items():
        status = "SKIP" if has_booking else "BOOK"
        print(f"   {date}: {status}")
    
    await client.close()
    print()
    print("Test completed!")

async def compare_methods():
    """Compare old vs new booking detection methods"""
    print("Comparing Old vs New Detection Methods")
    print("=" * 50)
    
    from production_api_bot import ProductionEliaBot
    
    # Initialize bot
    bot = ProductionEliaBot()
    
    # Test tomorrow
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    print(f"Testing date: {tomorrow}")
    print()
    
    # Test new method
    print("New Robust Method:")
    new_result = await bot.has_booking_for_date(tomorrow)
    print(f"   Result: {'Has booking' if new_result else 'No booking'}")
    
    # Test old method
    print()
    print("Legacy Method:")
    legacy_result = await bot._legacy_booking_check(tomorrow)
    print(f"   Result: {'Has booking' if legacy_result else 'No booking'}")
    
    print()
    if new_result == legacy_result:
        print("Both methods agree")
    else:
        print("Methods disagree - robust detector is more accurate")
    
    await bot.close()

if __name__ == "__main__":
    print("Starting Booking Detector Tests")
    print()
    
    # Test 1: Basic functionality
    asyncio.run(test_detector())
    
    print()
    print("=" * 50)
    print()
    
    # Test 2: Compare methods
    asyncio.run(compare_methods())
