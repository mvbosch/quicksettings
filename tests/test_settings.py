import pytest

from .conftest import BasicSettings, BoolSettings


def test_literal_values(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv("WEIGHT", "0.085")
    monkeypatch.setenv("PORT", "8080")
    monkeypatch.setenv("DESCRIPTION", "This is a test")
    settings = BasicSettings()
    assert settings.DEBUG is True
    assert settings.WEIGHT == 0.085
    assert settings.PORT == 8080
    assert settings.DESCRIPTION == "This is a test"


def test_env_prefix(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_DEBUG", "true")
    monkeypatch.setenv("APP_WEIGHT", "0.085")
    monkeypatch.setenv("APP_PORT", "8080")
    monkeypatch.setenv("APP_DESCRIPTION", "This is a test")
    monkeypatch.setattr(BasicSettings, "_env_prefix", "APP_")
    settings = BasicSettings()
    assert settings.DEBUG is True
    assert settings.WEIGHT == 0.085
    assert settings.PORT == 8080
    assert settings.DESCRIPTION == "This is a test"


@pytest.mark.parametrize(
    "value", ["true", "1", "yes", "y", "t", "TRUE", "YES", "Y", "T"]
)
def test_true_bool_values(monkeypatch: pytest.MonkeyPatch, value: str) -> None:
    monkeypatch.setenv("DEBUG", value)
    settings = BoolSettings()
    assert settings.DEBUG is True


@pytest.mark.parametrize(
    "value", ["false", "0", "no", "n", "f", "FALSE", "NO", "N", "F"]
)
def test_false_bool_values(monkeypatch: pytest.MonkeyPatch, value: str) -> None:
    monkeypatch.setenv("DEBUG", value)
    settings = BoolSettings()
    assert settings.DEBUG is False


@pytest.mark.parametrize("value", ["treu", "fasl", "production", "debug", "who"])
def test_invalid_bool_values(monkeypatch: pytest.MonkeyPatch, value: str) -> None:
    monkeypatch.setenv("DEBUG", value)
    with pytest.raises(ValueError):
        BoolSettings()
