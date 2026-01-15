"""
Android Compatibility Tests for HabitForge

Tests to ensure code is compatible with Android builds and python-for-android.
These tests prevent issues like:
- Python 3.10+ type hint syntax (| unions) incompatible with p4a
- Missing KivyMD dependencies
- Platform-specific code not properly guarded
"""

import ast
import re
from pathlib import Path
from typing import List, Set, Tuple


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent


def get_python_files() -> List[Path]:
    """Get all Python files in the app directory."""
    app_dir = get_project_root() / "app"
    return list(app_dir.rglob("*.py"))


def parse_requirements_file(filepath: Path) -> Set[str]:
    """
    Parse requirements file and return set of package names (without versions).

    Args:
        filepath: Path to requirements file

    Returns:
        Set of package names
    """
    packages = set()
    if not filepath.exists():
        return packages

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            # Extract package name (before ==, >=, etc.)
            match = re.match(r'^([a-zA-Z0-9_\-\[\]]+)', line)
            if match:
                pkg_name = match.group(1)
                # Remove extras like kivy[full] -> kivy
                pkg_name = re.sub(r'\[.*\]', '', pkg_name)
                packages.add(pkg_name.lower())

    return packages


class TestPythonVersionCompatibility:
    """Test Python 3.11 compatibility for Android builds."""

    def test_no_union_operator_type_hints(self):
        """
        Verify no Python 3.10+ union operator (|) is used in type hints.

        Python 3.11 on Android doesn't support the new union syntax.
        Must use typing.Optional[T] instead of T | None.
        """
        files_with_union_syntax = []

        for filepath in get_python_files():
            with open(filepath, 'r', encoding='utf-8') as f:
                try:
                    tree = ast.parse(f.read(), filename=str(filepath))
                except SyntaxError:
                    continue

                # Check for BitOr operator in type annotations
                for node in ast.walk(tree):
                    # Check function arguments
                    if isinstance(node, ast.FunctionDef):
                        for arg in node.args.args:
                            if arg.annotation and self._has_union_operator(arg.annotation):
                                files_with_union_syntax.append(
                                    f"{filepath.relative_to(get_project_root())}:{node.lineno} - "
                                    f"Function '{node.name}' parameter '{arg.arg}'"
                                )
                        # Check return annotation
                        if node.returns and self._has_union_operator(node.returns):
                            files_with_union_syntax.append(
                                f"{filepath.relative_to(get_project_root())}:{node.lineno} - "
                                f"Function '{node.name}' return type"
                            )

                    # Check variable annotations
                    if isinstance(node, ast.AnnAssign):
                        if self._has_union_operator(node.annotation):
                            files_with_union_syntax.append(
                                f"{filepath.relative_to(get_project_root())}:{node.lineno} - "
                                f"Variable annotation"
                            )

        assert not files_with_union_syntax, (
            f"Found {len(files_with_union_syntax)} type hints using '|' operator. "
            f"Use typing.Optional[T] instead for Android compatibility:\n" +
            "\n".join(files_with_union_syntax)
        )

    def _has_union_operator(self, node: ast.expr) -> bool:
        """Check if AST node contains BitOr operator (|) used for type unions."""
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
            return True
        for child in ast.walk(node):
            if isinstance(child, ast.BinOp) and isinstance(child.op, ast.BitOr):
                return True
        return False

    def test_typing_optional_imported_when_used(self):
        """
        Verify that files using Optional import it from typing module.
        """
        files_missing_optional = []

        for filepath in get_python_files():
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

                # Check if Optional is used
                if re.search(r'\bOptional\[', content):
                    # Check if Optional is imported
                    try:
                        tree = ast.parse(content, filename=str(filepath))
                    except SyntaxError:
                        continue

                    has_import = False
                    for node in ast.walk(tree):
                        # Check: from typing import Optional
                        if isinstance(node, ast.ImportFrom):
                            if node.module == 'typing':
                                for alias in node.names:
                                    if alias.name == 'Optional' or alias.name == '*':
                                        has_import = True
                                        break

                    if not has_import:
                        files_missing_optional.append(
                            str(filepath.relative_to(get_project_root()))
                        )

        assert not files_missing_optional, (
            f"Files using Optional[] but not importing it from typing:\n" +
            "\n".join(files_missing_optional)
        )


