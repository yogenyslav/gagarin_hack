from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Model(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    Rgb: _ClassVar[Model]
    Bytes: _ClassVar[Model]

class ResponseStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    Processing: _ClassVar[ResponseStatus]
    Success: _ClassVar[ResponseStatus]
    Error: _ClassVar[ResponseStatus]
    Canceled: _ClassVar[ResponseStatus]
Rgb: Model
Bytes: Model
Processing: ResponseStatus
Success: ResponseStatus
Error: ResponseStatus
Canceled: ResponseStatus

class Query(_message.Message):
    __slots__ = ("id", "source", "model")
    ID_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    id: int
    source: str
    model: Model
    def __init__(self, id: _Optional[int] = ..., source: _Optional[str] = ..., model: _Optional[_Union[Model, str]] = ...) -> None: ...

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
    __slots__ = ("ts", "links", "cls")
    TS_FIELD_NUMBER: _ClassVar[int]
    LINKS_FIELD_NUMBER: _ClassVar[int]
    CLS_FIELD_NUMBER: _ClassVar[int]
    ts: int
    links: _containers.RepeatedScalarFieldContainer[str]
    cls: str
    def __init__(self, ts: _Optional[int] = ..., links: _Optional[_Iterable[str]] = ..., cls: _Optional[str] = ...) -> None: ...

class ResultResp(_message.Message):
    __slots__ = ("anomalies",)
    ANOMALIES_FIELD_NUMBER: _ClassVar[int]
    anomalies: _containers.RepeatedCompositeFieldContainer[Anomaly]
    def __init__(self, anomalies: _Optional[_Iterable[_Union[Anomaly, _Mapping]]] = ...) -> None: ...
