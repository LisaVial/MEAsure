import matplotlib.pyplot as plt


class VoltageTracePlotter:
    def __init__(self, analog_stream, channel_idx):
        analog_stream = analog_stream
        channel_idx = channel_idx
        plot_analog_stream_channel(analog_stream, channel_idx)

    def plot_analog_stream_channel(analog_stream, channel_idx, from_in_s=0, to_in_s=None, show=True):
        """
        Plots data from a single AnalogStream channel

        :param analog_stream: A AnalogStream object
        :param channel_idx: A scalar channel index (0 <= channel_idx < # channels in the AnalogStream)
        :param from_in_s: The start timestamp of the plot (0 <= from_in_s < to_in_s). Default: 0
        :param to_in_s: The end timestamp of the plot (from_in_s < to_in_s <= duration). Default: None (= recording duration)
        :param show: If True (default), the plot is directly created. For further plotting, use show=False
        """
        # extract basic information
        ids = [c.channel_id for c in analog_stream.channel_infos.values()]
        channel_id = ids[channel_idx]
        channel_info = analog_stream.channel_infos[channel_id]
        sampling_frequency = channel_info.sampling_frequency.magnitude

        # get start and end index
        from_idx = max(0, int(from_in_s * sampling_frequency))
        if to_in_s is None:
            to_idx = analog_stream.channel_data.shape[1]
        else:
            to_idx = min(analog_stream.channel_data.shape[1], int(to_in_s * sampling_frequency))

        # get the timestamps for each sample
        time = analog_stream.get_channel_sample_timestamps(channel_id, from_idx, to_idx)

        # scale time to seconds:
        scale_factor_for_second = Q_(1, time[1]).to(ureg.s).magnitude
        time_in_sec = time[0] * scale_factor_for_second

        # get the signal
        signal = analog_stream.get_channel_in_range(channel_id, from_idx, to_idx)

        # scale signal to µV:
        scale_factor_for_uV = Q_(1, signal[1]).to(ureg.uV).magnitude
        signal_in_uV = signal[0] * scale_factor_for_uV

        # construct the plot
        print('plotting...')
        plt.figure(figsize=(20, 6))
        plt.plot(time_in_sec, signal_in_uV)
        plt.xlabel('Time (%s)' % ureg.s)
        plt.ylabel('Voltage (%s)' % ureg.uV)
        plt.title('Channel %s' % channel_info.info['Label'])

        plt.show()

        self.canvas.axes.cla()
        self.canvas.axes.plot(time, voltage)
        self.canvas.axes.set_xlabel('time [s]')
        self.canvas.axes.set_ylabel('voltage [' + r'$\mu$' + 'V]')
        ax = self.canvas.axes
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.get_xaxis().tick_bottom()
        ax.get_yaxis().tick_left()
        self.canvas.draw()

