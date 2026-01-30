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
        if not config.search.match_name:
            logger.error("MATCH_NAME not configured. Please set it in .env file.")
            sys.exit(1)
        
        logger.info("=" * 60)
        logger.info("Premier League Ticket Monitor")
        logger.info("=" * 60)
        logger.info(f"Match: {config.search.match_name}")
        logger.info(f"Price range: £{config.search.min_price} - £{config.search.max_price}")
        logger.info(f"Quantity needed: {config.search.quantity_needed}")
        if config.search.preferred_sections:
            logger.info(f"Preferred sections: {', '.join(config.search.preferred_sections)}")
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
