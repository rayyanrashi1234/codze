# scanner.py
import re
import os

class FileScanner:
    def __init__(self):
        # Local heuristic patterns for instant feedback
        self.malicious_patterns = [
            r'eval\s*\(', r'exec\s*\(', r'cmd\.exe', r'powershell', 
            r'<script', r'base64_decode', r'reverse_shell', r'/bin/sh'
        ]

    def scan_file_local(self, file_path):
        """Quick local scan for instant UI feedback"""
        try:
            # Read file as text (ignore errors for binary files)
            with open(file_path, 'r', errors='ignore') as f:
                # Read first 50KB for quick analysis
                content = f.read(50000) 
                
            for pattern in self.malicious_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    return {
                        "is_malicious": True, 
                        "confidence": 85, 
                        "reason": f"Local Heuristic: Matched '{pattern}'"
                    }
            return {"is_malicious": False, "confidence": 90, "reason": "Local scan clean"}
        except Exception as e:
            return {"is_malicious": False, "confidence": 0, "reason": f"Read error: {str(e)}"}
        