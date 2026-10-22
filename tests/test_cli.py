import contextlib
import io
import unittest

from powatlas.cli import main


class CliTest(unittest.TestCase):
    def test_version_flag(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), self.assertRaises(SystemExit) as ctx:
            main(["--version"])
        self.assertEqual(ctx.exception.code, 0)
        self.assertEqual(out.getvalue().strip(), "powatlas 0.1.0")


if __name__ == "__main__":
    unittest.main()
