# xmlAnalyzer

This script analyzes the current UI of a connected Android device to detect and highlight what it identifies as the most prominent popup window. It uses ADB to capture the screen and the UI layout hierarchy. After identifying the popup, it saves a new screenshot named `popup_highlighted.png` with a red rectangle drawn around the detected popup's boundaries and also prints the details of the interactive elements found within that popup to the console.

## Popup Identification Logic

The script identifies a UI element as a popup based on the following set of filters applied to the UI nodes from the `uiautomator` dump:

*   The element must be `clickable`.
*   It must be a container, not a single element (i.e., it has child elements).
*   It must not be a core system element (its `resource-id` does not contain "system").
*   It is not a scrollable container (e.g., `ScrollView` or `RecyclerView`).
*   Its area must be between 5% and 98% of the total screen area.
*   Among all elements that pass these filters, the one with the largest area is chosen as the popup.
