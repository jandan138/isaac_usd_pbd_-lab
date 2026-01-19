import time  # 导入时间模块


class FpsTimer:  # 帧率计时器类
    def __init__(self, interval_sec=1.0):  # 初始化计时器
        self.interval_sec = interval_sec  # 统计间隔秒数
        self._last_time = time.time()  # 记录上次时间
        self._frame_count = 0  # 记录帧计数

    def tick(self):  # 推进一帧并计算是否到达统计间隔
        self._frame_count += 1  # 帧数加一
        now = time.time()  # 获取当前时间
        elapsed = now - self._last_time  # 计算经过时间
        if elapsed >= self.interval_sec:  # 达到统计间隔
            fps = self._frame_count / max(elapsed, 1e-6)  # 计算帧率
            self._last_time = now  # 更新时间戳
            self._frame_count = 0  # 清零计数
            return True, fps, elapsed  # 返回统计结果
        return False, 0.0, 0.0  # 未到间隔时返回占位值
