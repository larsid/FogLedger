import numpy as np
import json


def parse_results(path: str) -> dict:
    # Parse results
    data = {}
    with open(path, 'r') as f:
        # transform to list in json format
        lines = f.readlines()
        # iterable lines in each 5 lines
        for i in range(0, len(lines), 5):
            # get name of the test
            axis = lines[i].strip()
            # get values of the test
            write = lines[i+2]
            read = lines[i+4]
            row = {
                'write': str_to_dict(write.strip()),
                'read': str_to_dict(read.strip()),
                'name': (axis)
            }
            data[axis] = row
    return data


def str_to_dict(string):
    # remove the curly braces from the string
    string = string.strip('{}')

    # split the string into key-value pairs
    pairs = string.split(', ')

    # use a dictionary comprehension to create the dictionary, converting the values to integers and removing the quotes from the keys
    return {key[1:-2]: float(value) for key, value in (pair.split(': ') for pair in pairs)}


if __name__ == "__main__":
    result = []
    for i in range(1, 10):
        data = parse_results(f'exp-larsid{i}.txt')
        result.append(data)

    # get avg of write and read of 1, 50, 100, 150, 200, 250
    avg = {}
    for i in range(1, 10):
        for key, value in result[i-1].items():
            if key in avg:
                avg[key]['write'].append(value['write'])
                avg[key]['read'].append(value['read'])
            else:
                avg[key] = {'write': [value['write']], 'read': [value['read']]}

    # calculate avg of write and read for each 1, 50, 100, 150, 200, 250
    calculared_avg = {}
    for key, value in avg.items():
        calculared_avg[key] = {}
        calculared_avg[key]['write'] = {}
        calculared_avg[key]['read'] = {}
        calculared_avg[key]['write']['avg'] = np.mean(
            [c['av'] for c in value['write']])
        calculared_avg[key]['read']['avg'] = np.mean(
            [c['av'] for c in value['read']])
        calculared_avg[key]['write']['std'] = np.std(
            [c['av'] for c in value['write']])
        calculared_avg[key]['read']['std'] = np.std(
            [c['av'] for c in value['read']])
        calculared_avg[key]['write']['max'] = np.max(
            [c['av'] for c in value['write']])
        calculared_avg[key]['read']['max'] = np.max(
            [c['av'] for c in value['read']])
        calculared_avg[key]['write']['min'] = np.min(
            [c['av'] for c in value['write']])
        calculared_avg[key]['read']['min'] = np.min(
            [c['av'] for c in value['read']])

    open('result_avg_larsid.json', 'w').write(json.dumps(calculared_avg))

    # get array of avg of write
    write_avg = []
    write_min = []
    write_max = []
    for key, value in calculared_avg.items():
        write_avg.append(value['write']['avg'])
        write_min.append(value['write']['min'])
        write_max.append(value['write']['max'])
    print(write_avg)
    print(write_min)
    print(write_max)
    print('---------------------')
    # get array of avg of write
    read_avg = []
    read_min = []
    read_max = []
    for key, value in calculared_avg.items():
        read_avg.append(value['read']['avg'])
        read_min.append(value['read']['min'])
        read_max.append(value['read']['max'])
    print(read_avg)
    print(read_min)
    print(read_max)
