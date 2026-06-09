import pytest
import requests

POLICY_URL = "http://localhost:8001/validate"

ALLOWED_TYPES = ["docker", "aws", "ec2"]
ALLOWED_ENVS = ["dev", "test", "qa", "staging"]

def validate_inputs(type: str, env: str):
    if not type or not type.strip():
        return "type cannot be empty"
    if not env or not env.strip():
        return "env cannot be empty"
    if type.lower() not in ALLOWED_TYPES:
        return f"Invalid type: {type}"
    if env.lower() not in ALLOWED_ENVS:
        return f"Invalid env: {env}"
    return None

def call_policy(type: str, env: str, user: str = "yakhaiyum") -> dict:
    resp = requests.post(POLICY_URL, json={"type": type, "env": env, "user": user}, timeout=10)
    resp.raise_for_status()
    return resp.json()

def test_policy_engine_is_running():
    resp = requests.post(POLICY_URL, json={"type": "docker", "env": "dev", "user": "testuser"}, timeout=5)
    assert resp.status_code == 200

def test_docker_dev_is_allowed():
    assert call_policy("docker", "dev")["allowed"] is True

def test_docker_test_is_allowed():
    assert call_policy("docker", "test")["allowed"] is True

def test_aws_dev_is_allowed():
    assert call_policy("aws", "dev")["allowed"] is True

def test_aws_staging_is_allowed():
    assert call_policy("aws", "staging")["allowed"] is True

def test_aws_prod_is_denied():
    assert call_policy("aws", "prod")["allowed"] is False

def test_gcp_dev_is_denied():
    assert call_policy("gcp", "dev")["allowed"] is False

def test_unauthorized_user_is_denied():
    assert call_policy("docker", "dev", user="hacker")["allowed"] is False

def test_empty_type_is_invalid():
    assert validate_inputs("", "dev") is not None

def test_empty_env_is_invalid():
    assert validate_inputs("docker", "") is not None

def test_invalid_type_is_rejected():
    assert validate_inputs("gcp", "dev") is not None

def test_invalid_env_is_rejected():
    assert validate_inputs("docker", "prod") is not None

def test_valid_inputs_pass():
    assert validate_inputs("docker", "dev") is None

def test_valid_aws_qa_passes():
    assert validate_inputs("aws", "qa") is None