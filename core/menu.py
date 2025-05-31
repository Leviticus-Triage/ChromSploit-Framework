#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromSploit Framework v2.0
Basis-Menüklasse für das Framework
Für Bildungs- und autorisierte Penetrationstests
"""

import os
import sys
import time
from typing import List, Dict, Any, Optional, Callable, Union, Tuple

from core.colors import Colors

class MenuItem:
    """
    Repräsentiert einen Menüeintrag im ChromSploit Framework
    """
    
    def __init__(self, text: str, action: Callable, color: str = Colors.WHITE):
        """
        Initialisiert einen Menüeintrag
        
        Args:
            text (str): Der anzuzeigende Text
            action (Callable): Die auszuführende Aktion
            color (str, optional): Die Farbe des Menüeintrags
        """
        self.text = text
        self.action = action
        self.color = color
    
    def execute(self) -> Any:
        """
        Führt die Aktion des Menüeintrags aus
        
        Returns:
            Any: Das Ergebnis der Aktion
        """
        return self.action()
    
    def __str__(self) -> str:
        """
        Gibt den Text des Menüeintrags zurück
        
        Returns:
            str: Der Text des Menüeintrags
        """
        return self.text

class Menu:
    """
    Basis-Menüklasse für das ChromSploit Framework
    """
    
    def __init__(self, title: str, parent=None):
        """
        Initialisiert ein Menü
        
        Args:
            title (str): Der Titel des Menüs
            parent (Menu, optional): Das übergeordnete Menü
        """
        self.title = title
        self.parent = parent
        self.items: List[MenuItem] = []
        self.info_text: Optional[str] = None
    
    def add_item(self, text: str, action: Callable, color: str = Colors.WHITE) -> None:
        """
        Fügt einen Menüeintrag hinzu
        
        Args:
            text (str): Der anzuzeigende Text
            action (Callable): Die auszuführende Aktion
            color (str, optional): Die Farbe des Menüeintrags
        """
        self.items.append(MenuItem(text, action, color))
    
    def set_info_text(self, text: str) -> None:
        """
        Setzt den Informationstext des Menüs
        
        Args:
            text (str): Der Informationstext
        """
        self.info_text = text
    
    def _clear(self) -> None:
        """
        Löscht den Bildschirm
        """
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def _draw_box(self, width: int, title: str, color: str = Colors.CYAN) -> None:
        """
        Zeichnet eine Box mit Titel
        
        Args:
            width (int): Die Breite der Box
            title (str): Der Titel der Box
            color (str, optional): Die Farbe der Box
        """
        print(f"{color}╭{'─' * (width - 2)}╮{Colors.RESET}")
        print(f"{color}│{Colors.YELLOW} {title}{' ' * (width - 3 - len(title))}{color}│{Colors.RESET}")
        print(f"{color}╰{'─' * (width - 2)}╯{Colors.RESET}")
    
    def _draw_separator(self, width: int, color: str = Colors.CYAN) -> None:
        """
        Zeichnet einen Separator
        
        Args:
            width (int): Die Breite des Separators
            color (str, optional): Die Farbe des Separators
        """
        print(f"{color}{'─' * width}{Colors.RESET}")
    
    def display(self) -> Any:
        """
        Zeigt das Menü an und verarbeitet die Benutzereingabe
        
        Returns:
            Any: Das Ergebnis der ausgewählten Aktion
        """
        while True:
            self._clear()
            
            # Box mit Titel zeichnen
            self._draw_box(80, self.title)
            
            # Informationstext anzeigen, falls vorhanden
            if self.info_text:
                print(f"\n{Colors.BRIGHT_WHITE}{self.info_text}{Colors.RESET}\n")
            
            # Menüeinträge anzeigen
            print(f"\n{Colors.BRIGHT_WHITE}Bitte wählen Sie eine Option:{Colors.RESET}\n")
            
            for i, item in enumerate(self.items, 1):
                print(f"{Colors.BRIGHT_BLUE}{i}){Colors.RESET} {item.color}{item.text}{Colors.RESET}")
            
            # Benutzereingabe verarbeiten
            try:
                choice = input(f"\n{Colors.BRIGHT_GREEN}Auswahl: {Colors.RESET}")
                
                # Zurück zum übergeordneten Menü, falls vorhanden
                if choice.lower() in ['q', 'quit', 'exit', 'zurück', 'back']:
                    if self.parent:
                        return None
                    else:
                        print(f"\n{Colors.YELLOW}Zum Beenden des Programms bitte 'exit' wählen.{Colors.RESET}")
                        time.sleep(1)
                        continue
                
                # Programm beenden
                if choice.lower() in ['exit', 'beenden']:
                    print(f"\n{Colors.CYAN}ChromSploit wird beendet. Auf Wiedersehen!{Colors.RESET}")
                    sys.exit(0)
                
                # Menüeintrag ausführen
                try:
                    index = int(choice) - 1
                    if 0 <= index < len(self.items):
                        result = self.items[index].execute()
                        
                        # Wenn das Ergebnis "exit" ist, zum übergeordneten Menü zurückkehren
                        if result == "exit":
                            return None
                        
                        # Wenn das Ergebnis nicht None ist, zurückgeben
                        if result is not None:
                            return result
                    else:
                        print(f"\n{Colors.RED}Ungültige Auswahl. Bitte erneut versuchen.{Colors.RESET}")
                        time.sleep(1)
                except ValueError:
                    print(f"\n{Colors.RED}Ungültige Eingabe. Bitte eine Zahl eingeben.{Colors.RESET}")
                    time.sleep(1)
            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}Abbruch durch Benutzer.{Colors.RESET}")
                if self.parent:
                    return None
                else:
                    print(f"\n{Colors.CYAN}ChromSploit wird beendet. Auf Wiedersehen!{Colors.RESET}")
                    sys.exit(0)
    
    def exit_menu(self):
        """Exit the current menu and return to parent"""
        return None
    
    def run(self):
        """Run the menu (alias for display)"""
        return self.display()
