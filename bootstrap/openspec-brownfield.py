#!/usr/bin/env python3
"""Install the OpenSpec brownfield governance overlay without owning project knowledge."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from typing import Any, Iterable


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_NAME = "openspec-brownfield-governance"
VERSION = (PACKAGE_ROOT / "VERSION").read_text(encoding="utf-8").strip()
CONTRACT_PATH = PACKAGE_ROOT / "config" / "brownfield-config.yaml"
TEMPLATE_PATH = PACKAGE_ROOT / "templates" / "deferred-changes-README.md"
RECEIPT_REL = Path(".openspec-brownfield-governance/receipt.json")
TARGET_CONFIG_REL = Path("openspec/config.yaml")
DEFERRED_INDEX_REL = Path("openspec/deferred-changes/README.md")
TARGET_MARKER_REL = Path(".agents/skills/.openspec-target")
SUPPORTED_OPENSPEC = ("1.12.0", "1.13.0")
KNOWN_CONFIG_CONTRACT_HASHES = {
    "0.1.0": "adbd8527b62c6c0e0f81e99e15942851c656c54627ad93974e5bf5a05a6d9dca"
}
SKILLS = {
    "brownfield-map": "e8dc54021787e5d9d850f41820bab42ef26a764f91a082b9c33ce5ff1ad087c5",
    "product-boundaries": "e230369e9fb0d4a65c3866948b5b895431155e56f61801a3ee6d9ac8207d686c",
    "cross-change-roadmap": "26d2ba26fa20af3b88b5d4a271d132f202a499003bfb0e0265808015562c024b",
}
KNOWN_SKILL_HASHES = {"0.1.0": SKILLS}
KNOWN_TEMPLATE_HASHES = {
    "0.1.0": "96f5090364bd6e0293e826ab0907f8ca6709a696550d28d2ed76958a7cad4afc"
}
PROJECT_OWNED_NOTICE_PATHS = (
    "PRD.canonical.md",
    "openspec/system/brownfield-map.md",
    "docs/product/product-model.md",
    "docs/product/product-boundaries.md",
    "docs/product/access-model.md",
    "openspec/roadmap.md",
)
class GovernanceError(RuntimeError):
    pass


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def contract_semantic_hash(contract: dict[str, Any]) -> str:
    canonical = json.dumps(
        contract,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return sha256_bytes(canonical)


def receipt_integrity(data: dict[str, Any]) -> str:
    unsigned = {key: value for key, value in data.items() if key != "integrity_sha256"}
    canonical = json.dumps(
        unsigned,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return sha256_bytes(canonical)


def run(
    args: list[str],
    *,
    cwd: Path | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    try:
        result = subprocess.run(
            args,
            cwd=cwd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
    except FileNotFoundError as exc:
        raise GovernanceError(f"required command not found: {args[0]}") from exc
    if check and result.returncode != 0:
        detail = result.stdout.strip()
        raise GovernanceError(
            f"command failed ({' '.join(args)}): {detail or f'exit {result.returncode}'}"
        )
    return result


def target_path(root: Path, relative: str | Path) -> Path:
    relative_path = Path(relative)
    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise GovernanceError(f"unsafe target-relative path: {relative}")
    candidate = root / relative_path
    try:
        candidate.resolve(strict=False).relative_to(root)
    except ValueError as exc:
        raise GovernanceError(
            f"target path escapes the Git root through a symlink: {relative}"
        ) from exc
    return candidate


def resolve_root(target: str) -> Path:
    requested = Path(target).expanduser().resolve()
    if not requested.exists():
        raise GovernanceError(f"target does not exist: {requested}")
    result = run(["git", "-C", str(requested), "rev-parse", "--show-toplevel"])
    root = Path(result.stdout.strip()).resolve()
    config_path = target_path(root, TARGET_CONFIG_REL)
    if not config_path.is_file():
        raise GovernanceError(
            f"already initialized OpenSpec project required; missing {config_path}"
        )
    return root


def inspect_openspec(root: Path) -> tuple[str, str]:
    binary = shutil.which("openspec")
    if not binary:
        raise GovernanceError("openspec is not available on PATH")
    version_output = run([binary, "--version"]).stdout.strip()
    match = re.search(r"\b(\d+\.\d+\.\d+)\b", version_output)
    if not match:
        raise GovernanceError(f"could not parse OpenSpec version: {version_output!r}")
    version = match.group(1)
    if version not in SUPPORTED_OPENSPEC:
        raise GovernanceError(
            f"OpenSpec {version} is untested; supported exact versions: "
            + ", ".join(SUPPORTED_OPENSPEC)
        )
    marker = target_path(root, TARGET_MARKER_REL)
    if not marker.is_file():
        raise GovernanceError(
            f"Codex/OpenSpec integration marker is missing: {marker}; "
            "the installer will not run openspec init or alter upstream integration"
        )
    targets = {line.strip() for line in marker.read_text(encoding="utf-8").splitlines()}
    if "codex" not in targets:
        raise GovernanceError(f"Codex is not declared in {marker}")
    return binary, version


def yaml_scalar(text: str) -> str:
    value = text.strip()
    if not value:
        raise GovernanceError("empty YAML scalar is not supported at a merge location")
    if value.startswith('"'):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError as exc:
            raise GovernanceError(f"unsupported quoted YAML scalar: {value}") from exc
        if not isinstance(parsed, str):
            raise GovernanceError(f"expected YAML string scalar: {value}")
        return parsed
    if value.startswith("'"):
        if not value.endswith("'"):
            raise GovernanceError(f"unsupported multiline YAML scalar: {value}")
        return value[1:-1].replace("''", "'")
    comment = re.search(r"\s+#", value)
    if comment:
        value = value[: comment.start()].rstrip()
    return value


def key_line(line: str, indent: int, key: str) -> str | None:
    pattern = "^" + (" " * indent) + re.escape(key) + r":\s*(.*?)\s*$"
    match = re.match(pattern, line)
    return match.group(1) if match else None


def line_indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def significant(line: str) -> bool:
    stripped = line.strip()
    return bool(stripped and not stripped.startswith("#"))


class YamlText:
    """Conservative editor for OpenSpec's block-style YAML configuration."""

    def __init__(self, text: str):
        self.newline = "\r\n" if "\r\n" in text else "\n"
        normalized = text.replace("\r\n", "\n")
        self.had_final_newline = normalized.endswith("\n")
        self.lines = normalized.splitlines()
        self._validate_no_tabs()

    def _validate_no_tabs(self) -> None:
        for number, line in enumerate(self.lines, 1):
            if "\t" in line[: len(line) - len(line.lstrip())]:
                raise GovernanceError(f"tab indentation is unsafe at config line {number}")

    def render(self) -> str:
        text = self.newline.join(self.lines)
        if self.had_final_newline:
            text += self.newline
        return text

    def find_direct_key(
        self, key: str, indent: int, start: int = 0, end: int | None = None
    ) -> tuple[int, str] | None:
        limit = len(self.lines) if end is None else end
        found: list[tuple[int, str]] = []
        for index in range(start, limit):
            if line_indent(self.lines[index]) != indent:
                continue
            tail = key_line(self.lines[index], indent, key)
            if tail is not None:
                found.append((index, tail))
        if len(found) > 1:
            raise GovernanceError(f"duplicate YAML key at merge location: {key}")
        return found[0] if found else None

    def section_end(self, index: int, indent: int) -> int:
        for cursor in range(index + 1, len(self.lines)):
            if (
                self.lines[cursor].strip()
                and line_indent(self.lines[cursor]) <= indent
            ):
                return cursor
        return len(self.lines)

    def locate_path(self, path: tuple[str, ...]) -> tuple[int, int, str] | None:
        start, end, indent = 0, len(self.lines), 0
        located: tuple[int, str] | None = None
        for component in path:
            located = self.find_direct_key(component, indent, start, end)
            if located is None:
                return None
            index, tail = located
            end = self.section_end(index, indent)
            start = index + 1
            indent += 2
        assert located is not None
        index, tail = located
        return index, self.section_end(index, indent - 2), tail

    def schema(self) -> str:
        found = self.find_direct_key("schema", 0)
        if found is None:
            raise GovernanceError("openspec/config.yaml has no top-level schema")
        _, tail = found
        return yaml_scalar(tail)

    def literal_block(self, key: str) -> tuple[int, int, list[str]] | None:
        found = self.find_direct_key(key, 0)
        if found is None:
            return None
        index, tail = found
        if not re.fullmatch(r"\|[+-]?", tail):
            raise GovernanceError(
                f"{key} must be a literal block scalar for safe round-trip merge"
            )
        end = self.section_end(index, 0)
        body: list[str] = []
        for number in range(index + 1, end):
            line = self.lines[number]
            if line and line_indent(line) < 2:
                raise GovernanceError(f"unsafe indentation in {key} block")
            body.append(line[2:] if line.startswith("  ") else "")
        return index, end, body

    def merge_context(self, contract: str) -> tuple[bool, bool, list[str]]:
        block = self.literal_block("context")
        created: list[str] = []
        if block is None:
            schema = self.find_direct_key("schema", 0)
            assert schema is not None
            insert_at = schema[0] + 1
            new_lines = ["", "context: |"] + [
                ("  " + line) if line else "  " for line in contract.split("\n")
            ]
            self.lines[insert_at:insert_at] = new_lines
            created.append("context")
            return True, False, created
        _, end, body = block
        existing = "\n".join(body).rstrip("\n")
        contract_body = contract.split("\n")
        occurrences = sum(
            body[offset : offset + len(contract_body)] == contract_body
            for offset in range(0, len(body) - len(contract_body) + 1)
        )
        if occurrences == 1:
            return False, True, created
        if occurrences > 1:
            raise GovernanceError(
                "duplicate brownfield context blocks detected; refusing to rewrite them"
            )
        contract_lines = {
            line.strip() for line in contract.split("\n") if line.strip()
        }
        existing_lines = {
            line.strip() for line in existing.split("\n") if line.strip()
        }
        if contract_lines & existing_lines:
            raise GovernanceError(
                "conflicting partial brownfield context detected; refusing to rewrite it"
            )
        insert_at = end
        while insert_at > 0 and not self.lines[insert_at - 1].strip():
            insert_at -= 1
        prefix = ["  "] if insert_at > 0 and self.lines[insert_at - 1].strip() else []
        addition = prefix + [
            ("  " + line) if line else "  " for line in contract.split("\n")
        ]
        self.lines[insert_at:insert_at] = addition
        return True, False, created

    def _ensure_list_path(self, path: tuple[str, ...]) -> tuple[int, int, list[str]]:
        created: list[str] = []
        for depth, component in enumerate(path):
            prefix = path[: depth + 1]
            located = self.locate_path(prefix)
            if located is not None:
                _, _, tail = located
                if tail and not tail.startswith("#"):
                    raise GovernanceError(
                        f"flow/inline YAML is unsafe at merge location: {'.'.join(prefix)}"
                    )
                continue
            parent = self.locate_path(path[:depth]) if depth else None
            indent = depth * 2
            line = (" " * indent) + component + ":"
            if parent is None:
                insert_at = len(self.lines)
                while insert_at > 0 and not self.lines[insert_at - 1].strip():
                    insert_at -= 1
                prefix_lines = [""] if insert_at else []
                self.lines[insert_at:insert_at] = prefix_lines + [line]
            else:
                _, parent_end, parent_tail = parent
                if parent_tail and not parent_tail.startswith("#"):
                    raise GovernanceError(
                        f"flow/inline YAML is unsafe at merge location: "
                        f"{'.'.join(path[:depth])}"
                    )
                insert_at = parent_end
                while insert_at > 0 and not self.lines[insert_at - 1].strip():
                    insert_at -= 1
                self.lines[insert_at:insert_at] = [line]
            created.append(".".join(prefix))
        located = self.locate_path(path)
        assert located is not None
        return located[0], located[1], created

    def list_values(self, path: tuple[str, ...]) -> list[tuple[int, str]]:
        located = self.locate_path(path)
        if located is None:
            return []
        index, end, tail = located
        if tail and not tail.startswith("#"):
            raise GovernanceError(
                f"flow/inline YAML is unsafe at merge location: {'.'.join(path)}"
            )
        item_indent = len(path) * 2
        values: list[tuple[int, str]] = []
        for cursor in range(index + 1, end):
            line = self.lines[cursor]
            if not significant(line):
                continue
            indent = line_indent(line)
            if indent == item_indent and line[indent:].startswith("- "):
                raw_value = line[indent + 2 :].strip()
                if re.fullmatch(r"[>|][+-]?[1-9]?(?:\s+#.*)?", raw_value):
                    raise GovernanceError(
                        f"block-scalar list item is unsafe at merge location: "
                        f"{'.'.join(path)}"
                    )
                values.append((cursor, yaml_scalar(raw_value)))
            elif indent > item_indent:
                raise GovernanceError(
                    f"multiline/nested list content is unsafe at merge location: "
                    f"{'.'.join(path)}"
                )
            elif indent <= item_indent:
                raise GovernanceError(
                    f"non-list YAML content at merge location: {'.'.join(path)}"
                )
        return values

    def merge_list(
        self, path: tuple[str, ...], required: list[str]
    ) -> tuple[list[str], list[str], list[str]]:
        _, end, created = self._ensure_list_path(path)
        existing = [value for _, value in self.list_values(path)]
        inserted: list[str] = []
        pre_existing: list[str] = []
        missing: list[str] = []
        for item in required:
            occurrences = existing.count(item)
            if occurrences > 1:
                raise GovernanceError(
                    f"duplicate brownfield config item at {'.'.join(path)}; "
                    "refusing to rewrite it"
                )
            if occurrences == 1:
                pre_existing.append(item)
            else:
                missing.append(item)
                inserted.append(item)
        if missing:
            located = self.locate_path(path)
            assert located is not None
            _, end, _ = located
            insert_at = end
            while insert_at > 0 and not self.lines[insert_at - 1].strip():
                insert_at -= 1
            indent = " " * (len(path) * 2)
            self.lines[insert_at:insert_at] = [
                f"{indent}- {json.dumps(item, ensure_ascii=False)}" for item in missing
            ]
        return inserted, pre_existing, created

    def remove_context(self, contract: str, context_created: bool) -> None:
        block = self.literal_block("context")
        if block is None:
            raise GovernanceError("inserted brownfield context is missing")
        index, end, body = block
        contract_lines = contract.split("\n")
        matches: list[int] = []
        for offset in range(0, len(body) - len(contract_lines) + 1):
            if body[offset : offset + len(contract_lines)] == contract_lines:
                matches.append(offset)
        if len(matches) != 1:
            raise GovernanceError(
                "inserted brownfield context was changed or duplicated; refusing uninstall"
            )
        offset = matches[0]
        if context_created:
            remaining = body[:offset] + body[offset + len(contract_lines) :]
            if not any(line.strip() for line in remaining):
                del self.lines[index:end]
                return
        start = index + 1 + offset
        finish = start + len(contract_lines)
        if start > index + 1 and not self.lines[start - 1].strip():
            start -= 1
        del self.lines[start:finish]

    def remove_list_items(self, path: tuple[str, ...], items: list[str]) -> None:
        values = self.list_values(path)
        by_value: dict[str, list[int]] = {}
        for index, value in values:
            by_value.setdefault(value, []).append(index)
        remove: list[int] = []
        for item in items:
            occurrences = by_value.get(item, [])
            if len(occurrences) != 1:
                raise GovernanceError(
                    f"inserted config item was changed, removed, or duplicated at "
                    f"{'.'.join(path)}"
                )
            remove.append(occurrences[0])
        for index in sorted(remove, reverse=True):
            del self.lines[index]

    def prune_created_nodes(self, paths: Iterable[str]) -> None:
        for dotted in sorted(set(paths), key=lambda value: value.count("."), reverse=True):
            path = tuple(dotted.split("."))
            located = self.locate_path(path)
            if located is None:
                continue
            index, end, _ = located
            if any(line.strip() for line in self.lines[index + 1 : end]):
                continue
            del self.lines[index:end]
            self._remove_one_adjacent_blank(index)

    def _remove_one_adjacent_blank(self, index: int) -> None:
        if index < len(self.lines) and not self.lines[index].strip():
            del self.lines[index]
        elif index > 0 and not self.lines[index - 1].strip():
            del self.lines[index - 1]


