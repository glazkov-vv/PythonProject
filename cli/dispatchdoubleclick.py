import time


class DispatchDoubleClick:
    def dispatch_double_click(self):
        if not hasattr(self, "_last_click"):
            self._last_click = 0
        ctime = time.time()
        if (abs(ctime - self._last_click) < 0.2):
            if hasattr(self, "double_click"):
                self.double_click()
        self._last_click = ctime
