#!/usr/bin/env python3
"""
SAP AI Core LLM Proxy - Desktop Application
A desktop application wrapper for the SAP AI Core LLM Proxy server.
Uses PyWebView to create a native window with the React frontend.
Supports system tray icon and background running.
"""

import os
import sys
import threading
import time
import queue
import logging
import webview
from io import StringIO
from PIL import Image

# Try to import pystray for system tray support
try:
    import pystray
    from pystray import MenuItem as item
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False
    logging.warning("pystray not available. System tray support disabled.")

# Ensure the current directory is in the path
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    APP_DIR = os.path.dirname(sys.executable)
else:
    # Running as script
    APP_DIR = os.path.dirname(os.path.abspath(__file__))

os.chdir(APP_DIR)
sys.path.insert(0, APP_DIR)

# Icon path
ICON_PATH = os.path.join(APP_DIR, 'icons', 'app.ico')
ICON_PNG_PATH = os.path.join(APP_DIR, 'icons', 'icon.png')

# Configure logging to capture logs for the log window
log_queue = queue.Queue(maxsize=1000)

class QueueHandler(logging.Handler):
    """Custom logging handler that puts log records into a queue."""
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue
    
    def emit(self, record):
        try:
            msg = self.format(record)
            # If queue is full, remove oldest item
            if self.log_queue.full():
                try:
                    self.log_queue.get_nowait()
                except queue.Empty:
                    pass
            self.log_queue.put_nowait(msg)
        except Exception:
            self.handleError(record)

# Setup queue handler for log window
queue_handler = QueueHandler(log_queue)
queue_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
queue_handler.setLevel(logging.INFO)

# Add handler to root logger
root_logger = logging.getLogger()
root_logger.addHandler(queue_handler)


class ServerManager:
    """Manages the Flask server lifecycle."""
    
    def __init__(self):
        self.server_thread = None
        self.is_running = False
        self.port = 3001
        self.host = '127.0.0.1'
        self.app = None
        self.server = None
        
    def start(self, config_path='config.json'):
        """Start the Flask server in a background thread."""
        if self.is_running:
            logging.info("Server is already running")
            return
        
        def run_server():
            try:
                # Import and configure the Flask app
                from proxy_server import app, load_config, proxy_config, ProxyConfig
                
                self.app = app
                
                # Load configuration
                logging.info(f"Loading configuration from: {config_path}")
                config = load_config(config_path)
                
                if isinstance(config, ProxyConfig):
                    # Copy config to global proxy_config
                    proxy_config.subaccounts = config.subaccounts
                    proxy_config.secret_authentication_tokens = config.secret_authentication_tokens
                    proxy_config.port = config.port
                    proxy_config.host = config.host
                    
                    # Initialize all subaccounts
                    proxy_config.initialize()
                    
                    self.host = proxy_config.host
                    self.port = proxy_config.port
                    
                    logging.info(f"Loaded configuration with {len(proxy_config.subaccounts)} subAccounts")
                
                self.is_running = True
                logging.info(f"Starting server on http://{self.host}:{self.port}")
                
                # Use waitress if available, otherwise use Flask dev server
                try:
                    from waitress import serve
                    logging.info("Using Waitress production server")
                    serve(app, host=self.host, port=self.port,
                          threads=100,
                          connection_limit=2000,
                          cleanup_interval=15,
                          channel_timeout=300)
                except ImportError:
                    logging.warning("Waitress not available, using Flask development server")
                    app.run(host=self.host, port=self.port, debug=False, threaded=True, use_reloader=False)
                    
            except Exception as e:
                logging.error(f"Server error: {e}", exc_info=True)
                self.is_running = False
        
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        
        # Wait for server to start
        time.sleep(2)
        logging.info("Server started successfully")
    
    def stop(self):
        """Stop the Flask server."""
        self.is_running = False
        logging.info("Server stopping...")


