#!/usr/bin/env python3
"""Offline deployment checks; no Fabric installation or SSH server required.

Run from the repository root:
    python -m unittest discover -s tests -p 'web_static_deployment_checks.py' -v

The Fabric API is replaced only inside these tests. Real tar commands verify
archive creation and extraction. Remote commands are recorded or modeled in a
temporary directory; the tests never contact either configured server.
"""

from contextlib import contextmanager, redirect_stdout
import functools
import importlib.util
import io
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
from unittest.mock import Mock, patch


ROOT = Path(__file__).resolve().parent.parent
PACK_FILES = (
    "1-pack_web_static.py",
    "2-do_deploy_web_static.py",
    "3-deploy_web_static.py",
)
DEPLOY_FILES = PACK_FILES[1:]


class Result:
    """Expose Fabric's success/failure flags without importing Fabric."""

    def __init__(self, failed=False):
        self.failed = failed
        self.succeeded = not failed


@contextmanager
def fake_settings(**kwargs):
    """Model the settings context; network operations are mocked separately."""
    yield


def fake_runs_once(function):
    """Model Fabric 1's cached return value, including a cached None."""
    called = [False]
    result = [None]

    @functools.wraps(function)
    def wrapped(*args, **kwargs):
        if not called[0]:
            result[0] = function(*args, **kwargs)
            called[0] = True
        return result[0]

    return wrapped


def local_command(command):
    """Execute only the two supported packaging operations, without a shell."""
    arguments = shlex.split(command)
    if arguments == ["mkdir", "-p", "versions"]:
        os.makedirs("versions", exist_ok=True)
        return Result()
    if arguments[:2] == ["tar", "-czf"]:
        exit_code = subprocess.call(
            arguments, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return Result(exit_code != 0)
    raise AssertionError("Unexpected local command: " + command)


def load_task(filename):
    """Load a hyphenated task filename with an isolated, fake Fabric module."""
    fabric = types.ModuleType("fabric")
    api = types.ModuleType("fabric.api")
    api.env = types.SimpleNamespace(hosts=[], host_string="web-01.test")
    api.local = Mock(side_effect=local_command)
    api.put = Mock(return_value=Result())
    api.run = Mock(return_value=Result())
    api.settings = fake_settings
    api.runs_once = fake_runs_once
    fabric.api = api
    spec = importlib.util.spec_from_file_location(
        "tested_" + filename.replace("-", "_").replace(".", "_"),
        str(ROOT / filename))
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, {"fabric": fabric, "fabric.api": api}):
        spec.loader.exec_module(module)
    return module, api


