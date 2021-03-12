# utility functions to handle mea channel index and labels

class ChannelUtility:

    column_characters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'R']

    @staticmethod
    def get_channel_labels(pad_with_zero=False):
        labels = []
        for col, c in enumerate(ChannelUtility.column_characters):
            for row, n in enumerate(range(1, 17)):
                if c == 'A' and n == 1 or c == 'A' and n == 16 or c == 'R' and n == 1 or c == 'R' and n == 16:
                    continue
                number_str = str(n)
                if pad_with_zero and n < 10:
                    # e.g. '5' -> 'B05'
                    number_str = '0' + number_str
                labels.append(c + number_str)
        return labels

    @staticmethod
    def get_ordered_index(label: str):
        # make sure column character is upper case
        column_character = label[0].upper()
        row_number = label[1:]
        corrected_label = column_character + row_number

        # check if label is padded with zero, e.g. 'R02'
        padded_with_zero = (int(row_number) < 10) and (len(label) == 3)

        # find and return index
        return ChannelUtility.get_channel_labels(padded_with_zero).index(corrected_label)

    @staticmethod
    def get_label_by_ordered_index(index: int, pad_with_zero=False):
        return ChannelUtility.get_channel_labels(pad_with_zero)[index]

    @staticmethod
    def get_label_count():
        return len(ChannelUtility.get_channel_labels())

