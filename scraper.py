"""Playwright-based scraper for fanpass.net ticket listings."""
import logging
import hashlib
from typing import List, Dict, Optional
from playwright.sync_api import sync_playwright, Page, TimeoutError as PlaywrightTimeoutError

logger = logging.getLogger(__name__)


class TicketScraper:
    """Scrapes ticket data from fanpass.net using Playwright."""
    
    def __init__(self, base_url: str = 'https://fanpass.net', headless: bool = True):
        self.base_url = base_url
        self.headless = headless
    
    def scrape_event(self, event_url: str) -> List[Dict]:
        """
        Scrape tickets from an event page.
        
        Args:
            event_url: URL of the event page
            
        Returns:
            List of ticket dictionaries with keys: price, quantity, section, row, url, ticket_id
        """
        tickets = []
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=self.headless)
                page = browser.new_page()
                
                # Set a realistic user agent
                page.set_extra_http_headers({
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                })
                
                logger.info(f"Navigating to {event_url}")
                page.goto(event_url, wait_until='networkidle', timeout=30000)
                
                # Wait for ticket listings to load
                # The site uses .listing-row divs for ticket listings
                try:
                    page.wait_for_selector('.listing-row', timeout=10000)
                except PlaywrightTimeoutError:
                    logger.warning("Ticket listings may not have loaded, continuing anyway")
                
                # Extract ticket data
                tickets = self._extract_tickets(page, event_url)
                
                browser.close()
                
        except Exception as e:
            logger.error(f"Error scraping {event_url}: {e}", exc_info=True)
        
        logger.info(f"Found {len(tickets)} tickets")
        return tickets
    
    def _extract_tickets(self, page: Page, event_url: str) -> List[Dict]:
        """Extract ticket information from the rendered page."""
        tickets = []
        
        try:
            # Find all ticket listing rows
            # The site uses .listing-row divs for ticket listings
            listing_rows = page.query_selector_all('.listing-row')
            
            for listing_row in listing_rows:
                try:
                    ticket = self._parse_ticket_element(listing_row, event_url)
                    if ticket:
                        tickets.append(ticket)
                except Exception as e:
                    logger.debug(f"Error parsing ticket element: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error extracting tickets: {e}", exc_info=True)
        
        return tickets
    
    def _parse_ticket_element(self, element, event_url: str) -> Optional[Dict]:
        """Parse a single ticket listing-row element."""
        try:
            # Extract quantity from data-desired attribute
            quantity = self._extract_quantity(element)
            
            # Extract price from .price div (contains "£336")
            price_elem = element.query_selector('.price')
            if not price_elem:
                return None
            
            price_text = price_elem.inner_text().strip()
            # Remove "£" and parse price
            import re
            price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
            if not price_match:
                return None
            
            price = float(price_match.group())
            currency = 'GBP'
            
            # Extract trustable seller status
            trustable_seller = self._extract_trustable_seller(element)
            
            # Extract section and row (if available)
            section = self._extract_section(element)
            row = self._extract_row(element)
            
            # Get ticket URL - might be in a link nearby
            url_elem = element.query_selector('a[href*="ticket"], a[href*="buy"]')
            ticket_url = url_elem.get_attribute('href') if url_elem else event_url
            
            # Create unique ticket ID
            ticket_id = self._generate_ticket_id(price, quantity, section, row)
            
            return {
                'price': price,
                'currency': currency,
                'quantity': quantity,
                'section': section,
                'row': row,
                'url': ticket_url,
                'trustable_seller': trustable_seller,
                'ticket_id': ticket_id
            }
        
        except Exception as e:
            logger.debug(f"Error parsing ticket element: {e}")
            return None
    
    def _extract_quantity(self, element) -> int:
        """Extract quantity from data-desired attribute."""
        try:
            # Quantity is in data-desired attribute of listing-row
            data_desired = element.get_attribute('data-desired')
            if data_desired:
                return int(data_desired)
        except:
            pass
        return 1  # Default to 1 if not found
    
    def _extract_section(self, element) -> Optional[str]:
        """Extract section/stand name from ticket element."""
        try:
            # Look for section indicators in the element itself
            section_elem = element.query_selector('[class*="section"], [class*="stand"], [data-section]')
            if section_elem:
                return section_elem.inner_text().strip()
            
            # Try to find section in nearby elements using XPath or CSS
            # Look for section info in the same container
            try:
                # Try evaluating JavaScript to find parent with section info
                section_text = element.evaluate('''el => {
                    let parent = el.parentElement;
                    for (let i = 0; i < 5 && parent; i++) {
                        let section = parent.querySelector('[class*="section"], [class*="stand"]');
                        if (section) return section.innerText.trim();
                        parent = parent.parentElement;
                    }
                    return null;
                }''')
                if section_text:
                    return section_text
            except:
                pass
        except:
            pass
        return None
    
    def _extract_row(self, element) -> Optional[str]:
        """Extract row information from ticket element."""
        try:
            row_elem = element.query_selector('[class*="row"], [data-row]')
            if row_elem:
                return row_elem.inner_text().strip()
        except:
            pass
        return None
    
    def _extract_trustable_seller(self, element) -> bool:
        """Extract trustable seller status from listing-row element."""
        try:
            # Check for .by-trustable-seller class
            trustable_elem = element.query_selector('.by-trustable-seller')
            if trustable_elem:
                return True
            
            # Check for data-blue-rh="true" attribute
            status_elem = element.query_selector('.status[data-blue-rh="true"]')
            if status_elem:
                return True
            
            # Also check if the listing-row itself or any child has data-blue-rh="true"
            blue_rh = element.query_selector('[data-blue-rh="true"]')
            if blue_rh:
                return True
        except:
            pass
        return False
    
    def _generate_ticket_id(self, price: float, quantity: int, section: Optional[str], row: Optional[str]) -> str:
        """Generate a unique ID for a ticket."""
        # Create hash from ticket characteristics
        ticket_str = f"{price}_{quantity}_{section or ''}_{row or ''}"
        return hashlib.md5(ticket_str.encode()).hexdigest()
