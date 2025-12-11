"""
Robust Elia Booking Detection Tool

This tool provides multiple methods to detect existing parking bookings
with high reliability and fallback mechanisms.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass

from fixed_graphql_client import FixedEliaGraphQLClient

logger = logging.getLogger(__name__)

@dataclass
class BookingInfo:
    """Data class for booking information"""
    booking_id: str
    date: str
    start_time: str
    end_time: str
    space_id: str
    space_name: str
    user_email: str
    is_parking: bool  # True for parking, False for office space

class RobustBookingDetector:
    """
    Robust booking detection with multiple methods and fallbacks
    """
    
    def __init__(self, client: FixedEliaGraphQLClient, user_email: str, floor_id: str):
        self.client = client
        self.user_email = user_email.lower()
        self.floor_id = floor_id
        
    async def has_booking_for_date(self, date: str) -> bool:
        """
        Check if user has a parking booking for specific date
        Uses multiple detection methods for robustness
        """
        logger.info(f"🔍 Robust booking detection for {date}")
        
        # Method 1: Direct user bookings query (most reliable)
        if await self._check_user_bookings_direct(date):
            logger.info(f"✅ Found booking via direct user query for {date}")
            return True
            
        # Method 2: Floor plan bookings with user filtering
        if await self._check_floor_plan_bookings(date):
            logger.info(f"✅ Found booking via floor plan for {date}")
            return True
            
        # Method 3: Bookings tab API (simulates Elia bookings tab)
        if await self._check_bookings_tab(date):
            logger.info(f"✅ Found booking via bookings tab for {date}")
            return True
            
        # Method 4: Local booking history (fallback)
        if await self._check_local_history(date):
            logger.info(f"✅ Found booking via local history for {date}")
            return True
            
        logger.info(f"❌ No booking found for {date} using any method")
        return False
    
    async def _check_user_bookings_direct(self, date: str) -> bool:
        """
        Method 1: Query user's bookings directly
        This is the most reliable method if the API supports it
        """
        try:
            # Try to get user-specific bookings
            query = """
            query GetUserBookings($input: UserBookingsInput!) {
              userBookings(input: $input) {
                bookings {
                  id
                  date
                  start
                  end
                  unit {
                    id
                    name
                    type
                  }
                  status
                }
              }
            }
            """
            
            variables = {
                "input": {
                    "userId": self.client.user_id,
                    "startDate": date,
                    "endDate": date,
                    "unitTypes": ["PARKING"]  # Only parking bookings
                }
            }
            
            result = await self.client.execute_query(query, variables)
            
            if result and "userBookings" in result:
                bookings = result["userBookings"].get("bookings", [])
                for booking in bookings:
                    if booking.get("date") == date:
                        unit = booking.get("unit", {})
                        if unit.get("type") == "PARKING":
                            logger.info(f"  📅 Found direct parking booking: {unit.get('name', 'Unknown')}")
                            return True
                            
        except Exception as e:
            logger.debug(f"  ⚠️ Direct user bookings query failed: {e}")
            
        return False
    
    async def _check_floor_plan_bookings(self, date: str) -> bool:
        """
        Method 2: Check floor plan bookings and filter by user
        Enhanced version of current method with better filtering
        """
        try:
            query = """
            query GetFloorBookings($input: FloorPlanBookingsInput!) {
              floorPlanBookings(input: $input) {
                users {
                  id
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
            
            result = await self.client.execute_query(query, variables)
            
            if result and "floorPlanBookings" in result:
                data = result["floorPlanBookings"]
                
                # First, get all users and find current user's ID
                users = data.get("users", [])
                user_id = None
                for user in users:
                    if user.get("email", "").lower() == self.user_email:
                        user_id = user.get("id")
                        break
                
                if not user_id:
                    logger.debug(f"  👤 User not found in floor plan users list")
                    return False
                
                # Now check bookings for this user
                bookings_by_space = data.get("bookingsBySpace", [])
                for space_booking in bookings_by_space:
                    bookings = space_booking.get("bookings", [])
                    for booking in bookings:
                        booking_user = booking.get("user", {})
                        
                        # Check if booking belongs to current user
                        if (isinstance(booking_user, dict) and 
                            booking_user.get("id") == user_id):
                            logger.info(f"  🎯 Found user booking in space {space_booking.get('spaceId')}")
                            return True
                            
        except Exception as e:
            logger.debug(f"  ⚠️ Floor plan bookings check failed: {e}")
            
        return False
    
    async def _check_bookings_tab(self, date: str) -> bool:
        """
        Method 3: Simulate the Elia bookings tab API
        This mimics what the bookings tab shows in the UI
        """
        try:
            # Try different booking API endpoints that the UI might use
            queries = [
                # Method 3a: Bookings by date range
                """
                query GetBookingsByDate($input: BookingsByDateInput!) {
                  bookingsByDate(input: $input) {
                    bookings {
                      id
                      date
                      startTime
                      endTime
                      unit {
                        id
                        name
                        type
                        category
                      }
                      user {
                        id
                        email
                      }
                      status
                    }
                  }
                }
                """,
                # Method 3b: User's active bookings
                """
                query GetActiveBookings($input: ActiveBookingsInput!) {
                  activeBookings(input: $input) {
                    bookings {
                      id
                      date
                      unit {
                        type
                        category
                      }
                      status
                    }
                  }
                }
                """
            ]
            
            variables_list = [
                {
                    "input": {
                        "startDate": date,
                        "endDate": date,
                        "userId": self.client.user_id,
                        "unitCategory": "PARKING"
                    }
                },
                {
                    "input": {
                        "userId": self.client.user_id,
                        "date": date
                    }
                }
            ]
            
            for i, (query, variables) in enumerate(zip(queries, variables_list)):
                try:
                    result = await self.client.execute_query(query, variables)
                    
                    # Check different possible response structures
                    booking_keys = ["bookingsByDate", "activeBookings", "bookings"]
                    
                    for key in booking_keys:
                        if key in result:
                            bookings = result[key].get("bookings", [])
                            for booking in bookings:
                                # Check if it's a parking booking
                                unit = booking.get("unit", {})
                                if (unit.get("category") == "PARKING" or 
                                    unit.get("type") == "PARKING" or
                                    "stationnement" in unit.get("name", "").lower()):
                                    
                                    # Check if booking is for our user
                                    booking_user = booking.get("user", {})
                                    if (booking_user.get("email", "").lower() == self.user_email or
                                        booking_user.get("id") == self.client.user_id):
                                        
                                        logger.info(f"  🅿️ Found parking booking via bookings tab method {i+1}")
                                        return True
                                        
                except Exception as e:
                    logger.debug(f"  ⚠️ Bookings tab method {i+1} failed: {e}")
                    continue
                    
        except Exception as e:
            logger.debug(f"  ⚠️ Bookings tab check failed: {e}")
            
        return False
    
    async def _check_local_history(self, date: str) -> bool:
        """
        Method 4: Check local booking history as fallback
        """
        try:
            history_file = Path("booking_history.json")
            if history_file.exists():
                with open(history_file, 'r') as f:
                    history = json.load(f)
                    
                successful_bookings = history.get("successful_bookings", [])
                if date in successful_bookings:
                    logger.info(f"  📋 Found {date} in local booking history")
                    return True
                    
        except Exception as e:
            logger.debug(f"  ⚠️ Local history check failed: {e}")
            
        return False
    
    async def get_all_user_bookings(self, start_date: str, end_date: str) -> List[BookingInfo]:
        """
        Get all parking bookings for user within date range
        Useful for debugging and verification
        """
        logger.info(f"📋 Getting all bookings from {start_date} to {end_date}")
        
        bookings = []
        
        try:
            # Use the most reliable method available
            query = """
            query GetUserBookingsRange($input: UserBookingsRangeInput!) {
              userBookings(input: $input) {
                bookings {
                  id
                  date
                  start
                  end
                  unit {
                    id
                    name
                    type
                    category
                  }
                  status
                }
              }
            }
            """
            
            variables = {
                "input": {
                    "userId": self.client.user_id,
                    "startDate": start_date,
                    "endDate": end_date,
                    "unitCategory": "PARKING"
                }
            }
            
            result = await self.client.execute_query(query, variables)
            
            if result and "userBookings" in result:
                booking_data = result["userBookings"].get("bookings", [])
                
                for booking in booking_data:
                    unit = booking.get("unit", {})
                    
                    # Filter for parking bookings (stationnement)
                    is_parking = (
                        unit.get("category") == "PARKING" or
                        unit.get("type") == "PARKING" or
                        "stationnement" in unit.get("name", "").lower()
                    )
                    
                    if is_parking:
                        booking_info = BookingInfo(
                            booking_id=booking.get("id", ""),
                            date=booking.get("date", ""),
                            start_time=booking.get("start", ""),
                            end_time=booking.get("end", ""),
                            space_id=unit.get("id", ""),
                            space_name=unit.get("name", ""),
                            user_email=self.user_email,
                            is_parking=is_parking
                        )
                        bookings.append(booking_info)
                        
        except Exception as e:
            logger.error(f"❌ Failed to get user bookings: {e}")
            
        logger.info(f"📊 Found {len(bookings)} parking bookings")
        return bookings

async def test_booking_detector():
    """
    Test function to verify booking detection works
    """
    from fixed_graphql_client import FixedEliaGraphQLClient
    import os
    
    # Initialize client
    client = FixedEliaGraphQLClient()
    await client.test_auth()
    
    # Get user email and floor ID
    user_email = os.getenv('ELIA_EMAIL', '')
    floor_id = os.getenv('FLOOR_ID', 'sp_Mkddt7JNKkLPhqTc')
    
    # Create detector
    detector = RobustBookingDetector(client, user_email, floor_id)
    
    # Test dates
    test_dates = [
        datetime.now().strftime('%Y-%m-%d'),  # Today
        (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),  # Tomorrow
        (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),  # Next week
    ]
    
    print("🧪 Testing booking detection:")
    for date in test_dates:
        has_booking = await detector.has_booking_for_date(date)
        print(f"  {date}: {'✅ Has booking' if has_booking else '❌ No booking'}")
    
    # Get all bookings for next 30 days
    end_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    bookings = await detector.get_all_user_bookings(
        datetime.now().strftime('%Y-%m-%d'),
        end_date
    )
    
    print(f"\n📋 All bookings in next 30 days:")
    for booking in bookings:
        print(f"  {booking.date}: {booking.space_name} ({booking.start_time} - {booking.end_time})")
    
    await client.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_booking_detector())
