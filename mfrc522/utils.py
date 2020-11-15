'''
Util functions and classes

Copyright (c) 2019 Christian Meffert <christian.meffert@googlemail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
'''

import traceback


class FormatString(object):
    '''
    Helper class to create log messages with string format()
    https://stackoverflow.com/questions/13131400/logging-variable-data-with-new-format-string/13131690#13131690

    Example:
    >>> logger.debug(FormatString('Message with {0} {name}', 2, name='placeholders'))
    '''

    def __init__(self, fmt, *args, **kwargs):
        self.fmt = fmt
        self.args = args
        self.kwargs = kwargs

    def __str__(self):
        try:
            message = self.fmt.format(*self.args, **self.kwargs)
        except Exception:
            message = 'ERROR creating log message! ' + "\n" + traceback.format_exc()
        return message


def format_hex(data):
    '''
    Helper function to create a readable string for a list of bytes
    '''
    try:
        result = ' '.join(format(x, '#04x') for x in data)
    except Exception:
        result = 'ERROR: {} is not a HEX list'.format(data)
    return result
