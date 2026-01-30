"""SQLite database for tracking seen tickets."""
import sqlite3
import logging
from typing import List, Dict, Set, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class TicketDatabase:
    """Manages SQLite database for tracking seen tickets."""
    
    def __init__(self, db_path: str = 'tickets.db'):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS seen_tickets (
                ticket_id TEXT PRIMARY KEY,
                match_name TEXT NOT NULL,
                price REAL NOT NULL,
                quantity INTEGER NOT NULL,
                section TEXT,
                row TEXT,
                url TEXT NOT NULL,
                first_seen TIMESTAMP NOT NULL,
                last_seen TIMESTAMP NOT NULL
            )
        ''')
        
        # Create index on match_name for faster queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_match_name 
            ON seen_tickets(match_name)
        ''')
        
        conn.commit()
        conn.close()
        logger.info(f"Database initialized at {self.db_path}")
    
    def is_seen(self, ticket_id: str) -> bool:
        """Check if a ticket has been seen before."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT 1 FROM seen_tickets WHERE ticket_id = ?', (ticket_id,))
        result = cursor.fetchone()
        
        conn.close()
        return result is not None
    
    def mark_seen(self, ticket: Dict, match_name: str):
        """Mark a ticket as seen (insert or update)."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        # Check if ticket already exists
        cursor.execute('SELECT first_seen FROM seen_tickets WHERE ticket_id = ?', (ticket['ticket_id'],))
        existing = cursor.fetchone()
        
        if existing:
            # Update last_seen timestamp
            cursor.execute('''
                UPDATE seen_tickets 
                SET last_seen = ?
                WHERE ticket_id = ?
            ''', (now, ticket['ticket_id']))
        else:
            # Insert new ticket
            cursor.execute('''
                INSERT INTO seen_tickets 
                (ticket_id, match_name, price, quantity, section, row, url, first_seen, last_seen)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                ticket['ticket_id'],
                match_name,
                ticket.get('price', 0),
                ticket.get('quantity', 0),
                ticket.get('section'),
                ticket.get('row'),
                ticket.get('url', ''),
                now,
                now
            ))
        
        conn.commit()
        conn.close()
    
    def get_new_tickets(self, tickets: List[Dict], match_name: str) -> List[Dict]:
        """
        Filter out tickets that have been seen before.
        
        Args:
            tickets: List of ticket dictionaries
            match_name: Name of the match
            
        Returns:
            List of tickets that haven't been seen before
        """
        new_tickets = []
        
        for ticket in tickets:
            ticket_id = ticket.get('ticket_id')
            if ticket_id and not self.is_seen(ticket_id):
                new_tickets.append(ticket)
                # Mark as seen immediately
                self.mark_seen(ticket, match_name)
        
        logger.info(f"Found {len(new_tickets)} new tickets out of {len(tickets)} total")
        return new_tickets
    
    def get_seen_ticket_ids(self, match_name: Optional[str] = None) -> Set[str]:
        """Get set of all seen ticket IDs, optionally filtered by match."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if match_name:
            cursor.execute('SELECT ticket_id FROM seen_tickets WHERE match_name = ?', (match_name,))
        else:
            cursor.execute('SELECT ticket_id FROM seen_tickets')
        
        ticket_ids = {row[0] for row in cursor.fetchall()}
        conn.close()
        
        return ticket_ids
    
    def cleanup_old_tickets(self, days: int = 30):
        """Remove tickets older than specified days."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = datetime.now().replace(day=datetime.now().day - days).isoformat()
        cursor.execute('DELETE FROM seen_tickets WHERE last_seen < ?', (cutoff_date,))
        
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        logger.info(f"Cleaned up {deleted_count} old tickets")
        return deleted_count
