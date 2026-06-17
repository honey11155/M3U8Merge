# M3U8 TS视频合并工具

一款功能强大的M3U8 TS视频文件合并工具，支持AES加密解密，可将多个TS视频片段合并为单个MP4文件。

## 功能特性

- **TS文件合并**：自动识别并合并目录中的所有TS文件，支持自然排序（1, 2, ..., 10, 11）
- **AES解密**：支持128/192/256位AES-CBC解密，可直接输入密钥或选择密钥文件
- **M3U8解析**：自动解析M3U8文件获取TS列表和加密信息
- **目录记忆**：自动记忆上次使用的TS文件目录和输出目录
- **自动命名**：按时间戳自动生成输出文件名
- **进度显示**：实时显示合并进度和状态信息
- **错误处理**：完善的错误提示和日志记录

## 使用说明

1. **选择TS文件目录**：点击"浏览"按钮选择包含TS文件的目录
2. **选择M3U8文件（可选）**：如果目录中存在index.m3u8会自动识别，也可手动选择
3. **选择输出目录**：指定MP4文件的保存目录，程序会自动生成时间戳文件名
4. **设置AES密钥（可选）**：
   - 不加密：默认选项
   - 直接输入密钥：输入16进制格式的密钥
   - 选择密钥文件：选择.key密钥文件
5. **开始合并**：点击"开始合并"按钮，等待合并完成

## 技术参数

- 支持密钥长度：16、24或32字节（自动填充）
- 输出格式：MP4（H.264 + AAC）
- 加密模式：AES-CBC
- 运行环境：Windows 10及以上

## 配置文件

程序会在运行目录下自动创建 `config.ini` 文件，保存以下配置：

```ini
[settings]
last_ts_dir = 上次使用的TS文件目录
last_output_dir = 上次使用的输出目录
```

## 命令行运行

```bash
python main.py
```

## 打包方式

```bash
pyinstaller --onefile --windowed --add-data "bin\ffmpeg.exe;bin" --name "M3U8Merge" main.py
```

## 文件结构

```
M3U8Merge/
├── src/
│   ├── aes_decrypt.py    # AES解密模块
│   ├── gui.py            # GUI界面模块
│   ├── m3u8_parser.py    # M3U8解析模块
│   └── ts_merger.py      # TS合并模块
├── bin/
│   └── ffmpeg.exe        # FFmpeg可执行文件
├── main.py               # 程序入口
├── config.ini            # 配置文件（自动生成）
└── M3U8Merge.exe         # 打包后的可执行文件
```

## 依赖

- Python 3.12+
- pycryptodome
- ffmpeg

## 许可证

MIT License