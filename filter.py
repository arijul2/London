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
        # Check price
        if not self._matches_price(ticket):
            return False
        
        # Check quantity
        if not self._matches_quantity(ticket):
            return False
        
        # Check trustable seller (if required)
        if not self._matches_trustable_seller(ticket):
            return False
        
        return True
    
    def _matches_price(self, ticket: Dict) -> bool:
        """Check if ticket price is within budget."""
        price = ticket.get('price', 0)
        return price <= self.criteria.max_price
    
    def _matches_quantity(self, ticket: Dict) -> bool:
        """Check if ticket quantity meets requirement."""
        quantity = ticket.get('quantity', 0)
        return quantity >= self.criteria.min_tickets
    
    def _matches_trustable_seller(self, ticket: Dict) -> bool:
        """Check if ticket is from trustable seller (if required)."""
        # If trustable_seller_only is False, accept all tickets
        if not self.criteria.trustable_seller_only:
            return True
        
        # If trustable_seller_only is True, only accept tickets from trustable sellers
        trustable_seller = ticket.get('trustable_seller', False)
        return trustable_seller
