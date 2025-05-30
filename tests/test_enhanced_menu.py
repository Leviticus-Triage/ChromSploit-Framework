#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromSploit Framework v2.0
Tests for enhanced menu system
"""

import sys
import pytest
from unittest.mock import Mock, patch, call
from tests.test_base import TestBase

from core.enhanced_menu import (
    EnhancedMenu, EnhancedMenuItem, ProgressBar
)
from core.error_handler import ErrorSeverity, ErrorCategory
from core.colors import Colors

class TestEnhancedMenuItem(TestBase):
    """Test enhanced menu item functionality"""
    
    def test_item_creation(self):
        """Test creating enhanced menu item"""
        action = Mock()
        item = EnhancedMenuItem(
            text="Test Item",
            action=action,
            color=Colors.GREEN,
            shortcut="t",
            description="Test description",
            dangerous=False
        )
        
        assert item.text == "Test Item"
        assert item.color == Colors.GREEN
        assert item.shortcut == "t"
        assert item.description == "Test description"
        assert not item.dangerous
        assert item.enabled
        assert item.badge is None
    
    def test_item_state_management(self):
        """Test item enable/disable and badge"""
        item = EnhancedMenuItem("Test", Mock())
        
        # Test enable/disable
        item.set_enabled(False)
        assert not item.enabled
        
        item.set_enabled(True)
        assert item.enabled
        
        # Test badge
        item.set_badge("NEW")
        assert item.badge == "NEW"
    
    def test_item_execution(self):
        """Test item action execution"""
        action = Mock(return_value="result")
        item = EnhancedMenuItem("Test", action)
        
        result = item.execute()
        
        action.assert_called_once()
        assert result == "result"

class TestProgressBar(TestBase):
    """Test progress bar functionality"""
    
    def test_progress_bar_creation(self):
        """Test creating progress bar"""
        bar = ProgressBar(total=100, width=50, title="Test")
        
        assert bar.total == 100
        assert bar.current == 0
        assert bar.width == 50
        assert bar.title == "Test"
    
    def test_progress_update(self):
        """Test progress bar updates"""
        bar = ProgressBar(total=10, width=10)
        
        bar.update(5)
        assert bar.current == 5
        
        bar.update(10)
        assert bar.current == 10
    
    def test_progress_finish(self):
        """Test progress bar completion"""
        bar = ProgressBar(total=10)
        bar.finish()
        
        assert bar.current == bar.total

class TestEnhancedMenu(TestBase):
    """Test enhanced menu functionality"""
    
    def test_menu_creation(self):
        """Test creating enhanced menu"""
        menu = EnhancedMenu("Test Menu")
        
        assert menu.title == "Test Menu"
        assert menu.parent is None
        assert len(menu.items) == 0
        assert len(menu.notifications) == 0
        assert menu.status_message is None
        assert menu.show_time
        assert menu.show_breadcrumb
        assert not menu.loading
    
    def test_add_enhanced_item(self):
        """Test adding enhanced menu items"""
        menu = EnhancedMenu("Test Menu")
        
        menu.add_enhanced_item(
            text="Item 1",
            action=Mock(),
            color=Colors.GREEN,
            shortcut="1",
            description="First item",
            dangerous=False
        )
        
        assert len(menu.items) == 1
        assert isinstance(menu.items[0], EnhancedMenuItem)
        assert menu.items[0].text == "Item 1"
        assert menu.items[0].shortcut == "1"
    
    def test_notifications(self):
        """Test notification system"""
        menu = EnhancedMenu("Test Menu")
        
        # Add notifications
        menu.add_notification("Info message", "info")
        menu.add_notification("Success message", "success")
        menu.add_notification("Warning message", "warning")
        menu.add_notification("Error message", "error")
        
        assert len(menu.notifications) == 4
        
        # Test notification colors
        assert menu.notifications[0]['color'] == Colors.CYAN
        assert menu.notifications[1]['color'] == Colors.GREEN
        assert menu.notifications[2]['color'] == Colors.YELLOW
        assert menu.notifications[3]['color'] == Colors.RED
        
        # Test notification limit
        for i in range(10):
            menu.add_notification(f"Message {i}", "info")
        
        assert len(menu.notifications) == 5  # Limited to 5
    
    def test_status_message(self):
        """Test status message"""
        menu = EnhancedMenu("Test Menu")
        
        menu.set_status("System running")
        assert menu.status_message == "System running"
    
    def test_loading_animation(self):
        """Test loading animation"""
        menu = EnhancedMenu("Test Menu")
        
        thread = menu.show_loading("Processing...", duration=0.1)
        thread.join(timeout=1)
        
        assert not menu.loading
    
    def test_breadcrumb_building(self):
        """Test breadcrumb trail building"""
        # Create menu hierarchy
        root = EnhancedMenu("Root")
        child1 = EnhancedMenu("Child 1", parent=root)
        child2 = EnhancedMenu("Child 2", parent=child1)
        
        breadcrumb = child2._build_breadcrumb()
        
        assert breadcrumb == ["Root", "Child 1", "Child 2"]
    
    @patch('builtins.input')
    def test_menu_navigation(self, mock_input):
        """Test menu navigation"""
        menu = EnhancedMenu("Test Menu")
        menu.add_enhanced_item("Option 1", lambda: "result1", shortcut="o")
        menu.add_enhanced_item("Exit", lambda: None)
        
        # Test numeric selection
        mock_input.side_effect = ["1"]
        with patch.object(menu, '_clear'), patch('builtins.print'):
            result = menu.display()
            assert result == "result1"
    
    @patch('builtins.input')
    def test_help_command(self, mock_input):
        """Test help command"""
        menu = EnhancedMenu("Test Menu")
        menu.add_enhanced_item("Option", Mock(), shortcut="o")
        
        mock_input.side_effect = ["?", "b"]
        menu.parent = Mock()  # Set parent to allow back navigation
        
        with patch.object(menu, '_clear'), patch('builtins.print') as mock_print:
            menu.display()
            
            # Check if help was displayed
            print_calls = [str(call) for call in mock_print.call_args_list]
            help_displayed = any("Navigation Commands" in call for call in print_calls)
            assert help_displayed
    
    @patch('builtins.input')
    def test_dangerous_action_confirmation(self, mock_input):
        """Test dangerous action confirmation"""
        menu = EnhancedMenu("Test Menu")
        dangerous_action = Mock(return_value="dangerous_result")
        
        menu.add_enhanced_item(
            "Dangerous Option",
            dangerous_action,
            dangerous=True
        )
        
        # Test confirmation
        mock_input.side_effect = ["1", "yes"]
        with patch.object(menu, '_clear'), patch('builtins.print'):
            result = menu.display()
            dangerous_action.assert_called_once()
            assert result == "dangerous_result"
    
    @patch('builtins.input')
    def test_disabled_item_handling(self, mock_input):
        """Test disabled menu item"""
        menu = EnhancedMenu("Test Menu")
        action = Mock()
        
        menu.add_enhanced_item("Disabled Option", action)
        menu.items[0].set_enabled(False)
        
        mock_input.side_effect = ["1", "b"]
        menu.parent = Mock()
        
        with patch.object(menu, '_clear'), patch('builtins.print'), patch('time.sleep'):
            menu.display()
            
            # Action should not be called
            action.assert_not_called()
            
            # Check notification
            assert any("disabled" in n['message'] for n in menu.notifications)
    
    @patch('builtins.input')
    def test_exit_confirmation(self, mock_input):
        """Test exit confirmation"""
        menu = EnhancedMenu("Test Menu")
        
        # Test exit cancellation and then confirmation
        mock_input.side_effect = ["q", "y"]
        
        with pytest.raises(SystemExit), patch.object(menu, '_clear'), patch('builtins.print'):
            menu.display()
    
    def test_error_handling_in_menu_item(self):
        """Test error handling when executing menu items"""
        menu = EnhancedMenu("Test Menu")
        
        def failing_action():
            raise ValueError("Test error")
        
        menu.add_enhanced_item("Failing Option", failing_action)
        
        # Execute item that raises exception
        with patch('time.sleep'):
            result = menu._execute_item(menu.items[0])
        
        assert result is None
        assert any("Error executing" in n['message'] for n in menu.notifications)

class TestMenuIntegration(TestBase):
    """Integration tests for menu system"""
    
    @patch('builtins.input')
    def test_complex_menu_navigation(self, mock_input):
        """Test navigating through multiple menu levels"""
        # Create menu hierarchy
        main = EnhancedMenu("Main Menu")
        sub1 = EnhancedMenu("Submenu 1", parent=main)
        
        # Add navigation items
        main.add_enhanced_item("Go to Submenu 1", lambda: sub1.display())
        
        sub1.add_enhanced_item("Action 1", lambda: "result1")
        
        # Navigate to submenu 1, execute action, go back
        mock_input.side_effect = ["1", "1", "b", "q", "y"]
        
        with pytest.raises(SystemExit), patch.object(main, '_clear'), patch.object(sub1, '_clear'), patch('builtins.print'):
            main.display()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])