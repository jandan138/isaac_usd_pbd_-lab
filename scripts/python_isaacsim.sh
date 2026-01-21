#!/usr/bin/env bash
# 这个脚本是 VS Code 的“伪解释器”入口
# 目的：让 VS Code 把它当成 Python 解释器，从而实现代码跳转/补全
# 原理：把所有参数原样转交给 /isaac-sim/python.sh
# 好处：稳定、路径统一、团队共享时更规范

# -e: 出错立即退出
# -u: 使用未定义变量时报错
# -o pipefail: 管道出错返回非 0
set -euo pipefail

# exec 会用目标进程替换当前进程
# 这样 VS Code 看起来就是在“直接运行解释器”
exec /isaac-sim/python.sh "$@"
