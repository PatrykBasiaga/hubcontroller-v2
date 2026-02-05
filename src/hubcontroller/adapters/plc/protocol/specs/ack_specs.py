from enum import Enum
from dataclasses import dataclass
from typing import Optional
from config.environment import Environments

class PlcDataType(str,Enum):
    INT = "int"
    BYTE = "byte"
    BOOL = "bool"
    STRING = "string"
    FLOAT = "float"
    DOUBLE = "double"

@dataclass(frozen=True, slots=True)
class FieldSpec:
    name: str
    offset: int
    dtype: PlcDataType
    max_len: Optional[int] = None
    bit_index: Optional[int] = None

    def __post_init__(self):
        if self.dtype == PlcDataType.STRING:
            if self.max_len is None:
                raise ValueError(f"STRING field '{self.name}' needs max_len")
            if self.bit_index is not None:
                raise ValueError(f"STRING field '{self.name}' cannot have bit_index")
            return
        if self.dtype == PlcDataType.BOOL:
            if self.max_len is not None:
                raise ValueError(f"BOOL field '{self.name}' cannot have max_len")
            if self.bit_index is None or not (0 <= self.bit_index <= 7):
                raise ValueError(f"BOOL field '{self.name}' needs bit_index in range 0..7")
            return
        if self.max_len is not None or self.bit_index is not None:
            raise ValueError(f"Field '{self.name}' of type {self.dtype} cannot have max_len/bit_index")

@dataclass(frozen=True, slots=True)
class FrameSpec:
    db_num: int
    start: int
    length: int
    fields: tuple[FieldSpec, ...]

    def __post_init__(self):
        # 1) unique field names
        names = [f.name for f in self.fields]
        if len(names) != len(set(names)):
            raise ValueError(f"Duplicate field names in FrameSpec: {names}")

        # 2) offsets vs start
        for f in self.fields:
            if f.offset < self.start:
                raise ValueError(
                    f"Field '{f.name}' offset {f.offset} < start {self.start}"
                )

        # 3) length covers all fields
        required = max(
            field_end_offset(f) for f in self.fields
        ) - self.start

        if self.length < required:
            raise ValueError(
                f"FrameSpec length too small: {self.length} < required {required}"
            )


def field_end_offset(field:FieldSpec) -> int:
    if field.dtype == PlcDataType.STRING:
        if field.max_len is None:
            raise ValueError(f"STRING field '{field.name}' needs max_len")
        return field.offset + field.max_len + 2
    if field.dtype == PlcDataType.INT:
        return field.offset + 2
    if field.dtype == PlcDataType.BYTE:
        return field.offset + 1
    if field.dtype == PlcDataType.BOOL:
        return field.offset + 1
    if field.dtype == PlcDataType.FLOAT:
        return field.offset + 4
    if field.dtype == PlcDataType.DOUBLE:
        return field.offset + 8
    else:
        raise ValueError(f"Unknown data type: {field.dtype}")

def get_max_length(fields: tuple[FieldSpec, ...], start: int = 0) -> int:
    if not fields: return 0
    else: return (max(field_end_offset(field) for field in fields) - start)

ACK_FIELDS = (
    FieldSpec(name="trigger", offset=0, dtype=PlcDataType.INT),
    FieldSpec(name="command", offset=2, dtype=PlcDataType.STRING, max_len=100),
    FieldSpec(name="error", offset=104, dtype=PlcDataType.INT),
    FieldSpec(name="message", offset=106, dtype=PlcDataType.STRING, max_len=100),
    FieldSpec(name="token", offset=208, dtype=PlcDataType.STRING, max_len=40),
    FieldSpec(name="mission_id", offset=250, dtype=PlcDataType.INT),
)


ACK_FRAME_SPEC = FrameSpec(
    db_num=Environments.PLC_ACK_READ_DB,
    start= 0,
    length=get_max_length(ACK_FIELDS) ,
    fields=ACK_FIELDS
)