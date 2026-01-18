#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Browser CVE & Exploit Finder
Sucht nach neuen Browser-CVEs und Exploits für ChromSploit Framework
"""

import requests
import json
import re
import subprocess
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path

class BrowserCVEFinder:
    """Findet Browser-CVEs und Exploits"""
    
    def __init__(self):
        self.browsers = {
            'chrome': ['chrome', 'chromium', 'google chrome'],
            'edge': ['edge', 'microsoft edge'],
            'firefox': ['firefox', 'mozilla'],
            'brave': ['brave', 'brave browser'],
            'vivaldi': ['vivaldi'],
            'comet': ['comet', 'perplexity']
        }
        self.cve_pattern = re.compile(r'CVE-\d{4}-\d{4,7}')
        self.found_cves = []
        
    def search_cve_mitre(self, browser: str, year: int = 2025) -> List[str]:
        """Suche CVEs auf CVE MITRE"""
        cves = []
        try:
            # CVE MITRE API (falls verfügbar) oder Web-Scraping
            url = f"https://cve.mitre.org/cgi-bin/cvekey.cgi?keyword={browser}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                found = self.cve_pattern.findall(response.text)
                cves.extend([cve for cve in found if str(year) in cve])
        except Exception as e:
            print(f"Fehler bei CVE MITRE Suche: {e}")
        return cves
    
    def search_exploitdb(self, cve_id: str) -> List[Dict]:
        """Suche Exploits auf Exploit-DB"""
        exploits = []
        try:
            # Versuche searchsploit zu verwenden
            result = subprocess.run(
                ['searchsploit', cve_id],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0 and 'No Exploits Found' not in result.stdout:
                # Parse searchsploit output
                lines = result.stdout.split('\n')
                for line in lines:
                    if '|' in line and cve_id.lower() in line.lower():
                        parts = [p.strip() for p in line.split('|')]
                        if len(parts) >= 3:
                            exploits.append({
                                'id': parts[0] if parts[0] else None,
                                'title': parts[1] if len(parts) > 1 else None,
                                'path': parts[-1] if parts else None
                            })
        except FileNotFoundError:
            print("searchsploit nicht gefunden - installiere exploitdb")
        except Exception as e:
            print(f"Fehler bei Exploit-DB Suche: {e}")
        return exploits
    
    def search_github(self, cve_id: str) -> List[Dict]:
        """Suche PoCs auf GitHub"""
        repos = []
        try:
            # GitHub API Search
            url = f"https://api.github.com/search/repositories"
            params = {
                'q': f'{cve_id} exploit OR poc',
                'sort': 'updated',
                'order': 'desc',
                'per_page': 10
            }
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for item in data.get('items', []):
                    repos.append({
                        'name': item.get('name'),
                        'url': item.get('html_url'),
                        'description': item.get('description'),
                        'language': item.get('language'),
                        'stars': item.get('stargazers_count')
                    })
        except Exception as e:
            print(f"Fehler bei GitHub Suche: {e}")
        return repos
    
    def find_all_browser_cves(self) -> Dict[str, List[str]]:
        """Finde CVEs für alle Browser"""
        results = {}
        for browser, keywords in self.browsers.items():
            print(f"\n[+] Suche CVEs für {browser.upper()}...")
            browser_cves = []
            for keyword in keywords:
                cves = self.search_cve_mitre(keyword)
                browser_cves.extend(cves)
            results[browser] = list(set(browser_cves))
            print(f"    Gefunden: {len(results[browser])} CVEs")
        return results
    
    def generate_report(self, output_file: str = "cve_research_report.json"):
        """Generiere Recherche-Report"""
        print("\n=== Browser CVE Recherche ===")
        
        all_cves = self.find_all_browser_cves()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'browsers': {}
        }
        
        for browser, cves in all_cves.items():
            browser_data = {
                'cves': cves,
                'exploits': {},
                'github_repos': {}
            }
            
            for cve in cves:
                print(f"\n[+] Recherchiere {cve}...")
                
                # Suche Exploits
                exploits = self.search_exploitdb(cve)
                if exploits:
                    browser_data['exploits'][cve] = exploits
                    print(f"    Exploit-DB: {len(exploits)} Exploits gefunden")
                
                # Suche GitHub PoCs
                repos = self.search_github(cve)
                if repos:
                    browser_data['github_repos'][cve] = repos
                    print(f"    GitHub: {len(repos)} Repositories gefunden")
            
            report['browsers'][browser] = browser_data
        
        # Speichere Report
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n[+] Report gespeichert: {output_file}")
        return report

if __name__ == "__main__":
    finder = BrowserCVEFinder()
    report = finder.generate_report("cve_research_report.json")
    
    # Zusammenfassung
    print("\n=== Zusammenfassung ===")
    for browser, data in report['browsers'].items():
        print(f"\n{browser.upper()}:")
        print(f"  CVEs: {len(data['cves'])}")
        print(f"  Mit Exploits: {len(data['exploits'])}")
        print(f"  Mit GitHub PoCs: {len(data['github_repos'])}")
