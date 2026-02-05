from hubcontroller.adapters.plc.transport.plc_adapter import PlcAdapter
from hubcontroller.adapters.plc.protocol.decoders.ack_decoder import AckDecoder
from hubcontroller.adapters.plc.protocol.specs.ack_specs import FrameSpec
from hubcontroller.adapters.plc.protocol.models.ack_snapshot import AckSnapshot

class PlcGateway:
    def __init__(self, plc_adapter: PlcAdapter, ack_decoder: AckDecoder, ack_frame_spec: FrameSpec):
        self._plc_adapter = plc_adapter
        self._ack_decoder = ack_decoder
        self._ack_frame_spec = ack_frame_spec
  
    def _read_ack_bytes(self) -> bytearray:
        return self._plc_adapter.read_db(db_number=self._ack_frame_spec.db_num, start=self._ack_frame_spec.start, length=self._ack_frame_spec.length)
    
    def _decode_ack_bytes(self, data: bytearray) -> AckSnapshot:
        return self._ack_decoder.decode(data)

    def read_ack_snapshot(self) -> AckSnapshot:
        data = self._read_ack_bytes()
        self._snapshot = self._decode_ack_bytes(data)
        return self._snapshot

    def consume_ack_trigger(self, snapshot: AckSnapshot) -> bool:
        if snapshot.trigger == 0:
            return False
        if snapshot.triggger != 0 and snapshot.token.strip() == "":
            raise ValueError("Token is required for trigger consumption")

        data = bytearray(b'\x00\x00')
        self._plc_adapter.write_db(db_number=self._ack_frame_spec.db_num, start=self._ack_frame_spec.start, data=data)
        return True


