import fileinput
import ntpath
import os
import sys

import maya.OpenMayaUI as mui
import maya.cmds as cmds
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from shiboken2 import wrapInstance

SCRIPT_NAME = "Magic Shade"


# ----------------------------------------------------------------------------------------------------------------------
# Returns an instance of Maya's main window
# ----------------------------------------------------------------------------------------------------------------------
def maya_main_window():
    main_window_ptr = mui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QWidget)


# ----------------------------------------------------------------------------------------------------------------------
# Class containing the plugin UI and all of its actions
# ----------------------------------------------------------------------------------------------------------------------
class MainUI(QMainWindow):
    # Set up file references
    icon_dir = os.path.expanduser("~/maya/scripts/magic-shade/resources/icons")
    spellbook_dir = os.path.expanduser("~/maya/scripts/magic-shade/spellbooks")
    pref_path = os.path.expanduser("~/maya/scripts/magic-shade/prefs")
    last_file_pref = "last_magicshade_spellbook"

    shader_list_model = QStringListModel(cmds.ls(materials=True))
    shader_list = cmds.ls(materials=True)
    object_list_model = QStringListModel(cmds.ls(geometry=True))
    object_list = cmds.ls(geometry=True)
    types_model = QStringListModel(["Shader", "Object"])

    # --------------------------------------------------------------------------------------------------------------
    # Property containing the current file being operated on. Automatically changes the window title
    # when the property is changed.
    # --------------------------------------------------------------------------------------------------------------
    # region current_file property
    @property
    def current_file(self):
        return self._current_file

    @current_file.setter
    def current_file(self, value):
        self._current_file = value
        if value is None:  # If we're setting the current file to None (i.e. creating a new file)
            file_display = "untitled"  # Set the window to "untitled"
        else:  # If we're setting the current file to an existing one
            file_display = ".../%s" % ntpath.basename(value)  # Set the window title to a shortened version of the path
        self.setWindowTitle("%s: %s" % (SCRIPT_NAME, file_display))  # Apply the new window title

    # endregion

    # --------------------------------------------------------------------------------------------------------------
    # Initializes variables, window, and UI elements
    # --------------------------------------------------------------------------------------------------------------
    def __init__(self, parent=maya_main_window()):
        super(MainUI, self).__init__(parent)

        self._current_file = None  # Initialize the current_file property

        # Set up the window
        # self.setWindowFlags(Qt.Tool)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.resize(500, 300)
        self.setWindowIcon(QIcon(self.icon_dir + "/magic.png"))

        self.create_menu()  # Initialize menu
        self.create_toolbar()  # Initialize toolbar
        self.create_controls()  # Initializes controls
        self.create_layout()  # Initializes the internal window layout

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
                        print(last_file_path)
                        if os.path.isfile(last_file_path):  # If the path we get exists
                            f.close()
                            print("found last file: " + last_file_path)
                            self.open_spellbook_from_file(last_file_path)  # Open the last-opened file
                            found_last_file_path = True
                            break
                f.close()

        if not found_last_file_path:
            print("no path in prefs")
            self.current_file = None
        pass  # I hate PyCharm
        # endregion

    # --------------------------------------------------------------------------------------------------------------
    # Initializes menu
    # --------------------------------------------------------------------------------------------------------------
    def create_menu(self):
        self.menu_bar = self.menuBar()  # Create the menu bar

        # Create the file menu
        # region File Menu
        # Create the "New Spellbook" action
        new_spellbook_action = QAction("&New Spellbook", self)
        new_spellbook_action.setShortcut("Ctrl+N")
        new_spellbook_action.setStatusTip("Create new spellbook")
        new_spellbook_action.triggered.connect(self.new_spellbook)  # Connect the action to its method

        # Create the "Open Spellbook" action
        open_spellbook_action = QAction("&Open Spellbook...", self)
        open_spellbook_action.setShortcut("Ctrl+O")
        open_spellbook_action.setStatusTip("Open existing spellbook")
        open_spellbook_action.triggered.connect(self.open_spellbook)  # Connect action

        # Create the "Save Spellbook" action
        save_spellbook_action = QAction("&Save Spellbook", self)
        save_spellbook_action.setShortcut("Ctrl+S")
        save_spellbook_action.setStatusTip("Save current spellbook")
        save_spellbook_action.triggered.connect(self.save_spellbook)  # Connect action

        # Create the "Save Spellbook As" action
        save_spellbook_as_action = QAction("Save Spellbook As...", self)
        save_spellbook_as_action.setShortcut("Ctrl+Shift+S")
        save_spellbook_as_action.setStatusTip("Save current spellbook under a new name")
        save_spellbook_as_action.triggered.connect(self.save_spellbook_as)  # Connect action

        # Create the "Refresh Shaders" action
        refresh_shaders_action = QAction("&Refresh Shaders", self)
        refresh_shaders_action.setShortcut("Ctrl+R")
        refresh_shaders_action.setStatusTip("Refresh shader lists")
        refresh_shaders_action.triggered.connect(self.refresh_models)  # Connect action

        # Create the "Exit" action
        exit_action = QAction("&Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Exit application")
        exit_action.triggered.connect(self.close)  # Connect action

        file_menu = self.menu_bar.addMenu("&File")  # Add the file menu to the menu bar
        file_menu.addAction(new_spellbook_action)  # Add the "New Spellbook" action to the file menu
        file_menu.addAction(open_spellbook_action)  # Add the "Open Spellbook" action to the file menu
        file_menu.addAction(save_spellbook_action)  # Add the "Save Spellbook" action to the file menu
        file_menu.addAction(save_spellbook_as_action)  # Add the "Save Spellbook As" action to the file menu
        file_menu.addSeparator()  # Add a visual separator to the file menu
        file_menu.addAction(refresh_shaders_action)  # Add the "Refresh Shaders" action to the file menu
        file_menu.addSeparator()  # Add a visual separator
        file_menu.addAction(exit_action)  # Add the "Exit" action to the file menu
        # endregion

        # Create the edit menu
        # region Edit Menu
        # Create the "New Spell" action
        new_spell_action = QAction("New S&pell", self)
        new_spell_action.setShortcut("Ctrl+P")
        new_spell_action.setStatusTip("Create new spell (shader replacement)")
        new_spell_action.triggered.connect(self.new_spell)  # Connect the action to its method

        # Create the "Delete Spell(s)" action
        delete_spell_action = QAction("&Delete Spell(s)", self)
        delete_spell_action.setShortcut("Delete")
        delete_spell_action.setStatusTip("Delete selected spell(s)")
        delete_spell_action.triggered.connect(self.delete_spell)  # Connect action

        # Create the "Move Spell(s) Up" action
        move_spell_up_action = QAction("Move Spell(s) Up", self)
        move_spell_up_action.setShortcut("PgUp")
        move_spell_up_action.setStatusTip("Move selected spell(s) up")
        move_spell_up_action.triggered.connect(self.move_up)  # Connect action

        # Create the "Move Spell(s) Down" action
        move_spell_down_action = QAction("Move Spell(s) Down", self)
        move_spell_down_action.setShortcut("PgDown")
        move_spell_down_action.setStatusTip("Move selected spell(s) down")
        move_spell_down_action.triggered.connect(self.move_down)  # Connect action

        edit_menu = self.menu_bar.addMenu("&Edit")  # Add the edit menu to the menu bar
        edit_menu.addAction(new_spell_action)  # Add the "New Spell" action to the edit menu
        edit_menu.addAction(delete_spell_action)  # Add the "Delete Spell(s)" action to the edit menu
        edit_menu.addSeparator()  # Add a visual separator to the edit menu
        edit_menu.addAction(move_spell_up_action)  # Add the "Move Spell(s) Up" action to the edit menu
        edit_menu.addAction(move_spell_down_action)  # Add the "Move Spell(s) Down" action to the edit menu
        # endregion

        # Create the cast menu
        # region Cast Menu
        # Create the "Cast Selected Spell(s)" action
        cast_spells_action = QAction("Cast Selected Spell(s)", self)
        cast_spells_action.setShortcut("Ctrl+C")
        cast_spells_action.setStatusTip("Cast selected spells")
        cast_spells_action.triggered.connect(self.cast_spells)  # Connect the action to its method

        # Create the "Cast All Spells" action
        cast_all_spells_action = QAction("&Cast All Spells", self)
        cast_all_spells_action.setShortcut("Ctrl+Shift+C")
        cast_all_spells_action.setStatusTip("Cast all spells")
        cast_all_spells_action.triggered.connect(self.cast_all_spells)  # Connect action

        cast_menu = self.menu_bar.addMenu("&Cast")  # Add the cast menu to the menu bar
        cast_menu.addAction(cast_spells_action)  # Add the "Cast Selected Spell(s)" action to the cast menu
        cast_menu.addAction(cast_all_spells_action)  # Add the "Cast All Spells" action to the cast menu
        # endregion

    # --------------------------------------------------------------------------------------------------------------
    # Initializes toolbar
    # --------------------------------------------------------------------------------------------------------------
    def create_toolbar(self):
        # Create the file toolbar
        # region File Toolbar
        # Create the "New Spellbook" action
        new_spellbook_action = QAction(QIcon(self.icon_dir + "/new.png"), "New Spellbook", self)
        new_spellbook_action.triggered.connect(self.new_spellbook)  # Connect the action to its method

        # Create the "Open Spellbook" action
        open_spellbook_action = QAction(QIcon(self.icon_dir + "/open.png"), "Open Spellbook", self)
        open_spellbook_action.triggered.connect(self.open_spellbook)  # Connect action

        # Create the "Save Spellbook" action
        save_spellbook_action = QAction(QIcon(self.icon_dir + "/save.png"), "Save Spellbook", self)
        save_spellbook_action.triggered.connect(self.save_spellbook)  # Connect action

        self.file_toolbar = self.addToolBar("File")  # Create the file toolbar
        self.file_toolbar.addAction(new_spellbook_action)  # Add the "New Spellbook" action to the file toolbar
        self.file_toolbar.addAction(open_spellbook_action)  # Add the "Open Spellbook" action to the file toolbar
        self.file_toolbar.addAction(save_spellbook_action)  # Add the "Save Spellbook" action to the file toolbar
        # endregion

        # Create the edit toolbar
        # region Edit Toolbar
        # Create the "New Spell" action
        new_spell_action = QAction(QIcon(self.icon_dir + "/plus.png"), "New Spell", self)
        new_spell_action.triggered.connect(self.new_spell)  # Connect the action to its method

        # Create the "Delete Spell(s)" action
        delete_spell_action = QAction(QIcon(self.icon_dir + "/minus.png"), "Delete Selected Spell(s)", self)
        delete_spell_action.triggered.connect(self.delete_spell)  # Connect action

        # Create the "Move Spell(s) Up" action
        move_spell_up_action = QAction(QIcon(self.icon_dir + "/up.png"), "Move Spell(s) Up", self)
        move_spell_up_action.triggered.connect(self.move_up)  # Connect action

        # Create the "Move Spell(s) Down" action
        move_spell_down_action = QAction(QIcon(self.icon_dir + "/down.png"), "Move Spell(s) Down", self)
        move_spell_down_action.triggered.connect(self.move_down)  # Connect action

        self.edit_toolbar = QToolBar("Edit")  # Create the edit toolbar
        self.addToolBar(Qt.RightToolBarArea, self.edit_toolbar)  # Add the edit toolbar to the right side of the window
        self.edit_toolbar.addAction(new_spell_action)  # Add the "New Spell" action to the edit toolbar
        self.edit_toolbar.addAction(delete_spell_action)  # Add the "Delete Spell(s)" action to the edit toolbar
        self.edit_toolbar.addAction(move_spell_up_action)  # Add the "Move Spell(s) Up" action to the edit toolbar
        self.edit_toolbar.addAction(move_spell_down_action)  # Add the "Move Spell(s) Down" action to the edit toolbar
        # endregion

        # Create the cast toolbar
        # region Cast Toolbar
        # Create the "Cast Selected Spell(s)" action
        cast_spells_action = QAction(QIcon(self.icon_dir + "/cast.png"), "Cast Selected Spell(s)", self)
        cast_spells_action.triggered.connect(self.cast_spells)  # Connect the action to its method

        # Create the "Cast All Spells" action
        cast_all_spells_action = QAction(QIcon(self.icon_dir + "/cast_all.png"), "Cast All Spells", self)
        cast_all_spells_action.triggered.connect(self.cast_all_spells)  # Connect action

        self.cast_toolbar = self.addToolBar("Cast")  # Add the cast menu to the toolbar
        self.cast_toolbar.addAction(cast_spells_action)  # Add the "Cast Selected Spell(s)" action to the cast toolbar
        self.cast_toolbar.addAction(cast_all_spells_action)  # Add the "Cast All Spells" action to the cast toolbar
        # endregion

    # --------------------------------------------------------------------------------------------------------------
    # Initializes controls
    # --------------------------------------------------------------------------------------------------------------
    def create_controls(self):
        self.spell_table = QTableWidget()  # Create the spell table
        self.spell_table.setColumnCount(3)  # Set table to 2 columns
        self.spell_table.setHorizontalHeaderLabels(["Original", "Replacement", "Type"])  # Set the column headers
        self.spell_table.setShowGrid(False)  # Don't show visual grid lines
        self.spell_table.setSelectionBehavior(QAbstractItemView.SelectRows)  # Make only rows selectable
        self.spell_table.setColumnWidth(0, 175)  # Set pixel width of column 1
        self.spell_table.setColumnWidth(1, 175)  # Set pixel width of column 2
        self.spell_table.setColumnWidth(2, 75)  # Set pixel width of column 3
        self.spell_table.verticalHeader().setSectionsMovable(True)  # Allow rows to be moved around
        self.spell_table.verticalHeader().setDragEnabled(True)  # Allow the user to drag rows around
        self.spell_table.verticalHeader().setDragDropMode(QAbstractItemView.InternalMove)  # Allow internal dragging

    # --------------------------------------------------------------------------------------------------------------
    # Initializes the internal window layout
    # --------------------------------------------------------------------------------------------------------------
    def create_layout(self):
        main_layout = QVBoxLayout()  # Create the main vertical layout
        main_layout.addWidget(self.menu_bar)  # Add menu bar at top
        main_layout.addWidget(self.spell_table)  # Add spell table under menu bar
        self.setCentralWidget(self.spell_table)  # Make the spell table the main widget so the toolbar will surround it

        self.setLayout(main_layout)  # Set the window layout to the main vertical layout

    # --------------------------------------------------------------------------------------------------------------
    # Clears the spell table
    # --------------------------------------------------------------------------------------------------------------
    def new_spellbook(self):
        print("New spellbook")
        self.spell_table.setRowCount(0)  # Clear the spell table
        self.current_file = None  # Set the current file to none (displays "untitled" in the window title)
        self.reset_shaders()  # Reset the shader list to only existing shaders

    # --------------------------------------------------------------------------------------------------------------
    # Opens a spellbook file based on user input and populates the spell table
    # --------------------------------------------------------------------------------------------------------------
    def open_spellbook(self):
        print("Open spellbook")
        # Ask the user for the file they want to open
        file_path = QFileDialog.getOpenFileName(None, "", self.spellbook_dir, "Spellbooks (*.spb)")[0]
        if file_path == "":  # If they cancel the dialog
            return  # Then just don't open anything

        self.open_spellbook_from_file(file_path)  # Otherwise, open the file the user chose

    # --------------------------------------------------------------------------------------------------------------
    # Opens a spellbook file and populates the spell table
    # --------------------------------------------------------------------------------------------------------------
    def open_spellbook_from_file(self, path):
        self.spell_table.setRowCount(0)  # Clear the current spell table
        self.reset_shaders()  # Reset the shader list to existing shaders

        with open(path) as f:
            data = f.read().splitlines()
            for spell in data:
                spell_split = spell.split(":")
                self.add_spell(spell_split[0], spell_split[1], spell_split[2])

        self.current_file = path
        self.save_last_file(path)

    # --------------------------------------------------------------------------------------------------------------
    # Saves the current spellbook to a file based on user input
    # --------------------------------------------------------------------------------------------------------------
    def save_spellbook(self):
        print("Save spellbook")
        if self.current_file is None:
            self.save_spellbook_as()
        else:
            self.save_spellbook_to_file(self.current_file)

    # --------------------------------------------------------------------------------------------------------------
    # Saves the current spellbook to a new file based on user input
    # --------------------------------------------------------------------------------------------------------------
    def save_spellbook_as(self):
        print("Save spellbook as")
        file_path = QFileDialog.getSaveFileName(None, "", self.spellbook_dir, "Spellbooks (*.spb)")[0]
        if file_path == "":
            return

        self.save_spellbook_to_file(file_path)

    # --------------------------------------------------------------------------------------------------------------
    # Saves the current spellbook to a file
    # --------------------------------------------------------------------------------------------------------------
    def save_spellbook_to_file(self, path):
        with open(path, "w") as f:
            for row in self.sort_visually(range(0, self.spell_table.rowCount())):
                original = self.spell_table.cellWidget(row, 0).currentText().replace(":", "_")
                replacement = self.spell_table.cellWidget(row, 1).currentText().replace(":", "_")
                spell_type = self.spell_table.cellWidget(row, 2).currentText()
                f.write("%s:%s:%s\n" % (original, replacement, spell_type))
            f.close()
        self.current_file = path
        self.save_last_file(path)

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

    # --------------------------------------------------------------------------------------------------------------
    # Refreshes the combo box models
    # --------------------------------------------------------------------------------------------------------------
    def refresh_models(self):
        rows = self.sort_visually(range(0, self.spell_table.rowCount()))
        current_selections = [[] for i in rows]

        for row in rows:
            current_selections[row] = [self.spell_table.cellWidget(row, 0).currentText(),
                                       self.spell_table.cellWidget(row, 1).currentText(),
                                       self.spell_table.cellWidget(row, 2).currentText()]

        old_shader_list = self.shader_list_model.stringList()
        shader_diff = [x for x in old_shader_list if x not in self.shader_list]
        old_object_list = self.object_list_model.stringList()
        object_diff = [x for x in old_object_list if x not in self.object_list]

        maya_materials_ls = cmds.ls(materials=True)
        new_shader_list = maya_materials_ls + shader_diff
        self.shader_list_model.setStringList(new_shader_list)
        self.shader_list = maya_materials_ls

        maya_objects_ls = cmds.ls(geometry=True)
        new_object_list = maya_objects_ls + object_diff
        self.object_list_model.setStringList(new_object_list)
        self.object_list = new_object_list

        for index, row in enumerate(current_selections):
            original_combo = self.spell_table.cellWidget(index, 0)
            original_combo.setCurrentIndex(original_combo.findText(row[0]))

            replacement_combo = self.spell_table.cellWidget(index, 1)
            replacement_combo.setCurrentIndex(replacement_combo.findText(row[1]))

    # --------------------------------------------------------------------------------------------------------------
    # Resets the list of shaders shown in internal combo boxes to only existing shaders
    # --------------------------------------------------------------------------------------------------------------
    def reset_shaders(self):
        maya_materials_ls = cmds.ls(materials=True)
        self.shader_list_model.setStringList(maya_materials_ls)
        self.shader_list = maya_materials_ls

    def new_spell(self):
        print("New spell")
        self.add_spell()

    def add_spell(self, original=None, replacement=None, spell_type=None):
        row_num = self.spell_table.rowCount()
        self.spell_table.insertRow(row_num)

        original_combo = QComboBox()
        if spell_type is None:
            original_combo.setModel(self.shader_list_model)
        else:
            if spell_type == "Object":
                original_combo.setModel(self.object_list_model)
            else:
                original_combo.setModel(self.shader_list_model)
        original_combo.setEditable(True)
        if original is not None:
            if original not in original_combo.model().stringList():
                original_combo.addItem(original)
            original_combo.setCurrentIndex(original_combo.findText(original))
        self.spell_table.setCellWidget(row_num, 0, original_combo)

        replacement_combo = QComboBox()
        replacement_combo.setModel(self.shader_list_model)
        replacement_combo.setEditable(True)
        if replacement is not None:
            if replacement not in replacement_combo.model().stringList():
                replacement_combo.addItem(replacement)
            replacement_combo.setCurrentIndex(replacement_combo.findText(replacement))
        self.spell_table.setCellWidget(row_num, 1, replacement_combo)

        type_combo = QComboBox()
        type_combo.setModel(self.types_model)
        if spell_type is not None:
            type_combo.setCurrentIndex(type_combo.findText(spell_type))
        type_combo.currentTextChanged.connect(lambda: self.change_type(original_combo, type_combo.currentText()))
        self.spell_table.setCellWidget(row_num, 2, type_combo)

    def change_type(self, original_combo, value):
        print(str(original_combo) + "," + str(value))
        curr_text = original_combo.currentText()
        if curr_text != value:
            if value == "Shader":
                original_combo.setModel(self.shader_list_model)
            elif value == "Object":
                original_combo.setModel(self.object_list_model)

    # --------------------------------------------------------------------------------------------------------------
    # Removes selected spells from the spell table
    # --------------------------------------------------------------------------------------------------------------
    def delete_spell(self):
        print("Delete selected spell(s)")
        for row in reversed(self.get_selected()):
            self.spell_table.removeRow(row)

    # --------------------------------------------------------------------------------------------------------------
    # Moves selected spells up the spell table
    # --------------------------------------------------------------------------------------------------------------
    def move_up(self):
        print("Move spell(s) up")
        for row in self.get_selected():
            vertical_header = self.spell_table.verticalHeader()
            visual_row = self.spell_table.visualRow(row)
            vertical_header.swapSections(visual_row, visual_row - 1)

    # --------------------------------------------------------------------------------------------------------------
    # Moves selected spells down the spell table
    # --------------------------------------------------------------------------------------------------------------
    def move_down(self):
        print("Move spell(s) down")
        for row in reversed(self.get_selected()):
            vertical_header = self.spell_table.verticalHeader()
            visual_row = self.spell_table.visualRow(row)
            vertical_header.swapSections(visual_row, visual_row + 1)

    # --------------------------------------------------------------------------------------------------------------
    # Applies selected spell replacements
    # --------------------------------------------------------------------------------------------------------------
    def cast_spells(self):
        print("Cast selected spell(s)")
        self.cast_spells_from_rows(self.get_selected())

    # --------------------------------------------------------------------------------------------------------------
    # Applies all spell replacements
    # --------------------------------------------------------------------------------------------------------------
    def cast_all_spells(self):
        print("Cast all spells")
        sorted_rows = self.sort_visually(range(0, self.spell_table.rowCount()))
        print(sorted_rows)
        self.cast_spells_from_rows(sorted_rows)

    # --------------------------------------------------------------------------------------------------------------
    # Applies spell replacements from rows
    # --------------------------------------------------------------------------------------------------------------
    def cast_spells_from_rows(self, rows):
        selection = cmds.ls(selection=True)
        cmds.select(deselect=True)
        for row in rows:
            original = self.spell_table.cellWidget(row, 0).currentText()
            replacement = self.spell_table.cellWidget(row, 1).currentText()
            spell_type = self.spell_table.cellWidget(row, 2).currentText()
            print("Replacing " + original + " " + spell_type + " with " + replacement)
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

    # --------------------------------------------------------------------------------------------------------------
    # Returns a list of selected rows in the spell table
    # --------------------------------------------------------------------------------------------------------------
    def get_selected(self):
        selected_rows = self.spell_table.selectionModel().selectedRows()
        rows = [selected_row.row() for selected_row in selected_rows]
        sorted_rows = self.sort_visually(rows)
        print(sorted_rows)
        return sorted_rows

    # --------------------------------------------------------------------------------------------------------------
    # Sorts a list of logical columns visually and returns the sorted lsit
    # --------------------------------------------------------------------------------------------------------------
    def sort_visually(self, rows):
        visual_rows = []
        for row in rows:
            visual_rows.append(self.spell_table.visualRow(row))
        visual_rows.sort()
        sorted_rows = []
        for visual_row in visual_rows:
            sorted_rows.append(self.spell_table.verticalHeader().logicalIndex(visual_row))
        return sorted_rows


# Dev code to automatically close old windows when running
try:
    ui.close()
except:
    pass

# Show a new instance of the UI
ui = MainUI()
ui.show()