def parse_contract() -> dict[str, Any]:
    editor = YamlText(CONTRACT_PATH.read_text(encoding="utf-8"))
    required = editor.find_direct_key("required_schema", 0)
    if required is None:
        raise GovernanceError("distribution config contract has no required_schema")
    schema = yaml_scalar(required[1])
    context_block = editor.literal_block("context_append")
    if context_block is None:
        raise GovernanceError("distribution config contract has no context_append")
    context = "\n".join(context_block[2]).rstrip("\n")
    rules: dict[str, list[str]] = {}
    for artifact in ("proposal", "design", "tasks"):
        rules[artifact] = [
            value for _, value in editor.list_values(("rules_append", artifact))
        ]
    operations: dict[str, list[str]] = {}
    for operation in ("apply", "archive"):
        operations[operation] = [
            value
            for _, value in editor.list_values(
                ("operations_append", operation, "guidance")
            )
        ]
    return {
        "required_schema": schema,
        "context": context,
        "rules": rules,
        "operations": operations,
    }


def merge_config(text: str, contract: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    editor = YamlText(text)
    if editor.schema() != contract["required_schema"]:
        raise GovernanceError(
            f"unsupported schema {editor.schema()!r}; required: "
            f"{contract['required_schema']}"
        )
    context_inserted, context_preexisting, created = editor.merge_context(
        contract["context"]
    )
    receipt: dict[str, Any] = {
        "contract_sha256": contract_semantic_hash(contract),
        "contract_snapshot": copy.deepcopy(contract),
        "context": {
            "inserted": context_inserted,
            "pre_existing": context_preexisting,
            "value": contract["context"],
        },
        "rules": {},
        "operations": {},
        "created_nodes": list(created),
    }
    for artifact, items in contract["rules"].items():
        inserted, preexisting, nodes = editor.merge_list(
            ("rules", artifact), items
        )
        receipt["rules"][artifact] = {
            "inserted": inserted,
            "pre_existing": preexisting,
        }
        receipt["created_nodes"].extend(nodes)
    for operation, items in contract["operations"].items():
        inserted, preexisting, nodes = editor.merge_list(
            ("operations", operation, "guidance"), items
        )
        receipt["operations"][operation] = {
            "inserted": inserted,
            "pre_existing": preexisting,
        }
        receipt["created_nodes"].extend(nodes)
    receipt["created_nodes"] = list(dict.fromkeys(receipt["created_nodes"]))
    return editor.render(), receipt


def config_complete(text: str, contract: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    try:
        editor = YamlText(text)
        if editor.schema() != contract["required_schema"]:
            issues.append(f"schema must be {contract['required_schema']}")
        block = editor.literal_block("context")
        context_body = [] if block is None else block[2]
        required_body = contract["context"].split("\n")
        occurrences = sum(
            context_body[offset : offset + len(required_body)] == required_body
            for offset in range(0, len(context_body) - len(required_body) + 1)
        )
        if occurrences != 1:
            issues.append("brownfield context block is incomplete")
        for artifact, required in contract["rules"].items():
            existing = [value for _, value in editor.list_values(("rules", artifact))]
            missing = [item for item in required if item not in existing]
            if missing:
                issues.append(f"rules.{artifact} is missing {len(missing)} item(s)")
            duplicates = [item for item in required if existing.count(item) > 1]
            if duplicates:
                issues.append(
                    f"rules.{artifact} duplicates {len(duplicates)} required item(s)"
                )
        for operation, required in contract["operations"].items():
            existing = [
                value
                for _, value in editor.list_values(
                    ("operations", operation, "guidance")
                )
            ]
            missing = [item for item in required if item not in existing]
            if missing:
                issues.append(
                    f"operations.{operation}.guidance is missing {len(missing)} item(s)"
                )
            duplicates = [item for item in required if existing.count(item) > 1]
            if duplicates:
                issues.append(
                    f"operations.{operation}.guidance duplicates "
                    f"{len(duplicates)} required item(s)"
                )
    except GovernanceError as exc:
        issues.append(str(exc))
    return issues


def merge_provenance(
    previous: dict[str, Any] | None, current: dict[str, Any]
) -> dict[str, Any]:
    if previous is None:
        return current
    merged = current
    previous_context = previous.get("context", {})
    if previous_context.get("inserted"):
        merged["context"] = {
            "inserted": True,
            "pre_existing": False,
            "value": merged["context"]["value"],
        }
    elif previous_context.get("pre_existing"):
        merged["context"] = {
            "inserted": False,
            "pre_existing": True,
            "value": merged["context"]["value"],
        }
    for group in ("rules", "operations"):
        for name, values in merged[group].items():
            old = previous.get(group, {}).get(name, {})
            old_inserted = set(old.get("inserted", []))
            newly_inserted = set(values["inserted"])
            all_values = values["inserted"] + values["pre_existing"]
            values["inserted"] = [
                item
                for item in all_values
                if item in old_inserted or item in newly_inserted
            ]
            values["pre_existing"] = [
                item
                for item in all_values
                if item not in values["inserted"]
            ]
    merged["created_nodes"] = list(
        dict.fromkeys(
            previous.get("created_nodes", []) + merged.get("created_nodes", [])
        )
    )
    return merged


def uninstall_config(text: str, receipt: dict[str, Any]) -> str:
    editor = YamlText(text)
    context = receipt.get("context", {})
    if context.get("inserted"):
        editor.remove_context(
            context["value"], "context" in receipt.get("created_nodes", [])
        )
    for artifact in ("proposal", "design", "tasks"):
        inserted = receipt.get("rules", {}).get(artifact, {}).get("inserted", [])
        if inserted:
            editor.remove_list_items(("rules", artifact), inserted)
    for operation in ("apply", "archive"):
        inserted = (
            receipt.get("operations", {}).get(operation, {}).get("inserted", [])
        )
        if inserted:
            editor.remove_list_items(
                ("operations", operation, "guidance"), inserted
            )
    editor.prune_created_nodes(receipt.get("created_nodes", []))
    return editor.render()


class Transaction:
    def __init__(self) -> None:
        self.originals: dict[Path, tuple[bytes | None, int | None]] = {}
        self.created_dirs: set[Path] = set()

    def _remember(self, path: Path) -> None:
        if path in self.originals:
            return
        if path.exists():
            self.originals[path] = (path.read_bytes(), path.stat().st_mode & 0o777)
        else:
            self.originals[path] = (None, None)

    def write(self, path: Path, data: bytes, mode: int | None = None) -> None:
        self._remember(path)
        original_mode = self.originals[path][1]
        effective_mode = mode if mode is not None else (original_mode or 0o644)
        missing: list[Path] = []
        parent = path.parent
        while not parent.exists():
            missing.append(parent)
            parent = parent.parent
        path.parent.mkdir(parents=True, exist_ok=True)
        self.created_dirs.update(missing)
        descriptor, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
        try:
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
            os.chmod(temp_name, effective_mode)
            os.replace(temp_name, path)
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)

    def remove(self, path: Path) -> None:
        self._remember(path)
        if path.exists():
            path.unlink()

    def rollback(self) -> None:
        for path, (data, mode) in reversed(list(self.originals.items())):
            if data is None:
                if path.exists():
                    path.unlink()
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
                if mode is not None:
                    path.chmod(mode)
        for directory in sorted(self.created_dirs, key=lambda p: len(p.parts), reverse=True):
            try:
                directory.rmdir()
            except OSError:
                pass


def _valid_hash(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def validate_receipt(data: Any, contract: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise GovernanceError("installation receipt must be a JSON object")
    if data.get("format") != 1:
        raise GovernanceError("unsupported installation receipt format")
    if data.get("integrity_sha256") != receipt_integrity(data):
        raise GovernanceError("installation receipt integrity check failed")
    if data.get("package") != PACKAGE_NAME:
        raise GovernanceError("receipt belongs to another package")
    for field in ("distribution_version", "openspec_version", "installed_at"):
        if not isinstance(data.get(field), str):
            raise GovernanceError(f"invalid receipt field: {field}")
    receipt_version = data["distribution_version"]
    known_skills = KNOWN_SKILL_HASHES.get(receipt_version)
    known_template = KNOWN_TEMPLATE_HASHES.get(receipt_version)
    known_contract = KNOWN_CONFIG_CONTRACT_HASHES.get(receipt_version)
    if known_skills is None or known_template is None or known_contract is None:
        raise GovernanceError(f"unknown distribution version in receipt: {receipt_version}")

    skills = data.get("skills")
    if not isinstance(skills, list) or len(skills) != len(SKILLS):
        raise GovernanceError("receipt skill inventory is invalid")
    seen: set[str] = set()
    for entry in skills:
        if not isinstance(entry, dict):
            raise GovernanceError("invalid receipt skill entry")
        name = entry.get("name")
        if name not in SKILLS or name in seen:
            raise GovernanceError("receipt contains an unknown or duplicate skill")
        seen.add(name)
        expected_path = str(Path(".agents/skills") / name / "SKILL.md")
        if entry.get("path") != expected_path:
            raise GovernanceError(f"unsafe receipt skill path for {name}")
        if not _valid_hash(entry.get("hash")):
            raise GovernanceError(f"invalid receipt skill hash for {name}")
        if entry["hash"] != known_skills[name]:
            raise GovernanceError(f"unknown managed skill hash for {name}")
        if not isinstance(entry.get("created"), bool):
            raise GovernanceError(f"invalid receipt ownership flag for {name}")
    if seen != set(SKILLS):
        raise GovernanceError("receipt skill inventory is incomplete")

    config = data.get("config")
    if not isinstance(config, dict):
        raise GovernanceError("receipt config provenance is invalid")
    snapshot = config.get("contract_snapshot")
    if not isinstance(snapshot, dict):
        raise GovernanceError("receipt config contract snapshot is invalid")
    snapshot_hash = contract_semantic_hash(snapshot)
    if (
        config.get("contract_sha256") != snapshot_hash
        or snapshot_hash != known_contract
    ):
        raise GovernanceError("receipt config contract hash is unknown")
    if snapshot.get("required_schema") != "spec-driven":
        raise GovernanceError("receipt config contract schema is invalid")
    context = config.get("context")
    if (
        not isinstance(context, dict)
        or not isinstance(context.get("inserted"), bool)
        or not isinstance(context.get("pre_existing"), bool)
        or (context["inserted"] and context["pre_existing"])
        or context.get("value") != snapshot.get("context")
    ):
        raise GovernanceError("receipt context provenance is invalid")
    for group in ("rules", "operations"):
        actual_group = config.get(group)
        expected_group = snapshot.get(group)
        if not isinstance(expected_group, dict):
            raise GovernanceError(f"receipt contract {group} is invalid")
        if not isinstance(actual_group, dict) or set(actual_group) != set(expected_group):
            raise GovernanceError(f"receipt {group} provenance is invalid")
        for name, allowed_items in expected_group.items():
            record = actual_group.get(name)
            if not isinstance(record, dict):
                raise GovernanceError(f"receipt {group}.{name} provenance is invalid")
            inserted = record.get("inserted")
            preexisting = record.get("pre_existing")
            if not isinstance(inserted, list) or not isinstance(preexisting, list):
                raise GovernanceError(f"receipt {group}.{name} lists are invalid")
            if not all(isinstance(item, str) for item in inserted + preexisting):
                raise GovernanceError(f"receipt {group}.{name} contains non-string items")
            if len(set(inserted)) != len(inserted) or len(set(preexisting)) != len(preexisting):
                raise GovernanceError(f"receipt {group}.{name} contains duplicates")
            if set(inserted) & set(preexisting):
                raise GovernanceError(f"receipt {group}.{name} provenance overlaps")
            if not set(inserted + preexisting).issubset(set(allowed_items)):
                raise GovernanceError(f"receipt {group}.{name} contains unknown clauses")
            if set(inserted + preexisting) != set(allowed_items):
                raise GovernanceError(f"receipt {group}.{name} provenance is incomplete")

    created_nodes = config.get("created_nodes")
    allowed_nodes = {
        "context",
        "rules",
        "rules.proposal",
        "rules.design",
        "rules.tasks",
        "operations",
        "operations.apply",
        "operations.apply.guidance",
        "operations.archive",
        "operations.archive.guidance",
    }
    if (
        not isinstance(created_nodes, list)
        or not all(isinstance(item, str) for item in created_nodes)
        or not set(created_nodes).issubset(allowed_nodes)
    ):
        raise GovernanceError("receipt created-node inventory is unsafe")

    generated = data.get("generated_structural_files")
    if not isinstance(generated, list) or len(generated) > 1:
        raise GovernanceError("receipt structural-file inventory is invalid")
    for entry in generated:
        if (
            not isinstance(entry, dict)
            or entry.get("path") != str(DEFERRED_INDEX_REL)
            or not _valid_hash(entry.get("hash"))
            or not isinstance(entry.get("created"), bool)
        ):
            raise GovernanceError("receipt structural-file entry is unsafe")
        if entry["created"] and entry["hash"] != known_template:
            raise GovernanceError("receipt managed structural-file hash is unknown")
    return data


def read_receipt(
    root: Path, contract: dict[str, Any]
) -> dict[str, Any] | None:
    path = target_path(root, RECEIPT_REL)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise GovernanceError(f"invalid installation receipt: {path}") from exc
    return validate_receipt(data, contract)


def skill_source(name: str) -> Path:
    return PACKAGE_ROOT / "skills" / name / "SKILL.md"


def skill_target(root: Path, name: str) -> Path:
    return target_path(root, Path(".agents/skills") / name / "SKILL.md")


def verify_package() -> None:
    known_skills = KNOWN_SKILL_HASHES.get(VERSION)
    known_contract = KNOWN_CONFIG_CONTRACT_HASHES.get(VERSION)
    known_template = KNOWN_TEMPLATE_HASHES.get(VERSION)
    if known_skills is None or known_contract is None or known_template is None:
        raise GovernanceError(f"package version {VERSION} has no integrity manifest")
    for name, expected in known_skills.items():
        actual = sha256_path(skill_source(name))
        if actual != expected:
            raise GovernanceError(
                f"distribution skill hash mismatch for {name}: {actual} != {expected}"
            )
    actual_contract = contract_semantic_hash(parse_contract())
    if actual_contract != known_contract:
        raise GovernanceError(
            "distribution config contract hash mismatch: "
            f"{actual_contract} != {known_contract}"
        )
    actual_template = sha256_path(TEMPLATE_PATH)
    if actual_template != known_template:
        raise GovernanceError(
            "distribution structural template hash mismatch: "
            f"{actual_template} != {known_template}"
        )


def verify_existing_install(
    root: Path, receipt: dict[str, Any], contract: dict[str, Any]
) -> list[str]:
    issues: list[str] = []
    receipt_skills = {
        entry.get("name"): entry for entry in receipt.get("skills", [])
    }
    if set(receipt_skills) != set(SKILLS):
        issues.append("receipt skill inventory does not match the distribution")
    for name, expected in SKILLS.items():
        entry = receipt_skills.get(name)
        if entry is None:
            continue
        if entry.get("hash") != expected:
            issues.append(f"receipt hash does not match distribution skill: {name}")
        path = target_path(root, entry["path"])
        if not path.is_file():
            issues.append(f"missing installed skill: {entry['path']}")
        elif sha256_path(path) != expected:
            issues.append(f"locally modified installed skill: {entry['path']}")
    issues.extend(
        config_complete(
            target_path(root, TARGET_CONFIG_REL).read_text(), contract
        )
    )
    for entry in receipt.get("generated_structural_files", []):
        path = target_path(root, entry["path"])
        if entry.get("created") and not path.exists():
            issues.append(f"generated structural file is missing: {entry['path']}")
    return issues


def build_receipt(
    openspec_version: str,
    skill_entries: list[dict[str, Any]],
    config_receipt: dict[str, Any],
    generated: list[dict[str, Any]],
    installed_at: str | None = None,
) -> dict[str, Any]:
    receipt = {
        "format": 1,
        "package": PACKAGE_NAME,
        "distribution_version": VERSION,
        "openspec_version": openspec_version,
        "installed_at": installed_at
        or datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "skills": skill_entries,
        "config": config_receipt,
        "generated_structural_files": generated,
    }
    receipt["integrity_sha256"] = receipt_integrity(receipt)
    return receipt


def plan_skills(
    root: Path, previous: dict[str, Any] | None
) -> tuple[list[dict[str, Any]], list[tuple[Path, bytes]]]:
    old_by_path = {
        entry["path"]: entry for entry in (previous or {}).get("skills", [])
    }
    receipt_entries: list[dict[str, Any]] = []
    writes: list[tuple[Path, bytes]] = []
    for name, expected in SKILLS.items():
        source = skill_source(name)
        data = source.read_bytes()
        relative = str(Path(".agents/skills") / name / "SKILL.md")
        target = target_path(root, relative)
        old = old_by_path.get(relative)
        if old is not None:
            if not target.is_file():
                raise GovernanceError(f"managed skill is missing: {relative}")
            actual = sha256_path(target)
            if actual != old["hash"]:
                raise GovernanceError(
                    f"locally modified skill will not be overwritten: {relative}"
                )
            created = bool(old.get("created", True))
            if not created and actual != expected:
                raise GovernanceError(
                    f"pre-existing skill is not distribution-owned and will not "
                    f"be updated: {relative}"
                )
        elif target.exists():
            actual = sha256_path(target)
            if actual != expected:
                raise GovernanceError(
                    f"existing non-matching skill will not be overwritten: {relative}"
                )
            created = False
        else:
            created = True
        if not target.exists() or sha256_path(target) != expected:
            writes.append((target, data))
        receipt_entries.append(
            {"name": name, "path": relative, "hash": expected, "created": created}
        )
    return receipt_entries, writes


def plan_structural_file(
    root: Path, previous: dict[str, Any] | None
) -> tuple[list[dict[str, Any]], list[tuple[Path, bytes]]]:
    path = target_path(root, DEFERRED_INDEX_REL)
    template = TEMPLATE_PATH.read_bytes()
    template_hash = sha256_bytes(template)
    previous_entries = {
        entry["path"]: entry
        for entry in (previous or {}).get("generated_structural_files", [])
    }
    old = previous_entries.get(str(DEFERRED_INDEX_REL))
    if old is not None:
        if not old.get("created"):
            if not path.exists():
                return [], []
            return [
                {
                    "path": str(DEFERRED_INDEX_REL),
                    "hash": sha256_path(path),
                    "created": False,
                }
            ], []
        if path.exists():
            actual = sha256_path(path)
            if actual != old["hash"]:
                return [
                    {
                        "path": str(DEFERRED_INDEX_REL),
                        "hash": actual,
                        "created": False,
                    }
                ], []
        entry = {
            "path": str(DEFERRED_INDEX_REL),
            "hash": template_hash,
            "created": True,
        }
        writes = (
            []
            if path.exists() and sha256_path(path) == template_hash
            else [(path, template)]
        )
        return [entry], writes
    if path.exists():
        return [
            {
                "path": str(DEFERRED_INDEX_REL),
                "hash": sha256_path(path),
                "created": False,
            }
        ], []
    entry = {
        "path": str(DEFERRED_INDEX_REL),
        "hash": template_hash,
        "created": True,
    }
    return [entry], [(path, template)]


def install_or_update(args: argparse.Namespace, update: bool) -> int:
    verify_package()
    contract = parse_contract()
    root = resolve_root(args.target)
    _, openspec_version = inspect_openspec(root)
    receipt_path = target_path(root, RECEIPT_REL)
    previous = read_receipt(root, contract)
    if update and previous is None:
        raise GovernanceError("no installation receipt; run install first")
    if not update and previous is not None:
        if previous.get("distribution_version") != VERSION:
            raise GovernanceError(
                f"version {previous.get('distribution_version')} is installed; "
                f"run update to install {VERSION}"
            )
        issues = verify_existing_install(root, previous, contract)
        if issues:
            raise GovernanceError(
                "existing installation is not healthy:\n- " + "\n- ".join(issues)
            )
        print(f"{PACKAGE_NAME} {previous['distribution_version']} is already installed")
        return 0

    config_path = target_path(root, TARGET_CONFIG_REL)
    old_config = config_path.read_text(encoding="utf-8")
    previous_config = (previous or {}).get("config")
    if (
        previous_config
        and previous_config.get("contract_sha256")
        != contract_semantic_hash(contract)
    ):
        migration_base = uninstall_config(old_config, previous_config)
        new_config, config_receipt = merge_config(migration_base, contract)
    else:
        new_config, config_receipt = merge_config(old_config, contract)
        config_receipt = merge_provenance(previous_config, config_receipt)
    skill_entries, skill_writes = plan_skills(root, previous)
    structural_entries, structural_writes = plan_structural_file(root, previous)
    new_receipt = build_receipt(
        openspec_version,
        skill_entries,
        config_receipt,
        structural_entries,
        (previous or {}).get("installed_at"),
    )
    receipt_data = (
        json.dumps(new_receipt, indent=2, ensure_ascii=False) + "\n"
    ).encode("utf-8")
    planned: list[str] = []
    if new_config != old_config:
        planned.append(f"merge {TARGET_CONFIG_REL}")
    planned.extend(f"write {path.relative_to(root)}" for path, _ in skill_writes)
    planned.extend(f"create {path.relative_to(root)}" for path, _ in structural_writes)
    receipt_changed = previous != new_receipt
    if receipt_changed:
        planned.append(f"write {RECEIPT_REL}")
    if args.dry_run:
        print(f"Dry run for {root}")
        for item in planned or ["no changes"]:
            print(f"- {item}")
        return 0

    transaction = Transaction()
    try:
        if new_config != old_config:
            transaction.write(config_path, new_config.encode("utf-8"))
        for path, data in skill_writes:
            transaction.write(path, data)
        for path, data in structural_writes:
            transaction.write(path, data)
        if receipt_changed:
            transaction.write(receipt_path, receipt_data)
    except Exception:
        transaction.rollback()
        raise
    verb = "Updated" if update else "Installed"
    print(f"{verb} {PACKAGE_NAME} {VERSION} in {root}")
    for item in planned:
        print(f"- {item}")
    return 0


def uninstall(args: argparse.Namespace) -> int:
    verify_package()
    contract = parse_contract()
    root = resolve_root(args.target)
    receipt = read_receipt(root, contract)
    if receipt is None:
        raise GovernanceError("no installation receipt; nothing can be proven safe to remove")

    removals: list[Path] = []
    for entry in receipt.get("skills", []):
        path = target_path(root, entry["path"])
        if not entry.get("created", True):
            continue
        if not path.exists():
            continue
        if sha256_path(path) != entry["hash"]:
            raise GovernanceError(
                f"locally modified skill will not be deleted: {entry['path']}"
            )
        removals.append(path)

    config_path = target_path(root, TARGET_CONFIG_REL)
    old_config = config_path.read_text(encoding="utf-8")
    new_config = uninstall_config(old_config, receipt["config"])

    preserved_structural: list[str] = []
    for entry in receipt.get("generated_structural_files", []):
        path = target_path(root, entry["path"])
        if not entry.get("created"):
            continue
        if not path.exists():
            continue
        if sha256_path(path) == entry["hash"]:
            removals.append(path)
        else:
            preserved_structural.append(entry["path"])

    receipt_path = target_path(root, RECEIPT_REL)
    if args.dry_run:
        print(f"Dry run for {root}")
        if new_config != old_config:
            print(f"- remove inserted clauses from {TARGET_CONFIG_REL}")
        for path in removals:
            print(f"- remove {path.relative_to(root)}")
        for path in preserved_structural:
            print(f"- preserve edited project knowledge: {path}")
        print(f"- remove {RECEIPT_REL}")
        return 0

    transaction = Transaction()
    try:
        if new_config != old_config:
            transaction.write(config_path, new_config.encode("utf-8"))
        for path in removals:
            transaction.remove(path)
        transaction.remove(receipt_path)
    except Exception:
        transaction.rollback()
        raise

    for path in removals:
        parent = path.parent
        while parent != root and parent.name not in (".agents", "openspec"):
            try:
                parent.rmdir()
            except OSError:
                break
            parent = parent.parent
    try:
        receipt_path.parent.rmdir()
    except OSError:
        pass
    print(f"Uninstalled {PACKAGE_NAME} from {root}")
    for path in preserved_structural:
        print(f"- preserved edited project knowledge: {path}")
    return 0


def doctor(args: argparse.Namespace) -> int:
    verify_package()
    contract = parse_contract()
    root = resolve_root(args.target)
    binary, version = inspect_openspec(root)
    receipt = read_receipt(root, contract)
    health: list[str] = []
    if receipt is None:
        health.append("installation receipt is missing")
    else:
        health.extend(verify_existing_install(root, receipt, contract))
        if receipt.get("distribution_version") != VERSION:
            health.append(
                f"receipt version {receipt.get('distribution_version')} != package {VERSION}"
            )

    notices: list[str] = []
    for relative in PROJECT_OWNED_NOTICE_PATHS:
        if not (root / relative).exists():
            notices.append(f"workflow input not yet present: {relative}")
    deferred = target_path(root, DEFERRED_INDEX_REL)
    if not deferred.exists():
        notices.append(f"deferred-work index not yet present: {DEFERRED_INDEX_REL}")
    elif deferred.read_bytes() == TEMPLATE_PATH.read_bytes():
        notices.append(f"deferred-work index is present but not yet populated")

    command_results: list[tuple[str, int, str]] = []
    for label, command in (
        ("openspec doctor", [binary, "doctor", "--json"]),
        (
            "openspec validate",
            [binary, "validate", "--all", "--strict", "--json", "--no-interactive"],
        ),
    ):
        result = run(command, cwd=root, check=False)
        command_results.append((label, result.returncode, result.stdout.strip()))
        if result.returncode != 0:
            health.append(f"{label} failed with exit {result.returncode}")

    print(f"Installation health: {'HEALTHY' if not health else 'UNHEALTHY'}")
    print(f"- root: {root}")
    print(f"- OpenSpec: {version}")
    print(f"- schema: {contract['required_schema']}")
    for issue in health:
        print(f"- ERROR: {issue}")
    print("Workflow readiness:")
    if notices:
        for notice in notices:
            print(f"- NOTICE: {notice}")
    else:
        print("- READY: all expected persistent inputs are present")
    for label, code, _ in command_results:
        print(f"- {label}: {'pass' if code == 0 else 'fail'}")
    return 1 if health else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Install the OpenSpec brownfield governance overlay"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("install", "update", "uninstall"):
        subparser = subparsers.add_parser(command)
        subparser.add_argument("--target", default=".")
        subparser.add_argument("--dry-run", action="store_true")
    doctor_parser = subparsers.add_parser("doctor")
    doctor_parser.add_argument("--target", default=".")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "install":
            return install_or_update(args, update=False)
        if args.command == "update":
            return install_or_update(args, update=True)
        if args.command == "uninstall":
            return uninstall(args)
        if args.command == "doctor":
            return doctor(args)
        raise GovernanceError(f"unsupported command: {args.command}")
    except GovernanceError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