class SystemTrayManager:
    """Manages the system tray icon and menu."""
    
    def __init__(self, app_manager):
        self.app_manager = app_manager
        self.icon = None
        self.is_visible = True
        self._stop_event = threading.Event()
        
    def create_icon(self):
        """Create the system tray icon."""
        if not TRAY_AVAILABLE:
            logging.warning("System tray not available")
            return None
        
        # Load icon image
        try:
            if os.path.exists(ICON_PNG_PATH):
                image = Image.open(ICON_PNG_PATH)
            elif os.path.exists(ICON_PATH):
                image = Image.open(ICON_PATH)
            else:
                # Create a simple default icon
                image = Image.new('RGB', (64, 64), color='#667eea')
                logging.warning("Icon file not found, using default color icon")
        except Exception as e:
            logging.error(f"Failed to load icon: {e}")
            image = Image.new('RGB', (64, 64), color='#667eea')
        
        return image
    
    def create_menu(self):
        """Create the system tray menu."""
        return pystray.Menu(
            item('显示窗口', self.show_window, default=True),
            item('隐藏窗口', self.hide_window),
            pystray.Menu.SEPARATOR,
            item('打开日志', self.open_logs),
            item('打开浏览器', self.open_browser),
            pystray.Menu.SEPARATOR,
            item('退出', self.quit_app)
        )
    
    def show_window(self, icon=None, item=None):
        """Show the main window."""
        if self.app_manager.main_window:
            try:
                self.app_manager.main_window.show()
                self.app_manager.main_window.restore()
                self.is_visible = True
                logging.info("Window shown")
            except Exception as e:
                logging.error(f"Failed to show window: {e}")
    
    def hide_window(self, icon=None, item=None):
        """Hide the main window to system tray."""
        if self.app_manager.main_window:
            try:
                self.app_manager.main_window.hide()
                self.is_visible = False
                logging.info("Window hidden to system tray")
            except Exception as e:
                logging.error(f"Failed to hide window: {e}")
    
    def open_logs(self, icon=None, item=None):
        """Open the log window."""
        if self.app_manager.main_api:
            self.app_manager.main_api.open_log_window()
    
    def open_browser(self, icon=None, item=None):
        """Open the application in the default browser."""
        import webbrowser
        url = f"http://localhost:{self.app_manager.server_manager.port}"
        webbrowser.open(url)
        logging.info(f"Opened browser: {url}")
    
    def quit_app(self, icon=None, item=None):
        """Quit the application."""
        logging.info("Quitting application from system tray")
        self._stop_event.set()
        if self.icon:
            self.icon.stop()
        self.app_manager.quit()
    
    def start(self):
        """Start the system tray icon."""
        if not TRAY_AVAILABLE:
            return
        
        def run_tray():
            image = self.create_icon()
            menu = self.create_menu()
            
            self.icon = pystray.Icon(
                "SAP AI Proxy",
                image,
                "SAP AI Core LLM Proxy",
                menu
            )
            
            logging.info("System tray icon started")
            self.icon.run()
        
        self.tray_thread = threading.Thread(target=run_tray, daemon=True)
        self.tray_thread.start()
    
    def stop(self):
        """Stop the system tray icon."""
        self._stop_event.set()
        if self.icon:
            try:
                self.icon.stop()
            except Exception as e:
                logging.error(f"Error stopping tray icon: {e}")


class LogWindowAPI:
    """JavaScript API for the log window."""
    
    def __init__(self, log_queue):
        self.log_queue = log_queue
        self._logs = []
        self._max_logs = 500
    
    def get_logs(self):
        """Get all logs and new logs from the queue."""
        # Get new logs from queue
        while not self.log_queue.empty():
            try:
                log = self.log_queue.get_nowait()
                self._logs.append(log)
                # Keep only the last max_logs
                if len(self._logs) > self._max_logs:
                    self._logs = self._logs[-self._max_logs:]
            except queue.Empty:
                break
        return self._logs
    
    def clear_logs(self):
        """Clear all logs."""
        self._logs = []
        # Also clear the queue
        while not self.log_queue.empty():
            try:
                self.log_queue.get_nowait()
            except queue.Empty:
                break
        return True


class MainWindowAPI:
    """JavaScript API for the main window."""
    
    def __init__(self, server_manager, log_window_api, tray_manager=None):
        self.server_manager = server_manager
        self.log_window_api = log_window_api
        self.tray_manager = tray_manager
        self.log_window = None
    
    def get_server_status(self):
        """Get the current server status."""
        return {
            'running': self.server_manager.is_running,
            'host': self.server_manager.host,
            'port': self.server_manager.port,
            'url': f"http://{self.server_manager.host}:{self.server_manager.port}"
        }
    
    def open_log_window(self):
        """Open the log window."""
        if self.log_window is None or not self.log_window.shown:
            self.log_window = webview.create_window(
                'Server Logs - SAP AI Core LLM Proxy',
                html=get_log_window_html(),
                width=900,
                height=600,
                js_api=self.log_window_api,
                resizable=True,
                min_size=(600, 400)
            )
        return True
    
    def open_external_url(self, url):
        """Open a URL in the default browser."""
        import webbrowser
        webbrowser.open(url)
        return True
    
    def minimize_to_tray(self):
        """Minimize the window to system tray."""
        if self.tray_manager:
            self.tray_manager.hide_window()
        return True


