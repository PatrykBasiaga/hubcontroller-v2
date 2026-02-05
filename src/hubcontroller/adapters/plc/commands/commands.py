from enum import Enum


class PlcSendStatus(str,Enum):
    OK = "write_ok"
    ERROR = "write_error"
    TIMEOUT = "write_timeout"
    INVALID_PARAMETERS = "write_invalid_parameters"


class PlcAckStatus(str,Enum):
    ACK_OK = "ack_ok"
    ACK_ERROR = "ack_error"
    ACK_TIMEOUT = "ack_timeout"
    ACK_INVALID_PARAMETERS = "ack_invalid_parameters"


class PlcExecStatus(str,Enum):
    EXEC_OK = "exec_ok"
    EXEC_ERROR = "exec_error"
    EXEC_TIMEOUT = "exec_timeout"
    EXEC_INVALID_PARAMETERS = "exec_invalid_parameters"


