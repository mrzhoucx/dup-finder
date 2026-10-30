# dup-finder

按文件内容（SHA-256）查找重复文件的小工具，零依赖，只需 Python 3。

## 安装

无需安装，下载 `dup_finder.py` 即可运行：

```bash
python3 dup_finder.py --help
```

## 用法

扫描当前目录（默认只报告，不删除任何文件）：

```bash
python3 dup_finder.py .
```

扫描指定目录，忽略小于 1KB 的文件：

```bash
python3 dup_finder.py ~/Downloads --min-size 1024
```

删除重复文件（每组保留排序后的第一个），必须同时加 `--yes` 才真正删除，
否则只打印将要删除的清单：

```bash
python3 dup_finder.py ~/Downloads --delete --yes
```

## 示例

```text
$ python3 dup_finder.py demo
Group 1: 2 copies x 12 bytes (wasted: 12 bytes)
  demo/a.txt
  demo/b.txt

1 duplicate group(s), 12 bytes wasted in total.
```

## 说明

- 先按文件大小分组，只对同大小的文件算哈希，扫描大目录也较快。
- 跳过符号链接，读不到的文件会打印提示并跳过，不会中断扫描。
