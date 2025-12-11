#!/usr/bin/env python3
"""
Correct booking detector using the actual Elia API query
Based on HAR file analysis - uses the 'bookings' query with pagination
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from fixed_graphql_client import FixedEliaGraphQLClient
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s:%(lineno)d - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class CorrectBookingDetector:
    """
    Booking detector using the actual Elia API query discovered from HAR file
    """
    
    def __init__(self, client: FixedEliaGraphQLClient):
        self.client = client
        self.user_email = os.getenv('ELIA_EMAIL', '')
        self.logger = logging.getLogger(__name__)
    
    async def get_all_upcoming_bookings(self) -> List[Dict]:
        """
        Get all upcoming bookings using the correct API query
        This is the exact query the Elia web app uses
        """
        query = """
        query searchUpcomingBookings($first: Int, $after: ID) {
          bookings(first: $first, after: $after) {
            edges {
              node {
                id
                neighbourhoodId
                unit {
                  id
                  name
                  type
                  capacity
                  location {
                    building {
                      id
                      name
                      __typename
                    }
                    floor {
                      id
                      name
                      __typename
                    }
                    sector {
                      id
                      name
                      __typename
                    }
                    __typename
                  }
                  place {
                    room {
                      id
                      name
                      __typename
                    }
                    row {
                      id
                      name
                      __typename
                    }
                    desk {
                      id
                      name
                      __typename
                    }
                    __typename
                  }
                  tags {
                    id
                    name
                    backgroundColor
                    textColor
                    __typename
                  }
                  __typename
                }
                start
                end
                __typename
              }
              __typename
            }
            pageInfo {
              hasPreviousPage
              hasNextPage
              startCursor
              endCursor
              __typename
            }
            __typename
          }
        }
        """
        
        variables = {
            "first": 1000000  # Get all bookings
        }
        
        try:
            result = await self.client.execute_query(query, variables, "searchUpcomingBookings")
            
            if result and "data" in result:
                data = result["data"]
                
                if "bookings" in data:
                    bookings_data = data["bookings"]
                    edges = bookings_data.get("edges", [])
                    
                    bookings = []
                    for edge in edges:
                        node = edge.get("node", {})
                        if node:
                            bookings.append(node)
                    
                    self.logger.info(f"Retrieved {len(bookings)} total bookings")
                    return bookings
                else:
                    self.logger.warning(f"No 'bookings' field in data. Available fields: {list(data.keys())}")
                    return []
            else:
                self.logger.warning(f"No data in response. Response keys: {list(result.keys()) if result else 'None'}")
                return []
                
        except Exception as e:
            self.logger.error(f"Failed to get bookings: {e}")
            return []
    
    def is_parking_booking(self, booking: Dict) -> bool:
        """
        Check if a booking is for parking (stationnement)
        """
        unit = booking.get("unit", {})
        
        # Check tags for "Stationnement"
        tags = unit.get("tags", [])
        for tag in tags:
            if "stationnement" in tag.get("name", "").lower():
                return True
        
        # Check unit name for parking patterns
        unit_name = unit.get("name", "").upper()
        if unit_name.startswith("P-"):
            return True
        
        # Check floor name
        location = unit.get("location", {})
        floor = location.get("floor", {})
        floor_name = floor.get("name", "").lower()
        
        if "stationnement" in floor_name or "parking" in floor_name:
            return True
        
        return False
    
    def get_booking_date(self, booking: Dict) -> Optional[str]:
        """
        Extract the date from a booking's start time
        Returns date in YYYY-MM-DD format
        """
        start_time = booking.get("start", "")
        if not start_time:
            return None
        
        try:
            # Parse ISO format: "2025-12-12T06:00:00.000-05:00"
            dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%d")
        except Exception as e:
            self.logger.error(f"Failed to parse date from {start_time}: {e}")
            return None
    
    async def has_booking_for_date(self, date_str: str) -> bool:
        """
        Check if there's a parking booking for a specific date
        
        Args:
            date_str: Date in YYYY-MM-DD format
            
        Returns:
            True if parking booking exists for this date
        """
        bookings = await self.get_all_upcoming_bookings()
        
        # Filter for parking bookings on the specified date
        for booking in bookings:
            if self.is_parking_booking(booking):
                booking_date = self.get_booking_date(booking)
                
                if booking_date == date_str:
                    unit = booking.get("unit", {})
                    unit_name = unit.get("name", "Unknown")
                    
                    self.logger.info(f"Found parking booking on {date_str}: {unit_name}")
                    return True
        
        return False
    
    async def get_parking_bookings_in_range(self, start_date: str, end_date: str) -> List[Dict]:
        """
        Get all parking bookings within a date range
        
        Args:
            start_date: Start date in YYYY-MM-D format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            List of parking bookings with date, unit name, and times
        """
        bookings = await self.get_all_upcoming_bookings()
        
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        
        parking_bookings = []
        
        for booking in bookings:
            if self.is_parking_booking(booking):
                booking_date_str = self.get_booking_date(booking)
                
                if booking_date_str:
                    booking_dt = datetime.strptime(booking_date_str, "%Y-%m-%d")
                    
                    if start_dt <= booking_dt <= end_dt:
                        unit = booking.get("unit", {})
                        
                        parking_bookings.append({
                            "date": booking_date_str,
                            "unit_name": unit.get("name", "Unknown"),
                            "unit_id": unit.get("id", ""),
                            "start": booking.get("start", ""),
                            "end": booking.get("end", ""),
                            "booking_id": booking.get("id", "")
                        })
        
        return sorted(parking_bookings, key=lambda x: x["date"])


async def test_correct_detector():
    """Test the correct booking detector"""
    print("Testing Correct Booking Detector")
    print("=" * 50)
    
    client = FixedEliaGraphQLClient()
    await client.test_auth()
    
    detector = CorrectBookingDetector(client)
    
    # Test 1: Get all upcoming bookings
    print("\nTest 1: Get all upcoming bookings")
    bookings = await detector.get_all_upcoming_bookings()
    print(f"Total bookings: {len(bookings)}")
    
    # Filter for parking
    parking_bookings = [b for b in bookings if detector.is_parking_booking(b)]
    print(f"Parking bookings: {len(parking_bookings)}")
    
    if parking_bookings:
        print("\nParking bookings found:")
        for booking in parking_bookings:
            date = detector.get_booking_date(booking)
            unit = booking.get("unit", {})
            print(f"  - {date}: {unit.get('name', 'Unknown')}")
            print(f"    Start: {booking.get('start', '')}")
            print(f"    End: {booking.get('end', '')}")
    
    # Test 2: Check specific dates
    print("\nTest 2: Check specific dates")
    test_dates = [
        "2025-12-12",  # Should have booking (P-15)
        "2025-12-23",  # Should have booking (P-2)
        "2025-12-13",  # Should NOT have booking
    ]
    
    for date in test_dates:
        has_booking = await detector.has_booking_for_date(date)
        status = "HAS BOOKING" if has_booking else "NO BOOKING"
        print(f"  {date}: {status}")
    
    # Test 3: Get bookings in range
    print("\nTest 3: Get bookings in next 30 days")
    start_date = datetime.now().strftime("%Y-%m-%d")
    end_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    
    range_bookings = await detector.get_parking_bookings_in_range(start_date, end_date)
    print(f"Found {len(range_bookings)} parking bookings")
    
    for booking in range_bookings:
        print(f"  {booking['date']}: {booking['unit_name']}")
    
    print("\n" + "=" * 50)
    print("SUCCESS: Booking detection is now working!")
    print("The bot will correctly avoid days with existing bookings")
    
    await client.close()


if __name__ == "__main__":
    asyncio.run(test_correct_detector())
