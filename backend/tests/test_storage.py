"""Test storage backend."""
import pytest
import tempfile
import shutil
from pathlib import Path
import io
from backend.app.storage import LocalFileStorage


@pytest.fixture
def temp_storage():
    """Create a temporary storage directory."""
    temp_dir = tempfile.mkdtemp()
    storage = LocalFileStorage(temp_dir)
    
    yield storage
    
    # Cleanup
    shutil.rmtree(temp_dir)


def test_save_and_load_file(temp_storage):
    """Test saving and loading a file."""
    content = b"Test resume content"
    file_obj = io.BytesIO(content)
    
    path = temp_storage.save(file_obj, "1/pdf/v_1/resume.pdf")
    
    assert path == "1/pdf/v_1/resume.pdf"
    assert temp_storage.exists(path)
    
    loaded_content = temp_storage.load(path)
    assert loaded_content == content


def test_storage_path_structure(temp_storage):
    """Test that storage creates correct directory structure."""
    content = b"Test content"
    file_obj = io.BytesIO(content)
    
    path = "123/latex/v_5/resume.tex"
    temp_storage.save(file_obj, path)
    
    full_path = temp_storage.get_full_path(path)
    assert full_path.exists()
    assert full_path.parent.name == "v_5"
    assert full_path.parent.parent.name == "latex"
    assert full_path.parent.parent.parent.name == "123"


def test_delete_file(temp_storage):
    """Test deleting a file."""
    content = b"Test content"
    file_obj = io.BytesIO(content)
    
    path = temp_storage.save(file_obj, "1/pdf/v_1/resume.pdf")
    assert temp_storage.exists(path)
    
    temp_storage.delete(path)
    assert not temp_storage.exists(path)


def test_exists_returns_false_for_nonexistent(temp_storage):
    """Test that exists returns False for non-existent files."""
    assert not temp_storage.exists("nonexistent/path/file.pdf")


def test_multiple_versions_in_same_format(temp_storage):
    """Test storing multiple versions in the same format."""
    for version in [1, 2, 3]:
        content = f"Resume version {version}".encode()
        file_obj = io.BytesIO(content)
        path = f"1/pdf/v_{version}/resume.pdf"
        temp_storage.save(file_obj, path)
    
    # All versions should exist independently
    for version in [1, 2, 3]:
        path = f"1/pdf/v_{version}/resume.pdf"
        assert temp_storage.exists(path)
        content = temp_storage.load(path)
        assert content == f"Resume version {version}".encode()
