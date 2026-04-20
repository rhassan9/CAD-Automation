# CAD Extraction Error Handling & Monitoring Guide

This guide serves as a diagnostic matrix for engineers and developers to understand the error-handling mechanisms inside the CAD Automation App. 

## 1. Architectural Philosophy
The automation app distinguishes between **Fatal Extraction Exceptions** (which immediately abort the job) and **Non-Fatal Extracted Warnings** (which complete the job but explicitly alert the engineer that certain sheets will be blank).

## 2. Fatal Extraction Errors 
*(Raised as `CADExtractionError`)*
These errors occur when the requested execution fundamentally cannot process core algorithms. When triggered, the `.exe` halts generation and displays a native GUI `MessageBox.showwarning` dialog.

| Condition | Source File | Dialog Output | Trigger |
| :--- | :--- | :--- | :--- |
| **Missing Job Callouts** | `cable_assistant.py` | "CRITICAL: No valid CABLE CALLOUT blocks found with an 'HSP.XX.XX' prefix. The Cable Sheet cannot compute its Job Prefix and will abort." | The CAD draftsman failed to include any structural Segment Name/Size identifiers, meaning Voronoi logic cannot map constraints. |
| **Blank Geometric Results** | `cable_assistant.py` | "WARNING: No valid Cable Sheet spans were successfully geometrically matched to Callouts. Result is empty." | Callouts theoretically exist, but the CAD scale is broken or Spans are outside the 1800 proximity bounds. |

## 3. Non-Fatal Warnings
*(Wrapped as `CADWarningInfo` struct)*
These errors do *not* abort the file. It is normal engineering protocol to sometimes run isolated DXFs (e.g. only doing a Splice drop). These warnings map to specific Excel sheets so the engineer knows *why* a particular sheet generated as a blank page.

They are aggregated and surfaced cleanly in the Success GUI prompt.

| Condition | Sheet Affected | Dialog Warning String | Trigger |
| :--- | :--- | :--- | :--- |
| **Missing Labor Block Context** | LABOR SPAN SHEET | "No explicitly designated ITEM# callouts detected for Labor Spans." | Engineering forgot to stamp the specific `MODELITEM` length blocks on proper crossing paths. |
| **Missing Splice Parent** | SPLICING 1X8 TO 1X4 SPLITS | "No 1x8 Primary Splitter blocks detected in drawing." | Cannot trace house routing topology without a primary root 1x8. |
| **Missing Splice Child** | SPLICING 1X8 TO 1X4 SPLITS | "No 1x4 Secondary Splitters detected." | Handhole blocks exist but sub-splitters inside them are missing. |
| **Missing House Addr.** | House Count | "No target houses successfully mapped to splitters." | No text mapping valid addresses near the distribution network. |

## 4. Unknown Python Stack Trace Failures
*(Raised as `Exception`)*
If openpyxl or tkinter severely breaks (e.g., out of memory, read-only file permission lock), the engine catches this via a blanket UI `try/except` block and displays an ugly stack trace in a `messagebox.showerror` dialog detailing the exact system fault.
