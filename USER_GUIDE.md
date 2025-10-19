# User Guide - AI Browser Controller

## Quick Start Guide

### 1. Installation

First, install the dependencies:

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. Get Your GitHub Models API Key

1. Visit [GitHub Marketplace - Models](https://github.com/marketplace/models)
2. Sign in with your GitHub account
3. Generate an API key for the models you want to use
4. Save this key - you'll need it in the next step

### 3. Start the Application

Run the application:

```bash
python browser_controller.py
```

You should see:
```
============================================================
AI Browser Controller
============================================================

Starting server...
Open your browser and go to: http://localhost:5000

Press Ctrl+C to stop the server
============================================================
```

### 4. Configure Settings

1. Open your web browser and go to `http://localhost:5000`
2. Click the **⚙️** icon in the top-right corner
3. Enter your configuration:
   - **API Key**: Your GitHub Models API key
   - **Primary Model**: `gpt-4o` (or another model you have access to)
   - **Backup Model 1**: `gpt-4o-mini` (used if primary fails)
   - **Backup Model 2**: `gpt-3.5-turbo` (used if both above fail)
4. Click **Save**

### 5. Start Using!

Now you can chat with the AI to control your browser. Try these examples:

#### Basic Navigation
- "Navigate to google.com"
- "Go to github.com"

#### Getting Page Information
- "What's on the page?"
- "Take a screenshot"

#### Interacting with Elements
- "Click on the search button"
- "Type 'hello world' in the search box"

#### Advanced Tasks
- "Search Google for 'Python tutorials'"
- "Fill the login form with username 'test' and password 'demo'"

## Features Explained

### Auto-Continue Mode

The **Auto-continue mode** checkbox at the bottom allows you to enable automatic task continuation:

- **Checked**: After the AI responds, if it says "CONTINUE", the system automatically sends "continue" back to the AI
- **Unchecked**: You manually control when to send the next message

This is useful for multi-step tasks like:
- "Search for Python tutorials and click on the first result"
- "Navigate to amazon.com, search for laptops, and show me the first 5 results"

### Available Commands

The AI can execute these Playwright commands:

1. **browser_navigate(url)** - Navigate to a URL
2. **browser_click(element, ref)** - Click an element
3. **browser_type(element, ref, text, submit)** - Type text
4. **browser_snapshot()** - Get page content
5. **browser_take_screenshot(filename)** - Capture screenshot
6. **browser_evaluate(function)** - Run JavaScript
7. **browser_press_key(key)** - Press a key
8. **browser_hover(element, ref)** - Hover over element
9. **browser_select_option(element, ref, values)** - Select from dropdown
10. **browser_wait_for(text/time)** - Wait for condition
11. **browser_navigate_back()** - Go back
12. **browser_fill_form(fields)** - Fill multiple fields

### Understanding the Interface

#### Chat Area (Center)
- **User messages** appear on the right in purple
- **AI responses** appear on the left in white
- **System messages** appear in yellow

#### Settings Dialog
- Stores configuration in `config.json` (not committed to git)
- Changes take effect immediately
- API key is stored locally on your machine

#### Input Area (Bottom)
- Type your command to the AI
- Press Enter or click Send
- Enable auto-continue for complex tasks

## Tips for Best Results

### Be Specific
Instead of: "Go to Google"
Try: "Navigate to google.com"

### Request Snapshots First
For complex interactions:
1. "Navigate to example.com"
2. "What's on the page?"
3. "Click on the login button"

### Use Natural Language
The AI understands context:
- "Search for cats"
- "Click the first result"
- "Go back to the search results"

## Troubleshooting

### "API key not configured"
- Click the ⚙️ settings icon
- Enter your GitHub Models API key
- Click Save

### "All models failed"
- Check your API key is correct
- Verify you have access to the models you specified
- Try using different model names

### Browser doesn't open
- Make sure Playwright is installed: `playwright install chromium`
- On Linux, you may need: `playwright install-deps chromium`

### Server won't start
- Check if port 5000 is already in use
- Try changing the port in `browser_controller.py`

## Security Notes

⚠️ **Important Security Information:**

- Your API key is stored in `config.json` on your local machine
- This file is excluded from git via `.gitignore`
- Never share your `config.json` file
- Never commit API keys to version control
- The AI can execute JavaScript and navigate to any URL
- Only use this tool on trusted websites
- Monitor browser activity when using auto-continue mode

## Advanced Usage

### Custom Models
You can use any model available through GitHub Models:
- gpt-4o
- gpt-4o-mini
- gpt-3.5-turbo
- claude-3-opus
- And more...

### Changing the Port
Edit `browser_controller.py` and modify:
```python
app.run(host='0.0.0.0', port=5000, debug=False)
```

### Running in Production
For production use, deploy with a proper WSGI server:
```bash
pip install gunicorn
gunicorn browser_controller:app
```

## Example Workflows

### Automated Research
1. "Navigate to scholar.google.com"
2. "Search for 'machine learning papers 2024'"
3. "Take a screenshot of the results"

### Web Testing
1. "Navigate to mywebsite.com"
2. "Click all the navigation links one by one"
3. "Take a screenshot of each page"

### Data Collection
1. "Navigate to example.com/products"
2. "What products are shown on this page?"
3. "Go to the next page"

## Getting Help

If you encounter issues:
1. Check the terminal output for error messages
2. Review this user guide
3. Check that your API key is valid
4. Ensure Playwright browsers are installed

## Updates and Contributions

This is an open-source project. Feel free to:
- Report bugs
- Suggest features
- Submit pull requests
- Share your use cases

Enjoy using AI Browser Controller! 🚀
