import sys  # 导入系统模块


def log_info(msg):  # 输出信息级日志
    print(f"[INFO] {msg}")  # 打印信息日志


def log_warn(msg):  # 输出警告级日志
    print(f"[WARN] {msg}")  # 打印警告日志


def log_error(msg):  # 输出错误级日志
    print(f"[ERROR] {msg}", file=sys.stderr)  # 打印错误到标准错误
