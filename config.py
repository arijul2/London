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
    min_tickets: int
    max_price: float
    trustable_seller_only: bool = False
    notify_seen_tickets: bool = False  # If True, include previously seen listings in notifications
    
    def get_event_url(self, base_url: str) -> str:
        """Construct event URL from match name."""
        # Convert "Arsenal vs Everton" to "tickets-arsenal-everton"
        match_slug = self.match_name.lower().replace(' vs ', '-').replace(' ', '-')
        return f"{base_url}/tickets-{match_slug}"


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
        self.notifications = NotificationSettings.from_env()
        self.monitor = MonitorSettings.from_env()
        self.searches = self._load_searches()
    
    def _load_searches(self) -> List[SearchCriteria]:
        """Load search criteria for all matches."""
        searches = []
        match_num = 1
        
        # Load matches in format: MATCH_1_NAME, MATCH_1_MIN_TICKETS, MATCH_1_MAX_PRICE
        while True:
            match_name = os.getenv(f'MATCH_{match_num}_NAME')
            if not match_name:
                # No more matches found
                break
            
            min_tickets = os.getenv(f'MATCH_{match_num}_MIN_TICKETS')
            max_price = os.getenv(f'MATCH_{match_num}_MAX_PRICE')
            trustable_seller_only = os.getenv(f'MATCH_{match_num}_TRUSTABLE_SELLER_ONLY', 'false').lower() == 'true'
            notify_seen_tickets = os.getenv(f'MATCH_{match_num}_NOTIFY_SEEN_TICKETS', 'false').lower() == 'true'
            
            if not min_tickets or not max_price:
                raise ValueError(
                    f"MATCH_{match_num}_NAME is set but MATCH_{match_num}_MIN_TICKETS "
                    f"or MATCH_{match_num}_MAX_PRICE is missing"
                )
            
            try:
                search = SearchCriteria(
                    match_name=match_name.strip(),
                    min_tickets=int(min_tickets),
                    max_price=float(max_price),
                    trustable_seller_only=trustable_seller_only,
                    notify_seen_tickets=notify_seen_tickets
                )
                searches.append(search)
            except ValueError as e:
                raise ValueError(
                    f"Invalid configuration for MATCH_{match_num}: {e}"
                )
            
            match_num += 1
        
        # If no matches found with MATCH_N format, try legacy single match format
        if not searches:
            match_name = os.getenv('MATCH_NAME')
            min_tickets = os.getenv('MIN_TICKETS', '2')
            max_price = os.getenv('MAX_PRICE', '500')
            trustable_seller_only = os.getenv('TRUSTABLE_SELLER_ONLY', 'false').lower() == 'true'
            notify_seen_tickets = os.getenv('NOTIFY_SEEN_TICKETS', 'false').lower() == 'true'
            
            if match_name:
                try:
                    search = SearchCriteria(
                        match_name=match_name.strip(),
                        min_tickets=int(min_tickets),
                        max_price=float(max_price),
                        trustable_seller_only=trustable_seller_only,
                        notify_seen_tickets=notify_seen_tickets
                    )
                    searches.append(search)
                except ValueError as e:
                    raise ValueError(f"Invalid configuration: {e}")
            else:
                # Default example
                searches.append(SearchCriteria(
                    match_name='Arsenal vs Everton',
                    min_tickets=2,
                    max_price=500.0,
                    trustable_seller_only=False,
                    notify_seen_tickets=False
                ))
        
        return searches
    
    def get_searches(self) -> List[SearchCriteria]:
        """Get all search criteria."""
        return self.searches
