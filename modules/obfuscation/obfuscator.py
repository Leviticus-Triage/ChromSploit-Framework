import os
import re
import base64
import random
import string
import hashlib
import subprocess
import tempfile
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum

class ObfuscationLevel(Enum):
    MINIMAL = 1
    STANDARD = 2
    AGGRESSIVE = 3
    MAXIMUM = 4

class ObfuscationTechnique(Enum):
    VARIABLE_RENAME = "variable_rename"
    STRING_ENCODING = "string_encoding"
    CONTROL_FLOW = "control_flow"
    DEAD_CODE = "dead_code"
    OPAQUE_PREDICATES = "opaque_predicates"
    FUNCTION_SPLITTING = "function_splitting"
    INSTRUCTION_SUBSTITUTION = "instruction_substitution"

class EnhancedObfuscator:
    def __init__(self):
        self.techniques_available = self._check_available_techniques()
        self.ollvm_available = self._check_ollvm()
        self.variable_mapping: Dict[str, str] = {}
        self.function_mapping: Dict[str, str] = {}
        
    def _check_available_techniques(self) -> List[ObfuscationTechnique]:
        """Check which obfuscation techniques are available"""
        available = [
            ObfuscationTechnique.VARIABLE_RENAME,
            ObfuscationTechnique.STRING_ENCODING,
            ObfuscationTechnique.DEAD_CODE
        ]
        
        # Check for advanced techniques based on dependencies
        try:
            import ast
            available.extend([
                ObfuscationTechnique.CONTROL_FLOW,
                ObfuscationTechnique.FUNCTION_SPLITTING
            ])
        except ImportError:
            pass
            
        return available
        
    def _check_ollvm(self) -> bool:
        """Check if OLLVM compiler is available"""
        try:
            result = subprocess.run(['clang++', '--version'], 
                                  capture_output=True, text=True)
            return 'ollvm' in result.stdout.lower()
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
            
    def obfuscate_javascript(self, code: str, level: ObfuscationLevel = ObfuscationLevel.STANDARD) -> str:
        """Obfuscate JavaScript code"""
        obfuscated = code
        
        if level.value >= ObfuscationLevel.MINIMAL.value:
            obfuscated = self._js_rename_variables(obfuscated)
            obfuscated = self._js_encode_strings(obfuscated)
            
        if level.value >= ObfuscationLevel.STANDARD.value:
            obfuscated = self._js_add_dead_code(obfuscated)
            obfuscated = self._js_control_flow_flattening(obfuscated)
            
        if level.value >= ObfuscationLevel.AGGRESSIVE.value:
            obfuscated = self._js_opaque_predicates(obfuscated)
            obfuscated = self._js_function_splitting(obfuscated)
            
        if level.value >= ObfuscationLevel.MAXIMUM.value:
            obfuscated = self._js_advanced_encoding(obfuscated)
            obfuscated = self._js_anti_debugging(obfuscated)
            
        return obfuscated
        
    def obfuscate_python(self, code: str, level: ObfuscationLevel = ObfuscationLevel.STANDARD) -> str:
        """Obfuscate Python code"""
        obfuscated = code
        
        if level.value >= ObfuscationLevel.MINIMAL.value:
            obfuscated = self._py_rename_variables(obfuscated)
            obfuscated = self._py_encode_strings(obfuscated)
            
        if level.value >= ObfuscationLevel.STANDARD.value:
            obfuscated = self._py_add_dead_code(obfuscated)
            obfuscated = self._py_lambda_transformation(obfuscated)
            
        if level.value >= ObfuscationLevel.AGGRESSIVE.value:
            obfuscated = self._py_marshal_encoding(obfuscated)
            obfuscated = self._py_dynamic_imports(obfuscated)
            
        if level.value >= ObfuscationLevel.MAXIMUM.value:
            obfuscated = self._py_bytecode_manipulation(obfuscated)
            
        return obfuscated
        
    def obfuscate_binary(self, binary_path: str, output_path: str, 
                        level: ObfuscationLevel = ObfuscationLevel.STANDARD) -> bool:
        """Obfuscate binary using OLLVM if available"""
        if not self.ollvm_available:
            # Fallback to basic obfuscation
            return self._basic_binary_obfuscation(binary_path, output_path)
            
        # OLLVM compilation flags based on level
        flags = []
        
        if level.value >= ObfuscationLevel.MINIMAL.value:
            flags.extend(['-mllvm', '-sub'])  # Instruction substitution
            
        if level.value >= ObfuscationLevel.STANDARD.value:
            flags.extend(['-mllvm', '-fla'])  # Control flow flattening
            
        if level.value >= ObfuscationLevel.AGGRESSIVE.value:
            flags.extend(['-mllvm', '-bcf'])  # Bogus control flow
            
        if level.value >= ObfuscationLevel.MAXIMUM.value:
            flags.extend([
                '-mllvm', '-sub_loop=3',
                '-mllvm', '-fla_split_num=5',
                '-mllvm', '-bcf_loop=3'
            ])
            
        return self._compile_with_ollvm(binary_path, output_path, flags)
        
    def _js_rename_variables(self, code: str) -> str:
        """Rename JavaScript variables to obfuscated names"""
        # Simple regex-based variable renaming
        var_pattern = re.compile(r'\b(var|let|const)\s+([a-zA-Z_]\w*)\b')
        
        def replace_var(match):
            keyword = match.group(1)
            var_name = match.group(2)
            
            # Skip built-in names
            if var_name in ['console', 'window', 'document', 'Math', 'Object', 'Array']:
                return match.group(0)
                
            if var_name not in self.variable_mapping:
                self.variable_mapping[var_name] = self._generate_obfuscated_name()
                
            return f"{keyword} {self.variable_mapping[var_name]}"
            
        obfuscated = var_pattern.sub(replace_var, code)
        
        # Replace variable usage
        for original, obfuscated_name in self.variable_mapping.items():
            # Simple word boundary replacement
            obfuscated = re.sub(rf'\b{original}\b', obfuscated_name, obfuscated)
            
        return obfuscated
        
    def _js_encode_strings(self, code: str) -> str:
        """Encode string literals in JavaScript"""
        string_pattern = re.compile(r'(["\'])([^"\']+)\1')
        
        def encode_string(match):
            quote = match.group(1)
            content = match.group(2)
            
            # Base64 encode
            encoded = base64.b64encode(content.encode()).decode()
            
            # Create decoder
            return f'atob({quote}{encoded}{quote})'
            
        return string_pattern.sub(encode_string, code)
        
    def _js_add_dead_code(self, code: str) -> str:
        """Add dead code branches to JavaScript"""
        dead_code_snippets = [
            "if(Math.random()<0){console.log('dead');}",
            "while(false){var x=1;}",
            "for(var i=0;i<0;i++){break;}",
            "if(typeof undefined!=='undefined'){}"
        ]
        
        lines = code.split('\n')
        result = []
        
        for line in lines:
            result.append(line)
            # Randomly insert dead code
            if random.random() < 0.2:
                result.append(random.choice(dead_code_snippets))
                
        return '\n'.join(result)
        
    def _js_control_flow_flattening(self, code: str) -> str:
        """Flatten control flow in JavaScript"""
        # Simple switch-based control flow flattening
        template = """
(function(){
    var _0x1 = 0;
    while(true){
        switch(_0x1){
            case 0:
                {original_code}
                _0x1 = -1;
                break;
            default:
                return;
        }
    }
})();
"""
        return template.replace('{original_code}', code)
        
    def _js_opaque_predicates(self, code: str) -> str:
        """Add opaque predicates to JavaScript"""
        predicates = [
            "(7*7-49===0)",
            "(Math.floor(Math.PI)===3)",
            "((0x1337^0x1337)===0)",
            "(parseInt('10',10)===10)"
        ]
        
        lines = code.split('\n')
        result = []
        
        for line in lines:
            # Add opaque predicate conditions
            if 'if' in line and random.random() < 0.3:
                predicate = random.choice(predicates)
                line = line.replace('if(', f'if({predicate}&&(')
                line = line.replace(')', '))', 1)
                
            result.append(line)
            
        return '\n'.join(result)
        
    def _js_function_splitting(self, code: str) -> str:
        """Split functions into multiple parts"""
        # This is a simplified version
        # Real implementation would parse AST
        return code
        
    def _js_advanced_encoding(self, code: str) -> str:
        """Apply advanced encoding techniques"""
        # Convert to character codes
        encoded = []
        for char in code:
            encoded.append(str(ord(char)))
            
        decoder = f"eval(String.fromCharCode({','.join(encoded)}))"
        return decoder
        
    def _js_anti_debugging(self, code: str) -> str:
        """Add anti-debugging code"""
        anti_debug = """
(function(){
    var devtools = {open: false, orientation: null};
    setInterval(function() {
        if (window.outerHeight - window.innerHeight > 100) {
            devtools.open = true;
        }
    }, 500);
    
    if(typeof console !== 'undefined' && console.clear) {
        console.clear();
    }
})();
"""
        return anti_debug + '\n' + code
        
    def _py_rename_variables(self, code: str) -> str:
        """Rename Python variables"""
        try:
            import ast
            
            class VariableRenamer(ast.NodeTransformer):
                def __init__(self, mapping):
                    self.mapping = mapping
                    
                def visit_Name(self, node):
                    if node.id in self.mapping:
                        node.id = self.mapping[node.id]
                    return node
                    
            # Parse code
            tree = ast.parse(code)
            
            # Find all variable names
            for node in ast.walk(tree):
                if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                    if node.id not in self.variable_mapping:
                        self.variable_mapping[node.id] = self._generate_obfuscated_name()
                        
            # Apply renaming
            renamer = VariableRenamer(self.variable_mapping)
            tree = renamer.visit(tree)
            
            # Convert back to code
            import astor
            return astor.to_source(tree)
            
        except (ImportError, SyntaxError):
            # Fallback to simple string replacement
            return self._simple_py_rename(code)
            
    def _simple_py_rename(self, code: str) -> str:
        """Simple Python variable renaming without AST"""
        # This is a basic implementation
        lines = code.split('\n')
        result = []
        
        for line in lines:
            # Skip comments and strings
            if line.strip().startswith('#') or '"""' in line or "'''" in line:
                result.append(line)
                continue
                
            # Simple variable assignment detection
            if '=' in line and not '==' in line:
                parts = line.split('=')
                if len(parts) == 2:
                    var_name = parts[0].strip()
                    if var_name.isidentifier() and not var_name.startswith('_'):
                        if var_name not in self.variable_mapping:
                            self.variable_mapping[var_name] = self._generate_obfuscated_name()
                            
            # Replace variables
            for original, obfuscated in self.variable_mapping.items():
                line = re.sub(rf'\b{original}\b', obfuscated, line)
                
            result.append(line)
            
        return '\n'.join(result)
        
    def _py_encode_strings(self, code: str) -> str:
        """Encode Python string literals"""
        string_pattern = re.compile(r'(["\'])([^"\']+)\1')
        
        def encode_string(match):
            quote = match.group(1)
            content = match.group(2)
            
            # Hex encoding
            hex_encoded = ''.join([f'\\x{ord(c):02x}' for c in content])
            return f'{quote}{hex_encoded}{quote}'
            
        return string_pattern.sub(encode_string, code)
        
    def _py_add_dead_code(self, code: str) -> str:
        """Add dead code to Python"""
        dead_code_snippets = [
            "if False: pass",
            "_ = lambda: None",
            "try: pass\nexcept: pass",
            "[None for _ in range(0)]"
        ]
        
        lines = code.split('\n')
        result = []
        indent_level = 0
        
        for line in lines:
            # Track indentation
            stripped = line.lstrip()
            if stripped:
                indent_level = len(line) - len(stripped)
                
            result.append(line)
            
            # Add dead code with proper indentation
            if random.random() < 0.15:
                indent = ' ' * indent_level
                result.append(indent + random.choice(dead_code_snippets))
                
        return '\n'.join(result)
        
    def _py_lambda_transformation(self, code: str) -> str:
        """Transform simple functions to lambda expressions"""
        # This is a simplified version
        # Real implementation would use AST
        return code
        
    def _py_marshal_encoding(self, code: str) -> str:
        """Encode Python code using marshal"""
        import marshal
        
        try:
            # Compile code
            compiled = compile(code, '<string>', 'exec')
            
            # Marshal the code object
            marshaled = marshal.dumps(compiled)
            
            # Create loader
            loader = f"""
import marshal
exec(marshal.loads({repr(marshaled)}))
"""
            return loader
            
        except SyntaxError:
            return code
            
    def _py_dynamic_imports(self, code: str) -> str:
        """Convert imports to dynamic imports"""
        import_pattern = re.compile(r'^import\s+(\w+)', re.MULTILINE)
        from_pattern = re.compile(r'^from\s+(\w+)\s+import\s+(.+)', re.MULTILINE)
        
        # Replace simple imports
        code = import_pattern.sub(r'__import__("\1")', code)
        
        # Replace from imports
        def replace_from_import(match):
            module = match.group(1)
            imports = match.group(2)
            return f'{imports} = __import__("{module}", fromlist=[{imports}]).{imports}'
            
        code = from_pattern.sub(replace_from_import, code)
        
        return code
        
    def _py_bytecode_manipulation(self, code: str) -> str:
        """Advanced bytecode manipulation"""
        # This would require bytecode editing libraries
        # For now, return marshal encoded version
        return self._py_marshal_encoding(code)
        
    def _basic_binary_obfuscation(self, binary_path: str, output_path: str) -> bool:
        """Basic binary obfuscation without OLLVM"""
        try:
            # Strip symbols
            subprocess.run(['strip', '-s', binary_path, '-o', output_path], check=True)
            
            # Add some entropy
            with open(output_path, 'ab') as f:
                f.write(os.urandom(random.randint(100, 1000)))
                
            return True
            
        except (subprocess.SubprocessError, IOError):
            return False
            
    def _compile_with_ollvm(self, source_path: str, output_path: str, flags: List[str]) -> bool:
        """Compile with OLLVM obfuscation"""
        try:
            cmd = ['clang++'] + flags + [source_path, '-o', output_path]
            subprocess.run(cmd, check=True)
            return True
            
        except subprocess.SubprocessError:
            return False
            
    def _generate_obfuscated_name(self) -> str:
        """Generate obfuscated variable/function name"""
        # Mix of underscore, hex, and random chars
        prefixes = ['_0x', '__', '_$', '$$_']
        prefix = random.choice(prefixes)
        
        # Generate random suffix
        suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        
        return prefix + suffix
        
    def get_obfuscation_report(self) -> Dict[str, Any]:
        """Get report of obfuscation applied"""
        return {
            'techniques_available': [t.value for t in self.techniques_available],
            'ollvm_available': self.ollvm_available,
            'variables_renamed': len(self.variable_mapping),
            'functions_renamed': len(self.function_mapping),
            'variable_mapping': self.variable_mapping,
            'function_mapping': self.function_mapping
        }

# Singleton instance
_obfuscator = None

def get_obfuscator() -> EnhancedObfuscator:
    """Get the global obfuscator instance"""
    global _obfuscator
    if _obfuscator is None:
        _obfuscator = EnhancedObfuscator()
    return _obfuscator