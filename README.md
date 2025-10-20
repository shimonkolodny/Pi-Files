# AI Browser Controller

An AI-powered browser automation tool that uses Playwright and GitHub Models to control a web browser through natural language commands.

## Features

- 🤖 **AI-Powered Control**: Use natural language to control your browser
- 🌐 **Full Browser Control**: Navigate, click, type, take screenshots, and more
- ⚙️ **Configurable**: Set your API key and choose from multiple AI models
- 🔄 **Auto-Continue Mode**: Automatically continue tasks until completion
- 🎨 **Modern UI**: Beautiful, user-friendly chat interface with rounded edges
- 🔐 **Secure**: API keys stored locally in config.json (not committed to git)

## Prerequisites

- Python 3.8 or higher
- GitHub Models API key ([Get one here](https://github.com/marketplace/models))

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/shimonkolodny/Pi-Files.git
   cd Pi-Files
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install Playwright browsers:
   ```bash
   playwright install chromium
   ```

## Usage

1. Start the application:
   ```bash
   python browser_controller.py
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

3. Click the settings icon (⚙️) in the top-right corner

4. Configure your settings:
   - **API Key**: Your GitHub Models API key
   - **Primary Model**: The main AI model to use (e.g., gpt-4o)
   - **Backup Model 1**: First fallback model (e.g., gpt-4o-mini)
   - **Backup Model 2**: Second fallback model (e.g., gpt-3.5-turbo)

5. Start chatting! Tell the AI what you want it to do with the browser.

## Example Commands

- "Navigate to google.com"
- "Take a screenshot of the current page"
- "What's on the page?"
- "Click on the search button"
- "Type 'hello world' in the search box"
- "Go back to the previous page"
- "Wait 3 seconds"

## Available Browser Commands

The AI can execute the following Playwright commands:

1. **browser_navigate(url)** - Navigate to a URL
2. **browser_click(element, ref)** - Click on an element
3. **browser_type(element, ref, text, submit)** - Type text into a field
4. **browser_snapshot()** - Get page content snapshot
5. **browser_take_screenshot(filename)** - Take a screenshot
6. **browser_evaluate(function)** - Execute JavaScript
7. **browser_press_key(key)** - Press a keyboard key
8. **browser_hover(element, ref)** - Hover over an element
9. **browser_select_option(element, ref, values)** - Select dropdown option
10. **browser_wait_for(text/time)** - Wait for text or time
11. **browser_navigate_back()** - Go back to previous page
12. **browser_fill_form(fields)** - Fill multiple form fields

## Auto-Continue Mode

Enable the "Auto-continue mode" checkbox to automatically send "continue" after each AI response until the task is complete. This is useful for multi-step tasks.

## Security Notes

- Your API key is stored locally in `config.json`
- `config.json` is excluded from git via `.gitignore`
- Never commit your API key to version control

## Troubleshooting

**Browser doesn't open:**
- Make sure Playwright browsers are installed: `playwright install chromium`

**API errors:**
- Verify your GitHub Models API key is correct
- Check that you have access to the models you're trying to use

**Port already in use:**
- Change the port in `browser_controller.py` by modifying the `app.run()` line

## License

MIT License - feel free to use and modify as needed.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
