import os
import pytest
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv(dotenv_path=os.environ.get("TEST_ENV_FILE", None))

def pytest_addoption(parser):
    parser.addoption("--base-url", action="store", default=os.environ.get("API_BASE","http://localhost:8888"))
    parser.addoption("--neo4j-uri", action="store", default=os.environ.get("NEO4J_URI","bolt://localhost:7687"))
    parser.addoption("--neo4j-user", action="store", default=os.environ.get("NEO4J_USER"))
    parser.addoption("--neo4j-password", action="store", default=os.environ.get("NEO4J_PASSWORD"))
    parser.addoption("--neo4j-db", action="store", default=os.environ.get("NEO4J_DATABASE"))
    parser.addoption("--wal-dir", action="store", default=os.environ.get("WAL_DIR"))
    parser.addoption("--device-id", action="store", default=os.environ.get("TEST_DEVICE_ID","test-device"))

@pytest.fixture(scope="session")
def base_url(pytestconfig):
    return pytestconfig.getoption("--base-url")

@pytest.fixture(scope="session")
def neo4j_session(pytestconfig):
    uri = pytestconfig.getoption("--neo4j-uri")
    user = pytestconfig.getoption("--neo4j-user")
    pwd  = pytestconfig.getoption("--neo4j-password")
    db   = pytestconfig.getoption("--neo4j-db") or None
    if not (uri and user and pwd):
        pytest.skip("Neo4j credentials not provided; skipping DB assertions")
    driver = GraphDatabase.driver(uri, auth=(user, pwd))
    sess = driver.session(database=db)
    yield sess
    sess.close()
    driver.close()

@pytest.fixture(scope="session")
def wal_dir(pytestconfig):
    wd = pytestconfig.getoption("--wal-dir")
    if not wd or not os.path.isdir(wd):
        pytest.skip("WAL_DIR not available; skipping WAL assertions")
    return wd

@pytest.fixture
def unique_device(pytestconfig):
    base = pytestconfig.getoption("--device-id")
    import uuid
    return f"{base}-{uuid.uuid4().hex[:8]}"
