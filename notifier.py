"""
Multi-channel Notification Handler
Supports Discord, Telegram, Email, and Windows notifications
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional
from loguru import logger


class Notifier:
    """Handles notifications across multiple channels"""
    
    def __init__(self, config: dict):
        self.config = config.get('notifications', {})
        self.enabled_channels = []
        
        # Check which channels are configured
        if self.config.get('discord_webhook'):
            self.enabled_channels.append('discord')
        
        if self.config.get('telegram_bot_token') and self.config.get('telegram_chat_id'):
            self.enabled_channels.append('telegram')
        
        if self.config.get('email', {}).get('enabled'):
            self.enabled_channels.append('email')
        
        logger.info(f"📢 Notifier initialized with channels: {', '.join(self.enabled_channels) if self.enabled_channels else 'None'}")
    
    def notify_success(self, spot_type: str, spot_id: str, details: str = ""):
        """Send success notification"""
        title = f"✅ Parking Reserved - {spot_type.title()}"
        message = f"Successfully reserved {spot_type} parking spot: {spot_id}\n\n{details}"
        
        self._send_to_all_channels(title, message, "success")
    
    def notify_failure(self, spot_type: str, error: str):
        """Send failure notification"""
        title = f"❌ Reservation Failed - {spot_type.title()}"
        message = f"Failed to reserve {spot_type} parking spot.\n\nError: {error}"
        
        self._send_to_all_channels(title, message, "error")
    
    def notify_no_spots(self, spot_type: str):
        """Notify when no spots are available"""
        title = f"⚠️ No Spots Available - {spot_type.title()}"
        message = f"No {spot_type} parking spots were available at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        self._send_to_all_channels(title, message, "warning")
    
    def notify_auth_required(self):
        """Notify when manual authentication is required"""
        title = "🔐 Authentication Required"
        message = "Elia Parking Bot requires manual authentication. Please run the setup process."
        
        self._send_to_all_channels(title, message, "error")
    
    def notify_startup(self):
        """Notify when bot starts"""
        title = "🚀 Bot Started"
        message = f"Elia Parking Bot started successfully at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        self._send_to_all_channels(title, message, "info")
    
    def _send_to_all_channels(self, title: str, message: str, level: str = "info"):
        """Send notification to all configured channels"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        full_message = f"[{timestamp}] {message}"
        
        for channel in self.enabled_channels:
            try:
                if channel == 'discord':
                    self._send_discord(title, full_message, level)
                elif channel == 'telegram':
                    self._send_telegram(title, full_message)
                elif channel == 'email':
                    self._send_email(title, full_message)
            except Exception as e:
                logger.error(f"❌ Failed to send {channel} notification: {e}")
    
    def _send_discord(self, title: str, message: str, level: str):
        """Send Discord webhook notification"""
        try:
            from discord_webhook import DiscordWebhook, DiscordEmbed
            
            webhook_url = self.config.get('discord_webhook')
            webhook = DiscordWebhook(url=webhook_url)
            
            # Color based on level
            color_map = {
                'success': '00ff00',
                'error': 'ff0000',
                'warning': 'ffaa00',
                'info': '0099ff'
            }
            
            embed = DiscordEmbed(
                title=title,
                description=message,
                color=color_map.get(level, '0099ff')
            )
            embed.set_footer(text='Elia Parking Bot V4')
            embed.set_timestamp()
            
            webhook.add_embed(embed)
            response = webhook.execute()
            
            if response.status_code == 200:
                logger.debug("✅ Discord notification sent")
            else:
                logger.warning(f"⚠️ Discord notification failed: {response.status_code}")
                
        except ImportError:
            logger.warning("⚠️ discord-webhook not installed")
        except Exception as e:
            logger.error(f"❌ Discord notification error: {e}")
    
    def _send_telegram(self, title: str, message: str):
        """Send Telegram notification"""
        try:
            import telegram
            import asyncio
            
            bot_token = self.config.get('telegram_bot_token')
            chat_id = self.config.get('telegram_chat_id')
            
            bot = telegram.Bot(token=bot_token)
            
            full_text = f"<b>{title}</b>\n\n{message}"
            
            # Run async send in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(
                bot.send_message(
                    chat_id=chat_id,
                    text=full_text,
                    parse_mode='HTML'
                )
            )
            loop.close()
            
            logger.debug("✅ Telegram notification sent")
            
        except ImportError:
            logger.warning("⚠️ python-telegram-bot not installed")
        except Exception as e:
            logger.error(f"❌ Telegram notification error: {e}")
    
    def _send_email(self, title: str, message: str):
        """Send email notification"""
        try:
            email_config = self.config.get('email', {})
            
            smtp_server = email_config.get('smtp_server')
            smtp_port = email_config.get('smtp_port', 587)
            from_email = email_config.get('from_email')
            to_email = email_config.get('to_email')
            password = email_config.get('password')
            
            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = to_email
            msg['Subject'] = title
            
            body = MIMEText(message, 'plain')
            msg.attach(body)
            
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(from_email, password)
                server.send_message(msg)
            
            logger.debug("✅ Email notification sent")
            
        except Exception as e:
            logger.error(f"❌ Email notification error: {e}")
    
    def send_windows_notification(self, title: str, message: str):
        """Send Windows toast notification"""
        try:
            from win10toast import ToastNotifier
            
            toaster = ToastNotifier()
            toaster.show_toast(
                title,
                message,
                icon_path=None,
                duration=10,
                threaded=True
            )
            
            logger.debug("✅ Windows notification sent")
            
        except ImportError:
            logger.debug("⚠️ win10toast not installed")
        except Exception as e:
            logger.error(f"❌ Windows notification error: {e}")


def test_notifier():
    """Test notification system"""
    config = {
        'notifications': {
            'discord_webhook': os.getenv('DISCORD_WEBHOOK_URL', ''),
            'telegram_bot_token': os.getenv('TELEGRAM_BOT_TOKEN', ''),
            'telegram_chat_id': os.getenv('TELEGRAM_CHAT_ID', ''),
            'email': {
                'enabled': False
            }
        }
    }
    
    notifier = Notifier(config)
    
    if notifier.enabled_channels:
        print(f"Testing notifications on: {', '.join(notifier.enabled_channels)}")
        notifier.notify_startup()
        notifier.notify_success('executive', 'P-123', 'Building A, Level 2')
    else:
        print("No notification channels configured. Set environment variables to test.")


if __name__ == "__main__":
    test_notifier()
