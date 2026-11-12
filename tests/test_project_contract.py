import ast
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class RepositoryContractTests(unittest.TestCase):
    def test_expected_glue_scripts_exist(self):
        expected = [
            "spark.py",
            "de-youtube-reference-explode-job.py",
            "de-youtube-raw-to-cleansed-glue-job.py",
            "de-youtube-statistics-reference-data-job.py",
        ]
        for filename in expected:
            with self.subTest(filename=filename):
                self.assertTrue((ROOT / "src" / "glue" / filename).is_file())

    def test_glue_scripts_parse_as_python(self):
        for path in (ROOT / "src" / "glue").glob("*.py"):
            with self.subTest(path=path.name):
                ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

    def test_sensitive_and_generated_paths_are_ignored(self):
        ignore = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
        self.assertIn("data/", ignore)
        self.assertIn(".env", ignore)
        self.assertIn("*.pem", ignore)
        self.assertNotIn(" data/", ignore)

    def test_sql_validation_file_exists(self):
        self.assertTrue((ROOT / "sql" / "01_table_validation.sql").is_file())


if __name__ == "__main__":
    unittest.main()
