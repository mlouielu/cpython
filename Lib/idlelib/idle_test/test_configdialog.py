"""Test idlelib.configdialog.

Half the class creates dialog, half works with user customizations.
Coverage: 46% just by creating dialog, 56% with current tests.
"""
from idlelib.configdialog import ConfigDialog, idleConf  # test import
from test.support import requires
requires('gui')
import tkinter as tk
import unittest
import idlelib.config as config

# Tests should not depend on fortuitous user configurations.
# They must not affect actual user .cfg files.
# Use solution from test_config: empty parsers with no filename.
usercfg = idleConf.userCfg
testcfg = {
    'main': config.IdleUserConfParser(''),
    'highlight': config.IdleUserConfParser(''),
    'keys': config.IdleUserConfParser(''),
    'extensions': config.IdleUserConfParser(''),
}

# ConfigDialog.changed_items is a 3-level hierarchical dictionary of
# pending changes that mirrors the multilevel user config dict.
# For testing, record args in a list for comparison with expected.
changes = []
root = None
configure = None


class TestDialog(ConfigDialog):
    def add_changed_item(self, *args):
        changes.append(args)


def setUpModule():
    global root, configure
    idleConf.userCfg = testcfg
    root = tk.Tk()
    root.withdraw()
    configure = TestDialog(root, 'Test', _utest=True)


def tearDownModule():
    global root, configure
    idleConf.userCfg = testcfg
    configure.remove_var_callbacks()
    del configure
    root.update_idletasks()
    root.destroy()
    del root


class FontTabTest(unittest.TestCase):

    def setUp(self):
        changes.clear()

    def test_font(self):
        # Set values guaranteed not to be defaults.
        default_font = idleConf.GetFont(root, 'main', 'EditorWindow')
        default_size = str(default_font[1])
        default_bold = default_font[2] == 'bold'
        configure.font_name.set('Test Font')
        expected = [
            ('main', 'EditorWindow', 'font', 'Test Font'),
            ('main', 'EditorWindow', 'font-size', default_size),
            ('main', 'EditorWindow', 'font-bold', default_bold)]
        self.assertEqual(changes, expected)
        changes.clear()
        configure.font_size.set(20)
        expected = [
            ('main', 'EditorWindow', 'font', 'Test Font'),
            ('main', 'EditorWindow', 'font-size', '20'),
            ('main', 'EditorWindow', 'font-bold', default_bold)]
        self.assertEqual(changes, expected)
        changes.clear()
        configure.font_bold.set(not default_bold)
        expected = [
            ('main', 'EditorWindow', 'font', 'Test Font'),
            ('main', 'EditorWindow', 'font-size', '20'),
            ('main', 'EditorWindow', 'font-bold', not default_bold)]
        self.assertEqual(changes, expected)

    #def test_sample(self): pass  # TODO

    def test_tabspace(self):
        configure.space_num.set(6)
        self.assertEqual(changes, [('main', 'Indent', 'num-spaces', 6)])


class HighlightTest(unittest.TestCase):

    def setUp(self):
        changes.clear()

    #def test_colorchoose(self): pass  # TODO


class KeysTest(unittest.TestCase):

    def setUp(self):
        changes.clear()

    def test_load_keys_list(self):
        """load_keys_list should load specific keyset"""
        configure.load_keys_list('')
        current_list = configure.list_bindings.get(0, tk.END)
        configure.load_keys_list('IDLE Classic Windows')
        changed_list = configure.list_bindings.get(0, tk.END)
        self.assertNotEqual(current_list, changed_list)

    def test_load_keys_list_with_selection(self):
        """load_keys_list should restore the selection index after load"""
        index = 5
        configure.load_keys_list('')
        current_list = configure.list_bindings.get(0, tk.END)
        configure.list_bindings.select_set(index)
        configure.list_bindings.select_anchor(index)
        self.assertTrue(configure.list_bindings.selection_includes(index))

        configure.load_keys_list('IDLE Classic Windows')
        changed_list = configure.list_bindings.get(0, tk.END)
        self.assertNotEqual(current_list, changed_list)
        self.assertEqual(configure.list_bindings.index(tk.ANCHOR), index)
        self.assertTrue(configure.list_bindings.selection_includes(index))

    def test_changed_key_binding(self):
        keyset_name = 'monty'
        index = 0
        event = configure.list_bindings.get(index).split(' - ')[0]
        binding = '<Control-Alt-Shift-Key-U>'
        configure.create_new_key_set(keyset_name)
        configure.list_bindings.select_set(index)
        configure.list_bindings.select_anchor(index)

        configure.keybinding.set(binding)
        self.assertEqual(changes[-1],
                         ('keys', 'monty', event, binding))

    def test_create_new_keyset(self):
        """Test create_new_key_set will create a new keyset"""
        keyset_name = 'obov'
        configure.load_keys_list('')
        self.assertNotEqual(configure.custom_keys.get(), keyset_name)

        configure.create_new_key_set(keyset_name)
        configure.load_keys_list('obov')
        self.assertFalse(configure.are_keys_builtin.get())
        self.assertEqual(configure.custom_keys.get(), keyset_name)


class GeneralTest(unittest.TestCase):

    def setUp(self):
        changes.clear()

    def test_startup(self):
        configure.radio_startup_edit.invoke()
        self.assertEqual(changes,
                         [('main', 'General', 'editor-on-startup', 1)])

    def test_autosave(self):
        configure.radio_save_auto.invoke()
        self.assertEqual(changes, [('main', 'General', 'autosave', 1)])

    def test_editor_size(self):
        configure.entry_win_height.insert(0, '1')
        self.assertEqual(changes, [('main', 'EditorWindow', 'height', '140')])
        changes.clear()
        configure.entry_win_width.insert(0, '1')
        self.assertEqual(changes, [('main', 'EditorWindow', 'width', '180')])

    #def test_help_sources(self): pass  # TODO


if __name__ == '__main__':
    unittest.main(verbosity=2)
