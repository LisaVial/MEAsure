

def text_parser(file_path):
    with open(file_path) as file:
        lines = file.readlines()

        time = []
        voltage = []
        for line in lines:
            if '\t' in line and '[' not in line:
                line_ls = line.split('\t')
                time.append(float(line_ls[0]))
                sec_ele = line_ls[1].split('\n')
                voltage.append(float(sec_ele[0]))
    return time, voltage
