"""Ticket filtering logic based on user criteria."""
import logging
from typing import List, Dict
from config import SearchCriteria

logger = logging.getLogger(__name__)


class TicketFilter:
    """Filters tickets based on user-defined criteria."""
    
    def __init__(self, criteria: SearchCriteria):
        self.criteria = criteria
    
    def filter_tickets(self, tickets: List[Dict]) -> List[Dict]:
        """
        Filter tickets based on search criteria.
        
        Args:
            tickets: List of ticket dictionaries
            
        Returns:
            List of tickets that match the criteria
        """
        matching_tickets = []
        
        for ticket in tickets:
            if self._matches_criteria(ticket):
                matching_tickets.append(ticket)
        
        logger.info(f"Filtered {len(tickets)} tickets down to {len(matching_tickets)} matches")
        return matching_tickets
    
    def _matches_criteria(self, ticket: Dict) -> bool:
        """Check if a ticket matches all criteria."""
        # Check price range
        if not self._matches_price(ticket):
            return False
        
        # Check quantity
        if not self._matches_quantity(ticket):
            return False
        
        # Check section preferences (if specified)
        if self.criteria.preferred_sections and not self._matches_section(ticket):
            return False
        
        return True
    
    def _matches_price(self, ticket: Dict) -> bool:
        """Check if ticket price is within range."""
        price = ticket.get('price', 0)
        return self.criteria.min_price <= price <= self.criteria.max_price
    
    def _matches_quantity(self, ticket: Dict) -> bool:
        """Check if ticket quantity meets requirement."""
        quantity = ticket.get('quantity', 0)
        return quantity >= self.criteria.quantity_needed
    
    def _matches_section(self, ticket: Dict) -> bool:
        """Check if ticket section matches preferences."""
        section = ticket.get('section', '')
        
        if not section:
            # If no section preference specified, allow tickets without section info
            if not self.criteria.preferred_sections:
                return True
            # If preferences exist but ticket has no section, exclude it
            return False
        
        section_lower = section.lower()
        
        # Check if any preferred section matches (case-insensitive, partial match)
        for preferred in self.criteria.preferred_sections:
            preferred_lower = preferred.lower()
            # Allow exact match or contains match
            if preferred_lower in section_lower or section_lower in preferred_lower:
                return True
        
        return False
