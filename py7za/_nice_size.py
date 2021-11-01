def nice_size(size, si=False, decimal_precision=1):
    """
    Returns a string representation of a file size in SI (KiB, MiB, etc.)
    or binary units (KB, MB, etc.)
    :param size: a size in single bytes
    :param si: whether to use SI units (or binary units, the default)
    :param decimal_precision: the number of decimals to show in rounded
        representations
    :return: a string representation of size
    """
    threshold = 1000 if si else 1024

    if abs(size) < threshold:
        return f'{size} B'

    units = ['kB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'] if si \
        else ['KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB']
    u = -1
    r = 10 ** decimal_precision

    while True:
        size /= threshold
        u += 1
        if round(abs(size) * r) / r < threshold or u == len(units) - 1:
            break

    # noinspection PyStringFormat
    return (f'%.{decimal_precision}f ' % size) + units[u]
