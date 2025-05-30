#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import json
from datetime import datetime
from core.enhanced_menu import EnhancedMenu
from core.colors import Colors
from core.enhanced_logger import get_logger
from core.error_handler import handle_errors

class ObfuscationMenu(EnhancedMenu):
    def __init__(self):
        super().__init__("Enhanced Obfuscation System")
        self.logger = get_logger()
        
        # Try to import obfuscation modules
        try:
            from modules.obfuscation import get_obfuscator, get_payload_obfuscator, ObfuscationLevel
            self.obfuscator = get_obfuscator()
            self.payload_obfuscator = get_payload_obfuscator()
            self.ObfuscationLevel = ObfuscationLevel
            self.obfuscation_available = True
        except ImportError:
            self.obfuscation_available = False
            
        self._setup_menu_items()
        
    def _setup_menu_items(self):
        """Setup menu items"""
        if not self.obfuscation_available:
            self.add_enhanced_item(
                "install", "Install Obfuscation Dependencies", 
                self._install_dependencies,
                description="Install required packages for obfuscation"
            )
            return
            
        self.add_enhanced_item(
            "javascript", "Obfuscate JavaScript", 
            self._obfuscate_javascript,
            description="Obfuscate JavaScript code with multiple techniques"
        )
        
        self.add_enhanced_item(
            "python", "Obfuscate Python", 
            self._obfuscate_python,
            description="Obfuscate Python code"
        )
        
        self.add_enhanced_item(
            "payload", "Obfuscate Exploit Payload", 
            self._obfuscate_payload,
            description="Advanced payload obfuscation for exploits"
        )
        
        self.add_enhanced_item(
            "binary", "Obfuscate Binary", 
            self._obfuscate_binary,
            description="Binary obfuscation with OLLVM (if available)"
        )
        
        self.add_enhanced_item(
            "multi", "Multi-Stage Payload", 
            self._create_multistage,
            description="Create multi-stage obfuscated payload"
        )
        
        self.add_enhanced_item(
            "test", "Test Obfuscation", 
            self._test_obfuscation,
            description="Test obfuscation techniques"
        )
        
        self.add_enhanced_item(
            "report", "Obfuscation Report", 
            self._show_report,
            description="View obfuscation statistics and report"
        )
        
    @handle_errors
    def _install_dependencies(self):
        """Install obfuscation dependencies"""
        print(f"\n{Colors.CYAN}[*] Installing Obfuscation Dependencies{Colors.RESET}")
        
        dependencies = [
            "astor",  # For Python AST manipulation
        ]
        
        print(f"{Colors.BLUE}[+] Required packages:{Colors.RESET}")
        for dep in dependencies:
            print(f"  - {dep}")
            
        print(f"\n{Colors.BLUE}[+] Optional tools:{Colors.RESET}")
        print(f"  - OLLVM (Obfuscator-LLVM) for binary obfuscation")
        print(f"    Install: apt install clang-ollvm (on supported systems)")
        
        confirm = input(f"\n{Colors.YELLOW}Install Python dependencies? (y/N): {Colors.RESET}")
        if confirm.lower() == 'y':
            import subprocess
            import sys
            
            for dep in dependencies:
                try:
                    print(f"{Colors.CYAN}[*] Installing {dep}...{Colors.RESET}")
                    subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
                    print(f"{Colors.GREEN}[+] {dep} installed successfully{Colors.RESET}")
                except subprocess.CalledProcessError as e:
                    print(f"{Colors.RED}[!] Failed to install {dep}: {e}{Colors.RESET}")
                    
            print(f"{Colors.GREEN}[+] Dependencies installation completed{Colors.RESET}")
            print(f"{Colors.YELLOW}[!] Please restart the framework to use obfuscation features{Colors.RESET}")
            
    @handle_errors
    def _obfuscate_javascript(self):
        """Obfuscate JavaScript code"""
        print(f"\n{Colors.CYAN}=== JavaScript Obfuscation ==={Colors.RESET}")
        
        # Get input method
        print(f"{Colors.BLUE}1.{Colors.RESET} Enter code manually")
        print(f"{Colors.BLUE}2.{Colors.RESET} Load from file")
        
        choice = input(f"\n{Colors.CYAN}Select input method: {Colors.RESET}")
        
        if choice == "1":
            print(f"{Colors.CYAN}Enter JavaScript code (end with 'EOF' on new line):{Colors.RESET}")
            lines = []
            while True:
                line = input()
                if line == 'EOF':
                    break
                lines.append(line)
            code = '\n'.join(lines)
            
        elif choice == "2":
            file_path = input(f"{Colors.CYAN}Enter file path: {Colors.RESET}")
            try:
                with open(file_path, 'r') as f:
                    code = f.read()
            except IOError as e:
                print(f"{Colors.RED}[!] Error reading file: {e}{Colors.RESET}")
                return
        else:
            print(f"{Colors.RED}[!] Invalid choice{Colors.RESET}")
            return
            
        # Select obfuscation level
        print(f"\n{Colors.CYAN}Select obfuscation level:{Colors.RESET}")
        levels = list(self.ObfuscationLevel)
        for i, level in enumerate(levels, 1):
            print(f"{Colors.BLUE}{i}.{Colors.RESET} {level.name}")
            
        try:
            level_choice = int(input(f"\n{Colors.CYAN}Select level: {Colors.RESET}"))
            if 1 <= level_choice <= len(levels):
                level = levels[level_choice - 1]
            else:
                print(f"{Colors.RED}[!] Invalid level{Colors.RESET}")
                return
        except ValueError:
            print(f"{Colors.RED}[!] Invalid input{Colors.RESET}")
            return
            
        # Obfuscate
        print(f"\n{Colors.CYAN}[*] Obfuscating JavaScript...{Colors.RESET}")
        
        start_time = time.time()
        obfuscated = self.obfuscator.obfuscate_javascript(code, level)
        elapsed = time.time() - start_time
        
        # Show results
        print(f"{Colors.GREEN}[+] Obfuscation completed in {elapsed:.2f}s{Colors.RESET}")
        print(f"{Colors.BLUE}Original size:{Colors.RESET} {len(code)} bytes")
        print(f"{Colors.BLUE}Obfuscated size:{Colors.RESET} {len(obfuscated)} bytes")
        print(f"{Colors.BLUE}Size ratio:{Colors.RESET} {len(obfuscated)/len(code):.2f}x")
        
        # Save option
        save = input(f"\n{Colors.CYAN}Save obfuscated code? (y/N): {Colors.RESET}")
        if save.lower() == 'y':
            output_path = input(f"{Colors.CYAN}Output file path: {Colors.RESET}")
            try:
                with open(output_path, 'w') as f:
                    f.write(obfuscated)
                print(f"{Colors.GREEN}[+] Saved to {output_path}{Colors.RESET}")
            except IOError as e:
                print(f"{Colors.RED}[!] Error saving file: {e}{Colors.RESET}")
                
        # Show preview
        print(f"\n{Colors.CYAN}=== Preview (first 500 chars) ==={Colors.RESET}")
        print(obfuscated[:500] + "..." if len(obfuscated) > 500 else obfuscated)
        
    @handle_errors
    def _obfuscate_python(self):
        """Obfuscate Python code"""
        print(f"\n{Colors.CYAN}=== Python Obfuscation ==={Colors.RESET}")
        
        # Similar to JavaScript but for Python
        file_path = input(f"{Colors.CYAN}Enter Python file path: {Colors.RESET}")
        try:
            with open(file_path, 'r') as f:
                code = f.read()
        except IOError as e:
            print(f"{Colors.RED}[!] Error reading file: {e}{Colors.RESET}")
            return
            
        # Select level
        print(f"\n{Colors.CYAN}Select obfuscation level:{Colors.RESET}")
        levels = list(self.ObfuscationLevel)
        for i, level in enumerate(levels, 1):
            print(f"{Colors.BLUE}{i}.{Colors.RESET} {level.name}")
            
        try:
            level_choice = int(input(f"\n{Colors.CYAN}Select level: {Colors.RESET}"))
            if 1 <= level_choice <= len(levels):
                level = levels[level_choice - 1]
            else:
                print(f"{Colors.RED}[!] Invalid level{Colors.RESET}")
                return
        except ValueError:
            print(f"{Colors.RED}[!] Invalid input{Colors.RESET}")
            return
            
        # Obfuscate
        print(f"\n{Colors.CYAN}[*] Obfuscating Python...{Colors.RESET}")
        
        obfuscated = self.obfuscator.obfuscate_python(code, level)
        
        print(f"{Colors.GREEN}[+] Obfuscation completed{Colors.RESET}")
        print(f"{Colors.BLUE}Original size:{Colors.RESET} {len(code)} bytes")
        print(f"{Colors.BLUE}Obfuscated size:{Colors.RESET} {len(obfuscated)} bytes")
        
        # Save
        output_path = file_path.replace('.py', '_obfuscated.py')
        save = input(f"\n{Colors.CYAN}Save to {output_path}? (y/N): {Colors.RESET}")
        if save.lower() == 'y':
            try:
                with open(output_path, 'w') as f:
                    f.write(obfuscated)
                print(f"{Colors.GREEN}[+] Saved to {output_path}{Colors.RESET}")
            except IOError as e:
                print(f"{Colors.RED}[!] Error saving file: {e}{Colors.RESET}")
                
    @handle_errors
    def _obfuscate_payload(self):
        """Obfuscate exploit payload"""
        print(f"\n{Colors.CYAN}=== Exploit Payload Obfuscation ==={Colors.RESET}")
        
        # Select exploit type
        print(f"{Colors.BLUE}Exploit types:{Colors.RESET}")
        print(f"{Colors.BLUE}1.{Colors.RESET} JavaScript exploit")
        print(f"{Colors.BLUE}2.{Colors.RESET} HTML exploit")
        print(f"{Colors.BLUE}3.{Colors.RESET} WebAssembly exploit")
        
        type_choice = input(f"\n{Colors.CYAN}Select type: {Colors.RESET}")
        
        exploit_types = {
            "1": "javascript",
            "2": "html", 
            "3": "wasm"
        }
        
        exploit_type = exploit_types.get(type_choice)
        if not exploit_type:
            print(f"{Colors.RED}[!] Invalid type{Colors.RESET}")
            return
            
        # Get payload
        print(f"\n{Colors.CYAN}Enter payload (end with 'EOF' on new line):{Colors.RESET}")
        lines = []
        while True:
            line = input()
            if line == 'EOF':
                break
            lines.append(line)
        payload = '\n'.join(lines)
        
        # Select level
        print(f"\n{Colors.CYAN}Select obfuscation level:{Colors.RESET}")
        levels = list(self.ObfuscationLevel)
        for i, level in enumerate(levels, 1):
            print(f"{Colors.BLUE}{i}.{Colors.RESET} {level.name}")
            
        try:
            level_choice = int(input(f"\n{Colors.CYAN}Select level: {Colors.RESET}"))
            if 1 <= level_choice <= len(levels):
                level = levels[level_choice - 1]
            else:
                print(f"{Colors.RED}[!] Invalid level{Colors.RESET}")
                return
        except ValueError:
            print(f"{Colors.RED}[!] Invalid input{Colors.RESET}")
            return
            
        # Obfuscate
        print(f"\n{Colors.CYAN}[*] Obfuscating payload...{Colors.RESET}")
        
        result = self.payload_obfuscator.obfuscate_exploit_payload(payload, exploit_type, level)
        
        # Show results
        print(f"{Colors.GREEN}[+] Payload obfuscation completed{Colors.RESET}")
        print(f"{Colors.BLUE}Original size:{Colors.RESET} {result['original_size']} bytes")
        print(f"{Colors.BLUE}Obfuscated size:{Colors.RESET} {result['obfuscated_size']} bytes")
        print(f"{Colors.BLUE}Size ratio:{Colors.RESET} {result['ratio']:.2f}x")
        print(f"{Colors.BLUE}Techniques used:{Colors.RESET} {', '.join(result['techniques_used'])}")
        
        # Save
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = f"obfuscated_payload_{timestamp}.{exploit_type}"
        
        save = input(f"\n{Colors.CYAN}Save to {output_path}? (y/N): {Colors.RESET}")
        if save.lower() == 'y':
            try:
                with open(output_path, 'w') as f:
                    f.write(result['obfuscated'])
                print(f"{Colors.GREEN}[+] Saved to {output_path}{Colors.RESET}")
            except IOError as e:
                print(f"{Colors.RED}[!] Error saving file: {e}{Colors.RESET}")
                
    @handle_errors
    def _obfuscate_binary(self):
        """Obfuscate binary file"""
        print(f"\n{Colors.CYAN}=== Binary Obfuscation ==={Colors.RESET}")
        
        if not self.obfuscator.ollvm_available:
            print(f"{Colors.YELLOW}[!] OLLVM not available, using basic obfuscation{Colors.RESET}")
            
        binary_path = input(f"{Colors.CYAN}Enter binary path: {Colors.RESET}")
        
        if not os.path.exists(binary_path):
            print(f"{Colors.RED}[!] File not found{Colors.RESET}")
            return
            
        output_path = binary_path + "_obfuscated"
        
        # Select level
        print(f"\n{Colors.CYAN}Select obfuscation level:{Colors.RESET}")
        levels = list(self.ObfuscationLevel)
        for i, level in enumerate(levels, 1):
            print(f"{Colors.BLUE}{i}.{Colors.RESET} {level.name}")
            
        try:
            level_choice = int(input(f"\n{Colors.CYAN}Select level: {Colors.RESET}"))
            if 1 <= level_choice <= len(levels):
                level = levels[level_choice - 1]
            else:
                print(f"{Colors.RED}[!] Invalid level{Colors.RESET}")
                return
        except ValueError:
            print(f"{Colors.RED}[!] Invalid input{Colors.RESET}")
            return
            
        # Obfuscate
        print(f"\n{Colors.CYAN}[*] Obfuscating binary...{Colors.RESET}")
        
        success = self.obfuscator.obfuscate_binary(binary_path, output_path, level)
        
        if success:
            print(f"{Colors.GREEN}[+] Binary obfuscated successfully{Colors.RESET}")
            print(f"{Colors.BLUE}Output:{Colors.RESET} {output_path}")
            
            # Show size comparison
            orig_size = os.path.getsize(binary_path)
            new_size = os.path.getsize(output_path)
            print(f"{Colors.BLUE}Original size:{Colors.RESET} {orig_size} bytes")
            print(f"{Colors.BLUE}Obfuscated size:{Colors.RESET} {new_size} bytes")
        else:
            print(f"{Colors.RED}[!] Binary obfuscation failed{Colors.RESET}")
            
    @handle_errors
    def _create_multistage(self):
        """Create multi-stage obfuscated payload"""
        print(f"\n{Colors.CYAN}=== Multi-Stage Payload Creation ==={Colors.RESET}")
        
        stages = []
        stage_count = 0
        
        print(f"{Colors.BLUE}Enter stages (type 'done' when finished):{Colors.RESET}")
        
        while True:
            stage_count += 1
            print(f"\n{Colors.CYAN}Stage {stage_count} (or 'done'):{Colors.RESET}")
            
            lines = []
            while True:
                line = input()
                if line == 'done' and not lines:
                    break
                if line == 'EOF':
                    break
                lines.append(line)
                
            if not lines:
                break
                
            stages.append('\n'.join(lines))
            
        if not stages:
            print(f"{Colors.RED}[!] No stages provided{Colors.RESET}")
            return
            
        # Select level
        print(f"\n{Colors.CYAN}Select obfuscation level:{Colors.RESET}")
        levels = list(self.ObfuscationLevel)
        for i, level in enumerate(levels, 1):
            print(f"{Colors.BLUE}{i}.{Colors.RESET} {level.name}")
            
        try:
            level_choice = int(input(f"\n{Colors.CYAN}Select level: {Colors.RESET}"))
            if 1 <= level_choice <= len(levels):
                level = levels[level_choice - 1]
            else:
                print(f"{Colors.RED}[!] Invalid level{Colors.RESET}")
                return
        except ValueError:
            print(f"{Colors.RED}[!] Invalid input{Colors.RESET}")
            return
            
        # Create multi-stage payload
        print(f"\n{Colors.CYAN}[*] Creating multi-stage payload...{Colors.RESET}")
        
        multi_stage = self.payload_obfuscator.create_multi_stage_payload(stages, level)
        
        print(f"{Colors.GREEN}[+] Multi-stage payload created{Colors.RESET}")
        print(f"{Colors.BLUE}Number of stages:{Colors.RESET} {len(stages)}")
        print(f"{Colors.BLUE}Total size:{Colors.RESET} {len(multi_stage)} bytes")
        
        # Save
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = f"multi_stage_payload_{timestamp}.js"
        
        save = input(f"\n{Colors.CYAN}Save to {output_path}? (y/N): {Colors.RESET}")
        if save.lower() == 'y':
            try:
                with open(output_path, 'w') as f:
                    f.write(multi_stage)
                print(f"{Colors.GREEN}[+] Saved to {output_path}{Colors.RESET}")
            except IOError as e:
                print(f"{Colors.RED}[!] Error saving file: {e}{Colors.RESET}")
                
    @handle_errors
    def _test_obfuscation(self):
        """Test obfuscation techniques"""
        print(f"\n{Colors.CYAN}=== Test Obfuscation Techniques ==={Colors.RESET}")
        
        # Test JavaScript
        test_js = """
function testFunction(param1, param2) {
    var result = param1 + param2;
    console.log("Result: " + result);
    return result;
}

var x = 10;
var y = 20;
testFunction(x, y);
"""
        
        print(f"{Colors.BLUE}Testing JavaScript obfuscation...{Colors.RESET}")
        print(f"\n{Colors.CYAN}Original:{Colors.RESET}")
        print(test_js)
        
        for level in self.ObfuscationLevel:
            print(f"\n{Colors.CYAN}Level: {level.name}{Colors.RESET}")
            obfuscated = self.obfuscator.obfuscate_javascript(test_js, level)
            print(f"Size: {len(obfuscated)} bytes (ratio: {len(obfuscated)/len(test_js):.2f}x)")
            print("Preview:", obfuscated[:200] + "..." if len(obfuscated) > 200 else obfuscated)
            
        # Test Python
        test_py = """
def test_function(param1, param2):
    result = param1 + param2
    print(f"Result: {result}")
    return result

x = 10
y = 20
test_function(x, y)
"""
        
        print(f"\n{Colors.BLUE}Testing Python obfuscation...{Colors.RESET}")
        print(f"\n{Colors.CYAN}Original:{Colors.RESET}")
        print(test_py)
        
        for level in [self.ObfuscationLevel.MINIMAL, self.ObfuscationLevel.STANDARD]:
            print(f"\n{Colors.CYAN}Level: {level.name}{Colors.RESET}")
            obfuscated = self.obfuscator.obfuscate_python(test_py, level)
            print(f"Size: {len(obfuscated)} bytes")
            
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
        
    @handle_errors
    def _show_report(self):
        """Show obfuscation report"""
        print(f"\n{Colors.CYAN}=== Obfuscation Report ==={Colors.RESET}")
        
        report = self.obfuscator.get_obfuscation_report()
        
        print(f"{Colors.BLUE}Available Techniques:{Colors.RESET}")
        for tech in report['techniques_available']:
            print(f"  - {tech}")
            
        print(f"\n{Colors.BLUE}OLLVM Available:{Colors.RESET} {Colors.GREEN if report['ollvm_available'] else Colors.RED}{report['ollvm_available']}{Colors.RESET}")
        
        print(f"\n{Colors.BLUE}Obfuscation Statistics:{Colors.RESET}")
        print(f"  Variables renamed: {report['variables_renamed']}")
        print(f"  Functions renamed: {report['functions_renamed']}")
        
        if report['variable_mapping']:
            print(f"\n{Colors.BLUE}Recent Variable Mappings:{Colors.RESET}")
            for orig, obf in list(report['variable_mapping'].items())[:10]:
                print(f"  {orig} -> {obf}")
                
        # Check for updates
        print(f"\n{Colors.BLUE}Obfuscation Levels:{Colors.RESET}")
        for level in self.ObfuscationLevel:
            print(f"  {level.value}. {level.name}")
            
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
    
    def run(self):
        """Run the menu"""
        self.display()

def main():
    """Main function for testing"""
    menu = ObfuscationMenu()
    menu.display()

if __name__ == "__main__":
    main()