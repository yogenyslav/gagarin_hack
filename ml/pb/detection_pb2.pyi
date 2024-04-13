from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ResponseStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    Processing: _ClassVar[ResponseStatus]
    Success: _ClassVar[ResponseStatus]
    Error: _ClassVar[ResponseStatus]
    Canceled: _ClassVar[ResponseStatus]
Processing: ResponseStatus
Success: ResponseStatus
Error: ResponseStatus
Canceled: ResponseStatus

class Query(_message.Message):
    __slots__ = ("id", "source")
    ID_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    id: int
    source: str
    def __init__(self, id: _Optional[int] = ..., source: _Optional[str] = ...) -> None: ...

class Response(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: ResponseStatus
    def __init__(self, status: _Optional[_Union[ResponseStatus, str]] = ...) -> None: ...

class ResultReq(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    def __init__(self, id: _Optional[int] = ...) -> None: ...

class Anomaly(_message.Message):
    __slots__ = ("ts", "link")
    TS_FIELD_NUMBER: _ClassVar[int]
    LINK_FIELD_NUMBER: _ClassVar[int]
    CLASS_FIELD_NUMBER: _ClassVar[int]
    ts: int
    link: str
    def __init__(self, ts: _Optional[int] = ..., link: _Optional[str] = ..., **kwargs) -> None: ...

class ResultResp(_message.Message):
    __slots__ = ("anomalies",)
    ANOMALIES_FIELD_NUMBER: _ClassVar[int]
    anomalies: _containers.RepeatedCompositeFieldContainer[Anomaly]
    def __init__(self, anomalies: _Optional[_Iterable[_Union[Anomaly, _Mapping]]] = ...) -> None: ...
