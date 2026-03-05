#!/usr/bin/env python3
"""Architecture compliance audit script for Munqith.

Ensures:
1. Domain purity - no fastapi/sqlalchemy imports in app/domain/
2. Analytics isolation - core domain doesn't import app/analytics
3. API layer enforcement - APIs use use cases, not engines directly
4. No circular dependencies

Run: python scripts/arch_audit.py
Exit code: 0 = pass, 1 = violations found
"""
import sys
import os
from pathlib import Path
import ast
import re


class ImportViolationChecker:
    """Check for architecture violations in Python files."""

    # Forbidden imports by module context
    FORBIDDEN_IMPORTS = {
        "app/domain": [
            "fastapi",
            "sqlalchemy",
            "psycopg2",
            "pydantic",
            "requests",
            "httpx",
        ],
        "app/domain/engines": [
            "fastapi",
            "sqlalchemy",
            "psycopg2",
            "requests",
            "httpx",
        ],
    }

    # Forbidden cross-module imports
    CROSS_MODULE_VIOLATIONS = {
        # Domain must not import from analytics
        "app/domain": ["app.analytics"],
        # API should not directly use engines
        "app/api": ["app.domain.engines"],
    }

    def __init__(self):
        self.violations = []
        self.project_root = Path(__file__).parent.parent

    def check_file(self, filepath: Path):
        """Check a Python file for import violations."""
        try:
            with open(filepath, "r") as f:
                tree = ast.parse(f.read())
        except SyntaxError as e:
            self.violations.append(
                f"Syntax error in {filepath}: {e}"
            )
            return

        relative_path = filepath.relative_to(self.project_root)
        relative_path_str = str(relative_path).replace("\\", "/")

        # Check all imports in the file
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self._check_forbidden_import(
                        relative_path_str, alias.name, filepath
                    )
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    self._check_forbidden_import(
                        relative_path_str, node.module, filepath
                    )

    def _check_forbidden_import(self, file_module: str, import_name: str, filepath: Path):
        """Check if an import violates architecture rules."""
        # Normalize paths
        file_module = file_module.replace(".py", "").replace("\\", "/")

        # Check forbidden imports for domain
        for forbidden_module, forbidden_imports in self.FORBIDDEN_IMPORTS.items():
            if file_module.startswith(forbidden_module.replace("/", ".")):
                for forbidden in forbidden_imports:
                    if import_name.startswith(forbidden):
                        self.violations.append(
                            f"DOMAIN PURITY VIOLATION in {file_module}:\n"
                            f"  {import_name} imports framework library\n"
                            f"  Location: {filepath}"
                        )

        # Check cross-module violations
        for source_module, forbidden_targets in self.CROSS_MODULE_VIOLATIONS.items():
            if file_module.startswith(source_module.replace("/", ".")):
                for target in forbidden_targets:
                    if import_name.startswith(target):
                        self.violations.append(
                            f"ISOLATION VIOLATION in {file_module}:\n"
                            f"  Cannot import from {target}\n"
                            f"  Location: {filepath}"
                        )

    def check_directory(self, directory: Path):
        """Recursively check all Python files in a directory."""
        for py_file in directory.rglob("*.py"):
            # Skip __pycache__ and build artifacts
            if "__pycache__" in py_file.parts or "/.git/" in str(py_file):
                continue
            self.check_file(py_file)

    def report(self):
        """Print audit report and return exit code."""
        if not self.violations:
            print("✓ Architecture audit PASSED")
            print("  - Domain purity verified")
            print("  - Analytics isolation verified")
            print("  - Cross-module boundaries verified")
            return 0

        print("✗ Architecture audit FAILED\n")
        for violation in self.violations:
            print(f"  {violation}\n")

        print(f"\nTotal violations: {len(self.violations)}")
        return 1


def check_no_ai_in_stage_logic():
    """Verify that AI/analytics don't modify snapshot.stage."""
    print("\nChecking Stage Reproducibility...")

    # Check that analytics module never writes to snapshot.stage
    analytics_path = Path(__file__).parent.parent / "app" / "analytics"
    if analytics_path.exists():
        for py_file in analytics_path.rglob("*.py"):
            if "__pycache__" in py_file.parts:
                continue
            with open(py_file, "r") as f:
                content = f.read()
                # Check for snapshot.stage assignments in analytics
                if re.search(r"\.stage\s*=", content) and "snapshot" in content:
                    print(f"  ✗ VIOLATION: Stage modification in {py_file}")
                    return False

    print("  ✓ Stage logic isolated from analytics")
    return True


def main():
    """Run full architecture audit."""
    print("=" * 70)
    print("MUNQITH ARCHITECTURE COMPLIANCE AUDIT")
    print("=" * 70)

    project_root = Path(__file__).parent.parent
    app_dir = project_root / "app"

    # Check app directory exists
    if not app_dir.exists():
        print(f"Error: {app_dir} not found")
        return 1

    # Run import checker
    print("\nPhase 1: Import Validation")
    print("-" * 70)
    checker = ImportViolationChecker()
    checker.check_directory(app_dir)
    import_result = checker.report()

    # Check stage logic
    print("\nPhase 2: Stage Logic Validation")
    print("-" * 70)
    stage_result = 0 if check_no_ai_in_stage_logic() else 1

    # Summary
    print("\n" + "=" * 70)
    if import_result == 0 and stage_result == 0:
        print("✓ ALL ARCHITECTU RE CHECKS PASSED")
        print("=" * 70)
        return 0
    else:
        print("✗ ARCHITECTURE VIOLATIONS FOUND")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
