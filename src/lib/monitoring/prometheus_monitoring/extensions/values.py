"""
    Values module copied from prometheus client
    Extends default values.py

    List of changes:
        - added 'delete' method for deleting metrics from multiprocess files
"""
# flake8: noqa
# pylint: skip-file
import os
from threading import Lock
import warnings

from prometheus_client.mmap_dict import mmap_key, MmapedDict

from .utils import delete_key


class MutexValue:
    """A float protected by a mutex."""

    _multiprocess = False

    def __init__(self, typ, metric_name,  # type: ignore[no-untyped-def]
                 name, labelnames, labelvalues, help_text, **kwargs):
        self._value = 0.0
        self._exemplar = None
        self._lock = Lock()

    def inc(self, amount):  # type: ignore[no-untyped-def]
        with self._lock:
            self._value += amount

    def set(self, value):  # type: ignore[no-untyped-def]
        with self._lock:
            self._value = value

    def delete(self):  # type: ignore[no-untyped-def]
        pass

    def set_exemplar(self, exemplar):  # type: ignore[no-untyped-def]
        with self._lock:
            self._exemplar = exemplar

    def get(self):  # type: ignore[no-untyped-def]
        with self._lock:
            return self._value

    def get_exemplar(self):  # type: ignore[no-untyped-def]
        with self._lock:
            return self._exemplar


def MultiProcessValue(process_identifier=os.getpid):  # type: ignore[no-untyped-def]
    """Returns a MmapedValue class based on a process_identifier function.

    The 'process_identifier' function MUST comply with this simple rule:
    when called in simultaneously running processes it MUST return distinct values.

    Using a different function than the default 'os.getpid' is at your own risk.
    """
    files = {}
    values = []
    pid = {'value': process_identifier()}
    # Use a single global lock when in multi-processing mode
    # as we presume this means there is no threading going on.
    # This avoids the need to also have mutexes in __MmapDict.
    lock = Lock()

    class MmapedValue:
        """A float protected by a mutex backed by a per-process mmaped file."""

        _multiprocess = True

        def __init__(self, typ, metric_name, name,  # type: ignore[no-untyped-def]
                     labelnames, labelvalues, help_text, multiprocess_mode='', **kwargs):
            self._params = typ, metric_name, name, labelnames, labelvalues, help_text, multiprocess_mode
            # This deprecation warning can go away in a few releases when removing the compatibility
            if 'prometheus_multiproc_dir' in os.environ and 'PROMETHEUS_MULTIPROC_DIR' not in os.environ:
                os.environ['PROMETHEUS_MULTIPROC_DIR'] = os.environ['prometheus_multiproc_dir']
                warnings.warn(
                    "prometheus_multiproc_dir variable has been deprecated in favor of the upper case naming PROMETHEUS_MULTIPROC_DIR",
                    DeprecationWarning)
            with lock:
                self.__check_for_pid_change()
                self.__reset()
                values.append(self)

        def __reset(self):  # type: ignore[no-untyped-def]
            typ, metric_name, name, labelnames, labelvalues, help_text, multiprocess_mode = self._params
            if typ == 'gauge':
                file_prefix = typ + '_' + multiprocess_mode
            else:
                file_prefix = typ
            if file_prefix not in files:
                filename = os.path.join(
                    os.environ.get('PROMETHEUS_MULTIPROC_DIR'),
                    '{}_{}.db'.format(file_prefix, pid['value']))

                files[file_prefix] = MmapedDict(filename)
            self._file = files[file_prefix]
            self._key = mmap_key(metric_name, name, labelnames, labelvalues, help_text)
            self._value = self._file.read_value(self._key)

        def __check_for_pid_change(self):  # type: ignore[no-untyped-def]
            actual_pid = process_identifier()
            if pid['value'] != actual_pid:
                pid['value'] = actual_pid
                # There has been a fork(), reset all the values.
                for f in files.values():
                    f.close()
                files.clear()
                for value in values:
                    value.__reset()

        def inc(self, amount):  # type: ignore[no-untyped-def]
            with lock:
                self.__check_for_pid_change()
                self._value += amount
                self._file.write_value(self._key, self._value)

        def set(self, value):  # type: ignore[no-untyped-def]
            with lock:
                self.__check_for_pid_change()
                self._value = value
                self._file.write_value(self._key, self._value)

        def delete(self):  # type: ignore[no-untyped-def]
            with lock:
                delete_key(self._file, self._key)

        def set_exemplar(self, exemplar):  # type: ignore[no-untyped-def]
            return

        def get(self):  # type: ignore[no-untyped-def]
            with lock:
                self.__check_for_pid_change()
                return self._value

        def get_exemplar(self):  # type: ignore[no-untyped-def]
            return None

    return MmapedValue


def get_value_class():  # type: ignore[no-untyped-def]
    # Should we enable multi-process mode?
    # This needs to be chosen before the first metric is constructed,
    # and as that may be in some arbitrary library the user/admin has
    # no control over we use an environment variable.
    if 'prometheus_multiproc_dir' in os.environ or 'PROMETHEUS_MULTIPROC_DIR' in os.environ:
        return MultiProcessValue()
    else:
        return MutexValue


ValueClass = get_value_class()