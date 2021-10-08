from PyQt5 import QtCore, QtWidgets
import numpy as np
import time
from IPython import embed


# This worker thread was needed to load hdf5 files into the program by using chunks, which are small parts of the total
# recording. Since we use the Virtual Machine (VM) this functionality is not needed anymore, since the VM has enough RAM

# First, the class is defined
class Worker(QtCore.QObject):
    # the next variables are for GUI things to work so that the user is able to know what happens in the background,
    # e.g. to have a loading screen the signal step might be used
    # worker_id, step_description: emitted every step through work() loop
    signal_step = QtCore.pyqtSignal(list)
    # worker id: emitted at the end of work()
    signal_done = QtCore.pyqtSignal(list)
    # message to be shown to the user:
    signal_message = QtCore.pyqtSignal(str)

    # Here the class is initialized, variables created in this block with the 'self' in front are stored in the class
    # and can be called in other scripts of the program (which is not necessary)
    def __init__(self, name, reader):
        super().__init__()
        self.reader = reader
        self.voltage_traces_dataset = self.reader.voltage_traces_dataset  # just a pointer to the dataset as a whole
        self.__name = name
        self.__abort = False
        self.app = QtWidgets.QApplication.instance()
        self.voltage_traces = None

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
        self.signal_message.emit('Running worker #{} from thread "{}" (#{})'.format(self.__name, thread_name,
                                                                                    thread_id))

        # before looping through chunks, create np.empty in the shape of whole voltage trace matrix
        # hopefully s will be shape-like tuple/list, then, the assignment to the np.empty-matrix
        # should be accessible through s
        shape_of_vt_dataset = self.voltage_traces_dataset.shape
        try:
            self.voltage_traces = np.empty(shape_of_vt_dataset)
            chunk_lens = []
            chunk_size = self.voltage_traces_dataset.chunks[1]
            steps = int(np.ceil(shape_of_vt_dataset[1] / chunk_size))
            chunk_iterator = np.linspace(0, chunk_size * steps, steps)
            max_index = shape_of_vt_dataset[1] - 1
            for i, chunk_index in enumerate(chunk_iterator):  # dset = voltage_traces
                next_index = min((chunk_index + chunk_size), max_index)
                chunk = self.voltage_traces_dataset[:, int(chunk_index): int(next_index)]
                self.voltage_traces[:, int(chunk_index):int(next_index)] = chunk
                chunk_lens.append(len(self.voltage_traces_dataset[:, int(chunk_index): int(next_index)]))
                time.sleep(0.1)
                # Here, the progress signal is calculated and then sent to the FilterTab
                progress = round(((i + 1) / len(chunk_iterator)) * 100.0, 2)
                self.signal_step.emit([progress, chunk_index, next_index, chunk])

                # check if we need to abort the loop; need to process events to receive signals;
                self.app.processEvents()  # this could cause change to self.__abort

        except MemoryError:
            print('cannot load the whole trace at once, processing time will be slower than usual')
            self.abort()

        if self.__abort:
            # note that "step" value will not necessarily be same for every thread
            try:
                self.signal_message.emit('Worker #{} aborting work at step {}'.format(self.__name, i))
            except UnboundLocalError:
                self.signal_message.emit('Worker #{} aborting work at step {}'.format(self.__name, 0))
        self.signal_done.emit([self.__name, self.voltage_traces])

    def abort(self):
        self.signal_message.emit('Worker #{} notified to abort'.format(self.__name))
        self.__abort = True
