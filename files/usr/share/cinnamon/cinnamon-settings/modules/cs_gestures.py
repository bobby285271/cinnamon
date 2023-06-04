#!/usr/bin/python3

import subprocess
from functools import cmp_to_key
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gio, Gtk

from SettingsWidgets import SidePage, SettingsWidget
from xapp.GSettingsWidgets import *

SCHEMA = "org.cinnamon.gestures";
NON_GESTURE_KEYS = [
    "swipe-percent-threshold",
    "pinch-percent-threshold"
]

class Module:
    name = "gestures"
    category = "prefs"
    comment = _("Manage touch gestures")

    def __init__(self, content_box):
        keywords = _("gesture, swipe, pinch, touch")
        sidePage = SidePage(_("Gestures"), "cs-gestures", keywords, content_box, 560, module=self)
        self.sidePage = sidePage

    def on_module_selected(self):
        if not self.loaded:
            print("Loading Gestures module")

            have_touchpad = False
            have_touchscreen =  False

            # Detect devices.
            out = subprocess.getoutput("csd-input-helper").replace("\t", " ").split("\n")[:4]
            for line in out:
                if "touchpad" in line and line.endswith("yes"):
                    have_touchpad = True
                if "touchscreen" in line and line.endswith("yes"):
                    have_touchscreen = True

            page = SettingsPage()
            have_touchpad = True
            if not have_touchpad and not have_touchscreen:
                self.sidePage.add_widget(page)
                image = Gtk.Image(icon_name="touch-disabled-symbolic", icon_size=Gtk.IconSize.DIALOG)
                page.pack_start(image, False,False, 0)
                label = Gtk.Label(label=_("<big><b>No compatible devices found</b></big>"), expand=True, use_markup=True)
                page.pack_start(label, True, True, 0)
                return

            self.gesture_settings = Gio.Settings(schema_id=SCHEMA)
            ssource = Gio.SettingsSchemaSource.get_default();
            schema = ssource.lookup(SCHEMA, True);
            all_keys = schema.list_keys();

            order = [ "left", "right", "up", "down", "in", "out" ]

            def sort_by_direction(key1, key2):
                v1 = 0
                v2 = 0
                for i in range(0, len(order)):
                    if order[i] in key1:
                        v1 = i
                    if order[i] in key2:
                        v2 = i

                if v1 < v2: return -1
                if v1 > v2: return 1
                return 0

            keys = sorted([key for key in all_keys if key not in NON_GESTURE_KEYS], key=cmp_to_key(sort_by_direction))

            self.sidePage.stack = SettingsStack()
            self.sidePage.add_widget(self.sidePage.stack)
            self.sidePage.stack.add_titled(page, "main", _("Gestures"))

            size_group = Gtk.SizeGroup.new(Gtk.SizeGroupMode.HORIZONTAL)

            actions = [
                ["", _("Disabled")],
                ["WORKSPACE_NEXT", _("Switch to the next workspace")],
                ["WORKSPACE_PREVIOUS", _("Switch to the previous workspace")],
                # ["WORKSPACE_UP", _("Switch to the workspace above")],
                # ["WORKSPACE_DOWN", _("Switch to the workspace below")],
                ["TOGGLE_EXPO", _("Show the workspace selection screen")],
                ["TOGGLE_OVERVIEW", _("Show the window selection screen")],
                ["WORKSPACE_UP", _("Switch to the workspace above")],
                ["WORKSPACE_UP", _("Switch to the workspace above")],
                ["WORKSPACE_UP", _("Switch to the workspace above")],
                ["WORKSPACE_UP", _("Switch to the workspace above")],
                ["MINIMIZE", _("Minimize window")],
                ["MAXIMIZE", _("Maximize window")],
                ["CLOSE", _("Close window")],
                ["FULLSCREEN", _("Make window fullscreen")],
                ["UNFULLSCREEN", _("Exit window fullscreen")],
                ["PUSH_TILE_UP", _("Push tile up")],
                ["PUSH_TILE_DOWN", _("Push tile down")],
                ["PUSH_TILE_LEFT", _("Push tile left")],
                ["PUSH_TILE_RIGHT", _("Push tile right")],
                ["TOGGLE_DESKTOP", _("Show desktop")],
                ["EXEC", _("Execute a command")]
            ]

            section = page.add_section(_("Swipe with 3 fingers"))

            for key in keys:
                label = self.get_key_label(key, "swipe", 3)
                if not label:
                    continue

                widget = GestureComboBox(label, self.gesture_settings, key, actions, size_group=size_group)
                section.add_row(widget)

            section = page.add_section(_("Swipe with 4 fingers"))

            for key in keys:
                label = self.get_key_label(key, "swipe", 4)
                if not label:
                    continue

                widget = GestureComboBox(label, self.gesture_settings, key, actions, size_group=size_group)
                section.add_row(widget)

            for fingers in range(2, 5):
                section = page.add_section(_("Pinch with %d fingers") % fingers)

                for key in keys:
                    label = self.get_key_label(key, "pinch", fingers)

                    if not label:
                        continue

                    widget = GestureComboBox(label, self.gesture_settings, key, actions, size_group=size_group)
                    section.add_row(widget)

            if have_touchscreen:
                page = SettingsPage()
                self.sidePage.stack.add_titled(page, "touchscreen", _("Touchscreen only"))

                size_group = Gtk.SizeGroup.new(Gtk.SizeGroupMode.HORIZONTAL)

                section = page.add_section(_("Swipe with 2 fingers"))

                for key in keys:
                    label = self.get_key_label(key, "swipe", 2)
                    if not label:
                        continue

                    widget = GestureComboBox(label, self.gesture_settings, key, actions, size_group=size_group)
                    section.add_row(widget)

                section = page.add_section(_("Swipe with 5 fingers"))

                for key in keys:
                    label = self.get_key_label(key, "swipe", 5)
                    if not label:
                        continue

                    widget = GestureComboBox(label, self.gesture_settings, key, actions, size_group=size_group)
                    section.add_row(widget)

                section = page.add_section(_("Pinch with 5 fingers"))

                for key in keys:
                    label = self.get_key_label(key, "pinch", 5)

                    if not label:
                        continue

                    widget = GestureComboBox(label, self.gesture_settings, key, actions, size_group=size_group)
                    section.add_row(widget)

                section = page.add_section(_("Tapping"))

                for fingers in range(2, 6):
                    for key in keys:
                        label = self.get_key_label(key, "tap", fingers)

                        if not label:
                            continue

                        widget = GestureComboBox(label, self.gesture_settings, key, actions, size_group=size_group)
                        section.add_row(widget)

            page = SettingsPage()
            self.sidePage.stack.add_titled(page, "tweaks", _("Tweaks"))

            size_group = Gtk.SizeGroup.new(Gtk.SizeGroupMode.HORIZONTAL)

            section = page.add_section(_("Trigger distances"),
                                       _("These values are the approximate length of the gesture (as a percentage of the touchpad or screen size) before "
                                         "the action will register."))

            widget = GSettingsRange(_("Swipe threshold"), "org.cinnamon.gestures", "swipe-percent-threshold", _("20%"), _("80%"), 20, 80, step=5, show_value=True)
            widget.add_mark(60, Gtk.PositionType.TOP, None)
            section.add_row(widget)
            widget = GSettingsRange(_("Pinch threshold"), "org.cinnamon.gestures", "pinch-percent-threshold", _("20%"), _("80%"), 20, 80, step=5, show_value=True)
            widget.add_mark(40, Gtk.PositionType.TOP, None)
            section.add_row(widget)


    def get_key_label(self, key, gtype, fingers):
        parts = key.split("-")
        if gtype != parts[0]:
            return None

        if gtype == "swipe":
            if int(parts[2]) != fingers:
                return None
            direction = parts[1]
            if direction == "left": return _("Left")
            elif direction == "right": return _("Right")
            elif direction == "up": return _("Up")
            elif direction == "down": return _("Down")
        elif gtype == "pinch":
            if int(parts[2]) != fingers:
                return None
            direction = parts[1]
            if direction == "in": return _("In")
            elif direction == "out": return _("Out")
        elif gtype == "tap":
            if int(parts[1]) != fingers:
                return
            return _("Tap with %d fingers") % fingers

        return None

