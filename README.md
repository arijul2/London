# Premier League Ticket Monitor

Automated ticket monitoring system for Premier League matches on fanpass.net. Monitors ticket listings and sends notifications when tickets matching your criteria become available.

## Features

- **Automated Monitoring**: Continuously checks for new tickets at configurable intervals
- **Smart Filtering**: Filter by price range, quantity, and preferred sections/stands
- **Duplicate Prevention**: Tracks seen tickets to avoid duplicate notifications
- **Multi-Channel Notifications**: Email, Pushover push notifications, and desktop notifications
- **Easy Configuration**: Simple `.env` file configuration

## Requirements

- Python 3.8+
- Playwright browser (installed automatically)

## Installation

1. **Clone or download this repository**

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Playwright browsers:**
   ```bash
   playwright install chromium
   ```

4. **Configure your settings:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your preferences:
   - Configure matches to monitor (each with its own criteria)
   - Set up notification preferences

## Configuration

Edit the `.env` file with your settings:

### Match Configuration

Each match requires three parameters:
- `MATCH_N_NAME`: Match name (e.g., "Arsenal vs Everton")
- `MATCH_N_MIN_TICKETS`: Minimum number of tickets needed
- `MATCH_N_MAX_PRICE`: Maximum price per ticket in GBP

Optional per-match:
- `MATCH_N_TRUSTABLE_SELLER_ONLY`: If `true`, only listings from trustable sellers (default: `false`)
- `MATCH_N_NOTIFY_SEEN_TICKETS`: If `true`, every check sends a notification with all current matching listings (including ones you’ve already seen). If `false`, you’re only notified when new matching tickets appear (default: `false`).

**Example for multiple matches:**
```bash
# Match 1
MATCH_1_NAME=Arsenal vs Everton
MATCH_1_MIN_TICKETS=2
MATCH_1_MAX_PRICE=500

# Match 2
MATCH_2_NAME=Liverpool vs Manchester City
MATCH_2_MIN_TICKETS=1
MATCH_2_MAX_PRICE=300
```

Each match is monitored independently with its own criteria. All matches are checked simultaneously every N minutes.

### Monitoring

- `CHECK_INTERVAL_MINUTES`: How often to check for tickets (default: 30 minutes)

### Notifications

#### Email (Gmail example)
- `EMAIL_ENABLED=true`
- `EMAIL_TO=your-email@example.com`
- `EMAIL_USERNAME=your-email@gmail.com`
- `EMAIL_PASSWORD=your-app-password` (use Gmail App Password, not regular password)

#### Pushover
1. Sign up at https://pushover.net
2. Get your User Key and create an Application to get API Key
3. Set `PUSHOVER_ENABLED=true` and add your keys

#### Desktop Notifications
- `DESKTOP_NOTIFICATIONS_ENABLED=true` (works on macOS and Linux)

## Usage

### Run continuously (monitoring mode)
```bash
python main.py
```

The monitor will check for tickets every N minutes (as configured) and send notifications when matching tickets are found.

### Run once (test mode)
```bash
RUN_ONCE=true python main.py
```

This runs a single check and exits. Useful for testing your configuration.

## How It Works

1. **Scraping**: Uses Playwright to load the fanpass.net event page and extract ticket data (price, quantity, section, row)
2. **Filtering**: Filters tickets based on your criteria (price range, quantity, section preferences)
3. **Deduplication**: Tracks seen tickets in SQLite database to avoid duplicate notifications
4. **Notifications**: Sends alerts through enabled notification channels when new matching tickets are found

## Database

The system uses SQLite (`tickets.db`) to track seen tickets. This file is created automatically and prevents duplicate notifications.

## Troubleshooting

### No tickets found
- Verify the match name is correct (check fanpass.net for exact format)
- The event page might not exist yet - check the URL manually
- Try running with `RUN_ONCE=true` to see detailed logs

### Notifications not working
- **Email**: Check your SMTP settings and use App Password for Gmail
- **Pushover**: Verify your API key and User key are correct
- **Desktop**: Ensure notifications are enabled in your OS settings

### Playwright errors
- Make sure you ran `playwright install chromium`
- Check your internet connection
- The website structure might have changed - check the logs

### Scraper not finding ticket details
- The website structure may have changed
- Try running with headless mode disabled (edit `scraper.py` to set `headless=False`) to see what's happening
- Check the logs for extraction errors

## Logs

Logs are written to:
- Console (stdout)
- `ticket_monitor.log` file

## Legal & Ethical Considerations

- This tool is for personal use only
- Be respectful with request frequency (default 30 minutes is reasonable)
- Review fanpass.net's Terms of Service
- Don't abuse the system or overload their servers

## License

This project is for personal use. Use responsibly and in accordance with fanpass.net's terms of service.
