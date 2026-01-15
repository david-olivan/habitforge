"""
Buildozer Spec Compliance Tests for HabitForge

Tests to ensure buildozer.spec meets 2025 Google Play requirements and
best practices for Android app distribution.
"""

import re
from pathlib import Path
from typing import Dict, Optional


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent


def parse_buildozer_spec() -> Dict[str, str]:
    """
    Parse buildozer.spec file and return key-value pairs.

    Returns:
        Dictionary of buildozer configuration values
    """
    spec_file = get_project_root() / "buildozer.spec"

    if not spec_file.exists():
        return {}

    config = {}
    with open(spec_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith('#') or line.startswith('['):
                continue

            # Parse key = value
            match = re.match(r'^([a-zA-Z_][a-zA-Z0-9_.]*)\s*=\s*(.+)$', line)
            if match:
                key = match.group(1)
                value = match.group(2).strip()
                config[key] = value

    return config


def parse_version(version_str: str) -> tuple:
    """
    Parse version string into tuple for comparison.

    Args:
        version_str: Version string like "26b" or "35"

    Returns:
        Tuple of (major, minor_or_letter)
    """
    # Handle NDK versions like "26b"
    match = re.match(r'^(\d+)([a-z]?)$', version_str)
    if match:
        major = int(match.group(1))
        letter = match.group(2) or ''
        return (major, letter)
    return (0, '')


class TestGooglePlay2025Compliance:
    """Test Google Play 2025 requirements compliance."""

    def test_target_api_level_35_or_higher(self):
        """
        Verify target API is 35 or higher.

        Google Play requirement as of August 31, 2025:
        All new apps and app updates must target API level 35 (Android 15).
        """
        config = parse_buildozer_spec()

        assert 'android.api' in config, "android.api not found in buildozer.spec"

        api_level = int(config['android.api'])

        assert api_level >= 35, (
            f"android.api = {api_level}, but Google Play requires API 35+ "
            f"(Android 15) as of August 31, 2025"
        )

    def test_minimum_api_level_reasonable(self):
        """
        Verify minimum API level is set and reasonable.

        Minimum API 24 (Android 7.0) is recommended for modern apps while
        maintaining reasonable backward compatibility.
        """
        config = parse_buildozer_spec()

        assert 'android.minapi' in config, "android.minapi not found in buildozer.spec"

        min_api = int(config['android.minapi'])

        assert 21 <= min_api <= 35, (
            f"android.minapi = {min_api}, should be between 21 and 35. "
            f"Recommended: 24 (Android 7.0) for good device coverage."
        )

    def test_ndk_version_26_or_higher(self):
        """
        Verify NDK version is r26 or higher.

        Google Play requirement as of November 1, 2025:
        Apps must support 16KB page sizes. NDK r26+ is recommended.
        """
        config = parse_buildozer_spec()

        assert 'android.ndk' in config, "android.ndk not found in buildozer.spec"

        ndk_version = config['android.ndk']
        ndk_major, ndk_letter = parse_version(ndk_version)

        assert ndk_major >= 26, (
            f"android.ndk = {ndk_version}, but NDK r26+ is required "
            f"for 16KB page size support (deadline: November 1, 2025)"
        )

    def test_sdk_version_matches_api_level(self):
        """
        Verify SDK version matches or exceeds target API level.

        SDK version should be at least as high as the target API level.
        """
        config = parse_buildozer_spec()

        if 'android.sdk' not in config:
            return  # SDK version is optional, skip if not set

        sdk_version = int(config['android.sdk'])
        api_level = int(config.get('android.api', 0))

        assert sdk_version >= api_level, (
            f"android.sdk ({sdk_version}) should be >= android.api ({api_level})"
        )

    def test_64bit_architecture(self):
        """
        Verify app targets 64-bit architecture.

        Google Play has required 64-bit support since August 2019.
        Recommended: arm64-v8a for best compatibility.
        """
        config = parse_buildozer_spec()

        assert 'android.arch' in config, "android.arch not found in buildozer.spec"

        arch = config['android.arch']
        valid_64bit_archs = ['arm64-v8a', 'x86_64']

        assert arch in valid_64bit_archs, (
            f"android.arch = {arch}, but 64-bit architecture required. "
            f"Valid options: {', '.join(valid_64bit_archs)}"
        )


class TestBuildozerConfiguration:
    """Test buildozer.spec has required configuration."""

    def test_buildozer_spec_exists(self):
        """Verify buildozer.spec file exists."""
        spec_file = get_project_root() / "buildozer.spec"
        assert spec_file.exists(), "buildozer.spec not found in project root"

    def test_required_fields_present(self):
        """
        Verify all required buildozer.spec fields are present.

        These fields are essential for building a valid APK.
        """
        config = parse_buildozer_spec()

        required_fields = [
            'title',
            'package.name',
            'package.domain',
            'source.dir',
            'version',
            'requirements',
        ]

        missing_fields = [f for f in required_fields if f not in config]

        assert not missing_fields, (
            f"Missing required fields in buildozer.spec: {missing_fields}"
        )

    def test_version_format(self):
        """
        Verify version follows semantic versioning.

        Version should be in format: MAJOR.MINOR.PATCH (e.g., 0.1.0)
        """
        config = parse_buildozer_spec()

        if 'version' not in config:
            return  # Skip if version not set

        version = config['version']

        # Check semantic versioning pattern
        pattern = r'^\d+\.\d+\.\d+$'
        assert re.match(pattern, version), (
            f"version = {version} doesn't follow semantic versioning (MAJOR.MINOR.PATCH). "
            f"Example: 0.1.0"
        )

    def test_package_name_format(self):
        """
        Verify package name follows Android conventions.

        Package name should be lowercase, no spaces, valid identifier.
        """
        config = parse_buildozer_spec()

        if 'package.name' not in config:
            return

        package_name = config['package.name']

        # Android package name rules
        pattern = r'^[a-z][a-z0-9_]*$'
        assert re.match(pattern, package_name), (
            f"package.name = {package_name} doesn't follow Android conventions. "
            f"Should be lowercase, start with letter, contain only letters/numbers/underscores."
        )

    def test_package_domain_format(self):
        """
        Verify package domain follows reverse domain notation.

        Domain should be like: com.company or org.project
        """
        config = parse_buildozer_spec()

        if 'package.domain' not in config:
            return

        domain = config['package.domain']

        # Reverse domain notation pattern
        pattern = r'^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$'
        assert re.match(pattern, domain), (
            f"package.domain = {domain} doesn't follow reverse domain notation. "
            f"Example: com.company or org.project"
        )


class TestDependencyConfiguration:
    """Test dependency configuration in buildozer.spec."""

    def test_requirements_field_present(self):
        """Verify requirements field exists and is not empty."""
        config = parse_buildozer_spec()

        assert 'requirements' in config, "requirements field not found in buildozer.spec"
        assert config['requirements'].strip(), "requirements field is empty"

    def test_python3_in_requirements(self):
        """Verify python3 is in requirements list."""
        config = parse_buildozer_spec()

        if 'requirements' not in config:
            return

        requirements = config['requirements'].lower()
        assert 'python3' in requirements, (
            "requirements must include 'python3' as the first requirement"
        )

    def test_kivy_in_requirements(self):
        """Verify kivy is in requirements list."""
        config = parse_buildozer_spec()

        if 'requirements' not in config:
            return

        requirements = config['requirements'].lower()
        assert 'kivy' in requirements, "requirements must include 'kivy'"

    def test_critical_kivymd_dependencies_in_requirements(self):
        """
        Verify critical KivyMD dependencies are in buildozer.spec requirements.

        Regression test for v0.1.1: Missing filetype and pillow caused crashes.
        """
        config = parse_buildozer_spec()

        if 'requirements' not in config:
            return

        requirements = config['requirements'].lower()

        # Check for KivyMD and its critical dependencies
        if 'kivymd' in requirements:
            assert 'filetype' in requirements, (
                "KivyMD requires 'filetype' package. Add to requirements to prevent crashes."
            )
            assert 'pillow' in requirements, (
                "KivyMD requires 'pillow' package. Add to requirements to prevent crashes."
            )

    def test_no_pydantic_in_requirements(self):
        """
        Verify Pydantic is not in buildozer.spec requirements.

        Pydantic 2.x is incompatible with python-for-android.
        """
        config = parse_buildozer_spec()

        if 'requirements' not in config:
            return

        requirements = config['requirements'].lower()
        assert 'pydantic' not in requirements, (
            "Pydantic found in buildozer.spec requirements. "
            "Pydantic 2.x is incompatible with python-for-android."
        )


class TestAssetConfiguration:
    """Test icon and presplash configuration."""

    def test_icon_file_specified(self):
        """Verify icon.filename is specified."""
        config = parse_buildozer_spec()

        assert 'icon.filename' in config, (
            "icon.filename not specified in buildozer.spec"
        )

    def test_presplash_file_specified(self):
        """Verify presplash.filename is specified."""
        config = parse_buildozer_spec()

        assert 'presplash.filename' in config, (
            "presplash.filename not specified in buildozer.spec"
        )

    def test_orientation_is_valid(self):
        """
        Verify orientation setting is valid.

        Valid values: landscape, portrait, sensor, or all
        """
        config = parse_buildozer_spec()

        if 'orientation' not in config:
            return

        orientation = config['orientation']
        valid_orientations = ['landscape', 'sensorLandscape', 'portrait', 'sensorPortrait', 'all', 'sensor']

        assert orientation in valid_orientations, (
            f"orientation = {orientation} is not valid. "
            f"Valid options: {', '.join(valid_orientations)}"
        )
