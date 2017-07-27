import fileinput
import os
import sys

import maya.OpenMayaUI as mui
import maya.cmds as cmds
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from shiboken2 import wrapInstance

SCRIPT_NAME = "Vehicular"


# ----------------------------------------------------------------------------------------------------------------------
# Returns an instance of Maya's main window
# ----------------------------------------------------------------------------------------------------------------------
def maya_main_window():
    main_window_ptr = mui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QWidget)


class MainUI(QDialog):
    # Set up file references
    icon_dir = os.path.expanduser("~/maya/scripts/magic-shade/resources/icons")
    spellbook_dir = os.path.expanduser("~/maya/scripts/magic-shade/spellbooks")
    pref_path = os.path.expanduser("~/maya/scripts/magic-shade/prefs")
    arnold_studio_path = os.path.expanduser("~/maya/scripts/magic-shade/Arnold_Studio_V3.mb")
    last_file_pref = "last_vehicular_spellbook"
    vehicle_library_dir = "//server1/DV_Templates/Media_Templates/3D Vehicle Library/Vehicles"

    # --------------------------------------------------------------------------------------------------------------
    # Initializes variables, window, and UI elements
    # --------------------------------------------------------------------------------------------------------------
    def __init__(self, parent=maya_main_window()):
        super(MainUI, self).__init__(parent)

        # Set up the window
        # self.setWindowFlags(Qt.Tool)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.resize(250, -1)
        self.setWindowTitle(SCRIPT_NAME)
        self.setWindowIcon(QIcon(self.icon_dir + "/car.png"))
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self.create_controls()  # Initializes controls
        self.create_layout()  # Initializes the internal window layout
        self.make_connections()

        # If we have a last-opened file saved in preferences, automatically open that file. Otherwise, just open
        # a new, empty file
        # region Open Last File
        found_last_file_path = False
        if os.path.isfile(self.pref_path):  # If the prefs file exists
            with open(self.pref_path) as f:
                data = f.read().splitlines()  # Read the prefs file
                found_last_file_path = False
                for line in data:
                    if line.startswith(self.last_file_pref + "="):  # If we find the last-opened file line in prefs
                        last_file_path = line[len(self.last_file_pref) + 1:]  # Get the last-opened file path
                        # print(last_file_path)
                        if os.path.isfile(last_file_path):  # If the path we get exists
                            # print("found last file: " + last_file_path)
                            self.choose_spellbook_edit.setText(last_file_path)  # Open the last-opened file
                            found_last_file_path = True
                            break
                f.close()

        if not found_last_file_path:
            # print("no path in prefs")
            self.current_file = None
        pass  # I hate PyCharm
        # endregion

    def create_controls(self):
        UI_ELEMENT_HEIGHT = 30

        self.load_studio_button = QPushButton(QIcon(self.icon_dir + "/template.png"), "Load Arnold Studio")
        self.load_studio_button.setMinimumHeight(UI_ELEMENT_HEIGHT)

        self.choose_vehicle_edit = QLineEdit()
        self.choose_vehicle_edit.setPlaceholderText("Vehicle File")
        self.choose_vehicle_edit.setMinimumHeight(UI_ELEMENT_HEIGHT)

        self.choose_vehicle_button = QPushButton(QIcon(self.icon_dir + "/open.png"), "")
        self.choose_vehicle_button.setMinimumHeight(UI_ELEMENT_HEIGHT)

        self.load_vehicle_button = QPushButton(QIcon(self.icon_dir + "/load.png"), "Load Vehicle")
        self.load_vehicle_button.setMinimumHeight(UI_ELEMENT_HEIGHT)

        self.choose_spellbook_edit = QLineEdit()
        self.choose_spellbook_edit.setPlaceholderText("MagicShade Spellbook File")
        self.choose_spellbook_edit.setMinimumHeight(UI_ELEMENT_HEIGHT)

        self.choose_spellbook_button = QPushButton(QIcon(self.icon_dir + "/open.png"), "")
        self.choose_spellbook_button.setMinimumHeight(UI_ELEMENT_HEIGHT)

        self.apply_spellbook_button = QPushButton(QIcon(self.icon_dir + "/cast_all.png"), "Apply Spellbook")
        self.apply_spellbook_button.setMinimumHeight(UI_ELEMENT_HEIGHT)

        self.remove_license_plate_button = QPushButton(QIcon(self.icon_dir + "/license_plate.png"),
                                                       "Remove License Plates")
        self.remove_license_plate_button.setMinimumHeight(UI_ELEMENT_HEIGHT)

        self.make_windows_transparent_button = QPushButton(QIcon(self.icon_dir + "/window.png"),
                                                           "Make Windows Transparent")
        self.make_windows_transparent_button.setMinimumHeight(UI_ELEMENT_HEIGHT)

        self.save_button = QPushButton(QIcon(self.icon_dir + "/save_as.png"), "Save As...")
        self.save_button.setMinimumHeight(UI_ELEMENT_HEIGHT)

    def create_layout(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(3)
        main_layout.addWidget(self.load_studio_button)

        main_layout.insertSpacing(-1, 10)

        load_vehicle_layout = QHBoxLayout()
        load_vehicle_layout.addWidget(self.choose_vehicle_edit)
        load_vehicle_layout.addWidget(self.choose_vehicle_button)
        main_layout.addLayout(load_vehicle_layout)

        main_layout.insertSpacing(-1, 1)

        main_layout.addWidget(self.load_vehicle_button)

        main_layout.insertSpacing(-1, 10)

        choose_spellbook_layout = QHBoxLayout()
        choose_spellbook_layout.addWidget(self.choose_spellbook_edit)
        choose_spellbook_layout.addWidget(self.choose_spellbook_button)
        main_layout.addLayout(choose_spellbook_layout)

        main_layout.insertSpacing(-1, 1)

        main_layout.addWidget(self.apply_spellbook_button)

        main_layout.insertSpacing(-1, 10)

        tools_group = QGroupBox("Extra Tools")
        tools_layout = QVBoxLayout()
        tools_layout.addWidget(self.remove_license_plate_button)
        tools_layout.addWidget(self.make_windows_transparent_button)
        tools_group.setLayout(tools_layout)
        main_layout.addWidget(tools_group)

        main_layout.insertSpacing(-1, 10)

        main_layout.addWidget(self.save_button)

        self.setLayout(main_layout)

    def make_connections(self):
        self.load_studio_button.clicked.connect(self.load_studio)
        self.choose_vehicle_button.clicked.connect(self.choose_vehicle)
        self.load_vehicle_button.clicked.connect(self.load_vehicle)
        self.choose_spellbook_button.clicked.connect(self.choose_spellbook)
        self.apply_spellbook_button.clicked.connect(self.apply_spellbook)
        self.remove_license_plate_button.clicked.connect(self.remove_license_plate)
        self.make_windows_transparent_button.clicked.connect(self.make_windows_transparent)
        self.save_button.clicked.connect(self.save)

    def load_studio(self):
        cmds.file(new=True, force=True)
        cmds.file(self.arnold_studio_path, open=True)

    def choose_vehicle(self):
        file_path = QFileDialog.getOpenFileName(None, "", self.vehicle_library_dir,
                                                "Vehicles (*.mb *.obj *.fbx);;All Files (*.*)")[0]
        if file_path == "":  # If they cancel the dialog
            return  # Then just don't open anything
        self.choose_vehicle_edit.setText(file_path)

    def load_vehicle(self):
        vehicle_path = self.choose_vehicle_edit.text()
        if os.path.isfile(vehicle_path):
            cmds.select(allDagObjects=True)
            prev_all_objects = cmds.ls(selection=True)
            cmds.select(deselect=True)
            # print(str(prev_all_objects))

            cmds.file(vehicle_path, i=True)

            cmds.select(allDagObjects=True)
            new_all_objects = cmds.ls(selection=True)
            cmds.select(deselect=True)
            # print(str(new_all_objects))

            diff = [x for x in new_all_objects if x not in prev_all_objects]
            # print(str(diff))

            cmds.group(diff, name="Vehicle")

            cmds.scale(0.0328, 0.0328, 0.0328, absolute=True, pivot=(0, 0, 0))

            cmds.select(deselect=True)
        else:
            warning_box = QMessageBox(QMessageBox.Warning, "No Vehicle Found",
                                      "No vehicle file found at the specified path.")
            warning_box.exec_()

    def choose_spellbook(self):
        file_path = QFileDialog.getOpenFileName(None, "", self.spellbook_dir, "Spellbooks (*.spb)")[0]
        if file_path == "":
            return
        self.choose_spellbook_edit.setText(file_path)
        self.save_last_file(file_path)

    # --------------------------------------------------------------------------------------------------------------
    # Writes the current file path to preferences
    # --------------------------------------------------------------------------------------------------------------
    def save_last_file(self, last_file_path):
        line_found = False
        if os.path.isfile(self.pref_path):  # If the prefs file exists
            for line in fileinput.input(self.pref_path, inplace=True):
                if line.startswith(self.last_file_pref):
                    line_found = True
                    line = self.last_file_pref + "=" + last_file_path + "\n"
                sys.stdout.write(line)

        if not line_found:
            with open(self.pref_path, "a") as f:
                f.write(self.last_file_pref + "=%s\n" % last_file_path)
                f.close()

    def apply_spellbook(self):
        spellbook_path = self.choose_spellbook_edit.text()
        if os.path.isfile(spellbook_path):
            selection = cmds.ls(selection=True)
            cmds.select(deselect=True)
            with open(spellbook_path) as f:
                data = f.read().splitlines()
                for spell in data:
                    spell_split = spell.split(":")
                    original = spell_split[0]
                    replacement = spell_split[1]
                    spell_type = spell_split[2]

                    # print("Replacing " + original + " " + spell_type + " with " + replacement)
                    if spell_type == "Shader":
                        cmds.hyperShade(objects=original)
                    elif spell_type == "Object":
                        cmds.select(original, replace=True)
                    else:
                        raise ValueError(
                            "Spell type invalid. Should be one of the following: " + str(self.types_model.stringList()))
                    cmds.hyperShade(assign=replacement)
                    cmds.select(deselect=True)
            cmds.select(selection)
        else:
            warning_box = QMessageBox(QMessageBox.Warning, "No Spellbook Found",
                                      "No spellbook file (*.spb) found at the specified path.")
            warning_box.exec_()

    def remove_license_plate(self):
        cmds.delete("LicPlate*")

    def make_windows_transparent(self):
        selection = cmds.ls(selection=True)

        cmds.select(deselect=True)
        cmds.hyperShade(objects="*Window*")
        windows = cmds.ls(selection=True)
        cmds.select(deselect=True)

        for window in windows:
            cmds.setAttr(window + ".aiOpaque", False)

        cmds.select(selection)

    def save(self):
        filename, file_extension = os.path.splitext(self.choose_vehicle_edit.text())
        save_as_filename = QFileDialog.getSaveFileName(None, "", filename + "_Arnold", "Maya Binary (*.mb)")[0]
        if save_as_filename == "":
            return

        cmds.file(rename=save_as_filename)
        cmds.file(save=True, type="mayaBinary")


# Dev code to automatically close old windows when running
try:
    ui.close()
except:
    pass

# Show a new instance of the UI
ui = MainUI()
ui.show()
