import os
import xml.etree.ElementTree as ET
import re
from PIL import Image, ImageDraw

ADB_PATH = "adb"

def capture_screenshot():
    os.system(f"{ADB_PATH} shell screencap -p /sdcard/screen.png")
    os.system(f"{ADB_PATH} pull /sdcard/screen.png screen.png")
    os.system(f"{ADB_PATH} shell rm /sdcard/screen.png")

def dump_ui_xml():
    os.system(f"{ADB_PATH} shell uiautomator dump /sdcard/window_dump.xml")
    os.system(f"{ADB_PATH} pull /sdcard/window_dump.xml window_dump.xml")
    os.system(f"{ADB_PATH} shell rm /sdcard/window_dump.xml")

def get_screen_size():
    output = os.popen(f"{ADB_PATH} shell wm size").read()
    if "Physical size" in output:
        size_str = output.strip().split(":")[1].strip()
        width, height = map(int, size_str.split("x"))
        return width, height
    return None

def parse_bounds(bounds_str):
    match = re.match(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]', bounds_str)
    if match:
        return tuple(map(int, match.groups()))
    return (0, 0, 0, 0)

def find_topmost_popup(xml_path="window_dump.xml", screen_size=(1080, 1920), min_area_ratio=0.05, max_area_ratio=0.95):
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
    except (FileNotFoundError, ET.ParseError):
        print(f"Error: Could not parse {xml_path}")
        return None

    screen_w, screen_h = screen_size
    screen_area = screen_w * screen_h
    if screen_area == 0:
        return None

    # Heuristic 1: A 'Dialog' class is the most reliable sign.
    for node in reversed(list(root.iter('node'))):
        if 'Dialog' in node.attrib.get('class', ''):
            return node

    # Heuristic 2: Find a large, clickable "scrim" and return its content panel.
    # This is a very common and stable UI pattern for popups and bottom sheets.
    for node in reversed(list(root.iter('node'))):
        attributes = node.attrib
        bounds_str = attributes.get('bounds')
        if not bounds_str or not list(node):
            continue
        
        bounds = parse_bounds(bounds_str)
        node_area = (bounds[2] - bounds[0]) * (bounds[3] - bounds[1])
        area_ratio = node_area / screen_area

        is_scrim = (attributes.get('clickable') == 'true' and 
                    area_ratio > 0.5 and 
                    area_ratio < 1.0)
        
        if is_scrim:
            # The scrim was found. The actual popup is its direct child.
            for child in node:
                child_bounds_str = child.attrib.get('bounds')
                if child_bounds_str and list(child):
                    child_bounds = parse_bounds(child_bounds_str)
                    child_area = (child_bounds[2] - child_bounds[0]) * (child_bounds[3] - child_bounds[1])
                    if child_area > 0 and child_area < node_area:
                        return child

    return None
def draw_box(image_path, bounds, output_path="popup_highlighted.png", label="Popup"):
    try:
        img = Image.open(image_path).convert("RGB")
        draw = ImageDraw.Draw(img)
        x1, y1, x2, y2 = bounds
        draw.rectangle([x1, y1, x2, y2], outline="red", width=5)
        font_size = 30
        try:
            from PIL import ImageFont
            font = ImageFont.truetype("arial.ttf", font_size)
        except IOError:
            font = ImageFont.load_default()
        draw.text((x1 + 10, y1 + 10), label, fill="red", font=font)
        img.save(output_path)
        print(f"Highlighted image saved as {output_path}")
    except FileNotFoundError:
        print(f"Error: Image not found at {image_path}")

def print_popup_elements(popup_node):
    print("\n--- Elements inside Popup ---")
    for element in popup_node.iter('node'):
        if element is popup_node:
            continue

        attrs = element.attrib
        text = attrs.get('text', '')
        res_id = attrs.get('resource-id', '')
        clickable = attrs.get('clickable') == 'true'

        if text or clickable:
            details = []
            if text:
                details.append(f'Text: "{text}"')
            if res_id:
                short_id = res_id.split('/')[-1]
                details.append(f'ID: {short_id}')
            if clickable:
                details.append('Clickable: true')
            
            print(f"  - Node: {', '.join(details)}")
    print("-----------------------------\n")

if __name__ == "__main__":
    print("Capturing live phone UI...")
    capture_screenshot()
    dump_ui_xml()

    screen_size = get_screen_size()
    if not screen_size:
        print("Could not determine screen size. Exiting.")
        exit()
    
    print(f"Screen size: {screen_size[0]} x {screen_size[1]}")

    popup_element = find_topmost_popup(screen_size=screen_size)
    
    if popup_element is not None:
        popup_id = popup_element.get('resource-id', 'N/A')
        popup_bounds_str = popup_element.get('bounds')
        popup_bounds = parse_bounds(popup_bounds_str)

        print(f"Popup Found: {popup_id} — bounds: {popup_bounds}")
        draw_box("screen.png", popup_bounds, label=popup_id)
        
        print_popup_elements(popup_element)
    else:
        print("No suitable popup found.")