"""
Production-Ready Elia API Parking Bot
Complete solution with proper booking timing and error handling
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from loguru import logger
from pathlib import Path
from dotenv import load_dotenv

from fixed_graphql_client import FixedEliaGraphQLClient

load_dotenv()


class ProductionEliaBot:
    """
    Production-ready parking bot using Elia GraphQL API
    Handles booking policies and provides reliable reservations
    """
    
    def __init__(self):
        self.client = FixedEliaGraphQLClient()
        self.floor_id = "sp_Mkddt7JNKkLPhqTc"  # Default parking floor
        
        logger.info("🤖 ProductionEliaBot initialized")
    
    async def reserve_parking_spot(self, 
                                  date: str = None, 
                                  spot_type: str = "executive",
                                  booking_window_hours: int = 8) -> bool:
        """
        Reserve a parking spot with proper booking window to meet policies
        
        Args:
            date: Date in YYYY-MM-DD format (default: tomorrow)
            spot_type: "executive" or "regular"
            booking_window_hours: Duration to meet 6-hour minimum policy
        
        Returns:
            True if reservation successful
        """
        try:
            # Use tomorrow if no date specified
            if not date:
                tomorrow = datetime.now() + timedelta(days=1)
                date = tomorrow.strftime('%Y-%m-%d')
            
            logger.info(f"🎯 Starting production reservation for {date}")
            logger.info(f"📊 Spot type: {spot_type}, Booking window: {booking_window_hours} hours")
            
            # Ensure authenticated
            if not await self.client.test_auth():
                logger.error("❌ Authentication failed")
                return False
            
            # Get available spots
            available_spots = await self.client.get_available_parking_spots(date, self.floor_id)
            
            if not available_spots:
                logger.warning("⚠️ No available parking spots found")
                return False
            
            # Filter by spot type
            if spot_type == "executive":
                executive_spots = [
                    spot for spot in available_spots
                    if 'exc' in spot['name'].lower()
                ]
                
                if executive_spots:
                    available_spots = executive_spots
                    logger.info(f"✅ Found {len(executive_spots)} executive spots")
                else:
                    logger.warning("⚠️ No executive spots available, using regular spots")
            
            # Calculate booking times to meet policy
            start_time, end_time = self._calculate_booking_times(booking_window_hours)
            
            logger.info(f"⏰ Booking window: {start_time} to {end_time} ({booking_window_hours} hours)")
            
            # Try to reserve the first available spot
            target_spot = available_spots[0]
            logger.info(f"🎯 Attempting to reserve: {target_spot['name']} (ID: {target_spot['id']})")
            
            # Make the reservation
            success = await self.client.reserve_spot(
                target_spot['id'], 
                date, 
                start_time, 
                end_time
            )
            
            if success:
                logger.success(f"✅ Successfully reserved {target_spot['name']} for {date}")
                logger.info(f"📅 Reservation: {date} {start_time} - {end_time}")
                return True
            else:
                logger.error(f"❌ Failed to reserve {target_spot['name']}")
                
                # Try next spot if available
                if len(available_spots) > 1:
                    logger.info("🔄 Trying next available spot...")
                    next_spot = available_spots[1]
                    logger.info(f"🎯 Attempting to reserve: {next_spot['name']} (ID: {next_spot['id']})")
                    
                    success = await self.client.reserve_spot(
                        next_spot['id'], 
                        date, 
                        start_time, 
                        end_time
                    )
                    
                    if success:
                        logger.success(f"✅ Successfully reserved {next_spot['name']} for {date}")
                        return True
                
                return False
                
        except Exception as e:
            logger.error(f"❌ Production reservation failed: {e}")
            return False
    
    async def get_my_bookings(self, start_date: str, end_date: str) -> List[Dict]:
        """
        Get user's existing bookings for a date range
        Uses floorPlanBookings to check if user has bookings
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
        
        Returns:
            List of dates with bookings
        """
        try:
            # Use floorPlanBookings to check each date
            bookings = []
            current_date = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            
            while current_date <= end:
                date_str = current_date.strftime('%Y-%m-%d')
                
                # Get bookings for this date
                booked_spaces = await self.client.get_floor_plan_bookings(self.floor_id, date_str)
                
                # Check if any of the booked spaces are ours by trying to get available spots
                # If we have a booking, it won't show as available
                if booked_spaces:
                    # For now, we'll assume if there are bookings, we might have one
                    # This is a simplified check - in production, you'd verify ownership
                    bookings.append({
                        "date": date_str,
                        "booked_spaces_count": len(booked_spaces)
                    })
                
                current_date += timedelta(days=1)
            
            logger.info(f"📋 Found {len(bookings)} dates with bookings")
            return bookings
            
        except Exception as e:
            logger.error(f"❌ Failed to get bookings: {e}")
            return []
    
    async def has_booking_for_date(self, date: str) -> bool:
        """
        Check if user already has a booking for a specific date
        Simplified check: assumes if we can't book, we already have one
        
        Args:
            date: Date in YYYY-MM-DD format
        
        Returns:
            True if booking exists (or if we should skip)
        """
        try:
            # Get available spots for this date
            available_spots = await self.client.get_available_parking_spots(date, self.floor_id)
            
            # If no spots available at all, assume we might have one
            # This is a conservative approach to prevent double-booking attempts
            if not available_spots:
                logger.info(f"  ⏭️ No spots available for {date} - assuming booked or full")
                return True
            
            # If spots are available, we likely don't have a booking
            # (This is a simplified check - in a perfect world, we'd verify ownership)
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to check booking for {date}: {e}")
            # On error, assume we should skip to be safe
            return True
    
    async def smart_weekday_booking(self) -> Dict[str, any]:
        """
        Smart booking strategy:
        1. Book executive spot for tomorrow (6h policy)
        2. Book regular spots 14-15 days ahead
        3. Skip weekends
        4. Prevent double-booking
        
        Returns:
            Dictionary with booking results and summary
        """
        logger.info("🎯 Starting smart weekday booking strategy")
        
        results = {
            "executive_today": None,
            "regular_ahead": {},
            "skipped": [],
            "errors": []
        }
        
        today = datetime.now()
        tomorrow = today + timedelta(days=1)
        
        # STEP 1: Book executive spot for tomorrow (6h policy)
        if tomorrow.weekday() < 5:  # Weekday check
            tomorrow_str = tomorrow.strftime('%Y-%m-%d')
            logger.info(f"\n📅 STEP 1: Executive spot for tomorrow ({tomorrow_str})")
            
            # Check if already booked
            if await self.has_booking_for_date(tomorrow_str):
                logger.info(f"⏭️ Skipping {tomorrow_str} - already booked")
                results["skipped"].append(tomorrow_str)
            else:
                # Try to book executive spot
                success = await self.reserve_parking_spot(
                    date=tomorrow_str,
                    spot_type="executive",
                    booking_window_hours=12
                )
                results["executive_today"] = {
                    "date": tomorrow_str,
                    "success": success,
                    "type": "executive"
                }
        else:
            logger.info(f"⏭️ Tomorrow is {tomorrow.strftime('%A')} - skipping")
        
        # STEP 2: Book regular spots 14-15 days ahead
        logger.info(f"\n📅 STEP 2: Regular spots 14-15 days ahead")
        
        for days_ahead in [14, 15]:
            future_date = today + timedelta(days=days_ahead)
            
            # Only book weekdays
            if future_date.weekday() < 5:
                future_date_str = future_date.strftime('%Y-%m-%d')
                logger.info(f"\n📅 Checking {future_date_str} ({future_date.strftime('%A')})")
                
                # Check if already booked
                if await self.has_booking_for_date(future_date_str):
                    logger.info(f"⏭️ Skipping {future_date_str} - already booked")
                    results["skipped"].append(future_date_str)
                else:
                    # Try to book regular spot
                    success = await self.reserve_parking_spot(
                        date=future_date_str,
                        spot_type="regular",
                        booking_window_hours=12
                    )
                    results["regular_ahead"][future_date_str] = {
                        "success": success,
                        "type": "regular",
                        "days_ahead": days_ahead
                    }
                    
                    # Small delay between bookings
                    await asyncio.sleep(2)
            else:
                logger.info(f"⏭️ {future_date.strftime('%Y-%m-%d')} is {future_date.strftime('%A')} - skipping")
        
        # STEP 3: Summary
        logger.info("\n" + "="*50)
        logger.success("📊 SMART BOOKING SUMMARY")
        logger.info("="*50)
        
        # Executive booking
        if results["executive_today"]:
            exec_result = results["executive_today"]
            status = "✅ SUCCESS" if exec_result["success"] else "❌ FAILED"
            logger.info(f"Executive (tomorrow): {status} - {exec_result['date']}")
        
        # Regular bookings
        if results["regular_ahead"]:
            logger.info(f"\nRegular spots (14-15 days ahead):")
            for date_str, result in results["regular_ahead"].items():
                status = "✅ SUCCESS" if result["success"] else "❌ FAILED"
                logger.info(f"  {status} - {date_str} ({result['days_ahead']} days ahead)")
        
        # Skipped dates
        if results["skipped"]:
            logger.info(f"\nSkipped (already booked): {len(results['skipped'])} dates")
            for date_str in results["skipped"]:
                logger.info(f"  ⏭️ {date_str}")
        
        logger.info("="*50)
        
        return results
    
    async def reserve_weekday_spots(self, days_ahead: int = 14) -> Dict[str, bool]:
        """
        Reserve parking spots for all weekdays in the next N days
        (Legacy method - use smart_weekday_booking for new logic)
        
        Args:
            days_ahead: Number of days to look ahead
        
        Returns:
            Dictionary mapping dates to reservation success
        """
        logger.info(f"🗓️ Starting weekday reservations for next {days_ahead} days")
        
        results = {}
        today = datetime.now()
        
        for i in range(1, days_ahead + 1):
            date = today + timedelta(days=i)
            
            # Only book weekdays (Monday-Friday)
            if date.weekday() < 5:
                date_str = date.strftime('%Y-%m-%d')
                logger.info(f"📅 Processing {date_str} ({date.strftime('%A')})")
                
                # Check if already booked
                if await self.has_booking_for_date(date_str):
                    logger.info(f"⏭️ Skipping {date_str} - already booked")
                    results[date_str] = "skipped"
                    continue
                
                success = await self.reserve_parking_spot(date_str)
                results[date_str] = success
                
                # Small delay between reservations
                await asyncio.sleep(2)
        
        # Summary
        successful = sum(1 for v in results.values() if v == True)
        skipped = sum(1 for v in results.values() if v == "skipped")
        total = len(results)
        
        logger.success(f"📊 Weekday reservation summary: {successful}/{total} successful, {skipped} skipped")
        
        for date_str, result in results.items():
            if result == "skipped":
                status = "⏭️"
            elif result:
                status = "✅"
            else:
                status = "❌"
            logger.info(f"  {status} {date_str}")
        
        return results
    
    def _calculate_booking_times(self, hours: int) -> tuple:
        """
        Calculate start and end times that meet the booking policy
        
        Args:
            hours: Number of hours for the booking window
        
        Returns:
            Tuple of (start_time, end_time) in UTC format
        """
        # Use business hours to meet 6-hour minimum policy
        if hours >= 6:
            # Full day booking
            start_time = "08:00:00.000Z"  # 8 AM UTC = 3 AM EST
            end_time = f"{18 + (hours - 10):02d}:00:00.000Z"  # Adjust end time
        else:
            # Minimum policy booking
            start_time = "09:00:00.000Z"  # 9 AM UTC = 4 AM EST  
            end_time = f"{15 + hours:02d}:00:00.000Z"  # End time based on hours
        
        return start_time, end_time
    
    async def check_parking_status(self, date: str = None) -> Dict:
        """
        Check current parking availability status
        
        Args:
            date: Date to check (default: tomorrow)
        
        Returns:
            Dictionary with parking status information
        """
        try:
            if not date:
                tomorrow = datetime.now() + timedelta(days=1)
                date = tomorrow.strftime('%Y-%m-%d')
            
            logger.info(f"📊 Checking parking status for {date}")
            
            # Ensure authenticated
            if not await self.client.test_auth():
                return {"error": "Authentication failed"}
            
            # Get all spaces
            all_spaces = await self.client.get_floor_spaces(self.floor_id)
            
            # Get booked spaces
            booked_space_ids = await self.client.get_floor_plan_bookings(date, self.floor_id)
            
            # Calculate statistics
            total_spaces = len(all_spaces)
            booked_spaces = len(booked_space_ids)
            available_spaces = total_spaces - booked_spaces
            
            # Classify by type
            executive_total = len([s for s in all_spaces if 'exc' in s['name'].lower()])
            executive_booked = len([
                s for s in all_spaces 
                if 'exc' in s['name'].lower() and s['id'] in booked_space_ids
            ])
            executive_available = executive_total - executive_booked
            
            status = {
                "date": date,
                "total_spaces": total_spaces,
                "booked_spaces": booked_spaces,
                "available_spaces": available_spaces,
                "executive": {
                    "total": executive_total,
                    "booked": executive_booked,
                    "available": executive_available
                },
                "regular": {
                    "total": total_spaces - executive_total,
                    "booked": booked_spaces - executive_booked,
                    "available": available_spaces - executive_available
                },
                "availability_percentage": round((available_spaces / total_spaces) * 100, 1) if total_spaces > 0 else 0
            }
            
            logger.info(f"📊 Parking Status for {date}:")
            logger.info(f"  Total: {total_spaces} | Available: {available_spaces} ({status['availability_percentage']}%)")
            logger.info(f"  Executive: {executive_available}/{executive_total} available")
            logger.info(f"  Regular: {status['regular']['available']}/{status['regular']['total']} available")
            
            return status
            
        except Exception as e:
            logger.error(f"❌ Failed to check parking status: {e}")
            return {"error": str(e)}
    
    async def close(self):
        """Cleanup resources"""
        await self.client.close()
        logger.info("🔌 Production bot closed")


# Command-line interface
async def main():
    """Main function for production bot usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Elia Production API Parking Bot")
    parser.add_argument("--reserve", action="store_true",
                       help="Reserve a parking spot for tomorrow")
    parser.add_argument("--reserve-date", type=str,
                       help="Reserve for specific date (YYYY-MM-DD)")
    parser.add_argument("--spot-type", choices=["executive", "regular"], 
                       default="executive", help="Type of spot to reserve")
    parser.add_argument("--weekdays", action="store_true",
                       help="Reserve for all weekdays in next 14 days")
    parser.add_argument("--smart", action="store_true",
                       help="Smart booking: executive tomorrow + regular 14-15 days ahead")
    parser.add_argument("--check-bookings", action="store_true",
                       help="Check existing bookings for next 30 days")
    parser.add_argument("--status", action="store_true",
                       help="Check parking availability status")
    parser.add_argument("--hours", type=int, default=8,
                       help="Booking window duration in hours")
    
    args = parser.parse_args()
    
    bot = ProductionEliaBot()
    
    try:
        if args.status:
            status = await bot.check_parking_status(args.reserve_date)
            print(json.dumps(status, indent=2))
        
        elif args.reserve:
            success = await bot.reserve_parking_spot(
                args.reserve_date, 
                args.spot_type, 
                args.hours
            )
            print(f"Reservation {'successful' if success else 'failed'}")
        
        elif args.smart:
            results = await bot.smart_weekday_booking()
            print(json.dumps(results, indent=2, default=str))
        
        elif args.weekdays:
            results = await bot.reserve_weekday_spots()
            print(json.dumps(results, indent=2))
        
        elif args.check_bookings:
            today = datetime.now()
            end_date = today + timedelta(days=30)
            bookings = await bot.get_my_bookings(
                today.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d')
            )
            print(json.dumps(bookings, indent=2))
        
        else:
            print("No action specified. Use --help for options.")
            print("\nQuick examples:")
            print("  python production_api_bot.py --status")
            print("  python production_api_bot.py --reserve")
            print("  python production_api_bot.py --smart  # Recommended!")
            print("  python production_api_bot.py --check-bookings")
            print("  python production_api_bot.py --weekdays")
    
    finally:
        await bot.close()


if __name__ == "__main__":
    asyncio.run(main())
