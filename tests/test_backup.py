from __future__ import annotations

from pathlib import Path
import shutil
import unittest
from zipfile import ZipFile

from dokumentverkstad.ai import AiRunRecord
from dokumentverkstad.archive import Archive
from dokumentverkstad.backup import (
    BackupError,
    create_backup,
    restore_backup,
    validate_backup,
)
from dokumentverkstad.config import AppConfig
from dokumentverkstad.index import document_index_path, list_indexed_documents
from dokumentverkstad.ingest import process_ingest_source
from helpers import workspace_tempdir, write_minimal_pdf


class BackupRestoreTests(unittest.TestCase):
    def test_backup_contains_archive_manifest_and_excludes_secrets_runtime_ingest(self) -> None:
        with workspace_tempdir() as tmp:
            root = Path(tmp)
            config = _config(root)
            archive, document_id = _realistic_archive(root)
            (root / ".dokumentverkstad" / "secrets.enc").write_text(
                "encrypted secret", encoding="utf-8"
            )
            (root / ".dokumentverkstad" / "secrets.toml").write_text(
                "[openai]\napi_key='sk-secret'\n", encoding="utf-8"
            )
            (config.runtime_root / "sqlite").mkdir(parents=True, exist_ok=True)
            (config.runtime_root / "sqlite" / "documents.sqlite3").write_text(
                "runtime", encoding="utf-8"
            )
            (config.ingest_source / "pending.pdf").write_text("ingest", encoding="utf-8")

            result = create_backup(config, output_dir=root / "backups")

            self.assertEqual(result.counts.documents, 1)
            self.assertEqual(result.counts.knowledge_objects, 2)
            self.assertEqual(result.counts.projects, 1)
            self.assertEqual(result.counts.ai_runs, 1)
            validate_backup(result.path)
            with ZipFile(result.path) as backup:
                names = backup.namelist()
            self.assertIn("backup-manifest.json", names)
            self.assertIn("config/portable.json", names)
            self.assertIn(f"archive/documents/{document_id}/metadata.json", names)
            self.assertIn(f"archive/documents/{document_id}/original.pdf", names)
            self.assertIn(f"archive/documents/{document_id}/processing/text.txt", names)
            self.assertTrue(any(name.startswith("archive/knowledge/") for name in names))
            self.assertTrue(any(name.startswith("archive/projects/") for name in names))
            self.assertTrue(any(name.startswith("archive/ai_runs/") for name in names))
            self.assertFalse(any("secrets.enc" in name for name in names))
            self.assertFalse(any("secrets.toml" in name for name in names))
            self.assertFalse(any(name.startswith("runtime/") for name in names))
            self.assertFalse(any(name.startswith("ingest/") for name in names))
            self.assertTrue(all(not Path(name).is_absolute() for name in names))
            self.assertTrue(all(".." not in name.replace("\\", "/").split("/") for name in names))
            self.assertEqual(archive.get_document(document_id).original_filename, "2024 Ångström.pdf")

    def test_restore_to_empty_installation_preserves_readable_archive_and_rebuilds_runtime(self) -> None:
        with workspace_tempdir() as tmp:
            root = Path(tmp)
            source_config = _config(root / "source")
            _realistic_archive(root / "source")
            backup = create_backup(source_config, output_dir=root).path
            target_config = _config(root / "target")
            target_config.archive_root.mkdir(parents=True)

            result = restore_backup(backup, target_config)
            restored = Archive(target_config.archive_root)

            documents = restored.list_documents()
            knowledge = restored.list_knowledge_objects()
            projects = restored.list_projects()
            ai_runs = restored.list_ai_runs()
            self.assertEqual(len(documents), 1)
            self.assertEqual(documents[0].title, "Ångström")
            self.assertEqual(documents[0].original_filename, "2024 Ångström.pdf")
            self.assertEqual(len(knowledge), 2)
            self.assertTrue(any(item.history for item in knowledge))
            self.assertEqual(len(projects), 1)
            self.assertEqual(len(ai_runs), 1)
            self.assertTrue(restored.original_file_path(documents[0].id).read_bytes())
            self.assertIn(
                "Machine readable text",
                restored.extracted_text_file_path(documents[0].id).read_text(encoding="utf-8"),
            )
            self.assertEqual(result.index_path, document_index_path(target_config.runtime_root))
            self.assertEqual([row["title"] for row in list_indexed_documents(target_config.runtime_root)], ["Ångström"])

    def test_runtime_can_be_removed_and_rebuilt_without_archive_data_loss(self) -> None:
        with workspace_tempdir() as tmp:
            root = Path(tmp)
            config = _config(root)
            archive, _ = _realistic_archive(root)
            create_backup(config, output_dir=root)
            shutil.rmtree(config.runtime_root)

            from dokumentverkstad.index import rebuild_document_index

            rebuild_document_index(Archive(config.archive_root), config.runtime_root)

            self.assertEqual(len(Archive(config.archive_root).list_documents()), 1)
            self.assertEqual(len(Archive(config.archive_root).list_knowledge_objects()), 2)
            self.assertEqual(len(Archive(config.archive_root).list_projects()), 1)
            self.assertEqual(len(Archive(config.archive_root).list_ai_runs()), 1)
            self.assertEqual([row["title"] for row in list_indexed_documents(config.runtime_root)], ["Ångström"])
            self.assertEqual(len(archive.list_documents()), 1)

    def test_restore_rejects_path_traversal_and_absolute_paths(self) -> None:
        with workspace_tempdir() as tmp:
            root = Path(tmp)
            traversal = root / "traversal.zip"
            with ZipFile(traversal, "w") as backup:
                backup.writestr("backup-manifest.json", '{"backup_format_version": "1"}')
                backup.writestr("archive/../escape.txt", "bad")
            with self.assertRaises(BackupError):
                validate_backup(traversal)

            absolute = root / "absolute.zip"
            with ZipFile(absolute, "w") as backup:
                backup.writestr("backup-manifest.json", '{"backup_format_version": "1"}')
                backup.writestr("/archive/documents/doc_1/metadata.json", "{}")
            with self.assertRaises(BackupError):
                validate_backup(absolute)

    def test_bad_backup_is_rejected_before_existing_archive_is_changed(self) -> None:
        with workspace_tempdir() as tmp:
            root = Path(tmp)
            config = _config(root)
            archive = Archive(config.archive_root)
            existing = archive.create_document("Existing")
            bad_backup = root / "bad.zip"
            bad_backup.write_text("not a zip", encoding="utf-8")

            with self.assertRaises(BackupError):
                restore_backup(bad_backup, config, force=True)

            self.assertEqual(Archive(config.archive_root).get_document(existing.id).title, "Existing")

    def test_restore_refuses_to_overwrite_non_empty_archive_without_force(self) -> None:
        with workspace_tempdir() as tmp:
            root = Path(tmp)
            source_config = _config(root / "source")
            _realistic_archive(root / "source")
            backup = create_backup(source_config, output_dir=root).path
            target_config = _config(root / "target")
            Archive(target_config.archive_root).create_document("Existing")

            with self.assertRaises(BackupError):
                restore_backup(backup, target_config)

            self.assertEqual(Archive(target_config.archive_root).list_documents()[0].title, "Existing")


