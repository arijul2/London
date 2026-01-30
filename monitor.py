"""Main monitoring loop with periodic checks."""
import logging
import time
from typing import List
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

from config import Config
from scraper import TicketScraper
from filter import TicketFilter
from database import TicketDatabase
from notifications import NotificationService

logger = logging.getLogger(__name__)


class TicketMonitor:
    """Main monitoring system that orchestrates scraping, filtering, and notifications."""
    
    def __init__(self, config: Config):
        self.config = config
        self.scraper = TicketScraper(base_url=config.monitor.base_url)
        self.filter = TicketFilter(config.search)
        self.database = TicketDatabase()
        self.notifications = NotificationService(config.notifications)
        self.scheduler = BlockingScheduler()
    
    def start(self):
        """Start the monitoring loop."""
        logger.info("Starting ticket monitor...")
        logger.info(f"Monitoring: {self.config.search.match_name}")
        logger.info(f"Check interval: {self.config.monitor.check_interval_minutes} minutes")
        
        # Run immediately on start
        self.check_tickets()
        
        # Schedule periodic checks
        trigger = IntervalTrigger(minutes=self.config.monitor.check_interval_minutes)
        self.scheduler.add_job(
            self.check_tickets,
            trigger=trigger,
            id='ticket_check',
            name='Check for matching tickets'
        )
        
        try:
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("Stopping ticket monitor...")
            self.scheduler.shutdown()
    
    def check_tickets(self):
        """Perform a single check cycle."""
        logger.info("=" * 60)
        logger.info(f"Checking tickets for {self.config.search.match_name}")
        
        try:
            # Get event URL
            event_url = self.config.get_event_url()
            logger.info(f"Event URL: {event_url}")
            
            # Scrape tickets
            all_tickets = self.scraper.scrape_event(event_url)
            
            if not all_tickets:
                logger.warning("No tickets found on page")
                return
            
            # Filter tickets by criteria
            matching_tickets = self.filter.filter_tickets(all_tickets)
            
            if not matching_tickets:
                logger.info("No tickets match your criteria")
                return
            
            # Check for new tickets
            new_tickets = self.database.get_new_tickets(
                matching_tickets,
                self.config.search.match_name
            )
            
            if new_tickets:
                logger.info(f"Found {len(new_tickets)} new matching ticket(s)!")
                self.notifications.send_notification(
                    new_tickets,
                    self.config.search.match_name
                )
            else:
                logger.info("No new tickets found")
        
        except Exception as e:
            logger.error(f"Error during ticket check: {e}", exc_info=True)
    
    def run_once(self):
        """Run a single check without scheduling (useful for testing)."""
        self.check_tickets()
