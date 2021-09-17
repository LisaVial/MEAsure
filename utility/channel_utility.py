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

    @staticmethod
    def get_neighbours(label: str, pad_with_zero=False):
        column_characters = ChannelUtility.column_characters.copy()  # use copy to avoid any unwanted modification
        last_column_index = len(column_characters) - 1  # useful for filtering out the missing corner channels
        column_index = column_characters.index(label[0].capitalize())
        row = int(label[1:])

        neighbours = []
        index_offsets = (-1, 0, 1)

        for row_offset in index_offsets:
            for column_offset in index_offsets:
                if column_offset == 0 and row_offset == 0:
                    continue  # same index as input, skip

                neighbour_column_index = column_index + column_offset
                if neighbour_column_index < 0 or neighbour_column_index > last_column_index:
                    continue  # invalid column index for neighbour

                neighbour_row = row + row_offset
                if neighbour_row < 1 or neighbour_row > 16:
                    continue  # invalid row index for neighbour

                if (neighbour_column_index == 0 or neighbour_column_index == last_column_index) \
                        and (neighbour_row == 1 or neighbour_row == 16):
                    continue  # neighbour is missing corner channel

                neighbour_row_string = str(neighbour_row)
                if pad_with_zero and neighbour_row < 10:
                    neighbour_row_string = '0' + neighbour_row_string

                neighbour_label = column_characters[neighbour_column_index] + neighbour_row_string
                neighbours.append(neighbour_label)

        return neighbours

    @staticmethod
    def get_sc_index(mcs_index: int, dead_channels: list):

        if mcs_index in dead_channels:
            raise Exception("MCS index is a dead channel and has no SC index")

        sc_index = 0
        for row_index in range(252):

            if row_index == mcs_index:
                return sc_index

            if row_index not in dead_channels:
                sc_index += 1

        raise Exception("MCS index not in valid range (0, 251)")

    @staticmethod
    def get_mcs_index(sc_index: int, dead_channels: list):

        # special case: sc index is 0 and mcs index 0 is not a dead channel
        if 0 not in dead_channels and sc_index == 0:
            return 0

        current_sc_index = 0
        for row_index in range(252):
            if row_index not in dead_channels:
                current_sc_index += 1
                if current_sc_index == sc_index:
                    return row_index

        raise Exception("SC index not in valid range (0, " + str(251 - len(dead_channels)) + ")")

    @staticmethod
    def get_label_for_mcs_index(mcs_index: int, ordered_mcs_indices: list, pad_with_zero: bool = False):
        return ChannelUtility.get_channel_labels(pad_with_zero)[ordered_mcs_indices.index(mcs_index)]

    @staticmethod
    def get_label_for_sc_index(sc_index: int, dead_channels: list, ordered_mcs_indices: list,
                               pad_with_zero: bool = False):
        return ChannelUtility.get_label_for_mcs_index(ChannelUtility.get_mcs_index(sc_index, dead_channels),
                                                      ordered_mcs_indices, pad_with_zero)

