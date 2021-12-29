import threading


class StoppableThread(threading.Thread):
    """
   Implements a thread that can be stopped.
   """

    def __init__(self, target, args=()):
        super(StoppableThread, self).__init__(target=target, args=args)
        self._status = 'running'

    def stop_me(self):
        if self._status == 'running':
            self._status = 'stopping'

    def stopped(self):
        self._status = 'stopped'

    def is_running(self):
        return self._status == 'running'

    def is_stopping(self):
        return self._status == 'stopping'

    def is_stopped(self):
        return self._status == 'stopped'

    def StopThread(self):
        if self.is_running():
            self.stop_me()
            self.join()
