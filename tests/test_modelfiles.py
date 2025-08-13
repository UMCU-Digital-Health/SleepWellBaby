
import hashlib
import os


def md5sum(filename):
    h = hashlib.md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()

def test_classifer_md5():
    # classifiers.bz2
    file_path = "src/sleepwellbaby/modelfiles/classifier.bz2"
    expected_md5 = "b4745b7c3f4c64f7b55585f7d1b67b02"
    assert os.path.exists(file_path), f"{file_path} does not exist"
    assert md5sum(file_path) == expected_md5, "MD5 checksum does not match"


def test_support_object_md5():
    file_path = "src/sleepwellbaby/modelfiles/trained_support_obj.pkl"
    expected_md5 = "19914f7106d786c3438ad17ee12ff10f"
    assert os.path.exists(file_path), f"{file_path} does not exist"
    assert md5sum(file_path) == expected_md5, "MD5 checksum does not match"
