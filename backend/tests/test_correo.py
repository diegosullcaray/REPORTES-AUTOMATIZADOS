import pytest

from reportes.comun import correo
from reportes.config import ConfiguracionError


def _env(monkeypatch, **extra):
    for k in ("SMTP_USER", "SMTP_PASSWORD", "SMTP_PORT", "LOGO_PATH", "GOOGLE_CHAT_WEBHOOK_URL", "CORREO_PRUEBA"):
        monkeypatch.delenv(k, raising=False)
    for k, v in extra.items():
        monkeypatch.setenv(k, v)


def test_sin_cuenta_en_el_env_pide_configurarla(monkeypatch):
    _env(monkeypatch)
    with pytest.raises(ConfiguracionError, match="SMTP_USER y SMTP_PASSWORD"):
        correo.config_desde_env()


def test_valores_por_defecto_y_opcionales(monkeypatch):
    _env(monkeypatch, SMTP_USER="mis@confianza.pe", SMTP_PASSWORD="x")
    cfg = correo.config_desde_env()
    assert (cfg.host, cfg.puerto, cfg.correo_prueba, cfg.logo, cfg.webhook) == ("smtp.gmail.com", 465, "diego.sullcaray@confianza.pe", None, None)
    assert cfg.remitente_nombre == "Sistemas de Información de Gestión" and cfg.remitente.endswith("<mis@confianza.pe>")   # nombre con tildes codificado en el encabezado


def test_puerto_invalido(monkeypatch):
    _env(monkeypatch, SMTP_USER="u", SMTP_PASSWORD="p", SMTP_PORT="abc")
    with pytest.raises(ConfiguracionError, match="SMTP_PORT"):
        correo.config_desde_env()


def test_lista_inexistente_o_vacia(tmp_path):
    with pytest.raises(ConfiguracionError, match="No existe"):
        correo.leer_destinatarios(tmp_path / "no.txt")
    vacia = tmp_path / "v.txt"
    vacia.write_text("# solo comentarios\n\n", encoding="utf-8")
    with pytest.raises(ConfiguracionError, match="vacía"):
        correo.leer_destinatarios(vacia)


def test_mensaje_html_con_imagen_en_linea_y_adjunto(monkeypatch, tmp_path):
    _env(monkeypatch, SMTP_USER="mis@confianza.pe", SMTP_PASSWORD="x")
    img, xlsx = tmp_path / "r.jpg", tmp_path / "d.xlsx"
    img.write_bytes(b"\xff\xd8\xff\xd9")
    xlsx.write_bytes(b"PK")
    msg = correo.construir_mensaje(correo.config_desde_env(), "Asunto", "<p><img src='cid:Reporte_Temporal.jpg'></p>", ["a@x.pe", "b@x.pe"],
                                   en_linea={"Reporte_Temporal.jpg": img}, adjuntos=[xlsx])
    assert msg["To"] == "a@x.pe, b@x.pe" and msg["Subject"] == "Asunto"
    assert [p.get_filename() for p in msg.walk() if p.get_filename()] == ["r.jpg", "d.xlsx"]
    assert any(p["Content-ID"] == "<Reporte_Temporal.jpg>" for p in msg.walk())
