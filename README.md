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
   - Set the match you want to monitor
   - Configure price range and quantity
   - Set up notification preferences

## Configuration

Edit the `.env` file with your settings:

### Search Criteria

- `MATCH_NAME`: The match to monitor (e.g., "Arsenal vs Everton")
- `MIN_PRICE`: Minimum price per ticket in GBP
- `MAX_PRICE`: Maximum price per ticket in GBP
- `QUANTITY_NEEDED`: Number of tickets needed
- `PREFERRED_SECTIONS`: Comma-separated list of preferred sections (optional)

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
