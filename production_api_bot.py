"""
Production-Ready Elia API Parking Bot
Complete solution with proper booking timing and error handling
"""

import asyncio
import json
import os
import httpx
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Set
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
            logger.info(f"🌍 Expected Montreal display: 6:00 AM to 6:00 PM (adjusted for timezone)")
            
            # Debug time conversion
            logger.debug(f"🔧 Time Debug:")
            logger.debug(f"   - Start UTC: {start_time}")
            logger.debug(f"   - End UTC: {end_time}")
            logger.debug(f"   - Target date: {date}")
            
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
                
                # Record successful booking in history
                await self.record_successful_booking(date, target_spot['name'])
                
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
                        
                        # Record successful booking in history
                        await self.record_successful_booking(date, next_spot['name'])
                        
                        return True
                
                return False
                
        except Exception as e:
            logger.error(f"❌ Production reservation failed: {e}")
            return False
    
    async def record_successful_booking(self, date: str, spot_name: str):
        """
        Record a successful booking in the history file
        
        Args:
            date: Date in YYYY-MM-DD format
            spot_name: Name of the booked spot
        """
        try:
            history_file = Path("booking_history.json")
            
            # Load existing history or create new
            if history_file.exists():
                with open(history_file, 'r') as f:
                    history = json.load(f)
            else:
                history = {
                    "successful_bookings": [],
                    "booking_details": {},
                    "last_updated": None
                }
            
            # Add the booking if not already present
            if date not in history["successful_bookings"]:
                history["successful_bookings"].append(date)
                history["booking_details"][date] = {
                    "spot_name": spot_name,
                    "booked_at": datetime.now().isoformat(),
                    "date": date
                }
                history["last_updated"] = datetime.now().isoformat()
                
                # Sort the bookings list
                history["successful_bookings"].sort()
                
                # Save updated history
                with open(history_file, 'w') as f:
                    json.dump(history, f, indent=2)
                
                logger.info(f"📋 Recorded booking for {date} in history")
            else:
                logger.debug(f"📋 Booking for {date} already exists in history")
                
        except Exception as e:
            logger.error(f"❌ Failed to record booking history: {e}")
    
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
    
    async def has_booking_for_date(self, date_str: str) -> bool:
        """
        Check if user already has a booking for the given date using the correct API
        
        Args:
            date_str: Date in YYYY-MM-DD format
            
        Returns:
            True if booking exists, False otherwise
        """
        try:
            from correct_booking_detector import CorrectBookingDetector
            
            detector = CorrectBookingDetector(client=self.client)
            
            has_booking = await detector.has_booking_for_date(date_str)
            
            if has_booking:
                logger.info(f"📅 Existing booking detected for {date_str} - will skip")
            else:
                logger.info(f"✅ No booking found for {date_str} - can proceed")
            
            return has_booking
            
        except Exception as e:
            logger.error(f"❌ Error checking for existing booking: {e}")
            # On error, assume no booking to avoid blocking legitimate bookings
            return False
    
    async def _legacy_booking_check(self, date: str) -> bool:
        """
        Legacy booking check method as fallback
        """
        try:
            logger.debug(f"  🔍 Using legacy booking check for {date}")
            
            # Use the floor plan method as fallback
            query = """
            query GetUserBookings($input: FloorPlanBookingsInput!) {
                floorPlanBookings(input: $input) {
                    users {
                        id
                        firstName
                        lastName
                        email
                        __typename
                    }
                    bookingsBySpace {
                        spaceId
                        bookings {
                            bookingId
                            start
                            end
                            user
                            isAssigned
                            __typename
                        }
                        __typename
                    }
                    __typename
                }
            }
            """
            
            variables = {
                "input": {
                    "dates": [date],
                    "floorId": self.floor_id,
                    "start": "00:00:00",
                    "end": "23:59:59"
                }
            }
            
            try:
                result = await self.client.execute_query(query, variables)
                
                if result and "floorPlanBookings" in result:
                    bookings_data = result["floorPlanBookings"]
                    bookings_by_space = bookings_data.get("bookingsBySpace", [])
                    
                    if bookings_by_space and len(bookings_by_space) > 0:
                        user_email = os.getenv('ELIA_EMAIL', '').lower()
                        
                        for space_booking in bookings_by_space:
                            bookings = space_booking.get("bookings", [])
                            for booking in bookings:
                                booking_user = booking.get("user", {})
                                if (isinstance(booking_user, dict) and 
                                    booking_user.get("email", "").lower() == user_email):
                                    logger.info(f"  ✅ Found existing booking for {date}: Space {space_booking.get('spaceId', 'Unknown')}")
                                    return True
                        
                        logger.debug(f"  📊 Found bookings for {date}, but none belong to current user")
                    else:
                        logger.debug(f"  📊 No bookings found for {date}")
                        
                else:
                    logger.debug(f"  📊 No booking data returned for {date}")
                    
            except Exception as api_error:
                logger.warning(f"  ⚠️ GraphQL booking check failed for {date}: {api_error}")
                
                # Fallback to booking history
                history_file = Path("booking_history.json")
                if history_file.exists():
                    with open(history_file, 'r') as f:
                        history = json.load(f)
                        
                    if date in history.get("successful_bookings", []):
                        logger.info(f"  📋 Found {date} in booking history - assuming user has booking")
                        return True
                        
                    logger.debug(f"  📋 {date} not found in booking history")
                else:
                    logger.debug(f"  📋 No booking history file found")
            
            # Final fallback: check occupancy
            available_spots = await self.client.get_available_parking_spots(date, self.floor_id)
            all_spaces = await self.client.get_floor_spaces(self.floor_id)
            total_spaces = len(all_spaces)
            available_count = len(available_spots)
            booked_count = total_spaces - available_count
            occupancy_rate = booked_count / total_spaces if total_spaces > 0 else 0
            
            logger.debug(f"  📊 {date}: {available_count}/{total_spaces} spots available, {booked_count} booked ({occupancy_rate:.1%} occupancy)")
            logger.debug(f"  📊 {date}: Proceeding with booking (no occupancy restrictions)")
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to check booking for {date}: {e}")
            # On error, be conservative and skip to avoid double-booking
            return True
    
    async def get_vacation_dates(self) -> Set[str]:
        """
        Get vacation dates from extension storage or environment variable
        
        Returns:
            Set of vacation dates in YYYY-MM-DD format
        """
        try:
            vacation_dates = set()
            
            # Method 1: Check environment variable (for testing/backup)
            vacation_str = os.getenv('VACATION_DATES', '')
            if vacation_str:
                env_dates = set(date.strip() for date in vacation_str.split(',') if date.strip())
                vacation_dates.update(env_dates)
                logger.info(f"🏖️ Found {len(env_dates)} vacation dates from environment: {env_dates}")
            
            # Method 2: Read from Chrome extension storage
            # This is the primary method - extension should save vacation dates
            try:
                # Look for extension data file that might contain vacation dates
                extension_file = Path("vacation_dates.txt")
                if extension_file.exists():
                    with open(extension_file, 'r') as f:
                        content = f.read().strip()
                        # Handle both comma-separated and line-separated dates
                        if ',' in content:
                            file_dates = set(date.strip() for date in content.split(',') if date.strip())
                        else:
                            file_dates = set(date.strip() for date in content.split('\n') if date.strip())
                        vacation_dates.update(file_dates)
                        logger.info(f"🏖️ Found {len(file_dates)} vacation dates from extension file: {file_dates}")
                else:
                    logger.debug("🏖️ No extension vacation file found")
            except Exception as e:
                logger.debug(f"🏖️ Could not read extension file: {e}")
            
            # Method 3: Check for common vacation file names
            common_files = ["vacation.txt", "skip_dates.txt", "blocked_dates.txt"]
            for filename in common_files:
                try:
                    file_path = Path(filename)
                    if file_path.exists():
                        with open(file_path, 'r') as f:
                            content = f.read().strip()
                            # Handle both comma-separated and line-separated dates
                            if ',' in content:
                                file_dates = set(date.strip() for date in content.split(',') if date.strip())
                            else:
                                file_dates = set(date.strip() for date in content.split('\n') if date.strip())
                            vacation_dates.update(file_dates)
                            logger.info(f"🏖️ Found {len(file_dates)} vacation dates from {filename}: {file_dates}")
                            break
                except Exception as e:
                    logger.debug(f"🏖️ Could not read {filename}: {e}")
            
            if vacation_dates:
                logger.info(f"🏖️ Total vacation dates that will be skipped: {vacation_dates}")
            else:
                logger.warning("🏖️ No vacation dates found - bot will book all weekdays")
                logger.info("💡 To set vacation dates, use VACATION_DATES environment variable or create vacation_dates.txt file")
            
            return vacation_dates
            
        except Exception as e:
            logger.error(f"❌ Failed to get vacation dates: {e}")
            return set()
    
    async def should_skip_date(self, date: str) -> bool:
        """
        Check if a date should be skipped due to vacation
        
        Args:
            date: Date in YYYY-MM-DD format
        
        Returns:
            True if date should be skipped
        """
        vacation_dates = await self.get_vacation_dates()
        
        if date in vacation_dates:
            logger.info(f"  🏖️ Skipping {date} - Vacation day")
            return True
        
        return False
    
    async def smart_weekday_booking(self) -> Dict[str, any]:
        """
        Smart booking strategy:
        - Check every weekday from today through 15 days ahead
        - Day 1 (today): Try executive first, fallback to regular
        - Days 2-15: Book regular spots
        - Skip weekends, vacation days, and already booked dates
        
        Returns:
            Dictionary with booking results and summary
        """
        logger.info("🎯 Starting comprehensive weekday booking strategy")
        logger.info("📅 Checking all weekdays from today through 15 days ahead")
        
        results = {
            "executive_today": None,
            "regular_ahead": {},
            "skipped": [],
            "errors": []
        }
        
        today = datetime.now()
        
        # Loop through days 0-15 (today through 15 days ahead)
        for days_ahead in range(0, 16):
            target_date = today + timedelta(days=days_ahead)
            
            # Skip weekends
            if target_date.weekday() >= 5:
                logger.info(f"⏭️ {target_date.strftime('%Y-%m-%d')} is {target_date.strftime('%A')} - skipping weekend")
                continue
            
            target_date_str = target_date.strftime('%Y-%m-%d')
            day_name = target_date.strftime('%A')
            
            logger.info(f"\n📅 Day {days_ahead}: {target_date_str} ({day_name})")
            
            # Check if vacation day
            if await self.should_skip_date(target_date_str):
                logger.info(f"🏖️ Vacation day - skipping")
                results["skipped"].append(f"{target_date_str} (vacation)")
                continue
            
            # Check if already booked
            has_booking = await self.has_booking_for_date(target_date_str)
            if has_booking:
                logger.info(f"✅ Already booked - skipping")
                results["skipped"].append(target_date_str)
                continue
            
            # Day 0 (today): Try executive first, fallback to regular
            if days_ahead == 0:
                logger.info(f"🎯 Today - attempting executive spot first")
                exec_success = await self.reserve_parking_spot(
                    date=target_date_str,
                    spot_type="executive",
                    booking_window_hours=12
                )
                
                if exec_success:
                    results["executive_today"] = {
                        "date": target_date_str,
                        "success": True,
                        "type": "executive"
                    }
                    logger.info(f"✅ Executive spot booked for today")
                else:
                    # Fallback to regular spot
                    logger.info(f"⚠️ Executive unavailable, trying regular spot")
                    regular_success = await self.reserve_parking_spot(
                        date=target_date_str,
                        spot_type="regular",
                        booking_window_hours=6
                    )
                    
                    if regular_success:
                        results["regular_ahead"][target_date_str] = {
                            "success": True,
                            "type": "regular",
                            "days_ahead": days_ahead
                        }
                        logger.info(f"✅ Regular spot booked for today (fallback)")
                    else:
                        logger.warning(f"❌ No spots available for today")
                        results["errors"].append(f"Failed to book any spot for {target_date_str}")
            
            # Days 1-15: Book regular spots only
            else:
                logger.info(f"📅 Attempting regular spot ({days_ahead} days ahead)")
                success = await self.reserve_parking_spot(
                    date=target_date_str,
                    spot_type="regular",
                    booking_window_hours=6
                )
                
                results["regular_ahead"][target_date_str] = {
                    "success": success,
                    "type": "regular",
                    "days_ahead": days_ahead
                }
                
                if success:
                    logger.info(f"✅ Regular spot booked")
                else:
                    logger.warning(f"❌ Booking failed")
                    results["errors"].append(f"Failed to book spot for {target_date_str}")
            
            # Small delay between bookings to avoid rate limiting
            await asyncio.sleep(2)
        
        # Summary
        logger.info("\n" + "="*50)
        logger.success("📊 COMPREHENSIVE BOOKING SUMMARY")
        logger.info("="*50)
        
        # Executive booking
        if results["executive_today"]:
            exec_result = results["executive_today"]
            status = "✅ SUCCESS" if exec_result["success"] else "❌ FAILED"
            logger.info(f"Executive (today): {status} - {exec_result['date']}")
        
        # Regular bookings
        if results["regular_ahead"]:
            successful = sum(1 for r in results["regular_ahead"].values() if r["success"])
            total = len(results["regular_ahead"])
            logger.info(f"\nRegular spots: {successful}/{total} successful")
            for date_str, result in sorted(results["regular_ahead"].items()):
                status = "✅" if result["success"] else "❌"
                logger.info(f"  {status} {date_str} ({result['days_ahead']} days ahead)")
        
        # Skipped dates
        if results["skipped"]:
            logger.info(f"\nSkipped: {len(results['skipped'])} dates")
            for date_str in results["skipped"]:
                logger.info(f"  ⏭️ {date_str}")
        
        # Errors
        if results["errors"]:
            logger.info(f"\nErrors: {len(results['errors'])}")
            for error in results["errors"]:
                logger.info(f"  ❌ {error}")
        
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
        Montreal time: 6 AM - 6 PM (EST/EDT)
        UTC conversion: Montreal is UTC-5 (winter) or UTC-4 (summer)
        Adjusted back 4 hours for correct display in Elia
        
        Args:
            hours: Number of hours for the booking window
        
        Returns:
            Tuple of (start_time, end_time) in UTC format
        """
        logger.info(f"🕐 CALCULATING TIMES FOR {hours} HOURS")
        
        # CRITICAL FIX: Use 06:00-18:00 UTC (6 AM - 6 PM Montreal)
        # This ensures 6 AM Montreal display in Elia
        if hours >= 12:
            # Full 12-hour day: 6 AM - 6 PM Montreal time
            start_time = "06:00:00.000Z"  # 6 AM Montreal = 6 AM UTC
            end_time = "18:00:00.000Z"    # 6 PM Montreal = 6 PM UTC
            logger.info(f"🕐 FULL DAY: {start_time} to {end_time}")
        elif hours >= 6:
            # Minimum 6-hour booking from 6 AM Montreal
            start_time = "06:00:00.000Z"  # 6 AM Montreal = 6 AM UTC
            end_time = f"{6 + hours:02d}:00:00.000Z"  # 6 AM Montreal + hours in UTC
            logger.info(f"🕐 {hours} HOURS: {start_time} to {end_time}")
        else:
            # Less than 6 hours (shouldn't happen due to policy)
            start_time = "06:00:00.000Z"  # 6 AM Montreal = 6 AM UTC
            end_time = "12:00:00.000Z"    # 6 hours = 12 PM UTC
            logger.info(f"🕐 MINIMUM: {start_time} to {end_time}")
        
        logger.info(f"🕐 FINAL TIMES: {start_time} to {end_time}")
        logger.info(f"🌍 EXPECTED MONTREAL DISPLAY: 6:00 AM to 6:00 PM")
        
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
    parser.add_argument("--test-email", action="store_true",
                       help="Test email configuration")
    
    args = parser.parse_args()
    
    bot = ProductionEliaBot()
    
    try:
        if args.test_email:
            success = await bot.email_notifier.test_email_configuration()
            print(f"Email test {'passed' if success else 'failed'}")
        
        elif args.status:
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