class GestureComboBox(SettingsWidget):
    def __init__(self, label, settings=None, key=None, options=[], size_group=None):
        super(GestureComboBox, self).__init__()

        self.option_map = {}

        self.settings = settings
        self.key = key

        self.label = SettingsLabel(label)

        self.content_widget = Gtk.ComboBox()
        renderer_text = Gtk.CellRendererText()

        self.custom_entry = Gtk.Entry(placeholder_text=_("Enter a custom command"), no_show_all=True)
        self.content_widget.pack_start(renderer_text, True)
        self.content_widget.add_attribute(renderer_text, "text", 1)

        self.pack_start(self.label, False, False, 0)
        self.pack_end(self.content_widget, False, False, 0)
        self.content_widget.set_valign(Gtk.Align.CENTER)
        self.pack_end(self.custom_entry, True, True, 0)

        self.set_options(options)

        self.settings.connect("changed::" + key, self.on_setting_changed)
        self.on_setting_changed(settings, key)
        self.content_widget.connect("changed", self.on_my_value_changed)
        self.custom_entry.connect("changed", self.on_custom_entry_changed)

        if size_group:
            self.add_to_size_group(size_group)

    def on_my_value_changed(self, widget):
        tree_iter = widget.get_active_iter()
        if tree_iter != None:
            self.value = self.model[tree_iter][0]

            if self.value not in list(self.option_map.keys())[0:-1]:
                self.custom_entry.show()
                self.settings.set_string(self.key, "EXEC:" + self.custom_entry.get_text())
            else:
                self.custom_entry.hide()
                self.settings.set_string(self.key, self.value)

    def on_custom_entry_changed(self, entry):
        if self.updating_from_setting:
            return
        self.settings.set_string(self.key, "EXEC:" + entry.get_text())

    def on_setting_changed(self, settings, key):
        self.updating_from_setting  = True

        self.value = settings.get_string(key)
        try:
            self.content_widget.set_active_iter(self.option_map[self.value])
            self.custom_entry.hide()
        except:
            self.content_widget.set_active_iter(self.option_map["EXEC"])
            self.custom_entry.show()
            self.custom_entry.set_text(self.value.replace("EXEC:", ""))

        self.updating_from_setting  = False

    def set_options(self, options):
        self.model = Gtk.ListStore(str, str)

        for option in options:
            self.option_map[option[0]] = self.model.append([option[0], option[1]])

        self.content_widget.set_model(self.model)
        self.content_widget.set_id_column(0)