import re
import os

class M3U8Parser:
    def __init__(self, m3u8_path):
        self.m3u8_path = m3u8_path
        self.ts_files = []
        self.key_info = None
        self.iv_info = None
        self.duration = 0.0
    
    def parse(self):
        if not os.path.exists(self.m3u8_path):
            raise FileNotFoundError(f"M3U8文件不存在: {self.m3u8_path}")
        
        with open(self.m3u8_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        lines = content.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if line.startswith('#EXT-X-KEY:'):
                self._parse_key(line)
            
            elif line.startswith('#EXTINF:'):
                duration_match = re.search(r'#EXTINF:([\d.]+)', line)
                if duration_match:
                    self.duration += float(duration_match.group(1))
                
                if i + 1 < len(lines):
                    ts_line = lines[i + 1].strip()
                    if ts_line and not ts_line.startswith('#'):
                        self.ts_files.append(ts_line)
                    i += 1
            
            elif line and not line.startswith('#'):
                if line.endswith('.ts'):
                    self.ts_files.append(line)
            
            i += 1
        
        if not self.ts_files:
            raise ValueError("M3U8文件中未找到TS文件列表")
        
        return self
    
    def _parse_key(self, key_line):
        self.key_info = {}
        
        method_match = re.search(r'METHOD=(\w+)', key_line)
        if method_match:
            self.key_info['method'] = method_match.group(1)
        
        uri_match = re.search(r'URI="([^"]+)"', key_line)
        if uri_match:
            self.key_info['uri'] = uri_match.group(1)
        
        iv_match = re.search(r'IV=([^\s,]+)', key_line)
        if iv_match:
            self.iv_info = iv_match.group(1)
    
    def get_ts_files(self):
        return self.ts_files
    
    def get_key_info(self):
        return self.key_info
    
    def get_iv(self):
        return self.iv_info
    
    def get_duration(self):
        return self.duration