class TestKivyMDDependencies:
    """Test that KivyMD required dependencies are present."""

    def test_kivymd_dependencies_in_requirements(self):
        """
        Verify critical KivyMD dependencies are in requirements-app.txt.

        Regression test for v0.1.1 crash: KivyMD 1.2.0 requires filetype
        and pillow but they weren't in requirements.
        """
        requirements_file = get_project_root() / "requirements-app.txt"
        packages = parse_requirements_file(requirements_file)

        required_kivymd_deps = {'filetype', 'pillow'}
        missing_deps = required_kivymd_deps - packages

        assert not missing_deps, (
            f"Missing KivyMD dependencies in requirements-app.txt: {missing_deps}\n"
            f"KivyMD 1.2.0 requires these packages to avoid runtime crashes."
        )

    def test_no_pydantic_in_requirements(self):
        """
        Verify Pydantic is not in requirements-app.txt.

        Pydantic 2.x uses pyproject.toml and doesn't work with python-for-android
        which requires setup.py.
        """
        requirements_file = get_project_root() / "requirements-app.txt"
        packages = parse_requirements_file(requirements_file)

        assert 'pydantic' not in packages, (
            "Pydantic found in requirements-app.txt. "
            "Pydantic 2.x is incompatible with python-for-android. "
            "Use native Python validation instead."
        )


class TestPlatformSpecificCode:
    """Test that platform-specific code is properly guarded."""

    def test_window_size_has_platform_check(self):
        """
        Verify Window.size is only set with platform check.

        Setting Window.size on Android causes crashes. Must be guarded with:
        if platform not in ('android', 'ios'):
        """
        main_file = get_project_root() / "app" / "main.py"

        if not main_file.exists():
            return  # Skip if main.py doesn't exist

        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # If Window.size is set, verify it's in a platform check
        if 'Window.size' in content:
            # Should have platform check nearby
            pattern = r"platform\s+not\s+in\s+\(['\"]android['\"],\s*['\"]ios['\"]\)"

            assert re.search(pattern, content), (
                "Found 'Window.size' in main.py but no platform check detected. "
                "Window.size must be guarded with: "
                "if platform not in ('android', 'ios'):"
            )

    def test_no_windows_specific_imports(self):
        """
        Verify no Windows-specific modules are imported in app code.

        Packages like pywin32, ptyprocess, etc. will fail on Android.
        """
        windows_modules = {'win32api', 'win32con', 'winreg', 'msvcrt', 'ptyprocess', 'pexpect'}
        files_with_windows_imports = []

        for filepath in get_python_files():
            with open(filepath, 'r', encoding='utf-8') as f:
                try:
                    tree = ast.parse(f.read(), filename=str(filepath))
                except SyntaxError:
                    continue

                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            if alias.name.split('.')[0] in windows_modules:
                                files_with_windows_imports.append(
                                    f"{filepath.relative_to(get_project_root())}:{node.lineno} - "
                                    f"import {alias.name}"
                                )

                    if isinstance(node, ast.ImportFrom):
                        if node.module and node.module.split('.')[0] in windows_modules:
                            files_with_windows_imports.append(
                                f"{filepath.relative_to(get_project_root())}:{node.lineno} - "
                                f"from {node.module}"
                            )

        assert not files_with_windows_imports, (
            f"Found Windows-specific imports in app code:\n" +
            "\n".join(files_with_windows_imports) +
            "\nThese will fail on Android builds."
        )


class TestRequirementsConsistency:
    """Test that requirements files are consistent and properly formatted."""

    def test_requirements_files_exist(self):
        """Verify all required requirements files exist."""
        root = get_project_root()
        required_files = [
            root / "requirements.txt",
            root / "requirements-app.txt",
        ]

        missing = [f for f in required_files if not f.exists()]
        assert not missing, f"Missing requirements files: {missing}"

    def test_no_windows_packages_in_app_requirements(self):
        """
        Verify Windows-specific packages are not in requirements-app.txt.

        Packages like kivy-deps.* are Windows-only and will break Android builds.
        """
        requirements_file = get_project_root() / "requirements-app.txt"

        with open(requirements_file, 'r', encoding='utf-8') as f:
            content = f.read().lower()

        windows_packages = ['kivy-deps', 'pywin32', 'pypiwin32', 'ptyprocess', 'pexpect']
        found_packages = [pkg for pkg in windows_packages if pkg in content]

        assert not found_packages, (
            f"Found Windows-specific packages in requirements-app.txt: {found_packages}\n"
            f"These packages should only be in requirements.txt for development."
        )

    def test_all_packages_have_versions(self):
        """
        Verify all packages in requirements-app.txt have version pins.

        Version pins ensure reproducible builds and prevent unexpected breakage.
        """
        requirements_file = get_project_root() / "requirements-app.txt"
        packages_without_versions = []

        with open(requirements_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue

                # Check if line has version specifier (==, >=, ~=, etc.)
                if not re.search(r'[=<>~!]', line):
                    packages_without_versions.append(f"Line {line_num}: {line}")

        assert not packages_without_versions, (
            f"Packages without version pins in requirements-app.txt:\n" +
            "\n".join(packages_without_versions) +
            "\nAll packages should have explicit versions (e.g., package==1.2.3)"
        )
