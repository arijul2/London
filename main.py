"""Entry point for the ticket monitoring system."""
import logging
import sys
from config import Config
from monitor import TicketMonitor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('ticket_monitor.log')
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Main entry point."""
    try:
        # Load configuration
        config = Config()
        
        # Validate configuration
        searches = config.get_searches()
        if not searches:
            logger.error("No matches configured. Please set MATCH_1_NAME, MATCH_1_MIN_TICKETS, MATCH_1_MAX_PRICE in .env file.")
            sys.exit(1)
        
        logger.info("=" * 60)
        logger.info("Premier League Ticket Monitor")
        logger.info("=" * 60)
        logger.info(f"Monitoring {len(searches)} match(es):")
        for search in searches:
            logger.info(f"  - {search.match_name}")
            logger.info(f"    Min tickets: {search.min_tickets}, Max price: £{search.max_price}")
        logger.info("=" * 60)
        
        # Create and start monitor
        monitor = TicketMonitor(config)
        
        # Check if running in test mode (single run)
        import os
        if os.getenv('RUN_ONCE', 'false').lower() == 'true':
            logger.info("Running in single-check mode")
            monitor.run_once()
        else:
            logger.info("Starting continuous monitoring...")
            monitor.start()
    
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
