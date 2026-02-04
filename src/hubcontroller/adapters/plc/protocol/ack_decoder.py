from hubcontroller.adapters.plc.protocol.ack_snapshot import AckSnapshot
from hubcontroller.adapters.plc.ack_specs import ACK_FRAME_SPEC, PlcDataType, FieldSpec
import struct
from typing import Any

class AckDecoder:

    def decode(self, data: bytearray) -> AckSnapshot:
        if len(data) >= ACK_FRAME_SPEC.length:
            raise ValueError(f"Data length mismatch: {len(data)} != {ACK_FRAME_SPEC.length}")
        values = {}
        for field in ACK_FRAME_SPEC.fields:
            index = field.offset - ACK_FRAME_SPEC.start
            values[field.name]= self.decode_field(data, field, offset=index)
        return AckSnapshot(**values)


    def decode_field(self, data: bytearray, field: FieldSpec, index: int) -> Any:
        if field.dtype == PlcDataType.INT:
            return self.decode_int(data, index)
        elif field.dtype == PlcDataType.STRING:
            return self.decode_string(data, index, field.max_len)
        elif field.dtype == PlcDataType.BOOL:
            return self.decode_bool(data, index, field.bit_index)
        elif field.dtype == PlcDataType.BYTE:
            return self.decode_byte(data, index)
        elif field.dtype == PlcDataType.FLOAT:
            return self.decode_float(data, index)
        elif field.dtype == PlcDataType.DOUBLE:
            return self.decode_double(data, index)
        else:
            raise ValueError(f"Unknown data type: {field.dtype}")
    

    def decode_int(self, data: bytearray, index: int) -> int:
        if index + 2 > len(data):
            raise ValueError(f"Index out of bounds: {index}")
        return int.from_bytes(data[index:index+2], byteorder='big', signed=True)
    
    def decode_string(self, data: bytearray, index: int, max_length: int) -> str:
        end = index + max_length + 2
        if end > len(data):
            raise ValueError(f"Index out of bounds: {index}")
        declared_max = data[index]
        current_len = data[index+1]
        if declared_max < max_length:
            pass
        if current_len > declared_max:
            current_len = min(current_len, max_length)
        raw = data[index+2:index+2+current_len]
        return raw.decode('utf-8', errors='replace').strip()
    
    def decode_bool(self, data: bytearray, index: int, bit_index: int) -> bool:
        if index + 1 > len(data):
            raise ValueError(f"Index out of bounds: {index}")
        if bit_index < 0 or bit_index > 7:
            raise ValueError(f"Bit index out of bounds: {bit_index}")
        return bool(data[index] & (1 << bit_index))

    def decode_byte(self, data: bytearray, index: int) -> int:
        if index + 1 > len(data):
            raise ValueError(f"Index out of bounds: {index}")
        return data[index]
    
    def decode_float(self, data: bytearray, index: int) -> float:
        if index + 4 > len(data):
            raise ValueError(f"Index out of bounds: {index}")
        return struct.unpack(">f", data[index:index+4])[0]
    
    def decode_double(self, data: bytearray, index: int) -> float:
        if index + 8 > len(data):
            raise ValueError(f"Index out of bounds: {index}")
        return struct.unpack(">d", data[index:index+8])[0]
    