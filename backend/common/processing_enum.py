from enum import StrEnum


class ProcessStatus(StrEnum):
    PROCESSING = 'processing',
    PROCESSED = 'processed',
    FAIL = 'failed',


class OperationType(StrEnum):
    INITIALIZE = 'initialize',
    APPLY_SCRIPT = 'apply_script',
    FILL_NULL = 'fill_null',
