from hubcontroller.adapters.plc.transport.plc_adapter import PlcAdapter
from hubcontroller.adapters.plc.protocol.decoders.exec_decoder import ExecDecoder
from hubcontroller.adapters.plc.protocol.specs.ack_specs import FrameSpec
from hubcontroller.adapters.plc.protocol.models.ack_snapshot import AckSnapshot

class AckGateway:
    def __init__(self, plc_adapter: PlcAdapter, ack_decoder: AckDecoder, ack_frame_spec: FrameSpec):
        self._plc_adapter = plc_adapter
        self._ack_decoder = ack_decoder
        self._ack_frame_spec = ack_frame_spec

        # --- FAIL-FAST konfiguracji ---
        try:
            trigger_offset = self._ack_frame_spec.get_field_offset("trigger")
        except Exception as e:
            raise ValueError(f"ACK gateway init failed: {e}") from e

        if trigger_offset < 0:
            raise ValueError(f"ACK FrameSpec misconfigured: trigger offset {trigger_offset} must be >= 0")

        # opcjonalna walidacja: czy trigger leży w zakresie ramki odczytu
        frame_start = self._ack_frame_spec.start
        frame_end_excl = self._ack_frame_spec.start + self._ack_frame_spec.length
        if not (frame_start <= trigger_offset < frame_end_excl):
            raise ValueError(
                "ACK FrameSpec misconfigured: trigger offset "
                f"{trigger_offset} is outside frame range "
                f"[{frame_start}, {frame_end_excl})"
            )

        self._trigger_offset = trigger_offset
  
    def _read_ack_bytes(self) -> bytearray:
        return self._plc_adapter.read_db(db_number=self._ack_frame_spec.db_num, start=self._ack_frame_spec.start, length=self._ack_frame_spec.length)
    
    def _decode_ack_bytes(self, data: bytearray) -> AckSnapshot:
        return self._ack_decoder.decode(data)

    def read_ack_snapshot(self) -> AckSnapshot:
        acksnapshot = self._decode_ack_bytes(self._read_ack_bytes())
        acksnapshot.token = acksnapshot.token.strip()
        return acksnapshot

    def consume_ack_trigger(self, snapshot: AckSnapshot) -> bool:
        if snapshot.trigger == 0:
            return False
        if snapshot.trigger != 0 and snapshot.token.strip() == "":
            raise ValueError("Token is required for trigger consumption")

        data = bytearray(b'\x00\x00')
        self._plc_adapter.write_db(db_number=self._ack_frame_spec.db_num, start=self._trigger_offset, data=data)
        return True