def _config(root: Path) -> AppConfig:
    return AppConfig(
        archive_root=root / ".dokumentverkstad" / "archive",
        runtime_root=root / ".dokumentverkstad" / "runtime",
        ingest_source=root / ".dokumentverkstad" / "ingest",
        encrypted_secrets_path=root / ".dokumentverkstad" / "secrets.enc",
        secrets_path=root / ".dokumentverkstad" / "secrets.toml",
    )


def _realistic_archive(root: Path) -> tuple[Archive, str]:
    config = _config(root)
    config.ingest_source.mkdir(parents=True)
    write_minimal_pdf(
        config.ingest_source / "2024 Ångström.pdf",
        title="",
        author="Test Author",
        text="Machine readable text",
    )
    archive = Archive(config.archive_root)
    document = process_ingest_source(archive, config.ingest_source, config.runtime_root)[0].document
    project = archive.create_project("Portabilitet", "Flyttbart arkiv")
    archive.set_document_projects(document.id, (project.id,))
    note = archive.create_knowledge_object(
        "Första noteringen.",
        document_id=document.id,
        source_location="s. 1",
        project_ids=(project.id,),
    )
    archive.update_knowledge_object(note.id, "Korrigerad notering.", source_location="s. 2")
    candidate = archive.create_ai_candidate(
        "AI-kandidat.",
        ai_run_id="airun_test",
        ai_provider="mock",
        ai_model="mock-model",
        prompt_version="test",
        capability="summary",
        document_id=document.id,
    )
    archive.save_ai_run(
        AiRunRecord(
            id="airun_test",
            document_id=document.id,
            provider="mock",
            model="mock-model",
            prompt_version="test",
            capabilities=("summary",),
            created_at="2026-08-18T10:30:00+00:00",
            status="completed",
            estimated_input_tokens=10,
            estimated_output_tokens=20,
            estimated_cost=0.0,
            candidate_ids=(candidate.id,),
        )
    )
    return archive, document.id


if __name__ == "__main__":
    unittest.main()
