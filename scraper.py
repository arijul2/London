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
                # Try multiple selectors that might contain ticket data
                try:
                    page.wait_for_selector('[itemprop="offers"]', timeout=10000)
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
            # Find all ticket offer elements
            # The site uses schema.org markup with itemprop="offers"
            offer_elements = page.query_selector_all('[itemprop="offers"]')
            
            for offer in offer_elements:
                try:
                    ticket = self._parse_ticket_element(offer, event_url)
                    if ticket:
                        tickets.append(ticket)
                except Exception as e:
                    logger.debug(f"Error parsing ticket element: {e}")
                    continue
            
            # If schema.org approach didn't work, try alternative selectors
            if not tickets:
                tickets = self._extract_tickets_alternative(page, event_url)
        
        except Exception as e:
            logger.error(f"Error extracting tickets: {e}", exc_info=True)
        
        return tickets
    
    def _parse_ticket_element(self, element, event_url: str) -> Optional[Dict]:
        """Parse a single ticket element."""
        try:
            # Extract price
            price_elem = element.query_selector('[itemprop="price"]')
            if not price_elem:
                return None
            
            price_text = price_elem.inner_text().strip()
            price = float(price_text.replace('GBP', '').replace(',', '').strip())
            
            # Extract currency
            currency_elem = element.query_selector('[itemprop="priceCurrency"]')
            currency = currency_elem.inner_text().strip() if currency_elem else 'GBP'
            
            # Try to find quantity, section, row from surrounding elements
            # These might be in parent containers or sibling elements
            quantity = self._extract_quantity(element)
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
                'ticket_id': ticket_id
            }
        
        except Exception as e:
            logger.debug(f"Error parsing ticket element: {e}")
            return None
    
    def _extract_tickets_alternative(self, page: Page, event_url: str) -> List[Dict]:
        """Alternative extraction method if schema.org approach fails."""
        tickets = []
        
        try:
            # Look for common ticket listing patterns
            # This is a fallback - we'll need to inspect the actual page structure
            # and adjust selectors based on what we find
            
            # Try finding price elements directly
            price_elements = page.query_selector_all('[class*="price"], [data-price], .price')
            
            for price_elem in price_elements:
                try:
                    price_text = price_elem.inner_text().strip()
                    # Extract numeric price
                    import re
                    price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                    if price_match:
                        price = float(price_match.group())
                        
                        ticket = {
                            'price': price,
                            'currency': 'GBP',
                            'quantity': 1,  # Default, will need to extract
                            'section': None,
                            'row': None,
                            'url': event_url,
                            'ticket_id': self._generate_ticket_id(price, 1, None, None)
                        }
                        tickets.append(ticket)
                
                except Exception as e:
                    logger.debug(f"Error in alternative extraction: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error in alternative extraction: {e}")
        
        return tickets
    
    def _extract_quantity(self, element) -> int:
        """Extract quantity available from ticket element."""
        try:
            # Look for quantity indicators
            quantity_elem = element.query_selector('[class*="quantity"], [class*="qty"], [data-quantity]')
            if quantity_elem:
                qty_text = quantity_elem.inner_text().strip()
                import re
                qty_match = re.search(r'\d+', qty_text)
                if qty_match:
                    return int(qty_match.group())
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
    
    def _generate_ticket_id(self, price: float, quantity: int, section: Optional[str], row: Optional[str]) -> str:
        """Generate a unique ID for a ticket."""
        # Create hash from ticket characteristics
        ticket_str = f"{price}_{quantity}_{section or ''}_{row or ''}"
        return hashlib.md5(ticket_str.encode()).hexdigest()
