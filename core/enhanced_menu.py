#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromSploit Framework v2.0
Enhanced Menu System with improved navigation and visual feedback
"""

import os
import sys
import time
import threading
from typing import List, Dict, Any, Optional, Callable, Union, Tuple
from datetime import datetime

from core.colors import Colors
from core.menu import Menu, MenuItem

class EnhancedMenuItem(MenuItem):
 """Enhanced menu item with additional features"""
 
 def __init__(self, text: str, action: Callable, color: str = Colors.WHITE, 
 shortcut: Optional[str] = None, description: Optional[str] = None,
 dangerous: bool = False, key: Optional[str] = None, title: Optional[str] = None):
 super().__init__(text, action, color)
 self.shortcut = shortcut
 self.description = description
 self.dangerous = dangerous
 self.key = key
 self.title = title
 self.enabled = True
 self.badge = None
 
 def set_enabled(self, enabled: bool):
 """Enable or disable the menu item"""
 self.enabled = enabled
 
 def set_badge(self, badge: str):
 """Set a badge (like 'NEW' or a count) for the item"""
 self.badge = badge

class ProgressBar:
 """Simple progress bar for visual feedback"""
 
 def __init__(self, total: int, width: int = 50, title: str = "Progress"):
 self.total = total
 self.current = 0
 self.width = width
 self.title = title
 self.start_time = time.time()
 
 def update(self, current: int):
 """Update progress bar"""
 self.current = current
 percent = (current / self.total) * 100
 filled = int((current / self.total) * self.width)
 bar = "█" * filled + "░" * (self.width - filled)
 
 elapsed = time.time() - self.start_time
 if current > 0:
 eta = (elapsed / current) * (self.total - current)
 eta_str = f"ETA: {int(eta)}s"
 else:
 eta_str = "ETA: --"
 
 print(f"\r{self.title}: [{bar}] {percent:.1f}% {eta_str}", end="", flush=True)
 
 def finish(self):
 """Complete the progress bar"""
 self.update(self.total)
 print()

class EnhancedMenu(Menu):
 """Enhanced menu with improved features"""
 
 def __init__(self, title: str, parent=None):
 super().__init__(title, parent)
 self.description = None
 self.breadcrumb = []
 self.notifications = []
 self.status_message = None
 self.show_time = True
 self.show_breadcrumb = True
 self.loading = False
 
 def set_description(self, description: str):
 """Set menu description"""
 self.description = description
 
 def add_enhanced_item(self, text: str, action: Callable, color: str = Colors.WHITE,
 shortcut: Optional[str] = None, description: Optional[str] = None,
 dangerous: bool = False, key: Optional[str] = None, title: Optional[str] = None) -> None:
 """Add an enhanced menu item"""
 item = EnhancedMenuItem(
 text=text, 
 action=action, 
 color=color, 
 shortcut=shortcut, 
 description=description, 
 dangerous=dangerous, 
 key=key, 
 title=title
 )
 self.items.append(item)
 
 def add_notification(self, message: str, type: str = "info"):
 """Add a notification to display"""
 colors = {
 "info": Colors.CYAN,
 "success": Colors.GREEN,
 "warning": Colors.YELLOW,
 "error": Colors.RED
 }
 self.notifications.append({
 "message": message,
 "type": type,
 "color": colors.get(type, Colors.WHITE),
 "timestamp": datetime.now()
 })
 # Keep only last 5 notifications
 if len(self.notifications) > 5:
 self.notifications.pop(0)
 
 def set_status(self, message: str):
 """Set a status message"""
 self.status_message = message
 
 def show_loading(self, message: str = "Loading...", duration: float = 2.0):
 """Show a loading animation"""
 self.loading = True
 spinner = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
 
 def spin():
 start_time = time.time()
 i = 0
 while self.loading and (time.time() - start_time) < duration:
 print(f"\r{Colors.CYAN}{spinner[i % len(spinner)]} {message}{Colors.RESET}", end="", flush=True)
 time.sleep(0.1)
 i += 1
 print("\r" + " " * (len(message) + 3) + "\r", end="", flush=True)
 self.loading = False
 
 thread = threading.Thread(target=spin)
 thread.start()
 return thread
 
 def _draw_header(self):
 """Draw enhanced header with breadcrumb and time"""
 width = 80
 
 # Top border
 print(f"{Colors.CYAN}╭{'─' * (width - 2)}╮{Colors.RESET}")
 
 # Title line
 title_str = f" {self.title} "
 padding = (width - 2 - len(title_str)) // 2
 print(f"{Colors.CYAN}│{' ' * padding}{Colors.YELLOW}{title_str}{Colors.CYAN}{' ' * (width - 2 - padding - len(title_str))}│{Colors.RESET}")
 
 # Breadcrumb line
 if self.show_breadcrumb and self.parent:
 breadcrumb = self._build_breadcrumb()
 breadcrumb_str = " > ".join(breadcrumb)
 if len(breadcrumb_str) > width - 4:
 breadcrumb_str = "..." + breadcrumb_str[-(width - 7):]
 print(f"{Colors.CYAN}│ {Colors.BLUE}{breadcrumb_str}{' ' * (width - 3 - len(breadcrumb_str))}{Colors.CYAN}│{Colors.RESET}")
 
 # Time line
 if self.show_time:
 time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
 print(f"{Colors.CYAN}│{' ' * (width - 3 - len(time_str))}{Colors.GREEN}{time_str} {Colors.CYAN}│{Colors.RESET}")
 
 # Bottom border
 print(f"{Colors.CYAN}╰{'─' * (width - 2)}╯{Colors.RESET}")
 
 def _build_breadcrumb(self):
 """Build breadcrumb trail"""
 breadcrumb = []
 current = self
 while current:
 breadcrumb.insert(0, current.title)
 current = current.parent
 return breadcrumb
 
 def _draw_notifications(self):
 """Draw notification area"""
 if self.notifications:
 print(f"\n{Colors.CYAN}── Notifications ──{Colors.RESET}")
 for notif in self.notifications[-3:]: # Show last 3
 icon = {"info": "ℹ", "success": "", "warning": "", "error": ""}.get(notif["type"], "•")
 time_str = notif["timestamp"].strftime("%H:%M")
 print(f"{notif['color']}{icon} [{time_str}] {notif['message']}{Colors.RESET}")
 
 def _draw_status(self):
 """Draw status bar"""
 if self.status_message:
 width = 80
 status = f" {self.status_message} "
 padding = (width - len(status)) // 2
 print(f"\n{Colors.CYAN}{'─' * padding}{status}{'─' * (width - padding - len(status))}{Colors.RESET}")
 
 def _draw_menu_items(self):
 """Draw menu items with enhanced formatting"""
 print(f"\n{Colors.BRIGHT_WHITE}Please select an option:{Colors.RESET}\n")
 
 for i, item in enumerate(self.items, 1):
 if isinstance(item, EnhancedMenuItem):
 # Build item string
 item_str = f"{Colors.BRIGHT_BLUE}{i}){Colors.RESET} "
 
 # Add danger indicator
 if item.dangerous:
 item_str += f"{Colors.RED} {Colors.RESET}"
 
 # Add item text with color
 if item.enabled:
 item_str += f"{item.color}{item.text}{Colors.RESET}"
 else:
 item_str += f"{Colors.DARK_GRAY}{item.text} (disabled){Colors.RESET}"
 
 # Add badge
 if item.badge:
 item_str += f" {Colors.YELLOW}[{item.badge}]{Colors.RESET}"
 
 # Add shortcut
 if item.shortcut:
 item_str += f" {Colors.DARK_GRAY}({item.shortcut}){Colors.RESET}"
 
 print(item_str)
 
 # Add description
 if item.description:
 print(f" {Colors.DARK_GRAY}{item.description}{Colors.RESET}")
 else:
 # Standard menu item
 print(f"{Colors.BRIGHT_BLUE}{i}){Colors.RESET} {item.color}{item.text}{Colors.RESET}")
 
 def _draw_help_line(self):
 """Draw help line at bottom"""
 help_items = []
 if self.parent:
 help_items.append("B/Back")
 help_items.extend(["Q/Quit", "?/Help"])
 
 help_str = " | ".join(help_items)
 print(f"\n{Colors.DARK_GRAY}[{help_str}]{Colors.RESET}")
 
 def display(self) -> Any:
 """Enhanced display with better navigation"""
 while True:
 self._clear()
 
 # Draw components
 self._draw_header()
 self._draw_notifications()
 
 if self.info_text:
 print(f"\n{Colors.BRIGHT_WHITE}{self.info_text}{Colors.RESET}")
 
 self._draw_status()
 self._draw_menu_items()
 self._draw_help_line()
 
 # Handle input
 try:
 choice = input(f"\n{Colors.BRIGHT_GREEN}Choice: {Colors.RESET}").strip()
 
 # Help command
 if choice == "?":
 self._show_help()
 continue
 
 # Check shortcuts FIRST (before quit check)
 shortcut_handled = False
 for i, item in enumerate(self.items):
 if isinstance(item, EnhancedMenuItem) and item.shortcut:
 if choice.lower() == item.shortcut.lower():
 shortcut_handled = True
 if not item.enabled:
 self.add_notification("This option is currently disabled", "warning")
 time.sleep(1)
 continue
 if item.dangerous and not self._confirm_dangerous_action(item.text):
 continue
 return self._execute_item(item)
 
 if shortcut_handled:
 continue
 
 # Back navigation
 if choice.lower() in ['b', 'back'] and self.parent:
 return None
 
 # Quit (only if not a shortcut)
 if choice.lower() in ['quit', 'exit'] or (choice.lower() == 'q' and not any(
 item.shortcut and item.shortcut.lower() == 'q' 
 for item in self.items if isinstance(item, EnhancedMenuItem)
 )):
 if self._confirm_exit():
 print(f"\n{Colors.CYAN}Exiting ChromSploit Framework. Goodbye!{Colors.RESET}")
 sys.exit(0)
 continue
 
 # Numeric selection
 try:
 index = int(choice) - 1
 if 0 <= index < len(self.items):
 item = self.items[index]
 
 if isinstance(item, EnhancedMenuItem):
 if not item.enabled:
 self.add_notification("This option is currently disabled", "warning")
 time.sleep(1)
 continue
 if item.dangerous and not self._confirm_dangerous_action(item.text):
 continue
 
 return self._execute_item(item)
 else:
 self.add_notification(f"Invalid selection. Please choose 1-{len(self.items)}", "error")
 time.sleep(1)
 except ValueError:
 self.add_notification("Invalid input. Please enter a number or command", "error")
 time.sleep(1)
 
 except KeyboardInterrupt:
 print(f"\n{Colors.YELLOW}Operation cancelled by user{Colors.RESET}")
 if self.parent:
 return None
 else:
 if self._confirm_exit():
 print(f"\n{Colors.CYAN}Exiting ChromSploit Framework. Goodbye!{Colors.RESET}")
 sys.exit(0)
 except Exception as e:
 self.add_notification(f"Error: {str(e)}", "error")
 time.sleep(2)
 
 def _execute_item(self, item: MenuItem) -> Any:
 """Execute menu item with error handling"""
 try:
 result = item.execute()
 if result == "exit":
 return None
 return result
 except Exception as e:
 self.add_notification(f"Error executing {item.text}: {str(e)}", "error")
 time.sleep(2)
 return None
 
 def _confirm_exit(self) -> bool:
 """Confirm exit action"""
 confirm = input(f"\n{Colors.YELLOW}Are you sure you want to exit? (y/N): {Colors.RESET}")
 return confirm.lower() == 'y'
 
 def _confirm_dangerous_action(self, action: str) -> bool:
 """Confirm dangerous action"""
 print(f"\n{Colors.RED} Warning: This is a potentially dangerous operation!{Colors.RESET}")
 print(f"{Colors.YELLOW}Action: {action}{Colors.RESET}")
 confirm = input(f"{Colors.RED}Are you sure you want to continue? (type 'yes' to confirm): {Colors.RESET}")
 return confirm.lower() == 'yes'
 
 def _show_help(self):
 """Show help screen"""
 self._clear()
 self._draw_box(80, "Help & Navigation")
 
 print(f"\n{Colors.CYAN}Navigation Commands:{Colors.RESET}")
 print(f" {Colors.GREEN}1-9{Colors.RESET} - Select menu option by number")
 print(f" {Colors.GREEN}B/Back{Colors.RESET} - Return to previous menu")
 print(f" {Colors.GREEN}Q/Quit{Colors.RESET} - Exit the application")
 print(f" {Colors.GREEN}?/Help{Colors.RESET} - Show this help screen")
 
 print(f"\n{Colors.CYAN}Shortcuts:{Colors.RESET}")
 for item in self.items:
 if isinstance(item, EnhancedMenuItem) and item.shortcut:
 print(f" {Colors.GREEN}{item.shortcut}{Colors.RESET} - {item.text}")
 
 print(f"\n{Colors.CYAN}Visual Indicators:{Colors.RESET}")
 print(f" {Colors.RED}{Colors.RESET} - Dangerous operation (requires confirmation)")
 print(f" {Colors.YELLOW}[NEW]{Colors.RESET} - New feature or update")
 print(f" {Colors.DARK_GRAY}(disabled){Colors.RESET} - Option currently unavailable")
 
 input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
 
 def exit_menu(self):
 """Exit the current menu and return to parent"""
 return None
 
 def run(self):
 """Run the menu (alias for display)"""
 return self.display()

def demo_enhanced_menu():
 """Demo function to test enhanced menu"""
 menu = EnhancedMenu("Enhanced Menu Demo")
 menu.set_info_text("This is a demonstration of the enhanced menu system")
 
 menu.add_enhanced_item("Normal Option", lambda: print("Normal action"), Colors.GREEN, "n", "A regular menu option")
 menu.add_enhanced_item("New Feature", lambda: print("New feature"), Colors.CYAN, "f", "Try out this new feature", False)
 menu.items[-1].set_badge("NEW")
 
 menu.add_enhanced_item("Dangerous Operation", lambda: print("Dangerous!"), Colors.RED, "d", "This will perform a dangerous operation", True)
 
 disabled_item = EnhancedMenuItem("Disabled Option", lambda: None, Colors.GRAY, "x", "This option is currently disabled")
 disabled_item.set_enabled(False)
 menu.items.append(disabled_item)
 
 menu.add_notification("Welcome to the enhanced menu system!", "success")
 menu.add_notification("Some features are still in development", "warning")
 
 menu.set_status("System Status: All services operational")
 
 return menu

if __name__ == "__main__":
 # Test the enhanced menu
 demo = demo_enhanced_menu()
 demo.display()