"""
Social Media Comment Analyzer - Application Launcher
This script handles the complete startup of both backend and frontend services.
"""

import subprocess
import sys
import os
import time
import socket
import webbrowser
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading

class AppLauncher:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.base_dir = Path(__file__).parent
        self.backend_port = 5000
        self.frontend_port = 3000
        
    def check_port_available(self, port):
        """Check if a port is available"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) != 0
    
    def wait_for_port(self, port, timeout=60):
        """Wait for a port to become available (service started)"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                if s.connect_ex(('localhost', port)) == 0:
                    return True
            time.sleep(1)
        return False
    
    def check_dependencies(self, log_callback):
        """Check if required dependencies are installed"""
        log_callback("Checking dependencies...\n")
        
        # Check Python
        try:
            python_version = sys.version.split()[0]
            log_callback(f"✓ Python {python_version} found\n")
        except:
            log_callback("✗ Python not found!\n")
            return False
        
        # Check Node.js
        try:
            result = subprocess.run(['node', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                log_callback(f"✓ Node.js {result.stdout.strip()} found\n")
            else:
                log_callback("✗ Node.js not found!\n")
                return False
        except:
            log_callback("✗ Node.js not found or not in PATH!\n")
            return False
        
        return True
    
    def install_backend_dependencies(self, log_callback):
        """Install Python backend dependencies"""
        log_callback("\nInstalling backend dependencies...\n")
        requirements_file = self.base_dir / 'backend' / 'requirements.txt'
        
        if not requirements_file.exists():
            log_callback("✗ requirements.txt not found!\n")
            return False
        
        try:
            process = subprocess.Popen(
                [sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=str(self.base_dir / 'backend')
            )
            
            for line in process.stdout:
                log_callback(line)
            
            process.wait()
            
            if process.returncode == 0:
                log_callback("✓ Backend dependencies installed successfully\n")
                return True
            else:
                log_callback("✗ Failed to install backend dependencies\n")
                return False
        except Exception as e:
            log_callback(f"✗ Error installing backend dependencies: {str(e)}\n")
            return False
    
    def install_frontend_dependencies(self, log_callback):
        """Install Node.js frontend dependencies"""
        log_callback("\nInstalling frontend dependencies...\n")
        frontend_dir = self.base_dir / 'frontend'
        
        if not (frontend_dir / 'package.json').exists():
            log_callback("✗ package.json not found!\n")
            return False
        
        try:
            process = subprocess.Popen(
                ['npm', 'install'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=str(frontend_dir),
                shell=True
            )
            
            for line in process.stdout:
                log_callback(line)
            
            process.wait()
            
            if process.returncode == 0:
                log_callback("✓ Frontend dependencies installed successfully\n")
                return True
            else:
                log_callback("✗ Failed to install frontend dependencies\n")
                return False
        except Exception as e:
            log_callback(f"✗ Error installing frontend dependencies: {str(e)}\n")
            return False
    
    def start_backend(self, log_callback):
        """Start the Flask backend server"""
        log_callback("\nStarting backend server...\n")
        
        # Check if port is already in use
        if not self.check_port_available(self.backend_port):
            log_callback(f"⚠ Port {self.backend_port} is already in use. Backend may already be running.\n")
            return True
        
        backend_dir = self.base_dir / 'backend'
        app_file = backend_dir / 'app.py'
        
        if not app_file.exists():
            log_callback("✗ app.py not found!\n")
            return False
        
        try:
            # Start backend process
            self.backend_process = subprocess.Popen(
                [sys.executable, 'app.py'],
                cwd=str(backend_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
            )
            
            log_callback("⏳ Waiting for backend to start...\n")
            
            # Wait for backend to be ready
            if self.wait_for_port(self.backend_port, timeout=60):
                log_callback(f"✓ Backend server started on http://localhost:{self.backend_port}\n")
                return True
            else:
                log_callback("✗ Backend server failed to start (timeout)\n")
                return False
                
        except Exception as e:
            log_callback(f"✗ Error starting backend: {str(e)}\n")
            return False
    
    def start_frontend(self, log_callback):
        """Start the React frontend server"""
        log_callback("\nStarting frontend server...\n")
        
        # Check if port is already in use
        if not self.check_port_available(self.frontend_port):
            log_callback(f"⚠ Port {self.frontend_port} is already in use. Frontend may already be running.\n")
            return True
        
        frontend_dir = self.base_dir / 'frontend'
        
        try:
            # Start frontend process
            env = os.environ.copy()
            env['BROWSER'] = 'none'  # Prevent auto-opening browser
            
            self.frontend_process = subprocess.Popen(
                ['npm', 'start'],
                cwd=str(frontend_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                env=env,
                shell=True,
                creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
            )
            
            log_callback("⏳ Waiting for frontend to start (this may take a minute)...\n")
            
            # Wait for frontend to be ready
            if self.wait_for_port(self.frontend_port, timeout=120):
                log_callback(f"✓ Frontend server started on http://localhost:{self.frontend_port}\n")
                return True
            else:
                log_callback("✗ Frontend server failed to start (timeout)\n")
                return False
                
        except Exception as e:
            log_callback(f"✗ Error starting frontend: {str(e)}\n")
            return False
    
    def open_browser(self, log_callback):
        """Open the application in default browser"""
        log_callback("\n🌐 Opening application in browser...\n")
        time.sleep(2)  # Give servers a moment to stabilize
        try:
            webbrowser.open(f'http://localhost:{self.frontend_port}')
            log_callback("✓ Application opened in browser\n")
            return True
        except Exception as e:
            log_callback(f"⚠ Could not open browser automatically: {str(e)}\n")
            log_callback(f"Please open http://localhost:{self.frontend_port} manually\n")
            return False
    
    def launch(self, log_callback):
        """Main launch sequence"""
        log_callback("=" * 60 + "\n")
        log_callback("Social Media Comment Analyzer - Starting Application\n")
        log_callback("=" * 60 + "\n\n")
        
        # Step 1: Check dependencies
        if not self.check_dependencies(log_callback):
            log_callback("\n✗ Dependency check failed!\n")
            log_callback("Please install Python 3.8+ and Node.js 14+ before running.\n")
            return False
        
        # Step 2: Install backend dependencies
        if not self.install_backend_dependencies(log_callback):
            log_callback("\n✗ Failed to install backend dependencies!\n")
            return False
        
        # Step 3: Install frontend dependencies
        if not self.install_frontend_dependencies(log_callback):
            log_callback("\n✗ Failed to install frontend dependencies!\n")
            return False
        
        # Step 4: Start backend
        if not self.start_backend(log_callback):
            log_callback("\n✗ Failed to start backend!\n")
            return False
        
        # Step 5: Start frontend
        if not self.start_frontend(log_callback):
            log_callback("\n✗ Failed to start frontend!\n")
            return False
        
        # Step 6: Open browser
        self.open_browser(log_callback)
        
        log_callback("\n" + "=" * 60 + "\n")
        log_callback("✓ APPLICATION STARTED SUCCESSFULLY!\n")
        log_callback("=" * 60 + "\n")
        log_callback(f"\n📱 Access the application at: http://localhost:{self.frontend_port}\n")
        log_callback(f"🔌 Backend API running at: http://localhost:{self.backend_port}\n")
        log_callback("\n⚠ Keep this window open while using the application.\n")
        log_callback("⚠ Close this window to stop all services.\n\n")
        
        return True
    
    def cleanup(self):
        """Stop all processes"""
        if self.backend_process:
            self.backend_process.terminate()
        if self.frontend_process:
            self.frontend_process.terminate()


class LauncherGUI:
    def __init__(self):
        self.launcher = AppLauncher()
        self.root = tk.Tk()
        self.root.title("Social Media Comment Analyzer")
        self.root.geometry("700x500")
        self.root.resizable(True, True)
        
        # Create GUI elements
        self.create_widgets()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_widgets(self):
        """Create GUI widgets"""
        # Title
        title_label = tk.Label(
            self.root, 
            text="Social Media Comment Analyzer",
            font=("Arial", 16, "bold"),
            pady=10
        )
        title_label.pack()
        
        # Status label
        self.status_label = tk.Label(
            self.root,
            text="Ready to start",
            font=("Arial", 10),
            fg="blue"
        )
        self.status_label.pack()
        
        # Log output
        log_frame = tk.Frame(self.root)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            wrap=tk.WORD,
            width=80,
            height=20,
            font=("Consolas", 9)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        
        self.start_button = tk.Button(
            button_frame,
            text="🚀 Start Application",
            command=self.start_application,
            font=("Arial", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            padx=20,
            pady=10
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.open_browser_button = tk.Button(
            button_frame,
            text="🌐 Open Browser",
            command=self.open_browser_manually,
            font=("Arial", 12),
            padx=20,
            pady=10,
            state=tk.DISABLED
        )
        self.open_browser_button.pack(side=tk.LEFT, padx=5)
        
        self.close_button = tk.Button(
            button_frame,
            text="❌ Close",
            command=self.on_closing,
            font=("Arial", 12),
            padx=20,
            pady=10
        )
        self.close_button.pack(side=tk.LEFT, padx=5)
    
    def log(self, message):
        """Add message to log"""
        self.log_text.insert(tk.END, message)
        self.log_text.see(tk.END)
        self.root.update()
    
    def start_application(self):
        """Start the application in a separate thread"""
        self.start_button.config(state=tk.DISABLED)
        self.status_label.config(text="Starting application...", fg="orange")
        
        def launch_thread():
            success = self.launcher.launch(self.log)
            
            if success:
                self.status_label.config(text="✓ Application running", fg="green")
                self.open_browser_button.config(state=tk.NORMAL)
            else:
                self.status_label.config(text="✗ Failed to start", fg="red")
                self.start_button.config(state=tk.NORMAL)
                messagebox.showerror(
                    "Error",
                    "Failed to start the application. Check the log for details."
                )
        
        thread = threading.Thread(target=launch_thread, daemon=True)
        thread.start()
    
    def open_browser_manually(self):
        """Open browser manually"""
        webbrowser.open(f'http://localhost:{self.launcher.frontend_port}')
    
    def on_closing(self):
        """Handle window close event"""
        if messagebox.askokcancel("Quit", "Do you want to quit? This will stop all services."):
            self.log("\n\nShutting down services...\n")
            self.launcher.cleanup()
            self.root.destroy()
    
    def run(self):
        """Run the GUI"""
        self.root.mainloop()


if __name__ == "__main__":
    app = LauncherGUI()
    app.run()
