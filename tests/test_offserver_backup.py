from __future__ import annotations

from contextlib import redirect_stdout
from dataclasses import replace
import importlib.util
import io
import json
from pathlib import Path
import shutil
import subprocess
import unittest
from unittest.mock import patch

from dokumentverkstad.archive import Archive
from dokumentverkstad.backup import BackupError, restore_backup
from dokumentverkstad.config import AppConfig
from helpers import workspace_tempdir


spec = importlib.util.spec_from_file_location(
    "offserver_backup", Path(__file__).resolve().parents[1] / "deploy/backup/offserver_backup.py"
)
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)


class OffserverBackupTests(unittest.TestCase):
    def setup_archive(self, root):
        config = AppConfig(root / "archive", root / "runtime", root / "ingest")
        archive = Archive(config.archive_root)
        document = archive.create_document("Remote restore test")
        note = archive.create_knowledge_object("Original note", document_id=document.id)
        spool = root / "spool"
        spool.mkdir()
        return config, spool, note

    def transport(self, root, corrupt=False, fail_marker=False):
        def copy(source, destination, config):
            def path(value):
                return root / value[len("remote:"):] if value.startswith("remote:") else Path(value)
            if fail_marker and destination.endswith("verified.json"):
                raise BackupError("marker upload failed")
            target = path(destination)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path(source), target)
            if corrupt and source.startswith("remote:"):
                target.write_bytes(b"damaged download")
        return copy

    def test_two_verified_generations_restore_to_separate_writable_installation(self):
        with workspace_tempdir() as tmp:
            root = Path(tmp)
            config, spool, note = self.setup_archive(root)
            with patch.object(adapter, "copy", side_effect=self.transport(root)):
                for _ in range(2):
                    adapter.snapshot(config, spool)
                    adapter.upload(config, spool, "remote:backups", root / "rclone.conf")
            receipts = list((root / "backups").glob("*/verified.json"))
            self.assertEqual(len(receipts), 2)
            for receipt_path in receipts:
                receipt = json.loads(receipt_path.read_text())
                backup = receipt_path.parent / receipt["file"]
                self.assertEqual(adapter.digest(backup), receipt["sha256"])
            target = replace(config, archive_root=root / "other/archive", runtime_root=root / "other/runtime")
            restore_backup(backup, target)
            restored = Archive(target.archive_root)
            restored.update_knowledge_object(note.id, "Writable after restore")
            self.assertEqual(restored.get_knowledge_object(note.id).content, "Writable after restore")
            self.assertEqual(Archive(config.archive_root).get_knowledge_object(note.id).content, "Original note")
            self.assertFalse((spool / "pending.json").exists())
            self.assertTrue((spool / "last-success.json").exists())

    def test_failed_transfer_or_readback_keeps_prior_success_and_local_backup(self):
        for failure in ("upload", "corrupt", "marker"):
            with self.subTest(failure=failure), workspace_tempdir() as tmp:
                root = Path(tmp)
                config, spool, _ = self.setup_archive(root)
                with patch.object(adapter, "copy", side_effect=self.transport(root)):
                    adapter.snapshot(config, spool)
                    adapter.upload(config, spool, "remote:backups", root / "rclone.conf")
                old_success = (spool / "last-success.json").read_bytes()
                old_files = {str(p): p.read_bytes() for p in (root / "backups").rglob("*") if p.is_file()}
                adapter.snapshot(config, spool)
                effect = BackupError("transport failed") if failure == "upload" else self.transport(
                    root, corrupt=failure == "corrupt", fail_marker=failure == "marker"
                )
                with patch.object(adapter, "copy", side_effect=effect), self.assertRaises(BackupError):
                    adapter.upload(config, spool, "remote:backups", root / "rclone.conf")
                self.assertEqual((spool / "last-success.json").read_bytes(), old_success)
                self.assertTrue((spool / "pending.json").exists())
                self.assertEqual(len(list(spool.glob("*/*.zip"))), 1)
                self.assertEqual(len(list((root / "backups").glob("*/verified.json"))), 1)
                for filename, data in old_files.items():
                    self.assertEqual(Path(filename).read_bytes(), data)

    def test_invalid_archive_is_not_marked_verified_even_when_transport_matches(self):
        with workspace_tempdir() as tmp:
            root = Path(tmp)
            config, spool, _ = self.setup_archive(root)
            # ZIP CRC alone cannot detect invalid application records.
            metadata = next(config.archive_root.glob("documents/*/metadata.json"))
            with patch.object(adapter, "copy", side_effect=self.transport(root)):
                adapter.snapshot(config, spool)
                pending = json.loads((spool / "pending.json").read_text())
                from zipfile import ZipFile
                backup = spool / pending["generation"] / pending["file"]
                with ZipFile(backup) as source:
                    entries = {name: source.read(name) for name in source.namelist()}
                entries["archive/" + metadata.relative_to(config.archive_root).as_posix()] = b"invalid JSON"
                with ZipFile(backup, "w") as target:
                    for name, content in entries.items():
                        target.writestr(name, content)
                with self.assertRaises(BackupError):
                    adapter.upload(config, spool, "remote:backups", root / "rclone.conf")
            self.assertFalse(list((root / "backups").glob("*/verified.json")))
            self.assertFalse((spool / "last-success.json").exists())

    def test_preflight_rejects_missing_remote_overlapping_storage_and_nested_secrets(self):
        with workspace_tempdir() as tmp:
            root = Path(tmp)
            config, spool, _ = self.setup_archive(root)
            credentials = root / "rclone.conf"
            credentials.write_text("test only")
            with patch.object(adapter.shutil, "which", return_value="rclone"):
                adapter.preflight(config, spool, "remote:backups", credentials)
                for remote in ("", "/local/path", ":http,url=secret:path"):
                    with self.assertRaises(BackupError):
                        adapter.preflight(config, spool, remote, credentials)
                with self.assertRaises(BackupError):
                    adapter.preflight(config, config.archive_root / "backups", "remote:backups", credentials)
                with self.assertRaises(BackupError):
                    adapter.preflight(replace(config, secrets_path=config.archive_root / "private/key"), spool,
                                      "remote:backups", credentials)

    def test_copy_failure_does_not_expose_provider_output(self):
        output = io.StringIO()
        with patch.object(adapter.subprocess, "run", return_value=subprocess.CompletedProcess(
            [], 5, stderr=b"credential=private-value"
        )), redirect_stdout(output), self.assertRaises(BackupError) as error:
            adapter.copy("local.zip", "remote:backups/file.zip", Path("rclone.conf"))
        self.assertNotIn("private-value", str(error.exception) + output.getvalue())
