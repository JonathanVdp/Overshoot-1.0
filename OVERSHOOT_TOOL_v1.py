"""
OVERSHOOT_v1.00 - (c) copyright
author:         Jonathan VANDREPOTTE
description:    
This script is a Maya script that creates a custom window tool to apply overshoot animation to objects in Maya. 
The script creates a window with a UI that includes sliders for Interpolation Factor and Amplitude Factor, 
checkboxes to select which attributes to animate (Translate X, Y, Z, Rotate X, Y, Z), 
and a checkbox for Reverse Curve. When the Overshoot button is clicked, 
the script will apply overshoot animation to the selected objects based on the values set in the UI. 
The overshoot animation is achieved by setting keyframes on the selected attributes and then adding an amplitude factor to the value of the attribute based on the sine of the interpolation factor. 
The resulting animation will have a characteristic overshoot and settling effect
"""


import maya.cmds as cmds
import maya.mel as mel

WINDOW_NAME = "OvershootTool"
slider = None
color_checkbox = None
translate_checkboxes = []
rotate_checkboxes = []
color_checkboxes = []
check_all = None
intensity_slider = None

def calculate_overshoot(value, velocity, intensity):
    return value + (velocity * intensity)

def apply_overshoot(direction):
    current_frame = cmds.currentTime(query=True)
    intensity = cmds.floatSliderGrp(intensity_slider, query=True, value=True)

    attribute_checkboxes = {
        "translateX": translate_checkboxes[0],
        "translateY": translate_checkboxes[1],
        "translateZ": translate_checkboxes[2],
        "rotateX": rotate_checkboxes[0],
        "rotateY": rotate_checkboxes[1],
        "rotateZ": rotate_checkboxes[2]
    }

    selected_objects = cmds.ls(selection=True)
    objects_data = {}

    for obj in selected_objects:
        attrs = cmds.listAttr(obj, keyable=True, st=["translate*", "rotate*"])
        if attrs is None:
            
            continue

        obj_data = {}
        for attr in attrs:
            if attr not in ["translateX", "translateY", "translateZ", "rotateX", "rotateY", "rotateZ"]:
               
                continue

            if not cmds.checkBox(attribute_checkboxes[attr], query=True, value=True):
                # Skip attributes that are not checked
                continue

            previous_key = cmds.findKeyframe(obj, attribute=attr, which="previous", time=(current_frame,))
            next_key = cmds.findKeyframe(obj, attribute=attr, which="next", time=(current_frame,))

            if previous_key is not None and next_key is not None and previous_key != next_key:
                prev_value = cmds.getAttr(obj + "." + attr, time=previous_key)
                next_value = cmds.getAttr(obj + "." + attr, time=next_key)
                current_value = cmds.getAttr(obj + "." + attr, time=current_frame)

                velocity = (next_value - prev_value) * direction
                overshoot_value = calculate_overshoot(current_value, velocity, float(intensity))

                obj_data[attr] = overshoot_value

        if obj_data:
            objects_data[obj] = obj_data

    cmds.select(selected_objects) 

    for obj, obj_data in objects_data.items():
        cmds.select(obj)
        for attr, value in obj_data.items():
            cmds.setAttr(obj + "." + attr, value)
            cmds.setKeyframe(obj, attribute=attr, time=(current_frame,), value=value)

        if cmds.checkBox(color_checkbox, query=True, value=True):
            mel_script = '''
                performSetKeyframeArgList 1 {"0", "animationList"};
                keyframe -time `currentTime -q` -tds 1;
            '''
            mel.eval(mel_script)

    cmds.select(selected_objects) 
    cmds.refresh()

def overshoot_positive(*args):
    apply_overshoot(1)

def overshoot_negative(*args):
    apply_overshoot(-1)

def toggle_all_checkboxes(*args):
    all_value = cmds.checkBox(check_all, query=True, value=True)
   
    for checkbox in translate_checkboxes + rotate_checkboxes:
        cmds.checkBox(checkbox, edit=True, value=all_value)

def create_window():
    if cmds.window(WINDOW_NAME, exists=True):
        cmds.deleteUI(WINDOW_NAME)
    window = cmds.window(WINDOW_NAME, title="Overshoot Tool V1.0", widthHeight=(300, 400), sizeable=True, resizeToFitChildren=True)

    global slider, color_checkbox, translate_checkboxes, rotate_checkboxes, color_checkboxes, check_all, intensity_slider

    
    bg_color = [0.4, 0.6, 0.4] 
    section_color = [0.8, 0.8, 0.8] 

    cmds.columnLayout(adjustableColumn=True, rowSpacing=10, bgc=bg_color)

    cmds.separator()

    cmds.columnLayout(adjustableColumn=True, bgc=bg_color)
    cmds.frameLayout(label="Intensity", collapsable=True, marginWidth=5, marginHeight=5, bgc=section_color)
    intensity_slider = cmds.floatSliderGrp(label="Intensity", field=True, minValue=0, maxValue=2.0, fieldMinValue=0, fieldMaxValue=20, value=0.1, sliderStep=0.1, columnWidth=(1, 40), columnAlign=(1, 'center'))

    cmds.setParent('..')

    cmds.separator()

    cmds.columnLayout(adjustableColumn=True, bgc=bg_color)
    cmds.frameLayout(label="Attributes", collapsable=True, marginWidth=5, marginHeight=5, bgc=section_color)
    cmds.rowColumnLayout(numberOfColumns=3, columnWidth=[(1, 100), (2, 100), (3, 100)], columnSpacing=[(1, 5), (2, 5), (3, 5)])
    check_all = cmds.checkBox(label="Check All", value=True, changeCommand=toggle_all_checkboxes, bgc=section_color)
    translate_checkboxes = [cmds.checkBox(label="Translate X", bgc=section_color), cmds.checkBox(label="Translate Y", bgc=section_color), cmds.checkBox(label="Translate Z", bgc=section_color)]
    rotate_checkboxes = [cmds.checkBox(label="Rotate X", bgc=section_color), cmds.checkBox(label="Rotate Y", bgc=section_color), cmds.checkBox(label="Rotate Z", bgc=section_color)]
    cmds.setParent('..')
    cmds.setParent('..')

    cmds.separator()

    cmds.columnLayout(adjustableColumn=True, bgc=bg_color)
    cmds.frameLayout(label="Overshoot Direction", collapsable=True, marginWidth=5, marginHeight=5, bgc=section_color)
    cmds.rowLayout(numberOfColumns=2, columnWidth=[(1, 150), (2, 150)], columnAttach=[(1, 'both', 0), (2, 'both', 0)], adjustableColumn=1, columnAlign=[(1, 'center'), (2, 'center')])
    cmds.button(label="Positive Direction", command=overshoot_positive, backgroundColor=[0.1, 0.5, 0.1])
    cmds.button(label="Negative Direction", command=overshoot_negative, backgroundColor=[0.5, 0.1, 0.1])
    cmds.setParent('..')
    cmds.setParent('..')

    cmds.separator()

    cmds.columnLayout(adjustableColumn=True, bgc=bg_color)
    cmds.frameLayout(label="Keys Color", collapsable=True, marginWidth=5, marginHeight=5, bgc=section_color)
    color_checkbox = cmds.checkBox(label="Green", value=False, bgc=section_color)
    cmds.setParent('..')
    cmds.setParent('..')

    cmds.separator()

    cmds.showWindow(window)
    toggle_all_checkboxes()
    
if __name__ == "__main__":
    create_window()
