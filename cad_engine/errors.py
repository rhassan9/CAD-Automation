class CADExtractionError(Exception):
    """Raised when critical, unrecoverable data faults occur halting entirely the topology pipeline."""
    pass

class CableAssistantError(Exception):
    """Raised when the supplementary Cable Assistant logic gracefully aborts due to incompatible DXF layouts."""
    pass

class CADWarningInfo:
    """
    A unified struct to hold non-fatal architectural warnings generated during extraction.
    e.g. "Missing 1x8 Splitters. Splicing sheets will be blank."
    """
    def __init__(self, message, sheet_affected="General"):
        self.message = message
        self.sheet_affected = sheet_affected