class AppManager:
    """Main application manager that coordinates all components."""
    
    def __init__(self, config_path='config.json', debug=False):
        self.config_path = config_path
        self.debug = debug
        self.server_manager = ServerManager()
        self.tray_manager = None
        self.main_window = None
        self.main_api = None
        self.log_api = None
        self._quit_requested = False
        
    def initialize(self):
        """Initialize all components."""
        # Initialize APIs
        self.log_api = LogWindowAPI(log_queue)
        
        # Initialize system tray
        if TRAY_AVAILABLE:
            self.tray_manager = SystemTrayManager(self)
        
        # Initialize main API
        self.main_api = MainWindowAPI(
            self.server_manager, 
            self.log_api,
            self.tray_manager
        )
    
    def create_main_window(self):
        """Create the main application window."""
        # Get icon path for window
        icon_path = ICON_PATH if os.path.exists(ICON_PATH) else None
        
        self.main_window = webview.create_window(
            'SAP AI Core LLM Proxy',
            html=get_loading_html(),
            width=1200,
            height=800,
            js_api=self.main_api,
            resizable=True,
            min_size=(800, 600),
            on_top=False,
            confirm_close=True  # Enable close confirmation
        )
        
        # Bind the closing event to minimize to tray instead of closing
        self.main_window.events.closing += self.on_window_closing
        
        return self.main_window
    
    def on_window_closing(self):
        """Handle window closing event - minimize to tray instead of closing."""
        if TRAY_AVAILABLE and self.tray_manager and not self._quit_requested:
            logging.info("Window close requested - minimizing to tray instead")
            # Hide window to tray
            def hide_async():
                time.sleep(0.1)
                if self.main_window:
                    try:
                        self.main_window.hide()
                        logging.info("Window hidden to system tray")
                    except Exception as e:
                        logging.error(f"Failed to hide window: {e}")
            threading.Thread(target=hide_async, daemon=True).start()
            return False  # Prevent window from closing
        return True  # Allow window to close
    
    def on_window_close(self):
        """Handle window close event - minimize to tray instead of closing."""
        if TRAY_AVAILABLE and self.tray_manager and not self._quit_requested:
            logging.info("Window close requested - minimizing to tray")
            self.tray_manager.hide_window()
            return False  # Prevent window from closing
        return True  # Allow window to close
    
    def on_loaded(self):
        """Called when the main window is loaded."""
        # Start the server
        self.server_manager.start(self.config_path)
        
        # Wait for server to be ready
        max_retries = 20
        for i in range(max_retries):
            time.sleep(0.5)
            if self.server_manager.is_running:
                break
            logging.info(f"Waiting for server to start... ({i+1}/{max_retries})")
        
        # Extra wait for server to fully initialize
        time.sleep(1)
        
        # Navigate to the actual application
        if self.server_manager.is_running:
            app_url = f'http://localhost:{self.server_manager.port}'
            self.main_window.load_url(app_url)
            logging.info(f"Application loaded: {app_url}")
        else:
            self.main_window.load_html('''
            <html>
            <body style="font-family: sans-serif; padding: 40px; background: #fff5f5;">
                <h1 style="color: #c53030;">Server Error</h1>
                <p>Failed to start the server. Please check the logs for details.</p>
            </body>
            </html>
            ''')
    
    def quit(self):
        """Quit the application."""
        self._quit_requested = True
        logging.info("Application quit requested")
        
        # Stop tray icon
        if self.tray_manager:
            self.tray_manager.stop()
        
        # Stop server
        self.server_manager.stop()
        
        # Close all windows
        try:
            for window in webview.windows:
                window.destroy()
        except Exception as e:
            logging.error(f"Error closing windows: {e}")
    
    def run(self):
        """Run the application."""
        # Initialize components
        self.initialize()
        
        # Create main window
        self.create_main_window()
        
        # Start system tray
        if self.tray_manager:
            self.tray_manager.start()
        
        # Start server after window is created
        def start_app():
            time.sleep(1)  # Wait for window to be ready
            self.on_loaded()
        
        threading.Thread(target=start_app, daemon=True).start()
        
        # Start the application
        logging.info("Starting PyWebView")
        webview.start(debug=self.debug)
        
        # Cleanup on exit
        logging.info("Application closing")
        self.quit()


