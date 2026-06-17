import os
import sys
import subprocess
import tempfile
import shutil
import re
from .aes_decrypt import AESDecryptor
from .m3u8_parser import M3U8Parser

class TSMerger:
    def __init__(self, ts_directory, ffmpeg_path=None):
        self.ts_directory = ts_directory
        self.ffmpeg_path = ffmpeg_path or self._find_ffmpeg()
        
        if not self.ffmpeg_path or not os.path.exists(self.ffmpeg_path):
            raise RuntimeError("未找到ffmpeg，请确保ffmpeg已安装或指定正确路径")
    
    def _find_ffmpeg(self):
        for path in ['ffmpeg', 'ffmpeg.exe']:
            try:
                result = subprocess.run(
                    [path, '-version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    return path
            except (subprocess.CalledProcessError, FileNotFoundError, TimeoutError):
                continue
        
        if hasattr(sys, '_MEIPASS'):
            ffmpeg_exe = os.path.join(sys._MEIPASS, 'bin', 'ffmpeg.exe')
            if os.path.exists(ffmpeg_exe):
                return ffmpeg_exe
        
        ffmpeg_dir = os.path.join(os.path.dirname(__file__), '..', 'bin')
        ffmpeg_exe = os.path.join(ffmpeg_dir, 'ffmpeg.exe')
        if os.path.exists(ffmpeg_exe):
            return ffmpeg_exe
        
        return None
    
    def _natural_key(self, string):
        return [int(s) if s.isdigit() else s.lower() for s in re.split(r'(\d+)', string)]
    
    def get_ts_files(self, m3u8_path=None):
        if m3u8_path and os.path.exists(m3u8_path):
            parser = M3U8Parser(m3u8_path)
            parser.parse()
            ts_files = parser.get_ts_files()
            return [os.path.join(self.ts_directory, ts) for ts in ts_files]
        
        ts_files = []
        for filename in os.listdir(self.ts_directory):
            if filename.endswith('.ts'):
                ts_files.append(os.path.join(self.ts_directory, filename))
        
        ts_files.sort(key=self._natural_key)
        return ts_files
    
    def decrypt_ts_files(self, ts_files, key, iv=None, progress_callback=None):
        decryptor = AESDecryptor(key, iv)
        decrypted_files = []
        temp_dir = tempfile.mkdtemp()
        
        for i, ts_file in enumerate(ts_files):
            if not os.path.exists(ts_file):
                continue
            
            try:
                output_file = os.path.join(temp_dir, f"decrypted_{i:04d}.ts")
                decryptor.decrypt_file(ts_file, output_file)
                decrypted_files.append(output_file)
                
                if progress_callback:
                    progress_callback(i + 1, len(ts_files), f"解密 {os.path.basename(ts_file)}")
            except Exception as e:
                if progress_callback:
                    progress_callback(i + 1, len(ts_files), f"解密失败: {str(e)}")
        
        return decrypted_files, temp_dir
    
    def merge_to_mp4(self, ts_files, output_path, progress_callback=None):
        if not ts_files:
            raise ValueError("没有TS文件可合并")
        
        temp_list_file = os.path.join(tempfile.gettempdir(), 'ts_list.txt')
        
        with open(temp_list_file, 'w', encoding='utf-8') as f:
            for ts_file in ts_files:
                f.write(f"file '{ts_file}'\n")
        
        cmd = [
            self.ffmpeg_path,
            '-f', 'concat',
            '-safe', '0',
            '-i', temp_list_file,
            '-c', 'copy',
            '-movflags', 'faststart',
            '-y',
            output_path
        ]
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        total_files = len(ts_files)
        processed_files = 0
        
        for line in iter(process.stdout.readline, ''):
            if 'frame=' in line:
                processed_files = min(processed_files + 1, total_files)
                if progress_callback:
                    progress_callback(processed_files, total_files, line.strip())
        
        process.wait()
        
        os.remove(temp_list_file)
        
        if process.returncode != 0:
            raise RuntimeError(f"ffmpeg执行失败，返回码: {process.returncode}")
        
        return True
    
    def process(self, m3u8_path, output_path, key=None, key_file=None, progress_callback=None):
        if progress_callback:
            progress_callback(0, 100, "正在解析M3U8文件...")
        
        ts_files = self.get_ts_files(m3u8_path)
        
        if not ts_files:
            raise ValueError("未找到任何TS文件")
        
        if progress_callback:
            progress_callback(5, 100, f"找到 {len(ts_files)} 个TS文件")
        
        temp_dir = None
        try:
            if key or key_file:
                if key_file:
                    key = AESDecryptor.load_key_from_file(key_file)
                
                if progress_callback:
                    progress_callback(10, 100, "开始解密TS文件...")
                
                ts_files, temp_dir = self.decrypt_ts_files(ts_files, key, progress_callback=progress_callback)
                
                if progress_callback:
                    progress_callback(50, 100, "解密完成，开始合并...")
            else:
                if progress_callback:
                    progress_callback(10, 100, "开始合并TS文件...")
            
            def merge_progress(current, total, status):
                if progress_callback:
                    base_progress = 50 if key or key_file else 10
                    progress = base_progress + int((current / total) * 40)
                    progress_callback(min(progress, 95), 100, status)
            
            self.merge_to_mp4(ts_files, output_path, progress_callback=merge_progress)
            
            if progress_callback:
                progress_callback(100, 100, "合并完成！")
            
            return True
        finally:
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)