# -*- coding:utf-8 -*-


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Event( object ):
    """
    Generic event to use with EventDispatcher.
    用于事件分发
    """

    def __init__(self, event_type, data=None):
        """
        The constructor accepts an event type as string and a custom data
        定义event的类型和数据
        """
        self._type = event_type
        self._data = data

    @property
    def type(self):
        """
        Returns the event type
        返回event类型
        """
        return self._type

    @property
    def data(self):
        """
        Returns the data associated to the event
        返回event传递的数据
        """
        return self._data


class EventDispatcher( object ):
    """
    Generic event dispatcher which listen and dispatch events
    event分发类 监听和分发event事件
    """

    def __init__(self):
        """
        初始化类
        """
        self._events = dict()

    def __del__(self):
        """
        清空所有event
        """
        self._events = None

    def has_listener(self, event_type, listener):
        """
        Return true if listener is register to event_type
        返回注册到event_type的listener
        """
        # Check for event type and for the listener
        if event_type in self._events.keys():
            return listener in self._events[ event_type ]
        else:
            return False

    def dispatch_event(self, event):
        """
        Dispatch an instance of Event class
        """
        # 分发event到所有关联的listener
        if event.type in self._events.keys():
            listeners = self._events[ event.type ]

            for listener in listeners:
                listener( event )

    def add_event_listener(self, event_type, listener):
        """
        Add an event listener for an event type
        给某种事件类型添加listener
        """
        # Add listener to the event type
        if not self.has_listener( event_type, listener ):
            listeners = self._events.get( event_type, [] )

            listeners.append( listener )

            self._events[ event_type ] = listeners

    def remove_event_listener(self, event_type, listener):
        """
        移出某种事件类型的所有listener
        """
        # Remove the listener from the event type
        if self.has_listener( event_type, listener ):
            listeners = self._events[ event_type ]

            if len( listeners ) == 1:
                # Only this listener remains so remove the key
                del self._events[ event_type ]

            else:
                # Update listeners chain
                listeners.remove( listener )

                self._events[ event_type ] = listeners