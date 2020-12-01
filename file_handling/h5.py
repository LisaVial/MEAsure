from PyQt5 import QtCore, QtWidgets
import sys
import time


class Worker(QtCore.QObject):
    # worker_id, step_description: emitted every step through work() loop
    signal_step = QtCore.pyqtSignal(int, str)
    # worker id: emitted at the end of work()
    signal_done = QtCore.pyqtSignal(int)
    # message to be shown to the user:
    signal_message = QtCore.pyqtSignal(str)

    def __init__(self, id):
        super().__init__()
        self.__id = id
        self.__abort = False

    @QtCore.pyqtSlot()
    def work(self):
        """
        Pretend this worker method does work that takes a long time. During this time, the thread's
        event loop is blocked, except if the application's processEvents() is called: this gives every
        thread (incl. main) a chance to process events, which in this sample means processing signals
        received from GUI (such as abort).
        """
        thread_name = QtCore.QThread.currentThread().objectName()
        thread_id = int(QtCore.QThread.currentThreadId())  # cast to int() is necessary
        self.sig_msg.emit('Running worker #{} from thread "{}" (#{})'.format(self.__id, thread_name, thread_id))

        for step in range(100):
            time.sleep(0.1)
            self.sig_step.emit(self.__id, 'step ' + str(step))

            # check if we need to abort the loop; need to process events to receive signals;
            app.processEvents()  # this could cause change to self.__abort
            if self.__abort:
                # note that "step" value will not necessarily be same for every thread
                self.sig_msg.emit('Worker #{} aborting work at step {}'.format(self.__id, step))
                break

        self.sig_done.emit(self.__id)

    def abort(self):
        self.sig_msg.emit('Worker #{} notified to abort'.format(self.__id))
        self.__abort = True