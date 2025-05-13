from typing import Callable, Optional
from datetime import datetime, timedelta
from calendar import monthrange


DATE_PREFIX = {
    'on or after': '>=',
    'in or after': '>=',
    'on or before': '<=',
    'in or before': '<=',
    'on': '=',
    'in': '=',
    '==': '=',
    'before': '<',
    'after': '>',
}


class ExpressionError(Exception):
    pass


def create_date_test(expr: str) -> Optional[Callable[[datetime], bool]]:
    if not expr:
        raise ExpressionError('Empty date expression')

    # lower case and replace date prefixes like 'after', 'before', etc.
    _expr = expr.lower()
    for x, y in DATE_PREFIX.items():
        _expr = _expr.replace(x, y)

    # logical and / or
    if ' and ' in _expr:
        return lambda s: all(create_date_test(p)(s) for p in _expr.split(' and '))
    if ' or ' in _expr:
        return lambda s: any(create_date_test(p)(s) for p in _expr.split(' or '))

    # determine and remove operator
    if _expr[0] not in '<>=':
        _operator = '='
    else:
        if _expr.startswith('<='):
            _operator, _expr = '<=', _expr[2:]
        elif _expr.startswith('>='):
            _operator, _expr = '>=', _expr[2:]
        else:
            _operator, _expr = _expr[0], _expr[1:]
    _expr = _expr.strip()

    # interpret date expression
    while True:
        try:
            _start = datetime.strptime(_expr, '%Y-%m-%d %H:%M:%S')
            _end = _start + timedelta(seconds=1)
            break
        except ValueError:
            pass
        try:
            _start = datetime.strptime(_expr, '%Y-%m-%d %H:%M')
            _end = _start + timedelta(minutes=1, seconds=-1)
            break
        except ValueError:
            pass
        try:
            _start = datetime.strptime(_expr, '%Y-%m-%d')
            _end = _start + timedelta(days=1, seconds=-1)
            break
        except ValueError:
            pass
        try:
            _start = datetime.strptime(_expr, '%Y-%m')
            _end = _start + timedelta(days=monthrange(_start.year, _start.month)[1], seconds=-1)
            break
        except ValueError:
            pass
        try:
            _start = datetime.strptime(_expr, '%Y')
            _end = datetime(_start.year + 1, 1, 1) + timedelta(seconds=-1)
            break
        except ValueError:
            pass
        try:
            _start = datetime.strptime(_expr, '%m-%d')
            _end = _start + timedelta(days=1, seconds=-1)
            break
        except ValueError:
            pass
        raise ExpressionError(f'Unknown date expression `{expr}`')

    # create a test function based on operator and date range
    if _operator == '=':
        return lambda s: _start <= s <= _end
    elif _operator == '<':
        return lambda s: s < _start
    elif _operator == '>':
        return lambda s: s > _end
    elif _operator == '<=':
        return lambda s: s <= _end
    elif _operator == '>=':
        return lambda s: s >= _start
    else:
        raise ExpressionError(f'Unknown operator `{_operator}`')