import toml

from sleepwellbaby import package_root, version


def test_version_matches_pyproject():
    pyproject_path = package_root / "pyproject.toml"
    pyproject = toml.load(pyproject_path)
    expected_version = pyproject["project"]["version"]
    assert version == expected_version
