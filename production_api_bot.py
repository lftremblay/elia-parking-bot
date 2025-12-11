"""
Production-Ready Elia API Parking Bot
Complete solution with proper booking timing and error handling
"""

import asyncio
import json
import os
import httpx
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Set
from loguru import logger
from pathlib import Path
from dotenv import load_dotenv

from fixed_graphql_client import FixedEliaGraphQLClient

load_dotenv()


class EmailNotifier:
    """Handle email notifications for bot results"""
    
    def __init__(self):
        # Force reload environment variables
        load_dotenv(override=True)
        
        self.email_address = os.getenv('EMAIL_ADDRESS')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        
        # Debug configuration
        logger.info(f"📧 EMAIL INITIALIZATION DEBUG:")
        logger.info(f"   - EMAIL_ADDRESS from env: '{os.getenv('EMAIL_ADDRESS')}'")
        logger.info(f"   - SMTP_PASSWORD from env: '{'SET' if os.getenv('SMTP_PASSWORD') else 'MISSING'}'")
        logger.info(f"   - SMTP_HOST from env: '{os.getenv('SMTP_HOST')}'")
        logger.info(f"   - SMTP_PORT from env: '{os.getenv('SMTP_PORT')}'")
        
        # Check if email is configured
        self.enabled = all([self.email_address, self.smtp_password])
        
        logger.info(f"📧 Email Configuration Debug:")
        logger.info(f"   - EMAIL_ADDRESS: {'✅ Set' if self.email_address else '❌ Missing'}")
        logger.info(f"   - SMTP_PASSWORD: {'✅ Set' if self.smtp_password else '❌ Missing'}")
        logger.info(f"   - SMTP_HOST: {self.smtp_host}")
        logger.info(f"   - SMTP_PORT: {self.smtp_port}")
        logger.info(f"   - ENABLED: {self.enabled}")
        
        if self.enabled:
            logger.info("📧 Email notifications enabled")
        else:
            logger.warning("📧 Email notifications disabled - missing configuration")
            logger.info("💡 To enable emails:")
            logger.info("   1. Set SMTP_PASSWORD in your .env file")
            logger.info("   2. Or use alternative notifications (Discord/Telegram)")
    
    async def send_notification(self, subject: str, body: str, is_success: bool = True):
        """Send email notification"""
        if not self.enabled:
            logger.info("📧 Email notification skipped - not configured")
            logger.info(f"📧 Email Status Check:")
            logger.info(f"   - Enabled: {self.enabled}")
            logger.info(f"   - Email Address: {self.email_address}")
            logger.info(f"   - SMTP Password Set: {'Yes' if self.smtp_password else 'No'}")
            logger.info(f"   - SMTP Host: {self.smtp_host}")
            logger.info(f"   - SMTP Port: {self.smtp_port}")
            
            # Try alternative notifications
            await self._send_alternative_notifications(subject, body, is_success)
            return False
        
        try:
            logger.info(f"📧 Attempting to send email to {self.email_address}")
            logger.info(f"📧 Using SMTP server: {self.smtp_host}:{self.smtp_port}")
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_address
            msg['To'] = self.email_address
            msg['Subject'] = f"🤖 Parking Bot: {subject}"
            
            # Add emoji based on success/failure
            emoji = "✅" if is_success else "❌"
            
            # Create HTML body
            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: {'#d4edda' if is_success else '#f8d7da'}; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h2 style="color: {'#155724' if is_success else '#721c24'}; margin: 0;">
                        {emoji} {subject}
                    </h2>
                    <p style="margin: 10px 0 0 0; color: {'#155724' if is_success else '#721c24'};">
                        {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
                    </p>
                </div>
                
                <div style="background: #f8f9fa; padding: 20px; border-radius: 8px;">
                    <pre style="white-space: pre-wrap; font-family: monospace; font-size: 14px; margin: 0;">{body}</pre>
                </div>
                
                <div style="text-align: center; margin: 20px 0; color: #6c757d; font-size: 12px;">
                    <p>Sent by Elia Parking Bot</p>
                </div>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(html_body, 'html'))
            
            # Send email
            logger.info(f"📧 Connecting to SMTP server...")
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            
            # Videotron internal SMTP doesn't use TLS or authentication
            if self.smtp_host != 'smtp-int.int.videotron.com':
                logger.info(f"📧 Starting TLS encryption...")
                server.starttls()
                logger.info(f"📧 Authenticating with {self.email_address}...")
                server.login(self.email_address, self.smtp_password)
            else:
                logger.info(f"📧 Using Videotron internal SMTP (no auth required)")
            
            logger.info(f"📧 Sending message...")
            server.send_message(msg)
            server.quit()
            
            logger.success("📧 Email notification sent successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send email: {e}")
            logger.error(f"❌ Email error details: {type(e).__name__}: {str(e)}")
            # Try alternatives if email fails
            await self._send_alternative_notifications(subject, body, is_success)
            return False
    
    async def test_email_configuration(self):
        """Test email configuration with a simple test email"""
        logger.info("📧 Testing email configuration...")
        
        if not self.enabled:
            logger.error("❌ Email not configured - cannot test")
            return False
        
        try:
            test_subject = "🧪 Email Configuration Test"
            test_body = f"This is a test email from your Elia Parking Bot.\n\nSent at: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}\n\nIf you receive this, email notifications are working correctly!"
            
            result = await self.send_notification(test_subject, test_body, True)
            
            if result:
                logger.success("✅ Email configuration test passed!")
            else:
                logger.error("❌ Email configuration test failed!")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Email test failed: {e}")
            return False
    
    async def _send_alternative_notifications(self, subject: str, body: str, is_success: bool = True):
        """Send Discord or Telegram notifications as alternatives"""
        
        # Try Discord notification
        discord_webhook = os.getenv('DISCORD_WEBHOOK_URL')
        if discord_webhook:
            try:
                await self._send_discord_notification(subject, body, is_success)
            except Exception as e:
                logger.error(f"❌ Discord notification failed: {e}")
        
        # Try Telegram notification
        telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        if telegram_token and telegram_chat_id:
            try:
                await self._send_telegram_notification(subject, body, is_success)
            except Exception as e:
                logger.error(f"❌ Telegram notification failed: {e}")
        
        # If no alternatives are configured, show helpful message
        if not discord_webhook and not (telegram_token and telegram_chat_id):
            logger.info("💡 Configure alternative notifications:")
            logger.info("   - Discord: Set DISCORD_WEBHOOK_URL in .env")
            logger.info("   - Telegram: Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env")
    
    async def _send_discord_notification(self, subject: str, body: str, is_success: bool = True):
        """Send Discord webhook notification"""
        import httpx
        
        emoji = "✅" if is_success else "❌"
        color = 0x28a745 if is_success else 0xdc3545
        
        # Truncate body if too long for Discord
        body_truncated = body[:1500] + "..." if len(body) > 1500 else body
        
        payload = {
            "embeds": [{
                "title": f"{emoji} {subject}",
                "description": f"```\n{body_truncated}\n```",
                "color": color,
                "timestamp": datetime.now().isoformat(),
                "footer": {
                    "text": "Elia Parking Bot"
                }
            }]
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(os.getenv('DISCORD_WEBHOOK_URL'), json=payload)
            response.raise_for_status()
        
        logger.success("📱 Discord notification sent successfully")
    
    async def _send_telegram_notification(self, subject: str, body: str, is_success: bool = True):
        """Send Telegram bot notification"""
        import httpx
        
        emoji = "✅" if is_success else "❌"
        
        # Format message for Telegram
        message = f"{emoji} *{subject}*\n\n"
        message += f"```\n{body}\n```"
        message += f"\n\n📅 {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
        
        url = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_BOT_TOKEN')}/sendMessage"
        
        payload = {
            "chat_id": os.getenv('TELEGRAM_CHAT_ID'),
            "text": message,
            "parse_mode": "Markdown"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
        
        logger.success("📱 Telegram notification sent successfully")

class ProductionEliaBot:
    """
    Production-ready parking bot using Elia GraphQL API
    Handles booking policies and provides reliable reservations
    """
    
    def __init__(self):
        self.client = FixedEliaGraphQLClient()
        self.floor_id = "sp_Mkddt7JNKkLPhqTc"  # Default parking floor
        self.email_notifier = EmailNotifier()  # Email notifications
        
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
        
        # STEP 1: Book spots for tomorrow (both executive and regular if available)
        if tomorrow.weekday() < 5:  # Weekday check
            tomorrow_str = tomorrow.strftime('%Y-%m-%d')
            logger.info(f"\n📅 STEP 1: Spots for tomorrow ({tomorrow_str})")
            
            # Check if vacation day
            if await self.should_skip_date(tomorrow_str):
                results["skipped"].append(f"{tomorrow_str} (vacation)")
            # Check if already booked
            has_booking = await self.has_booking_for_date(tomorrow_str)
            logger.info(f"  🔍 Booking check result for {tomorrow_str}: {has_booking}")
            
            if has_booking:
                logger.info(f"⏭️ Skipping {tomorrow_str} - already booked")
                results["skipped"].append(tomorrow_str)
            else:
                # Try to book executive spot first
                logger.info(f"🎯 Attempting executive spot for tomorrow")
                exec_success = await self.reserve_parking_spot(
                    date=tomorrow_str,
                    spot_type="executive",
                    booking_window_hours=12  # Use 12 hours for full day booking
                )
                
                if exec_success:
                    results["executive_today"] = {
                        "date": tomorrow_str,
                        "success": True,
                        "type": "executive"
                    }
                    logger.info(f"✅ Executive spot booked for tomorrow")
                else:
                    # If executive fails, try regular spot as fallback
                    logger.info(f"⚠️ Executive spot failed, trying regular spot for tomorrow")
                    regular_success = await self.reserve_parking_spot(
                        date=tomorrow_str,
                        spot_type="regular",
                        booking_window_hours=6
                    )
                    
                    if regular_success:
                        results["regular_ahead"][tomorrow_str] = {
                            "success": True,
                            "type": "regular",
                            "days_ahead": 1
                        }
                        logger.info(f"✅ Regular spot booked for tomorrow (fallback)")
                    else:
                        logger.warning(f"❌ Both executive and regular spots failed for tomorrow")
                        results["errors"].append(f"Failed to book any spot for {tomorrow_str}")
        else:
            logger.info(f"⏭️ Tomorrow is {tomorrow.strftime('%A')} - skipping")
        
        # STEP 2: Book regular spots 14 days ahead (not 15 to comply with policy)
        logger.info(f"\n📅 STEP 2: Regular spots 14 days ahead")
        
        for days_ahead in [14]:  # Only 14 days to stay within 15-day policy
            future_date = today + timedelta(days=days_ahead)
            
            # Only book weekdays
            if future_date.weekday() < 5:
                future_date_str = future_date.strftime('%Y-%m-%d')
                logger.info(f"\n📅 Checking {future_date_str} ({future_date.strftime('%A')})")
                
                # Check if vacation day
                if await self.should_skip_date(future_date_str):
                    results["skipped"].append(f"{future_date_str} (vacation)")
                # Check if already booked
                elif await self.has_booking_for_date(future_date_str):
                    logger.info(f"⏭️ Skipping {future_date_str} - already booked")
                    results["skipped"].append(future_date_str)
                else:
                    # Try to book regular spot
                    success = await self.reserve_parking_spot(
                        date=future_date_str,
                        spot_type="regular",
                        booking_window_hours=6  # FIXED: Use 6 hours to meet policy minimum
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
        
        # Send email notification
        await self.send_booking_email_notification(results)
        
        return results
    
    async def send_booking_email_notification(self, results: Dict[str, any]):
        """Send email notification with booking results"""
        try:
            # Determine overall success
            exec_result = results.get("executive_today")
            exec_success = exec_result.get("success", False) if exec_result else False
            regular_successes = sum(1 for r in results.get("regular_ahead", {}).values() if r.get("success", False))
            total_bookings = len(results.get("regular_ahead", {})) + (1 if exec_result else 0)
            
            is_success = exec_success or regular_successes > 0
            
            # Create subject
            if is_success:
                subject = f"✅ Parking Booked Successfully ({regular_successes + (1 if exec_success else 0)} spots)"
            else:
                subject = "❌ Parking Booking Failed"
            
            # Create email body
            body_lines = []
            body_lines.append("🤖 Elia Parking Bot - Smart Booking Results")
            body_lines.append("=" * 50)
            body_lines.append(f"📅 Run Date: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
            body_lines.append("")
            
            # Executive results
            if results.get("executive_today"):
                exec_result = results["executive_today"]
                status = "✅ SUCCESS" if exec_result["success"] else "❌ FAILED"
                body_lines.append(f"🎯 Executive Spot (Tomorrow):")
                body_lines.append(f"   {status} - {exec_result['date']}")
                body_lines.append("")
            
            # Regular results
            if results.get("regular_ahead"):
                body_lines.append(f"📅 Regular Spots (14-15 Days Ahead):")
                for date_str, result in results["regular_ahead"].items():
                    status = "✅ SUCCESS" if result["success"] else "❌ FAILED"
                    body_lines.append(f"   {status} - {date_str} ({result['days_ahead']} days ahead)")
                body_lines.append("")
            
            # Skipped dates
            if results.get("skipped"):
                body_lines.append(f"⏭️ Skipped Dates ({len(results['skipped'])} total):")
                for date_str in results["skipped"]:
                    if "vacation" in date_str:
                        body_lines.append(f"   🏖️ {date_str}")
                    else:
                        body_lines.append(f"   ⏭️ {date_str}")
                body_lines.append("")
            
            # Summary
            body_lines.append("📊 SUMMARY:")
            body_lines.append(f"   Executive booked: {'✅ Yes' if exec_success else '❌ No'}")
            body_lines.append(f"   Regular spots booked: {regular_successes}/{len(results.get('regular_ahead', {}))}")
            body_lines.append(f"   Total skipped: {len(results.get('skipped', []))}")
            body_lines.append("")
            body_lines.append("🔗 View detailed logs: https://github.com/lftremblay/elia-parking-bot/actions")
            
            body = "\n".join(body_lines)
            
            # Send email
            await self.email_notifier.send_notification(subject, body, is_success)
            
        except Exception as e:
            logger.error(f"❌ Failed to send booking notification email: {e}")
    
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
