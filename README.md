# xmlAnalyzer

This script analyzes the current UI of a connected Android device to detect and highlight what it identifies as the most prominent popup window. It uses ADB to capture the screen and the UI layout hierarchy. After identifying the popup, it saves a new screenshot named `popup_highlighted.png` with a red rectangle drawn around the detected popup's boundaries and also prints the details of the interactive elements found within that popup to the console.

## Popup Identification Logic

The script identifies the topmost popup using a two-step heuristic approach on the UI nodes from the `uiautomator` dump:

1.  **Dialog Class Priority**: The script first searches for any UI element that has "Dialog" in its `class` attribute. This is a highly reliable indicator of a popup, and if found, that element is immediately considered the popup. The search is performed from the last node to the first, assuming the popup is one of the last elements added to the UI hierarchy.

2.  **Scrim-based Detection**: If no "Dialog" element is found, the script looks for a common UI pattern: a "scrim" overlay. A scrim is a semi-transparent layer that covers the underlying UI, focusing attention on the popup. The script identifies a scrim by looking for a large, clickable element that is not the root window itself.
    *   Once a scrim is identified, the script assumes that the actual popup is one of its direct child elements. It returns the first child that has a valid size.

This approach is more robust as it relies on common Android UI design patterns (Dialogs and Scrims) rather than a rigid set of rules about size and clickability.
