import ast
import json
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
            "youtube-tutorial-staging-validation.py",
            "youtube-pipeline-staging-v1.py",
            "youtube-pipeline-curation-v1.py",
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

    def test_state_machine_contract(self):
        definition = json.loads((ROOT / "orchestration" / "youtube-trending-state-machine.asl.json").read_text(encoding="utf-8"))
        states = definition["States"]
        self.assertEqual(definition["StartAt"], "AssignRunId")
        self.assertIn("States.UUID()", states["AssignRunId"]["Parameters"]["run_id.$"])
        self.assertEqual(states["StageRawCSVs"]["Parameters"]["JobName"], "youtube-pipeline-staging-v1")
        self.assertEqual(states["CurateAndQuarantine"]["Parameters"]["JobName"], "youtube-pipeline-curation-v1")
        self.assertIn("StartStagingCrawler", states)
        self.assertIn("StartSafeCrawler", states)
        self.assertIn("StartQuarantineCrawler", states)
        self.assertEqual(states["StagingCrawlerFailed"]["Type"], "Fail")
        self.assertEqual(states["SafeCrawlerFailed"]["Type"], "Fail")
        self.assertEqual(states["QuarantineCrawlerFailed"]["Type"], "Fail")
        self.assertEqual(definition["TimeoutSeconds"], 7200)

    def test_pipeline_jobs_are_run_isolated(self):
        staging = (ROOT / "src" / "glue" / "youtube-pipeline-staging-v1.py").read_text(encoding="utf-8")
        curation = (ROOT / "src" / "glue" / "youtube-pipeline-curation-v1.py").read_text(encoding="utf-8")
        self.assertIn("partitionBy(\"run_id\", \"region\")", staging)
        self.assertIn("mode(\"append\")", staging)
        self.assertIn("list_objects_v2", staging)
        self.assertIn("push_down_predicate", curation)
        self.assertIn("conflicting_business_key", curation)
        self.assertIn("mode(\"append\")", curation)
        self.assertIn("list_objects_v2", curation)

    def test_dashboard_exists(self):
        dashboard = ROOT / "docs" / "dashboard" / "index.html"
        self.assertTrue(dashboard.is_file())
        self.assertIn("Static query snapshot", dashboard.read_text(encoding="utf-8"))

    def test_dashboard_refresh_contract(self):
        refresh_script = ROOT / "scripts" / "refresh_dashboard.py"
        active_workflow = ROOT / ".github" / "workflows" / "refresh-dashboard-data.yml"
        archived_workflow = ROOT / "docs" / "disabled-workflows" / "refresh-dashboard-data.yml.disabled"
        dashboard_data = ROOT / "docs" / "dashboard" / "data.json"
        dashboard_html = (ROOT / "docs" / "dashboard" / "index.html").read_text(encoding="utf-8")
        self.assertTrue(refresh_script.is_file())
        self.assertFalse(active_workflow.exists())
        self.assertTrue(archived_workflow.is_file())
        self.assertTrue(dashboard_data.is_file())
        ast.parse(refresh_script.read_text(encoding="utf-8"), filename=str(refresh_script))
        payload = json.loads(dashboard_data.read_text(encoding="utf-8"))
        self.assertEqual(payload["quality"]["safe_rows"], 359936)
        self.assertEqual(payload["quality"]["duplicate_key_groups"], 0)
        self.assertEqual(len(payload["regions"]), 10)
        self.assertEqual(len(payload["categories"]), 15)
        self.assertIn("fetch('./data.json'", dashboard_html)
        self.assertIn("categoryRows", dashboard_html)

    def test_sql_files_exist(self):
        self.assertTrue((ROOT / "sql" / "01_table_validation.sql").is_file())
        self.assertTrue((ROOT / "sql" / "03_duplicate_audit.sql").is_file())
        self.assertTrue((ROOT / "sql" / "09_pipeline_region_kpis.sql").is_file())
        self.assertTrue((ROOT / "sql" / "10_pipeline_category_performance.sql").is_file())
        self.assertTrue((ROOT / "sql" / "11_pipeline_top_videos.sql").is_file())


if __name__ == "__main__":
    unittest.main()
