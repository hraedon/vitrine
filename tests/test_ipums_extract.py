import hashlib
import io
import json
import sys
from pathlib import Path
from urllib.error import HTTPError

import pytest

from scripts import ipums_extract as ipums


def test_api_v2_and_1950_definition(monkeypatch: pytest.MonkeyPatch) -> None:
    seen = []

    def fake_open(request):
        seen.append(request)
        return io.BytesIO(json.dumps({"number": 42, "status": "queued"}).encode())

    monkeypatch.setattr(ipums, "_open", fake_open)
    monkeypatch.setattr(ipums.IpumsClient, "_throttle", lambda _: None)
    client = ipums.IpumsClient("secret-key")
    spec = ipums.build_1950_family_income_extract()
    assert spec["sample_ids"] == ["us1950a"]
    assert {"FTOTINC", "SLWT", "METRO"}.issubset(spec["variables"])
    result = client.submit_extract(**spec)
    assert result["number"] == 42
    assert "version=2" in seen[0].full_url
    assert seen[0].get_header("Authorization") == "secret-key"
    assert json.loads(seen[0].data)["samples"] == {"us1950a": {}}
    with pytest.raises(ValueError):
        ipums.build_vitrine_extract("1950")


def test_download_separate_auth_validate_atomic(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    data = b"sample output"
    digest = hashlib.sha256(data).hexdigest()
    client = ipums.IpumsClient("secret-key")
    url = "https://api.ipums.org/downloads/usa_00042.csv.gz?token=private"
    metadata = {"url": url, "bytes": len(data), "sha256": digest}
    monkeypatch.setattr(
        client,
        "get_status",
        lambda _: {
            "status": "completed",
            "extractDefinition": {"downloadLinks": {"data": metadata}},
        },
    )
    monkeypatch.setattr(client, "_throttle", lambda: None)
    requests = []

    def open_download(request):
        requests.append(request)
        return io.BytesIO(data)

    monkeypatch.setattr(ipums, "_open", open_download)
    paths = client.download_extract(42, tmp_path)
    assert paths[0].name == "usa_00042.csv.gz"
    assert paths[0].read_bytes() == data
    assert requests[0].get_header("Authorization") is None
    with pytest.raises(FileExistsError):
        client.download_extract(42, tmp_path)
    paths[0].unlink()
    metadata["sha256"] = "0" * 64
    with pytest.raises(RuntimeError, match="digest mismatch"):
        client.download_extract(42, tmp_path)
    assert not list(tmp_path.iterdir())
    metadata["sha256"] = digest
    metadata["bytes"] = len(data) + 1
    with pytest.raises(RuntimeError, match="size mismatch"):
        client.download_extract(42, tmp_path)
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize(
    "url",
    [
        "http://api.ipums.org/usa_00042.csv.gz",
        "https://ipums.org.evil.example/usa_00042.csv.gz",
        "https://ipums.org@evil.example/usa_00042.csv.gz",
        "https://api.ipums.org/../usa_00042.csv.gz",
        "https://api.ipums.org/%2e%2e/usa_00042.csv.gz",
        "https://api.ipums.org/usa_00041.csv.gz",
        "https://api.ipums.org/usa_00042.exe",
    ],
)
def test_invalid_download_urls(url: str) -> None:
    with pytest.raises(ValueError):
        ipums._safe_download(url, "usa", 42)


def test_http_error_hides_url_and_body(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeOpener:
        def open(self, request, timeout):
            raise HTTPError(
                "https://secret.invalid/", 403, "email@example.com", {}, io.BytesIO(b"secret")
            )

    monkeypatch.setattr(ipums, "build_opener", lambda *_: FakeOpener())
    from urllib.request import Request

    with pytest.raises(RuntimeError) as exc:
        ipums._open(Request("https://api.ipums.org/"))
    assert str(exc.value) == "HTTP request failed (status 403)"


def test_status_cli_hides_response_secrets(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("IPUMS_API_KEY", "secret-key")
    monkeypatch.setattr(
        ipums.IpumsClient,
        "get_status",
        lambda *_: {
            "status": "completed",
            "email": "person@example.com",
            "downloadLinks": {"data": "https://example.com/?secret"},
        },
    )
    monkeypatch.setattr(sys, "argv", ["ipums_extract", "--status", "42"])
    ipums.main()
    assert capsys.readouterr().out == "Status: completed\n"


def test_list_extracts_v2_page_envelope(monkeypatch: pytest.MonkeyPatch) -> None:
    client = ipums.IpumsClient("secret-key")
    response = {
        "data": [{"number": 42, "status": "completed", "email": "private@example.com"}],
        "totalCount": 1,
        "pageNumber": 1,
        "pageSize": 10,
        "links": {"next": "https://api.ipums.org/?private=token"},
    }
    monkeypatch.setattr(client, "_request", lambda method, path: response)
    assert client.list_extracts() == response["data"]
    response["data"] = "invalid"
    with pytest.raises(RuntimeError, match="Invalid API response"):
        client.list_extracts()


@pytest.mark.parametrize(
    ("url", "authenticated"),
    [
        ("https://api.ipums.org/downloads/usa/api/v1/extracts/901/usa_00042.sts", True),
        ("https://api.ipums.org/downloads/usa/api/v1/extracts/901/usa_00042.csv.gz?token=x", True),
        ("https://demo.api.ipums.org/downloads/usa/api/v1/extracts/901/usa_00042.sts", False),
        ("https://api.ipums.org/downloads/usa/api/v1/extracts/notdigits/usa_00042.sts", False),
        ("https://api.ipums.org/other/usa_00042.sts", False),
        ("https://api.ipums.org:443/downloads/usa/api/v1/extracts/901/usa_00042.sts", False),
    ],
)
def test_download_auth_only_protected_api_path(
    url: str, authenticated: bool, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    client = ipums.IpumsClient("secret-key")
    monkeypatch.setattr(client, "_throttle", lambda: None)
    monkeypatch.setattr(
        client,
        "get_status",
        lambda _: {"status": "completed", "downloadLinks": {"file": {"url": url}}},
    )
    requests = []

    def fake_open(request):
        requests.append(request)
        return io.BytesIO(b"data")

    monkeypatch.setattr(ipums, "_open", fake_open)
    client.download_extract(42, tmp_path)
    assert requests[0].get_header("Authorization") == ("secret-key" if authenticated else None)
