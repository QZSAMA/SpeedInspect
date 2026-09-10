import os
import tempfile

# Tests never connect to a developer or production database.
os.environ["SECRET_KEY"] = "synthetic-test-secret"
os.environ["JWT_SECRET"] = "synthetic-test-jwt-secret"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test-unused.db"
os.environ["STORAGE_LOCAL_PATH"] = tempfile.mkdtemp(prefix="speedinspect-tests-")
