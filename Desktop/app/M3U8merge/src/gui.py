import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
import time
import configparser
import sys
from .ts_merger import TSMerger
from .m3u8_parser import M3U8Parser

class M3U8MergeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("M3U8 TS视频合并工具")
        self.root.geometry("600x600")
        self.root.resizable(False, False)
        self.ts_directory = tk.StringVar()
        self.output_path = tk.StringVar()
        self.key_input = tk.StringVar()
        self.key_file_path = tk.StringVar()
        self.m3u8_path = tk.StringVar()
        
        self.is_processing = False
        
        self.last_ts_dir = self._load_last_ts_dir()
        self.last_output_dir = self._load_last_output_dir()
        
        self.ts_directory.set(self.last_ts_dir)
        self.output_path.set(self.last_output_dir)
        
        self._setup_ui()
    
    def _setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="M3U8 TS视频合并工具", font=('微软雅黑', 16, 'bold')).pack(pady=(0, 20))
        
        ts_frame = ttk.LabelFrame(main_frame, text="TS文件目录", padding="10")
        ts_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Entry(ts_frame, textvariable=self.ts_directory, width=50).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(ts_frame, text="浏览", command=self._browse_ts_directory).pack(side=tk.RIGHT)
        
        m3u8_frame = ttk.LabelFrame(main_frame, text="M3U8文件（可选）", padding="10")
        m3u8_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Entry(m3u8_frame, textvariable=self.m3u8_path, width=50).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(m3u8_frame, text="浏览", command=self._browse_m3u8_file).pack(side=tk.RIGHT)
        
        output_frame = ttk.LabelFrame(main_frame, text="输出MP4文件目录", padding="10")
        output_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Entry(output_frame, textvariable=self.output_path, width=50).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(output_frame, text="浏览", command=self._browse_output_path).pack(side=tk.RIGHT)
        
        key_frame = ttk.LabelFrame(main_frame, text="AES密钥设置", padding="10")
        key_frame.pack(fill=tk.X, pady=(0, 10))
        
        key_input_frame = ttk.Frame(key_frame)
        key_input_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.key_option = tk.StringVar(value="none")
        
        ttk.Radiobutton(key_input_frame, text="不加密", variable=self.key_option, value="none").pack(side=tk.LEFT, padx=(0, 20))
        ttk.Radiobutton(key_input_frame, text="直接输入密钥", variable=self.key_option, value="input").pack(side=tk.LEFT, padx=(0, 20))
        ttk.Radiobutton(key_input_frame, text="选择密钥文件", variable=self.key_option, value="file").pack(side=tk.LEFT)
        
        ttk.Entry(key_frame, textvariable=self.key_input, width=50, show='*').pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(key_frame, text="浏览", command=self._browse_key_file).pack(side=tk.RIGHT)
        
        self.progress_bar = ttk.Progressbar(main_frame, orient=tk.HORIZONTAL, length=500, mode='determinate')
        self.progress_bar.pack(pady=(10, 10))
        
        self.status_label = ttk.Label(main_frame, text="就绪", font=('微软雅黑', 10))
        self.status_label.pack(pady=(0, 10))
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="开始合并", command=self._start_merge, width=15).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="清空日志", command=self._clear_log).pack(side=tk.RIGHT)
        
        log_frame = ttk.LabelFrame(main_frame, text="日志", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(log_frame, height=6, state=tk.DISABLED)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.pack(fill=tk.BOTH, expand=True)
    
    def _browse_ts_directory(self):
        last_dir = self._load_last_ts_dir()
        directory = filedialog.askdirectory(title="选择TS文件目录", initialdir=last_dir)
        if directory:
            self.ts_directory.set(directory)
            self._save_last_ts_dir(directory)
            m3u8_file = os.path.join(directory, 'index.m3u8')
            if os.path.exists(m3u8_file):
                self.m3u8_path.set(m3u8_file)
    
    def _browse_m3u8_file(self):
        last_dir = self._load_last_ts_dir()
        file_path = filedialog.askopenfilename(title="选择M3U8文件", filetypes=[("M3U8文件", "*.m3u8")], initialdir=last_dir)
        if file_path:
            self.m3u8_path.set(file_path)
            self.ts_directory.set(os.path.dirname(file_path))
            self._save_last_ts_dir(os.path.dirname(file_path))
    
    def _browse_output_path(self):
        last_dir = self._load_last_output_dir()
        directory = filedialog.askdirectory(title="选择输出目录", initialdir=last_dir)
        if directory:
            self.output_path.set(directory)
            self._save_last_output_dir(directory)
    
    def _browse_key_file(self):
        file_path = filedialog.askopenfilename(title="选择密钥文件", filetypes=[("密钥文件", "*.key"), ("所有文件", "*.*")])
        if file_path:
            self.key_file_path.set(file_path)
            self.key_option.set("file")
    
    def _load_last_ts_dir(self):
        # 获取运行目录（支持打包后的exe）
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.dirname(__file__))
        
        config_path = os.path.join(base_dir, 'config.ini')
        if os.path.exists(config_path):
            config = configparser.ConfigParser()
            config.read(config_path)
            if 'settings' in config and 'last_ts_dir' in config['settings']:
                return config['settings']['last_ts_dir']
        return os.path.expanduser('~')
    
    def _save_last_ts_dir(self, directory):
        # 获取运行目录（支持打包后的exe）
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.dirname(__file__))
        
        config_path = os.path.join(base_dir, 'config.ini')
        config = configparser.ConfigParser()
        if os.path.exists(config_path):
            config.read(config_path)
        if 'settings' not in config:
            config['settings'] = {}
        config['settings']['last_ts_dir'] = directory
        with open(config_path, 'w') as f:
            config.write(f)
    
    def _load_last_output_dir(self):
        # 获取运行目录（支持打包后的exe）
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.dirname(__file__))
        
        config_path = os.path.join(base_dir, 'config.ini')
        if os.path.exists(config_path):
            config = configparser.ConfigParser()
            config.read(config_path)
            if 'settings' in config and 'last_output_dir' in config['settings']:
                return config['settings']['last_output_dir']
        return os.path.join(os.path.expanduser('~'), 'Documents')
    
    def _save_last_output_dir(self, directory):
        # 获取运行目录（支持打包后的exe）
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.dirname(__file__))
        
        config_path = os.path.join(base_dir, 'config.ini')
        config = configparser.ConfigParser()
        if os.path.exists(config_path):
            config.read(config_path)
        if 'settings' not in config:
            config['settings'] = {}
        config['settings']['last_output_dir'] = directory
        with open(config_path, 'w') as f:
            config.write(f)
    
    def _log(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update_idletasks()
    
    def _clear_log(self):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def _update_progress(self, current, total, status):
        if isinstance(current, float):
            progress = int(current)
        else:
            progress = int((current / total) * 100)
        
        self.progress_bar['value'] = progress
        self.status_label.config(text=status)
        self._log(status)
        self.root.update_idletasks()
    
    def _start_merge(self):
        if self.is_processing:
            messagebox.showwarning("警告", "正在处理中，请等待完成")
            return
        
        ts_dir = self.ts_directory.get().strip()
        output = self.output_path.get().strip()
        
        if not ts_dir:
            messagebox.showerror("错误", "请选择TS文件目录")
            return
        
        if not os.path.exists(ts_dir):
            messagebox.showerror("错误", "TS文件目录不存在")
            return
        
        if not output:
            messagebox.showerror("错误", "请指定输出目录")
            return
        
        if not os.path.exists(output):
            messagebox.showerror("错误", "输出目录不存在")
            return
        
        # 生成时间戳文件名
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(output, f"{timestamp}.mp4")
        
        key = None
        key_file = None
        
        key_option = self.key_option.get()
        
        if key_option == "input":
            key_input = self.key_input.get().strip()
            if key_input:
                key = key_input
        elif key_option == "file":
            key_file = self.key_file_path.get().strip()
            if key_file and not os.path.exists(key_file):
                messagebox.showerror("错误", "密钥文件不存在")
                return
        
        m3u8 = self.m3u8_path.get().strip()
        if m3u8 and not os.path.exists(m3u8):
            messagebox.showerror("错误", "M3U8文件不存在")
            return
        
        self.is_processing = True
        self.progress_bar['value'] = 0
        self._clear_log()
        self._log("开始处理...")
        
        thread = threading.Thread(target=self._merge_thread, args=(ts_dir, output_file, m3u8, key, key_file))
        thread.daemon = True
        thread.start()
    
    def _merge_thread(self, ts_dir, output_file, m3u8, key, key_file):
        try:
            merger = TSMerger(ts_dir)
            merger.process(
                m3u8_path=m3u8 if m3u8 else None,
                output_path=output_file,
                key=key,
                key_file=key_file,
                progress_callback=self._update_progress
            )
            self._save_last_output_dir(os.path.dirname(output_file))
            messagebox.showinfo("成功", f"视频合并完成！\n输出文件: {output_file}")
        except Exception as e:
            self._log(f"错误: {str(e)}")
            messagebox.showerror("错误", str(e))
        finally:
            self.is_processing = False

def main():
    root = tk.Tk()
    app = M3U8MergeApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()