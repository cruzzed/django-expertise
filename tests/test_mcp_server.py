import pytest

from django_expertise import mcp_server


def test_build_mcp_server_requires_mcp(monkeypatch):
    def _fake_require():
        raise RuntimeError("mcp not installed")

    monkeypatch.setattr(mcp_server, "_require_mcp", _fake_require)
    with pytest.raises(RuntimeError, match="mcp not installed"):
        mcp_server.build_mcp_server()
