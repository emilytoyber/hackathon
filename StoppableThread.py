import threading


class StoppableThread(threading.Thread):
    """
   Implements a thread that can be stopped.
   """

    def _init_(self,  *args, **kwargs):
        super(StoppableThread, self)._init_(*args, **kwargs)
        self._stop_event = threading.Event()

    def StopThread(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()