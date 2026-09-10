from uuid import uuid4

import pytest

from src.app.features.files.service import FileService


@pytest.fixture
def stored_file(tmp_path):
    owner, other, file_id = str(uuid4()), str(uuid4()), str(uuid4())
    directory = tmp_path / owner
    directory.mkdir()
    path = directory / f"{file_id}.webm"
    path.write_bytes(b"synthetic-video")
    service = FileService()
    service.local_path = tmp_path
    return service, owner, other, file_id, path


async def test_owner_can_read(stored_file):
    service, owner, _, file_id, path = stored_file
    assert await service.get_file_path(file_id, owner) == path


async def test_other_user_cannot_read(stored_file):
    service, _, other, file_id, _ = stored_file
    assert await service.get_file_path(file_id, other) is None


async def test_other_user_cannot_delete(stored_file):
    service, _, other, file_id, path = stored_file
    assert await service.delete_file(file_id, other) is False
    assert path.exists()


async def test_missing_owner_cannot_read(stored_file):
    service, _, _, file_id, _ = stored_file
    assert await service.get_file_path(file_id) is None


@pytest.mark.parametrize("file_id", ["*", "../*", "../../secret", "not-a-uuid"])
async def test_invalid_file_identifiers_are_rejected(stored_file, file_id):
    service, owner, _, _, _ = stored_file
    assert await service.get_file_path(file_id, owner) is None


async def test_invalid_owner_is_rejected(stored_file):
    service, _, _, file_id, _ = stored_file
    assert await service.get_file_path(file_id, "../") is None