def get_log_window_html():
    """Generate the HTML for the log window."""
    return '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Server Logs</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            background: #1e1e1e;
            color: #d4d4d4;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        .toolbar {
            background: #333;
            padding: 8px 12px;
            display: flex;
            gap: 10px;
            align-items: center;
            border-bottom: 1px solid #444;
        }
        .toolbar button {
            background: #0e639c;
            color: white;
            border: none;
            padding: 6px 14px;
            border-radius: 3px;
            cursor: pointer;
            font-size: 12px;
        }
        .toolbar button:hover {
            background: #1177bb;
        }
        .toolbar .status {
            margin-left: auto;
            font-size: 12px;
            color: #888;
        }
        .log-container {
            flex: 1;
            overflow-y: auto;
            padding: 10px;
        }
        .log-line {
            padding: 2px 0;
            white-space: pre-wrap;
            word-break: break-all;
            font-size: 12px;
            line-height: 1.4;
        }
        .log-line.info { color: #4fc1ff; }
        .log-line.warning { color: #cca700; }
        .log-line.error { color: #f14c4c; }
        .log-line.debug { color: #888; }
        .log-line:hover {
            background: #2d2d2d;
        }
        #auto-scroll {
            margin-left: 10px;
        }
        label {
            font-size: 12px;
            color: #ccc;
        }
    </style>
</head>
<body>
    <div class="toolbar">
        <button onclick="clearLogs()">Clear Logs</button>
        <button onclick="copyLogs()">Copy All</button>
        <label>
            <input type="checkbox" id="auto-scroll" checked>
            Auto-scroll
        </label>
        <span class="status" id="log-count">0 logs</span>
    </div>
    <div class="log-container" id="log-container"></div>
    
    <script>
        let lastLogCount = 0;
        
        function getLogLevel(logLine) {
            if (logLine.includes(' - ERROR - ') || logLine.includes('ERROR:')) return 'error';
            if (logLine.includes(' - WARNING - ') || logLine.includes('WARNING:')) return 'warning';
            if (logLine.includes(' - DEBUG - ') || logLine.includes('DEBUG:')) return 'debug';
            return 'info';
        }
        
        async function refreshLogs() {
            try {
                const logs = await pywebview.api.get_logs();
                const container = document.getElementById('log-container');
                const autoScroll = document.getElementById('auto-scroll').checked;
                const wasAtBottom = container.scrollHeight - container.scrollTop <= container.clientHeight + 50;
                
                if (logs.length !== lastLogCount) {
                    container.innerHTML = logs.map(log => {
                        const level = getLogLevel(log);
                        return `<div class="log-line ${level}">${escapeHtml(log)}</div>`;
                    }).join('');
                    
                    lastLogCount = logs.length;
                    document.getElementById('log-count').textContent = `${logs.length} logs`;
                    
                    if (autoScroll && wasAtBottom) {
                        container.scrollTop = container.scrollHeight;
                    }
                }
            } catch (e) {
                console.error('Failed to refresh logs:', e);
            }
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        async function clearLogs() {
            await pywebview.api.clear_logs();
            lastLogCount = 0;
            document.getElementById('log-container').innerHTML = '';
            document.getElementById('log-count').textContent = '0 logs';
        }
        
        function copyLogs() {
            const container = document.getElementById('log-container');
            const text = container.innerText;
            navigator.clipboard.writeText(text).then(() => {
                alert('Logs copied to clipboard!');
            });
        }
        
        // Refresh logs every 500ms
        setInterval(refreshLogs, 500);
        refreshLogs();
    </script>
</body>
</html>
'''


def get_loading_html():
    """Generate a loading page HTML."""
    return '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Loading...</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        .loader-container {
            text-align: center;
            color: white;
        }
        .loader {
            width: 50px;
            height: 50px;
            border: 4px solid rgba(255,255,255,0.3);
            border-top-color: white;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        h1 {
            font-size: 24px;
            margin-bottom: 10px;
        }
        p {
            font-size: 14px;
            opacity: 0.8;
        }
    </style>
</head>
<body>
    <div class="loader-container">
        <div class="loader"></div>
        <h1>SAP AI Core LLM Proxy</h1>
        <p>Starting server...</p>
    </div>
</body>
</html>
'''


def main():
    """Main entry point for the desktop application."""
    import argparse
    
    parser = argparse.ArgumentParser(description="SAP AI Core LLM Proxy Desktop Application")
    parser.add_argument("--config", type=str, default="config.json", help="Path to configuration file")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()
    
    # Set logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug("Debug mode enabled")
    else:
        logging.getLogger().setLevel(logging.INFO)
    
    logging.info("Starting SAP AI Core LLM Proxy Desktop Application")
    
    # Check if config file exists
    config_path = args.config
    if not os.path.exists(config_path):
        logging.error(f"Configuration file not found: {config_path}")
        webview.create_window(
            'Error - SAP AI Core LLM Proxy',
            html=f'''
            <html>
            <body style="font-family: sans-serif; padding: 40px; background: #fff5f5;">
                <h1 style="color: #c53030;">Configuration Error</h1>
                <p>Configuration file not found: <code>{config_path}</code></p>
                <p>Please create a <code>config.json</code> file in the application directory.</p>
                <p>You can copy from <code>config.json.example</code> as a template.</p>
            </body>
            </html>
            ''',
            width=500,
            height=300
        )
        webview.start()
        return
    
    # Create and run the application
    app = AppManager(config_path=config_path, debug=args.debug)
    app.run()


if __name__ == '__main__':
    main()