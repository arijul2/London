"""Multi-channel notification system for ticket alerts."""
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Optional
import requests
import subprocess
import platform

from config import NotificationSettings

logger = logging.getLogger(__name__)


class NotificationService:
    """Handles sending notifications through multiple channels."""
    
    def __init__(self, settings: NotificationSettings):
        self.settings = settings
    
    def send_notification(self, tickets: List[Dict], match_name: str):
        """
        Send notifications for matching tickets through all enabled channels.
        
        Args:
            tickets: List of matching ticket dictionaries
            match_name: Name of the match
        """
        if not tickets:
            return
        
        message = self._format_message(tickets, match_name)
        
        # Send through all enabled channels
        if self.settings.email_enabled:
            self._send_email(message, match_name, tickets)
        
        if self.settings.pushover_enabled:
            self._send_pushover(message, match_name)
        
        if self.settings.desktop_notifications_enabled:
            self._send_desktop_notification(message, match_name, len(tickets))
    
    def _format_message(self, tickets: List[Dict], match_name: str) -> str:
        """Format ticket information into a readable message."""
        lines = [
            f"🎫 Found {len(tickets)} matching ticket(s) for {match_name}!",
            "",
        ]
        
        for i, ticket in enumerate(tickets, 1):
            lines.append(f"Ticket {i}:")
            lines.append(f"  Price: £{ticket.get('price', 'N/A'):.2f}")
            lines.append(f"  Quantity: {ticket.get('quantity', 'N/A')}")
            
            trustable_seller = ticket.get('trustable_seller', False)
            if trustable_seller:
                lines.append(f"  Trustable Seller: ✓")
            
            section = ticket.get('section')
            if section:
                lines.append(f"  Section: {section}")
            
            row = ticket.get('row')
            if row:
                lines.append(f"  Row: {row}")
            
            url = ticket.get('url', '')
            if url:
                lines.append(f"  Link: {url}")
            
            lines.append("")
        
        return "\n".join(lines)
    
    def _send_email(self, message: str, subject: str, tickets: List[Dict]):
        """Send email notification."""
        if not self.settings.email_to or not self.settings.email_username:
            logger.warning("Email not configured properly")
            return
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.settings.email_username
            msg['To'] = self.settings.email_to
            msg['Subject'] = f"Ticket Alert: {subject}"
            
            msg.attach(MIMEText(message, 'plain'))
            
            server = smtplib.SMTP(self.settings.email_smtp_server, self.settings.email_smtp_port)
            server.starttls()
            server.login(self.settings.email_username, self.settings.email_password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email notification sent to {self.settings.email_to}")
        
        except Exception as e:
            logger.error(f"Failed to send email: {e}", exc_info=True)
    
    def _send_pushover(self, message: str, title: str):
        """Send push notification via Pushover."""
        if not self.settings.pushover_api_key or not self.settings.pushover_user_key:
            logger.warning("Pushover not configured properly")
            return
        
        try:
            url = "https://api.pushover.net/1/messages.json"
            data = {
                'token': self.settings.pushover_api_key,
                'user': self.settings.pushover_user_key,
                'title': f"Ticket Alert: {title}",
                'message': message,
                'priority': 1  # High priority
            }
            
            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()
            
            logger.info("Pushover notification sent")
        
        except Exception as e:
            logger.error(f"Failed to send Pushover notification: {e}", exc_info=True)
    
    def _send_desktop_notification(self, message: str, title: str, ticket_count: int):
        """Send desktop notification (macOS/Linux/Windows)."""
        try:
            system = platform.system()
            
            if system == 'Darwin':  # macOS
                # Use osascript for macOS notifications
                short_message = f"Found {ticket_count} matching ticket(s) for {title}"
                script = f'''
                    display notification "{short_message}" with title "Ticket Alert"
                '''
                subprocess.run(['osascript', '-e', script], check=False)
            
            elif system == 'Linux':
                # Use notify-send for Linux
                short_message = f"Found {ticket_count} matching ticket(s)"
                subprocess.run(
                    ['notify-send', f'Ticket Alert: {title}', short_message],
                    check=False
                )
            
            elif system == 'Windows':
                # Use Windows toast notification
                # This would require additional setup with win10toast or similar
                logger.debug("Windows desktop notifications not implemented")
            
            logger.info("Desktop notification sent")
        
        except Exception as e:
            logger.debug(f"Failed to send desktop notification: {e}")
