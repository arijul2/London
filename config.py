"""Configuration management for ticket monitoring system."""
import os
from dataclasses import dataclass
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()


@dataclass
class SearchCriteria:
    """Search criteria for ticket matching."""
    match_name: str
    min_price: float
    max_price: float
    quantity_needed: int
    preferred_sections: List[str]
    
    @classmethod
    def from_env(cls) -> 'SearchCriteria':
        """Load search criteria from environment variables."""
        match_name = os.getenv('MATCH_NAME', 'Arsenal vs Everton')
        min_price = float(os.getenv('MIN_PRICE', '200'))
        max_price = float(os.getenv('MAX_PRICE', '500'))
        quantity_needed = int(os.getenv('QUANTITY_NEEDED', '2'))
        
        sections_str = os.getenv('PREFERRED_SECTIONS', '')
        preferred_sections = [s.strip() for s in sections_str.split(',') if s.strip()]
        
        return cls(
            match_name=match_name,
            min_price=min_price,
            max_price=max_price,
            quantity_needed=quantity_needed,
            preferred_sections=preferred_sections
        )


@dataclass
class NotificationSettings:
    """Notification configuration."""
    email_enabled: bool = False
    email_to: Optional[str] = None
    email_smtp_server: Optional[str] = None
    email_smtp_port: Optional[int] = None
    email_username: Optional[str] = None
    email_password: Optional[str] = None
    
    pushover_enabled: bool = False
    pushover_api_key: Optional[str] = None
    pushover_user_key: Optional[str] = None
    
    desktop_notifications_enabled: bool = True
    
    @classmethod
    def from_env(cls) -> 'NotificationSettings':
        """Load notification settings from environment variables."""
        email_enabled = os.getenv('EMAIL_ENABLED', 'false').lower() == 'true'
        pushover_enabled = os.getenv('PUSHOVER_ENABLED', 'false').lower() == 'true'
        desktop_enabled = os.getenv('DESKTOP_NOTIFICATIONS_ENABLED', 'true').lower() == 'true'
        
        return cls(
            email_enabled=email_enabled,
            email_to=os.getenv('EMAIL_TO'),
            email_smtp_server=os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com'),
            email_smtp_port=int(os.getenv('EMAIL_SMTP_PORT', '587')),
            email_username=os.getenv('EMAIL_USERNAME'),
            email_password=os.getenv('EMAIL_PASSWORD'),
            pushover_enabled=pushover_enabled,
            pushover_api_key=os.getenv('PUSHOVER_API_KEY'),
            pushover_user_key=os.getenv('PUSHOVER_USER_KEY'),
            desktop_notifications_enabled=desktop_enabled
        )


@dataclass
class MonitorSettings:
    """Monitoring configuration."""
    check_interval_minutes: int = 30
    base_url: str = 'https://fanpass.net'
    
    @classmethod
    def from_env(cls) -> 'MonitorSettings':
        """Load monitor settings from environment variables."""
        interval = int(os.getenv('CHECK_INTERVAL_MINUTES', '30'))
        return cls(
            check_interval_minutes=interval,
            base_url=os.getenv('FANPASS_BASE_URL', 'https://fanpass.net')
        )


class Config:
    """Main configuration class."""
    
    def __init__(self):
        self.search = SearchCriteria.from_env()
        self.notifications = NotificationSettings.from_env()
        self.monitor = MonitorSettings.from_env()
    
    def get_event_url(self) -> str:
        """Construct event URL from match name."""
        # Convert "Arsenal vs Everton" to "tickets-arsenal-everton"
        match_slug = self.search.match_name.lower().replace(' vs ', '-').replace(' ', '-')
        return f"{self.monitor.base_url}/tickets-{match_slug}"
