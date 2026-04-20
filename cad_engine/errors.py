class CADExtractionError(Exception):
    """
    Exception raised for serious operational faults during CAD extraction.
    Used when crucial data is fundamentally missing (e.g. no CABLE CALLOUT blocks).
    """
    pass

class CADWarningInfo:
    """
    A unified struct to hold non-fatal architectural warnings generated during extraction.
    e.g. "Missing 1x8 Splitters. Splicing sheets will be blank."
    """
    def __init__(self, message, sheet_affected="General"):
        self.message = message
        self.sheet_affected = sheet_affected
