import unittest
from main import ShellEmulator, hostname

class TestShellEmulatorExit(unittest.TestCase):

    def setUp(self):
        self.emulator = ShellEmulator(hostname, "virtual_fs.zip") 
    
    def test_who(self):
        expected_output = self.emulator.hostname
        output = self.emulator.execute_command("who")  
        self.assertEqual(output, expected_output)

    def test_rev(self):
        output = self.emulator.execute_command("rev")
        self.assertEqual(output, "/")

    def test_exit(self):
        with self.assertRaises(SystemExit):
            self.emulator.execute_command("exit")

if __name__ == "__main__":
    unittest.main()
