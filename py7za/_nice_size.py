SI_UNITS = ['kB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
L_SI_UNITS = [unit.lower() for unit in SI_UNITS]
BIN_UNITS = ['KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB']
L_BIN_UNITS = [unit.lower() for unit in BIN_UNITS]


def nice_size(size: int, si: bool = False, decimal_precision: int = 1) -> str:
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

    units = SI_UNITS if si else BIN_UNITS
    u = -1
    r = 10 ** decimal_precision

    while True:
        size /= threshold
        u += 1
        if round(abs(size) * r) / r < threshold or u == len(units) - 1:
            break

    # noinspection PyStringFormat
    return (f'%.{decimal_precision}f ' % size) + units[u]


def size_to_int(s: str, si: bool = False) -> int:
    """
    Returns an integer value for a string as it would have been generated by
    nice_size (e.g. '900 B', '4.5 GiB', etc.)
    :param s: a string representing a size in SI or binary units
        (e.g. '900 B', '4.5 GiB', etc.)
    :param si: whether to use SI units (or binary units, the default)
    :return: a round integer value matching the nice size string
    """
    t = s.lower().strip().split()
    if len(t) != 2:
        raise ValueError(f'cannot convert {s} to number of bytes')
    elif t[1].lower() == 'b':
        return int(t[0])
    if si:
        return int(1000 ** (L_SI_UNITS.index(t[1]) + 1) * float(t[0]))
    else:
        return int(1024 ** (L_BIN_UNITS.index(t[1]) + 1) * float(t[0]))