class WebStaticDeploymentChecks(unittest.TestCase):
    """Verify outcomes and failure boundaries using disposable local data."""

    def setUp(self):
        self.original_directory = os.getcwd()
        self.temporary = tempfile.TemporaryDirectory()
        os.chdir(self.temporary.name)
        self.output = io.StringIO()
        self.redirect = redirect_stdout(self.output)
        self.redirect.__enter__()

    def tearDown(self):
        self.redirect.__exit__(None, None, None)
        os.chdir(self.original_directory)
        self.temporary.cleanup()

    def make_website(self):
        website = Path("web_static")
        website.mkdir(exist_ok=True)
        (website / "index.html").write_text("<h1>Deployment test</h1>")
        (website / ".hidden").write_text("hidden file")
        assets = website / "assets with spaces"
        assets.mkdir(exist_ok=True)
        (assets / "style sheet.css").write_text("body { color: blue; }")
        (assets / ".nested-hidden").write_text("nested hidden file")
        return website

    def make_archive_placeholder(self, name="web_static_test.tgz"):
        archive = Path("versions") / name
        archive.parent.mkdir(exist_ok=True)
        archive.write_bytes(b"placeholder for mocked upload tests")
        return str(archive)

    def assert_no_current_change(self, api):
        commands = [call[0][0] for call in api.run.call_args_list]
        self.assertFalse(any("/data/web_static/current" in command
                             for command in commands), commands)

    @unittest.skipUnless(shutil.which("tar"), "tar must be installed")
    def test_all_packers_produce_archives_with_complete_directory_tree(self):
        self.make_website()
        for filename in PACK_FILES:
            with self.subTest(filename=filename):
                module, api = load_task(filename)
                archive = module.do_pack()
                self.assertIsNotNone(archive)
                self.assertRegex(archive, r"^versions/web_static_\d{14}\.tgz$")
                contents = subprocess.check_output(
                    ["tar", "-tzf", archive]).decode("utf-8")
                self.assertIn("web_static/index.html", contents)
                self.assertIn("web_static/.hidden", contents)
                self.assertIn("web_static/assets with spaces/style sheet.css",
                              contents)
                self.assertIn("web_static/assets with spaces/.nested-hidden",
                              contents)
                self.assertEqual(api.local.call_count, 2)
                os.remove(archive)

    def test_missing_web_static_returns_none_without_running_commands(self):
        for filename in PACK_FILES:
            with self.subTest(filename=filename):
                module, api = load_task(filename)
                self.assertIsNone(module.do_pack())
                api.local.assert_not_called()

    def test_pack_command_failures_return_none_and_remove_partial_archive(self):
        self.make_website()
        for filename in PACK_FILES:
            for failure in ("mkdir", "tar", "exception"):
                with self.subTest(filename=filename, failure=failure):
                    module, api = load_task(filename)

                    def fail_operation(command):
                        arguments = shlex.split(command)
                        if failure == "exception":
                            raise RuntimeError("simulated command error")
                        if arguments[0] == failure:
                            if failure == "tar":
                                Path(arguments[2]).write_bytes(b"partial")
                            return Result(failed=True)
                        return local_command(command)

                    api.local.side_effect = fail_operation
                    self.assertIsNone(module.do_pack())
                    self.assertEqual(list(Path("versions").glob("*.tgz")), [])

    def test_pack_refuses_to_overwrite_timestamp_collision(self):
        self.make_website()
        archive = self.make_archive_placeholder(
            "web_static_20000102030405.tgz")
        for filename in PACK_FILES:
            with self.subTest(filename=filename):
                module, api = load_task(filename)
                module.datetime = Mock()
                module.datetime.now.return_value.strftime.return_value = (
                    "20000102030405")
                self.assertIsNone(module.do_pack())
                api.local.assert_not_called()
                self.assertEqual(Path(archive).read_bytes(),
                                 b"placeholder for mocked upload tests")

    def test_missing_or_invalid_archive_does_not_contact_server(self):
        invalid = self.make_archive_placeholder("web_static.txt")
        for filename in DEPLOY_FILES:
            for archive in ("versions/missing.tgz", invalid):
                with self.subTest(filename=filename, archive=archive):
                    module, api = load_task(filename)
                    self.assertIs(module.do_deploy(archive), False)
                    api.run.assert_not_called()
                    api.put.assert_not_called()

    def test_unconfigured_host_does_not_contact_server(self):
        archive = self.make_archive_placeholder()
        for filename in DEPLOY_FILES:
            for host in ("", "<IP web-01>"):
                with self.subTest(filename=filename, host=host):
                    module, api = load_task(filename)
                    api.env.host_string = host
                    self.assertIs(module.do_deploy(archive), False)
                    api.run.assert_not_called()
                    api.put.assert_not_called()

    def test_existing_release_is_not_overwritten(self):
        archive = self.make_archive_placeholder()
        for filename in DEPLOY_FILES:
            with self.subTest(filename=filename):
                module, api = load_task(filename)
                api.run.return_value = Result(failed=True)
                self.assertIs(module.do_deploy(archive), False)
                api.put.assert_not_called()
                self.assert_no_current_change(api)

    def test_failed_or_interrupted_upload_keeps_current_untouched(self):
        archive = self.make_archive_placeholder()
        for filename in DEPLOY_FILES:
            for raises in (False, True):
                with self.subTest(filename=filename, raises=raises):
                    module, api = load_task(filename)
                    if raises:
                        api.put.side_effect = RuntimeError("upload interrupted")
                    else:
                        api.put.return_value = Result(failed=True)
                    self.assertIs(module.do_deploy(archive), False)
                    self.assert_no_current_change(api)
                    self.assertEqual(api.run.call_count, 1)

    def test_prepublication_command_failure_stops_before_current_change(self):
        archive = self.make_archive_placeholder()
        for filename in DEPLOY_FILES:
            for prefix in ("mkdir ", "tar ", "rm -f /tmp/", "chmod "):
                with self.subTest(filename=filename, prefix=prefix):
                    module, api = load_task(filename)
                    api.run.side_effect = lambda command: Result(
                        failed=command.startswith(prefix))
                    self.assertIs(module.do_deploy(archive), False)
                    self.assert_no_current_change(api)
                    self.assertTrue(
                        api.run.call_args_list[-1][0][0].startswith(prefix))

    def test_remote_exception_returns_false_without_switching_current(self):
        archive = self.make_archive_placeholder()
        for filename in DEPLOY_FILES:
            with self.subTest(filename=filename):
                module, api = load_task(filename)
                api.run.side_effect = RuntimeError("SSH command interrupted")
                self.assertIs(module.do_deploy(archive), False)
                self.assert_no_current_change(api)

    @unittest.skipUnless(shutil.which("tar"), "tar must be installed")
    def test_actual_deployment_extraction_places_all_files_at_release_root(self):
        self.make_website()
        packer, unused_api = load_task(PACK_FILES[0])
        archive = packer.do_pack()
        self.assertIsNotNone(archive)
        spaced_archive = str(Path("versions") / "web static test.tgz")
        os.rename(archive, spaced_archive)
        for index, filename in enumerate(DEPLOY_FILES):
            with self.subTest(filename=filename):
                module, api = load_task(filename)
                extracted = Path(self.temporary.name) / ("release " + str(index))
                extracted.mkdir()

                def simulate_remote(command):
                    arguments = shlex.split(command)
                    if arguments[0] == "tar":
                        arguments[2] = spaced_archive
                        arguments[arguments.index("-C") + 1] = str(extracted)
                        status = subprocess.call(
                            arguments, stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL)
                        return Result(failed=status != 0)
                    if arguments[0] == "ln":
                        self.assertTrue((extracted / "index.html").is_file())
                        self.assertFalse((extracted / "web_static").exists())
                        self.assertEqual(arguments[-1],
                                         "/data/web_static/current")
                        self.assertEqual(arguments[-2],
                                         "/data/web_static/releases/"
                                         "web static test")
                    return Result()

                api.run.side_effect = simulate_remote
                self.assertIs(module.do_deploy(spaced_archive), True)
                api.put.assert_called_once_with(
                    spaced_archive, "/tmp/web static test.tgz", use_glob=False)
                self.assertEqual((extracted / ".hidden").read_text(),
                                 "hidden file")
                self.assertEqual(
                    (extracted / "assets with spaces" /
                     ".nested-hidden").read_text(), "nested hidden file")
                self.assertTrue(
                    (extracted / "assets with spaces" /
                     "style sheet.css").is_file())
                self.assertTrue(api.run.call_args_list[-1][0][0].startswith(
                    "ln -s "))

    @unittest.skipUnless(shutil.which("tar"), "tar must be installed")
    def test_deploy_packs_once_and_uploads_same_archive_on_both_hosts(self):
        self.make_website()
        module, api = load_task("3-deploy_web_static.py")
        uploads = []

        def record_upload(source, destination, **kwargs):
            uploads.append((api.env.host_string, source, destination))
            return Result()

        api.put.side_effect = record_upload
        api.env.hosts = ["web-01.test", "web-02.test"]
        for host in api.env.hosts:
            api.env.host_string = host
            self.assertIs(module.deploy(), True)
        self.assertEqual([row[0] for row in uploads], api.env.hosts)
        self.assertEqual(uploads[0][1:], uploads[1][1:])
        tar_calls = [call for call in api.local.call_args_list
                     if call[0][0].startswith("tar ")]
        self.assertEqual(len(tar_calls), 1)
        self.assertEqual(len(list(Path("versions").glob("*.tgz"))), 1)

    def test_failed_pack_is_cached_and_does_not_start_deployment(self):
        self.make_website()
        module, api = load_task("3-deploy_web_static.py")
        api.local.return_value = Result(failed=True)
        api.local.side_effect = None
        module.do_deploy = Mock()
        for host in ("web-01.test", "web-02.test"):
            api.env.host_string = host
            self.assertIs(module.deploy(), False)
        self.assertEqual(api.local.call_count, 1)
        module.do_deploy.assert_not_called()

    def test_deploy_propagates_deployment_success_and_failure(self):
        for result in (True, False):
            with self.subTest(result=result):
                module, unused_api = load_task("3-deploy_web_static.py")
                module.do_pack = Mock(return_value="versions/prepared.tgz")
                module.do_deploy = Mock(return_value=result)
                self.assertIs(module.deploy(), result)
                module.do_deploy.assert_called_once_with(
                    "versions/prepared.tgz")


if __name__ == "__main__":
    unittest.main()
