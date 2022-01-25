from abc import ABCMeta, abstractmethod


# didn't subclass mutable mapping because I don't
# want to implement such mapping methods as update, clear, etc.
class AbstractBasePool(metaclass=ABCMeta):
    """Abstract base class for pool"""

    @abstractmethod
    def add(self, *args, **kwargs):
        ...

    @abstractmethod
    def remove(self, *args, **kwargs):
        ...

    @abstractmethod
    def startup(self):
        ...

    @abstractmethod
    def shutdown(self):
        ...

    @abstractmethod
    def get(self, k):
        ...

    @abstractmethod
    def pop(self, k):
        ...

    @abstractmethod
    def _bind(self, *args):
        ...

    @abstractmethod
    def _unbind(self, *args):
        ...

    @abstractmethod
    def __contains__(self, item):
        ...

    @abstractmethod
    def __len__(self):
        ...

    @abstractmethod
    def __iter__(self):
        ...

    @abstractmethod
    def __getitem__(self, item):
        ...

    # @abstractmethod
    # def __setitem__(self, key, value): ...

    @abstractmethod
    def __delitem__(self, key):
        ...

    @abstractmethod
    def __bool__(self):
        ...
