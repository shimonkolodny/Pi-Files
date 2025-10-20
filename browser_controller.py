#!/usr/bin/env python3
"""
AI-Controlled Browser using Playwright and GitHub Models
This application provides a chat interface to control a browser using AI.
"""

import json
import os
import threading
import time
from flask import Flask, render_template_string, request, jsonify, session
from playwright.sync_api import sync_playwright
import requests

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Global playwright browser instance
browser_instance = None
page_instance = None
playwright_instance = None

# Configuration file path
CONFIG_FILE = 'config.json'

def load_config():
    """Load configuration from file or return defaults"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {
        'api_key': '',
        'primary_model': 'gpt-4o',
        'backup_model_1': 'gpt-4o-mini',
        'backup_model_2': 'gpt-3.5-turbo'
    }

def save_config(config):
    """Save configuration to file"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

SYSTEM_INSTRUCTIONS = """You are an AI assistant that controls a web browser using Playwright commands. 

Available Commands:
1. browser_navigate(url) - Navigate to a specific URL
   Say: "Navigate to [URL]" or "Go to [URL]"
   
2. browser_click(element, ref) - Click on an element
   Say: "Click on [element description]"
   
3. browser_type(element, ref, text, submit=False) - Type text into an input field
   Say: "Type '[text]' in [element]" or "Enter '[text]' in [element]"
   
4. browser_snapshot() - Take an accessibility snapshot of the current page
   Say: "What's on the page?" or "Show me the current page"
   
5. browser_take_screenshot(filename) - Take a screenshot
   Say: "Take a screenshot" or "Screenshot the page"
   
6. browser_evaluate(function) - Execute JavaScript on the page
   Say: "Execute JavaScript: [code]"
   
7. browser_press_key(key) - Press a keyboard key
   Say: "Press [key]"
   
8. browser_hover(element, ref) - Hover over an element
   Say: "Hover over [element]"
   
9. browser_select_option(element, ref, values) - Select option from dropdown
   Say: "Select [option] from [dropdown]"
   
10. browser_wait_for(text/time) - Wait for text to appear or time to pass
    Say: "Wait for [text]" or "Wait [X] seconds"
    
11. browser_navigate_back() - Go back to previous page
    Say: "Go back" or "Navigate back"
    
12. browser_fill_form(fields) - Fill multiple form fields
    Say: "Fill form with [field details]"

When a user asks you to do something with the browser, analyze their request and respond with the appropriate command using the exact function call format. Always explain what you're doing before executing commands.

If you need more information about the current page state, use browser_snapshot() first.

IMPORTANT: After completing each action, if you're not done with the full task, end your response with exactly "CONTINUE" on a new line. If the task is complete, end with "DONE".
"""

