import pytest

from reportes.config import SERVIDORES, ConfiguracionError, servidor_de_base, servidor_de_tabla


@pytest.mark.parametrize("base,servidor", [
    ("storage", "mish"), ("staging", "mish"), ("mod_rep", "mish"),
    ("dwh", "slc"), ("dma", "slc"), ("csd", "slc"), ("INTCOM", "slc"), ("slc", "slc"),
    ("dbriesgos", "rcc"), ("DBRCC", "rcc"), ("DW_Raw_v2", "rcc"), ("DW_Metadata", "rcc"),
])
def test_cada_base_vive_en_su_servidor(base, servidor):
    assert servidor_de_base(base) == servidor


def test_bases_mensuales_son_del_servidor_rcc():
    assert servidor_de_base("DB202609") == "rcc"
    assert servidor_de_tabla("db{yyyymm}.dbo.ccd{yyyymmdd}") == "rcc"


def test_linked_server_rcc_cd_se_consulta_desde_slc():
    assert servidor_de_tabla("rcc_cd.db{yyyymm}.dbo.ccp{yyyymmdd}") == "slc"


def test_tabla_por_su_base():
    assert servidor_de_tabla("storage.com_act.hcda001") == "mish"
    assert servidor_de_tabla("dwh.dbo.bregmod001") == "slc"


def test_base_desconocida_falla_claro():
    with pytest.raises(ConfiguracionError, match="config.BASES_DE"):
        servidor_de_base("no_existe")


def test_todo_servidor_mapeado_existe():
    from reportes.config import BASES_DE

    assert set(BASES_DE) == set(SERVIDORES)
