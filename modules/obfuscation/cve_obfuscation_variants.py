#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CVE Obfuscation Variants
Obfuscation variants for new CVE exploits to bypass detection
"""

import base64
import random
import string
import re
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class CVEObfuscationVariants:
    """Obfuscation variants for CVE exploits"""
    
    def __init__(self):
        self.variant_count = 0
        
    def generate_variant_name(self, cve_id: str, variant_num: int) -> str:
        """Generate variant name"""
        return f"{cve_id}_variant_{variant_num:03d}"
    
    def obfuscate_cve_2025_49741(self, payload: str, variant: int = 1) -> str:
        """Generate obfuscated variant for CVE-2025-49741"""
        obfuscated = payload
        
        if variant == 1:
            # Variant 1: Base64 encoding + variable renaming
            obfuscated = self._base64_encode_strings(obfuscated)
            obfuscated = self._rename_variables(obfuscated, prefix='_x')
            
        elif variant == 2:
            # Variant 2: Hex encoding + whitespace manipulation
            obfuscated = self._hex_encode_strings(obfuscated)
            obfuscated = self._manipulate_whitespace(obfuscated)
            
        elif variant == 3:
            # Variant 3: Unicode encoding + dead code injection
            obfuscated = self._unicode_encode_strings(obfuscated)
            obfuscated = self._inject_dead_code(obfuscated)
            
        elif variant == 4:
            # Variant 4: String concatenation + timing variations
            obfuscated = self._split_strings(obfuscated)
            obfuscated = self._add_timing_delays(obfuscated)
            
        elif variant == 5:
            # Variant 5: Combined obfuscation
            obfuscated = self._base64_encode_strings(obfuscated)
            obfuscated = self._rename_variables(obfuscated, prefix='_v')
            obfuscated = self._manipulate_whitespace(obfuscated)
            obfuscated = self._inject_dead_code(obfuscated)
        
        return obfuscated
    
    def obfuscate_cve_2020_6519(self, payload: str, variant: int = 1) -> str:
        """Generate obfuscated variant for CVE-2020-6519"""
        obfuscated = payload
        
        if variant == 1:
            # Variant 1: URL encoding variations
            obfuscated = self._encode_urls(obfuscated)
            obfuscated = self._rename_variables(obfuscated, prefix='_csp')
            
        elif variant == 2:
            # Variant 2: CSP directive variations
            obfuscated = self._vary_csp_directives(obfuscated)
            obfuscated = self._manipulate_whitespace(obfuscated)
            
        elif variant == 3:
            # Variant 3: Protocol variations
            obfuscated = self._vary_protocols(obfuscated)
            obfuscated = self._inject_dead_code(obfuscated)
            
        elif variant == 4:
            # Variant 4: Element creation variations
            obfuscated = self._vary_element_creation(obfuscated)
            obfuscated = self._add_timing_delays(obfuscated)
            
        elif variant == 5:
            # Variant 5: Maximum obfuscation
            obfuscated = self._encode_urls(obfuscated)
            obfuscated = self._vary_csp_directives(obfuscated)
            obfuscated = self._vary_protocols(obfuscated)
            obfuscated = self._rename_variables(obfuscated, prefix='_max')
            obfuscated = self._inject_dead_code(obfuscated)
        
        return obfuscated
    
    def obfuscate_cve_2017_5375(self, payload: str, variant: int = 1) -> str:
        """Generate obfuscated variant for CVE-2017-5375"""
        obfuscated = payload
        
        if variant == 1:
            # Variant 1: Float constant variations
            obfuscated = self._vary_float_constants(obfuscated)
            obfuscated = self._rename_variables(obfuscated, prefix='_asm')
            
        elif variant == 2:
            # Variant 2: Heap spray pattern variations
            obfuscated = self._vary_heap_spray(obfuscated)
            obfuscated = self._manipulate_whitespace(obfuscated)
            
        elif variant == 3:
            # Variant 3: ASM.JS module structure variations
            obfuscated = self._vary_asmjs_structure(obfuscated)
            obfuscated = self._inject_dead_code(obfuscated)
            
        elif variant == 4:
            # Variant 4: Trigger code variations
            obfuscated = self._vary_trigger_code(obfuscated)
            obfuscated = self._add_timing_delays(obfuscated)
            
        elif variant == 5:
            # Variant 5: Complete obfuscation
            obfuscated = self._vary_float_constants(obfuscated)
            obfuscated = self._vary_heap_spray(obfuscated)
            obfuscated = self._vary_asmjs_structure(obfuscated)
            obfuscated = self._rename_variables(obfuscated, prefix='_jit')
            obfuscated = self._inject_dead_code(obfuscated)
        
        return obfuscated
    
    def _base64_encode_strings(self, code: str) -> str:
        """Encode strings in Base64"""
        def encode_match(match):
            string_content = match.group(1)
            encoded = base64.b64encode(string_content.encode()).decode()
            return f"atob('{encoded}')"
        
        # Encode string literals
        pattern = r"'([^']+)'"
        code = re.sub(pattern, encode_match, code)
        
        return code
    
    def _hex_encode_strings(self, code: str) -> str:
        """Encode strings in hex"""
        def encode_match(match):
            string_content = match.group(1)
            encoded = ''.join(f'\\x{ord(c):02x}' for c in string_content)
            return f"'{encoded}'"
        
        pattern = r"'([^']+)'"
        code = re.sub(pattern, encode_match, code)
        
        return code
    
    def _unicode_encode_strings(self, code: str) -> str:
        """Encode strings using Unicode escapes"""
        def encode_match(match):
            string_content = match.group(1)
            encoded = ''.join(f'\\u{ord(c):04x}' for c in string_content)
            return f"'{encoded}'"
        
        pattern = r"'([^']+)'"
        code = re.sub(pattern, encode_match, code)
        
        return code
    
    def _rename_variables(self, code: str, prefix: str = '_') -> str:
        """Rename variables to obfuscated names"""
        # Find variable declarations
        var_pattern = r'\b(var|let|const)\s+([a-zA-Z_]\w*)\b'
        var_map = {}
        
        def replace_var(match):
            keyword = match.group(1)
            var_name = match.group(2)
            
            # Skip built-ins
            if var_name in ['console', 'window', 'document', 'Math', 'Object', 'Array', 'String', 'Number']:
                return match.group(0)
            
            if var_name not in var_map:
                var_map[var_name] = f"{prefix}{self._generate_random_name()}"
            
            return f"{keyword} {var_map[var_name]}"
        
        code = re.sub(var_pattern, replace_var, code)
        
        # Replace variable usage
        for original, obfuscated in var_map.items():
            code = re.sub(rf'\b{original}\b', obfuscated, code)
        
        return code
    
    def _manipulate_whitespace(self, code: str) -> str:
        """Manipulate whitespace to obfuscate"""
        # Add random whitespace
        lines = code.split('\n')
        obfuscated_lines = []
        
        for line in lines:
            obfuscated_lines.append(line)
            # Randomly add empty lines
            if random.random() < 0.1:
                obfuscated_lines.append('')
        
        return '\n'.join(obfuscated_lines)
    
    def _inject_dead_code(self, code: str) -> str:
        """Inject dead code"""
        dead_code_snippets = [
            "var _dead = Math.random();",
            "function _unused() { return false; }",
            "var _temp = Date.now();",
            "if (false) { console.log('dead'); }",
            "var _dummy = [1,2,3].map(x => x*2);"
        ]
        
        # Insert dead code randomly
        lines = code.split('\n')
        for i in range(len(lines) - 1, 0, -1):
            if random.random() < 0.15:
                lines.insert(i, random.choice(dead_code_snippets))
        
        return '\n'.join(lines)
    
    def _split_strings(self, code: str) -> str:
        """Split strings into concatenated parts"""
        def split_match(match):
            string_content = match.group(1)
            if len(string_content) < 5:
                return match.group(0)
            
            # Split into 2-3 parts
            parts = []
            chunk_size = len(string_content) // random.randint(2, 3)
            for i in range(0, len(string_content), chunk_size):
                parts.append(f"'{string_content[i:i+chunk_size]}'")
            
            return ' + '.join(parts)
        
        pattern = r"'([^']{5,})'"
        code = re.sub(pattern, split_match, code)
        
        return code
    
    def _add_timing_delays(self, code: str) -> str:
        """Add timing delays"""
        # Add setTimeout calls randomly
        delay_code = "setTimeout(function(){}, Math.random() * 100);"
        
        lines = code.split('\n')
        for i in range(len(lines) - 1, 0, -1):
            if 'function' in lines[i] and random.random() < 0.2:
                lines.insert(i + 1, '    ' + delay_code)
        
        return '\n'.join(lines)
    
    def _encode_urls(self, code: str) -> str:
        """Encode URLs"""
        # URL encode URLs in code
        pattern = r"http://([^'\"]+)"
        def encode_url(match):
            url = match.group(0)
            encoded = ''.join(f'%{ord(c):02x}' if c not in ':/' else c for c in url)
            return encoded
        
        code = re.sub(pattern, encode_url, code)
        return code
    
    def _vary_csp_directives(self, code: str) -> str:
        """Vary CSP directives"""
        # Replace CSP directives with variations
        variations = {
            "object-src 'none'": ["object-src 'self'", "object-src *", "object-src data:"],
            "child-src 'none'": ["child-src 'self'", "child-src *", "child-src data:"],
            "script-src 'self'": ["script-src *", "script-src 'unsafe-inline'", "script-src 'unsafe-eval'"]
        }
        
        for original, variants in variations.items():
            if original in code:
                code = code.replace(original, random.choice(variants))
        
        return code
    
    def _vary_protocols(self, code: str) -> str:
        """Vary protocols"""
        # Change javascript: to variations
        variations = [
            "javascript:",
            "JAVASCRIPT:",
            "java\u0073cript:",
            "java\\x73cript:"
        ]
        
        if "javascript:" in code:
            code = code.replace("javascript:", random.choice(variations))
        
        return code
    
    def _vary_element_creation(self, code: str) -> str:
        """Vary element creation methods"""
        # Vary createElement calls
        variations = {
            "document.createElement": ["document['createElement']", "window.document.createElement"],
            ".appendChild": [".append", ".insertBefore"]
        }
        
        for original, variants in variations.items():
            if original in code:
                code = code.replace(original, random.choice(variants), 1)
        
        return code
    
    def _vary_float_constants(self, code: str) -> str:
        """Vary float constants in ASM.JS"""
        # Add small variations to float constants
        pattern = r'(-?\d+\.\d+e[+-]\d+)'
        def vary_float(match):
            val = float(match.group(1))
            # Add small random variation
            variation = random.uniform(-0.001, 0.001)
            new_val = val * (1 + variation)
            return str(new_val)
        
        code = re.sub(pattern, vary_float, code)
        return code
    
    def _vary_heap_spray(self, code: str) -> str:
        """Vary heap spray patterns"""
        # Vary array sizes
        pattern = r'new Array\((\d+)\)'
        def vary_size(match):
            size = int(match.group(1))
            variation = random.randint(-100, 100)
            new_size = max(1, size + variation)
            return f"new Array({new_size})"
        
        code = re.sub(pattern, vary_size, code)
        return code
    
    def _vary_asmjs_structure(self, code: str) -> str:
        """Vary ASM.JS module structure"""
        # Add dummy parameters or reorder
        if '"use asm"' in code:
            # Add comments
            code = code.replace('"use asm"', '"use asm" /* obfuscated */')
        
        return code
    
    def _vary_trigger_code(self, code: str) -> str:
        """Vary trigger code"""
        # Vary innerHTML assignments
        variations = [
            ".innerHTML =",
            "['innerHTML'] =",
            ".setAttribute('innerHTML',"
        ]
        
        if ".innerHTML = " in code:
            code = code.replace(".innerHTML = ", random.choice(variations), 1)
        
        return code
    
    def _generate_random_name(self, length: int = 8) -> str:
        """Generate random name"""
        chars = string.ascii_lowercase + string.digits
        return ''.join(random.choice(chars) for _ in range(length))
    
    def generate_all_variants(self, cve_id: str, payload: str, num_variants: int = 5) -> Dict[str, str]:
        """Generate all obfuscation variants for a CVE"""
        variants = {}
        
        if cve_id == 'CVE-2025-49741':
            for i in range(1, num_variants + 1):
                variant_name = self.generate_variant_name(cve_id, i)
                variants[variant_name] = self.obfuscate_cve_2025_49741(payload, i)
                
        elif cve_id == 'CVE-2020-6519':
            for i in range(1, num_variants + 1):
                variant_name = self.generate_variant_name(cve_id, i)
                variants[variant_name] = self.obfuscate_cve_2020_6519(payload, i)
                
        elif cve_id in ['CVE-2017-5375', 'CVE-2016-1960']:
            for i in range(1, num_variants + 1):
                variant_name = self.generate_variant_name(cve_id, i)
                variants[variant_name] = self.obfuscate_cve_2017_5375(payload, i)
        
        return variants


def get_obfuscation_variants() -> CVEObfuscationVariants:
    """Get obfuscation variants instance"""
    return CVEObfuscationVariants()