def call_github_models(messages, model, api_key):
    """Call GitHub Models API"""
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    
    data = {
        'model': model,
        'messages': messages,
        'temperature': 0.7,
        'max_tokens': 2000
    }
    
    try:
        response = requests.post(
            'https://models.github.com/v1/chat/completions',
            headers=headers,
            json=data,
            timeout=30
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        raise Exception(f"API Error: {str(e)}")

def init_browser():
    """Initialize Playwright browser"""
    global browser_instance, page_instance, playwright_instance
    
    if playwright_instance is None:
        try:
            playwright_instance = sync_playwright().start()
            browser_instance = playwright_instance.chromium.launch(headless=False)
            page_instance = browser_instance.new_page()
            page_instance.set_viewport_size({"width": 1280, "height": 720})
        except Exception as e:
            raise Exception(f"Failed to initialize browser. Make sure Playwright is installed with 'playwright install chromium'. Error: {str(e)}")
    
    return page_instance

def close_browser():
    """Close Playwright browser"""
    global browser_instance, page_instance, playwright_instance
    
    if page_instance:
        page_instance.close()
        page_instance = None
    if browser_instance:
        browser_instance.close()
        browser_instance = None
    if playwright_instance:
        playwright_instance.stop()
        playwright_instance = None

def execute_playwright_command(command, params):
    """Execute a Playwright command"""
    page = init_browser()
    
    try:
        if command == 'browser_navigate':
            page.goto(params['url'])
            return f"Navigated to {params['url']}"
            
        elif command == 'browser_click':
            # In a real implementation, we'd use the ref from snapshot
            # For now, we'll use a simple selector
            page.click(params.get('selector', 'body'))
            return f"Clicked on {params.get('element', 'element')}"
            
        elif command == 'browser_type':
            page.fill(params.get('selector', 'input'), params['text'])
            if params.get('submit'):
                page.press(params.get('selector', 'input'), 'Enter')
            return f"Typed '{params['text']}'"
            
        elif command == 'browser_snapshot':
            # Get page title and URL
            title = page.title()
            url = page.url()
            # Get visible text (simplified)
            text = page.evaluate("() => document.body.innerText")
            return f"Page: {title}\nURL: {url}\n\nVisible text (first 500 chars):\n{text[:500]}"
            
        elif command == 'browser_take_screenshot':
            filename = params.get('filename', f'screenshot_{int(time.time())}.png')
            page.screenshot(path=filename)
            return f"Screenshot saved as {filename}"
            
        elif command == 'browser_evaluate':
            result = page.evaluate(params['function'])
            return f"JavaScript result: {result}"
            
        elif command == 'browser_press_key':
            page.keyboard.press(params['key'])
            return f"Pressed key: {params['key']}"
            
        elif command == 'browser_hover':
            page.hover(params.get('selector', 'body'))
            return f"Hovered over {params.get('element', 'element')}"
            
        elif command == 'browser_navigate_back':
            page.go_back()
            return "Navigated back"
            
        elif command == 'browser_wait_for':
            if 'time' in params:
                time.sleep(params['time'])
                return f"Waited {params['time']} seconds"
            else:
                page.wait_for_selector(f"text={params['text']}")
                return f"Waited for text: {params['text']}"
                
        else:
            return f"Unknown command: {command}"
            
    except Exception as e:
        return f"Error executing command: {str(e)}"

# HTML Template with CSS and JavaScript
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Browser Controller</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .container {
            width: 100%;
            max-width: 800px;
            height: 90vh;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .header h1 {
            font-size: 24px;
            font-weight: 600;
        }
        
        .settings-btn {
            background: rgba(255, 255, 255, 0.2);
            border: none;
            color: white;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            cursor: pointer;
            font-size: 20px;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .settings-btn:hover {
            background: rgba(255, 255, 255, 0.3);
            transform: rotate(45deg);
        }
        
        .chat-container {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: #f7f7f8;
        }
        
        .message {
            margin-bottom: 15px;
            display: flex;
            animation: fadeIn 0.3s;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .message.user {
            justify-content: flex-end;
        }
        
        .message-content {
            max-width: 70%;
            padding: 12px 18px;
            border-radius: 18px;
            word-wrap: break-word;
        }
        
        .message.user .message-content {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-bottom-right-radius: 4px;
        }
        
        .message.assistant .message-content {
            background: white;
            color: #333;
            border-bottom-left-radius: 4px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }
        
        .message.system .message-content {
            background: #fff3cd;
            color: #856404;
            border-left: 4px solid #ffc107;
            max-width: 100%;
        }
        
        .input-container {
            padding: 20px;
            background: white;
            border-top: 1px solid #e0e0e0;
        }
        
        .input-wrapper {
            display: flex;
            gap: 10px;
            align-items: center;
        }
        
        .input-box {
            flex: 1;
            padding: 12px 18px;
            border: 2px solid #e0e0e0;
            border-radius: 25px;
            font-size: 14px;
            outline: none;
            transition: all 0.3s;
        }
        
        .input-box:focus {
            border-color: #667eea;
        }
        
        .send-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 25px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s;
        }
        
        .send-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .send-btn:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }
        
        .auto-checkbox {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-top: 10px;
            font-size: 14px;
            color: #666;
        }
        
        .auto-checkbox input[type="checkbox"] {
            width: 18px;
            height: 18px;
            cursor: pointer;
        }
        
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }
        
        .modal.active {
            display: flex;
        }
        
        .modal-content {
            background: white;
            padding: 30px;
            border-radius: 20px;
            width: 90%;
            max-width: 500px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        }
        
        .modal-header {
            font-size: 24px;
            font-weight: 600;
            margin-bottom: 20px;
            color: #333;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
            color: #555;
        }
        
        .form-group input {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 14px;
            outline: none;
            transition: all 0.3s;
        }
        
        .form-group input:focus {
            border-color: #667eea;
        }
        
        .modal-buttons {
            display: flex;
            gap: 10px;
            justify-content: flex-end;
            margin-top: 25px;
        }
        
        .modal-btn {
            padding: 10px 20px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s;
        }
        
        .modal-btn.save {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .modal-btn.cancel {
            background: #e0e0e0;
            color: #333;
        }
        
        .modal-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        }
        
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255,255,255,.3);
            border-radius: 50%;
            border-top-color: white;
            animation: spin 1s ease-in-out infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 AI Browser Controller</h1>
            <button class="settings-btn" onclick="openSettings()">⚙️</button>
        </div>
        
        <div class="chat-container" id="chatContainer">
            <div class="message system">
                <div class="message-content">
                    Welcome! I'm your AI browser assistant. I can help you navigate the web, click elements, fill forms, and more. 
                    Configure your API key in settings (⚙️) and then tell me what you'd like me to do!
                </div>
            </div>
        </div>
        
        <div class="input-container">
            <div class="input-wrapper">
                <input type="text" class="input-box" id="messageInput" 
                       placeholder="Tell me what to do with the browser..." 
                       onkeypress="if(event.key==='Enter') sendMessage()">
                <button class="send-btn" id="sendBtn" onclick="sendMessage()">Send</button>
            </div>
            <div class="auto-checkbox">
                <input type="checkbox" id="autoCheckbox">
                <label for="autoCheckbox">Auto-continue mode (automatically continue until task is done)</label>
            </div>
        </div>
    </div>
    
    <div class="modal" id="settingsModal">
        <div class="modal-content">
            <div class="modal-header">⚙️ Settings</div>
            
            <div class="form-group">
                <label for="apiKey">GitHub Models API Key</label>
                <input type="password" id="apiKey" placeholder="Enter your API key">
            </div>
            
            <div class="form-group">
                <label for="primaryModel">Primary Model</label>
                <input type="text" id="primaryModel" placeholder="e.g., gpt-4o">
            </div>
            
            <div class="form-group">
                <label for="backupModel1">Backup Model 1</label>
                <input type="text" id="backupModel1" placeholder="e.g., gpt-4o-mini">
            </div>
            
            <div class="form-group">
                <label for="backupModel2">Backup Model 2</label>
                <input type="text" id="backupModel2" placeholder="e.g., gpt-3.5-turbo">
            </div>
            
            <div class="modal-buttons">
                <button class="modal-btn cancel" onclick="closeSettings()">Cancel</button>
                <button class="modal-btn save" onclick="saveSettings()">Save</button>
            </div>
        </div>
    </div>
    
    <script>
        let conversationHistory = [];
        let isProcessing = false;
        
        async function loadSettings() {
            const response = await fetch('/api/config');
            const config = await response.json();
            document.getElementById('apiKey').value = config.api_key || '';
            document.getElementById('primaryModel').value = config.primary_model || 'gpt-4o';
            document.getElementById('backupModel1').value = config.backup_model_1 || 'gpt-4o-mini';
            document.getElementById('backupModel2').value = config.backup_model_2 || 'gpt-3.5-turbo';
        }
        
        function openSettings() {
            loadSettings();
            document.getElementById('settingsModal').classList.add('active');
        }
        
        function closeSettings() {
            document.getElementById('settingsModal').classList.remove('active');
        }
        
        async function saveSettings() {
            const config = {
                api_key: document.getElementById('apiKey').value,
                primary_model: document.getElementById('primaryModel').value,
                backup_model_1: document.getElementById('backupModel1').value,
                backup_model_2: document.getElementById('backupModel2').value
            };
            
            await fetch('/api/config', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(config)
            });
            
            closeSettings();
            addMessage('system', 'Settings saved successfully!');
        }
        
        function addMessage(type, content) {
            const chatContainer = document.getElementById('chatContainer');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${type}`;
            
            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            contentDiv.textContent = content;
            
            messageDiv.appendChild(contentDiv);
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
        
        async function sendMessage(isAuto = false) {
            const input = document.getElementById('messageInput');
            const message = isAuto ? 'continue' : input.value.trim();
            
            if (!message || isProcessing) return;
            
            if (!isAuto) {
                addMessage('user', message);
                input.value = '';
            }
            
            isProcessing = true;
            document.getElementById('sendBtn').disabled = true;
            document.getElementById('sendBtn').innerHTML = '<span class="loading"></span>';
            
            conversationHistory.push({role: 'user', content: message});
            
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        messages: conversationHistory
                    })
                });
                
                const data = await response.json();
                
                if (data.error) {
                    addMessage('system', `Error: ${data.error}`);
                } else {
                    addMessage('assistant', data.response);
                    conversationHistory.push({role: 'assistant', content: data.response});
                    
                    // Check if auto-continue is enabled and response ends with CONTINUE
                    const autoMode = document.getElementById('autoCheckbox').checked;
                    if (autoMode && data.response.trim().endsWith('CONTINUE')) {
                        // Wait a bit before continuing
                        setTimeout(() => sendMessage(true), 1000);
                        return; // Don't reset isProcessing yet
                    }
                }
            } catch (error) {
                addMessage('system', `Error: ${error.message}`);
            }
            
            isProcessing = false;
            document.getElementById('sendBtn').disabled = false;
            document.getElementById('sendBtn').textContent = 'Send';
        }
        
        // Load settings on page load
        loadSettings();
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Serve the main page"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/config', methods=['GET', 'POST'])
def config():
    """Get or update configuration"""
    if request.method == 'POST':
        config = request.json
        save_config(config)
        return jsonify({'status': 'success'})
    else:
        return jsonify(load_config())

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    data = request.json
    messages = data.get('messages', [])
    
    # Load config
    config = load_config()
    api_key = config.get('api_key')
    
    if not api_key:
        return jsonify({'error': 'Please configure your API key in settings'})
    
    # Add system instructions
    full_messages = [{'role': 'system', 'content': SYSTEM_INSTRUCTIONS}] + messages
    
    # Try primary model first, then backups
    models_to_try = [
        config.get('primary_model', 'gpt-4o'),
        config.get('backup_model_1', 'gpt-4o-mini'),
        config.get('backup_model_2', 'gpt-3.5-turbo')
    ]
    
    last_error = None
    for model in models_to_try:
        try:
            response = call_github_models(full_messages, model, api_key)
            
            # Parse response for Playwright commands (simplified)
            # In a real implementation, you'd parse for specific command patterns
            # For now, we'll just return the AI response
            
            return jsonify({'response': response})
        except Exception as e:
            # Log the error for debugging but don't expose details to user
            print(f"Model {model} failed: {str(e)}")
            last_error = "API request failed"
            continue
    
    return jsonify({'error': 'All configured models failed. Please check your API key and model configuration.'})

def main():
    """Main entry point"""
    print("=" * 60)
    print("AI Browser Controller")
    print("=" * 60)
    print("\nStarting server...")
    print("Open your browser and go to: http://localhost:5000")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        close_browser()
        print("Goodbye!")

if __name__ == '__main__':
    main()
