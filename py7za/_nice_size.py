def nice_size(size, si=False, dp=1):
    threshold = 1000 if si else 1024

    if (abs(size) < threshold):
        return f'{size} B'

    units = ['kB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'] if si \
        else ['KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB']
    u = -1
    r = 10 ** dp

    while True:
        size /= threshold
        u += 1
        if round(abs(size) * r) / r < threshold or u == len(units) - 1:
            break

    # noinspection PyStringFormat
    return (f'%.{dp}f ' % size) + units[u]
