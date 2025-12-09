"""
Fixed Elia GraphQL API Client
Based on actual captured queries from Elia application
"""

import asyncio
import httpx
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from loguru import logger
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()


class FixedEliaGraphQLClient:
    """
    Fixed GraphQL client using the exact queries captured from Elia
    """
    
    def __init__(self):
        self.base_url = "https://api.elia.io/graphql"
        self.access_token = os.getenv('ELIA_GRAPHQL_TOKEN')
        
        # Session management
        self.session = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
                'Accept': 'application/graphql-response+json, application/graphql+json, application/json',
                'Content-Type': 'application/json',
                'Referer': 'https://app.elia.io/',
            }
        )
        
        logger.info("🔌 FixedEliaGraphQLClient initialized")
    
    async def test_auth(self) -> bool:
        """Test if current token is valid"""
        try:
            query = """
            query CurrentUserWithPermissions($preferredLanguage: String) {
              meWithPermissions(preferredLanguage: $preferredLanguage) {
                id
                email
                __typename
              }
            }
            """
            
            response = await self._execute_query(
                query, 
                {"preferredLanguage": "fr"},
                "CurrentUserWithPermissions"
            )
            
            if response and 'data' in response:
                # Store user ID for later use
                user_data = response['data'].get('meWithPermissions', {})
                self.user_id = user_data.get('id')
                return True
            
            return False
            
        except Exception as e:
            logger.debug(f"Auth test failed: {e}")
            return False
    
    async def get_floor_spaces(self, floor_id: str) -> List[Dict]:
        """
        Get all spaces on a specific floor
        This is the correct way to get available parking spots
        """
        try:
            logger.info(f"🔍 Fetching spaces for floor {floor_id}...")
            
            # Use the exact captured query
            query = """
            query FloorSpaces($floorId: ID!) {
              floorSpaces(floorId: $floorId) {
                id
                name
                plan
                spaces {
                  id
                  buildingId
                  floorId
                  name
                  capacity
                  typeId
                  position {
                    x
                    y
                    __typename
                  }
                  placeType
                  pictureUrl
                  __typename
                }
                buildingId
                __typename
              }
            }
            """
            
            variables = {"floorId": floor_id}
            
            response = await self._execute_query(query, variables, "FloorSpaces")
            
            if response and 'data' in response:
                floor_data = response['data'].get('floorSpaces', {})
                spaces = floor_data.get('spaces', [])
                
                # Filter for parking spaces (based on placeType or name)
                parking_spaces = [
                    {
                        'id': space['id'],
                        'name': space['name'],
                        'capacity': space.get('capacity', 1),
                        'type': space.get('placeType', 'unknown'),
                        'building_id': space['buildingId'],
                        'floor_id': space['floorId']
                    }
                    for space in spaces
                    if self._is_parking_space(space)
                ]
                
                logger.success(f"✅ Found {len(parking_spaces)} parking spaces")
                return parking_spaces
            else:
                logger.error("❌ Failed to get floor spaces")
                return []
                
        except Exception as e:
            logger.error(f"❌ Failed to get floor spaces: {e}")
            return []
    
    async def get_floor_plan_bookings(self, floor_id: str, date: str) -> List[Dict]:
        """
        Get current bookings for a floor on a specific date
        This shows which spots are already taken
        """
        try:
            logger.info(f"🔍 Fetching bookings for floor {floor_id} on {date}...")
            
            # Use the exact captured query
            query = """
            query FloorPlanBookings($input: FloorPlanBookingsInput!) {
              floorPlanBookings(input: $input) {
                users {
                  id
                  firstName
                  lastName
                  title
                  profilePictureUrl
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
                    neighbourhoodId
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
                    "floorId": floor_id,
                    "start": "00:00:00",
                    "end": "23:59:59"
                }
            }
            
            response = await self._execute_query(query, variables, "FloorPlanBookings")
            
            if response and 'data' in response:
                bookings_data = response['data'].get('floorPlanBookings', {})
                bookings_by_space = bookings_data.get('bookingsBySpace', [])
                
                # Extract booked spaces
                booked_spaces = set()
                for space_bookings in bookings_by_space:
                    space_id = space_bookings['spaceId']
                    bookings = space_bookings.get('bookings', [])
                    
                    if bookings:  # If there are any bookings for this space
                        booked_spaces.add(space_id)
                
                logger.info(f"📊 Found {len(booked_spaces)} already booked spaces")
                return list(booked_spaces)
            else:
                logger.error("❌ Failed to get floor plan bookings")
                return []
                
        except Exception as e:
            logger.error(f"❌ Failed to get floor plan bookings: {e}")
            return []
    
    async def reserve_spot(self, space_id: str, date: str, start_time: str = "09:00:00.000Z", end_time: str = "17:00:00.000Z") -> bool:
        """
        Reserve a specific parking spot
        """
        try:
            logger.info(f"🎯 Reserving space {space_id} for {date}...")
            
            # Use the exact captured mutation
            mutation = """
            mutation MultiDateBook($input: AddBookingsInput!) {
              multiDateBook(input: $input)
            }
            """
            
            # Ensure we have the user ID
            if not hasattr(self, 'user_id') or not self.user_id:
                await self.test_auth()
            
            variables = {
                "input": {
                    "addToCalendar": False,
                    "dateTimeWindows": [
                        {
                            "end": f"{date}T{end_time}",
                            "start": f"{date}T{start_time}"
                        }
                    ],
                    "eventDescription": "",
                    "eventInviteesEmail": [],
                    "eventTitle": "Parking Reservation",
                    "unitId": space_id,
                    "userId": self.user_id
                }
            }
            
            response = await self._execute_query(mutation, variables, "MultiDateBook")
            
            if response and 'data' in response:
                result = response['data'].get('multiDateBook')
                
                if result:  # Non-null result typically means success
                    logger.success(f"✅ Successfully reserved space {space_id}")
                    return True
                else:
                    logger.error(f"❌ Reservation failed for space {space_id}")
                    return False
            else:
                logger.error("❌ Failed to reserve space")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to reserve space: {e}")
            return False
    
    async def get_available_parking_spots(self, date: str, floor_id: str = "sp_Mkddt7JNKkLPhqTc") -> List[Dict]:
        """
        Get available parking spots for a specific date
        Combines floor spaces with current bookings
        """
        try:
            logger.info(f"🔍 Finding available parking spots for {date}...")
            
            # Get all parking spaces on the floor
            all_spaces = await self.get_floor_spaces(floor_id)
            
            # Get already booked spaces for this date
            booked_space_ids = await self.get_floor_plan_bookings(floor_id, date)
            
            # Filter out already booked spaces
            available_spaces = [
                space for space in all_spaces
                if space['id'] not in booked_space_ids
            ]
            
            logger.success(f"✅ Found {len(available_spaces)} available parking spots for {date}")
            
            for space in available_spaces[:5]:  # Show first 5
                logger.info(f"  - {space['name']} (ID: {space['id']})")
            
            return available_spaces
            
        except Exception as e:
            logger.error(f"❌ Failed to get available parking spots: {e}")
            return []
    
    def _is_parking_space(self, space: Dict) -> bool:
        """Determine if a space is a parking space"""
        name = space.get('name', '').lower()
        place_type = space.get('placeType', '').lower()
        
        # Check for parking-related keywords
        parking_keywords = [
            'parking', 'spot', 'place', 'stationnement',
            'p', 'pk', 'st', 'ps'
        ]
        
        # Check name and type
        for keyword in parking_keywords:
            if keyword in name or keyword in place_type:
                return True
        
        # Check if it's a space with capacity 1 (likely a parking spot)
        if space.get('capacity') == 1 and any(char.isdigit() for char in name):
            return True
        
        return False
    
    async def _execute_query(self, query: str, variables: Dict, operation_name: str) -> Optional[Dict]:
        """Execute a GraphQL query"""
        try:
            if not self.access_token:
                raise Exception("No access token available")
            
            payload = {
                'query': query,
                'variables': variables,
                'operationName': operation_name
            }
            
            headers = {
                'Authorization': f'Bearer {self.access_token}'
            }
            
            response = await self.session.post(
                self.base_url,
                json=payload,
                headers=headers
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Check for GraphQL errors
            if 'errors' in data:
                logger.error(f"GraphQL errors: {data['errors']}")
                return None
            
            return data
            
        except Exception as e:
            logger.error(f"GraphQL query failed: {e}")
            return None
    
    async def close(self):
        """Close HTTP session"""
        await self.session.aclose()
        logger.info("🔌 GraphQL client closed")


# Test function
async def test_fixed_client():
    """Test the fixed GraphQL client"""
    client = FixedEliaGraphQLClient()
    
    try:
        # Test authentication
        if await client.test_auth():
            print("✅ Authentication successful")
            
            # Test getting available spots for tomorrow
            tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            available_spots = await client.get_available_parking_spots(tomorrow)
            
            if available_spots:
                print(f"✅ Found {len(available_spots)} available spots")
                
                # Try to reserve the first one
                first_spot = available_spots[0]
                print(f"🎯 Attempting to reserve: {first_spot['name']}")
                
                success = await client.reserve_spot(first_spot['id'], tomorrow)
                if success:
                    print("✅ Test reservation successful!")
                else:
                    print("❌ Test reservation failed")
            else:
                print("⚠️ No available spots found")
        else:
            print("❌ Authentication failed")
    
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(test_fixed_client())
