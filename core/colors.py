#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromSploit Framework v2.0
Farb-Definitionen für das Framework
Für Bildungs- und autorisierte Penetrationstests
"""

class Colors:
    """
    ANSI-Farbdefinitionen für die Konsolenausgabe
    """
    # Standard-Farben
    RESET = "\033[0m"
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # Helle Farben
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"
    
    # Formatierung
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    ITALIC = "\033[3m"
    
    # Benutzerdefinierte Farben
    ORANGE = "\033[38;5;208m"
    PURPLE = "\033[38;5;135m"
    NEON_GREEN = "\033[38;5;82m"
    NEON_BLUE = "\033[38;5;39m"
    DARK_RED = "\033[38;5;88m"
    
    # Hintergrundfarben
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"
    
    # Helle Hintergrundfarben
    BG_BRIGHT_BLACK = "\033[100m"
    BG_BRIGHT_RED = "\033[101m"
    BG_BRIGHT_GREEN = "\033[102m"
    BG_BRIGHT_YELLOW = "\033[103m"
    BG_BRIGHT_BLUE = "\033[104m"
    BG_BRIGHT_MAGENTA = "\033[105m"
    BG_BRIGHT_CYAN = "\033[106m"
    BG_BRIGHT_WHITE = "\033[107m"
    
    @staticmethod
    def colorize(text, color):
        """
        Färbt einen Text mit der angegebenen Farbe ein
        
        Args:
            text (str): Der einzufärbende Text
            color (str): Die ANSI-Farbsequenz
            
        Returns:
            str: Der eingefärbte Text
        """
        return f"{color}{text}{Colors.RESET}"
    
    @staticmethod
    def status_success(text):
        """
        Formatiert einen Erfolgs-Status
        
        Args:
            text (str): Der Statustext
            
        Returns:
            str: Der formatierte Statustext
        """
        return f"{Colors.BRIGHT_GREEN}[+] {text}{Colors.RESET}"
    
    @staticmethod
    def status_info(text):
        """
        Formatiert einen Info-Status
        
        Args:
            text (str): Der Statustext
            
        Returns:
            str: Der formatierte Statustext
        """
        return f"{Colors.BRIGHT_BLUE}[*] {text}{Colors.RESET}"
    
    @staticmethod
    def status_warning(text):
        """
        Formatiert einen Warnungs-Status
        
        Args:
            text (str): Der Statustext
            
        Returns:
            str: Der formatierte Statustext
        """
        return f"{Colors.BRIGHT_YELLOW}[!] {text}{Colors.RESET}"
    
    @staticmethod
    def status_error(text):
        """
        Formatiert einen Fehler-Status
        
        Args:
            text (str): Der Statustext
            
        Returns:
            str: Der formatierte Statustext
        """
        return f"{Colors.BRIGHT_RED}[-] {text}{Colors.RESET}"
    
    @staticmethod
    def status_debug(text):
        """
        Formatiert einen Debug-Status
        
        Args:
            text (str): Der Statustext
            
        Returns:
            str: Der formatierte Statustext
        """
        return f"{Colors.BRIGHT_MAGENTA}[D] {text}{Colors.RESET}"
