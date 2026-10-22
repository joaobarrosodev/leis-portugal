"""Transporte do Diário da República Eletrónico (diariodarepublica.pt).

O DRE não publica uma API documentada. Este cliente usa os mesmos pedidos
"screenservices" (OutSystems) que a aplicação web faz no browser:

1. lê o token CSRF anónimo de `OutSystems.js` e a versão do módulo de
   `moduleservices/moduleversioninfo`;
2. descobre o URL e o `apiVersion` de cada ação nos ficheiros JavaScript de cada
   ecrã, por prefixo do nome, para absorver renomeações entre deploys;
3. faz POST com o `viewName` do ecrã. Respostas HTML ou com `exception` são erros:
   nunca são tratadas como "dia sem diplomas".

As respostas são devolvidas em bruto (dicionários do DRE); a conversão para o
modelo do acervo está em `sources.dre.mapper`.
"""

from __future__ import annotations

import re
from typing import Any

from leis_portugal.errors import FetchError
from leis_portugal.infrastructure.http import HttpClient
from leis_portugal.sources.dre.constants import DRE_BASE_URL


BASE = f"{DRE_BASE_URL}/dr"
SITEMAP_CONSOLIDATED = "https://files.diariodarepublica.pt/sitemap/legislacao-consolidada-sitemap-1.xml"

_CALL_DATA_ACTION = re.compile(
    r'callDataAction\s*\(\s*"([^"]+)"\s*,\s*(?:"[0-9a-f-]{36}"\s*,\s*)?"([^"]+)"\s*,\s*"([^"]+)"'
)
_CSRF_PATTERNS = (
    r'AnonymousCSRFToken\s*=\s*"([^"]+)"',
    r'"X-CSRFToken","([^"]+)"',
    r'csrfTokenValue\s*=\s*"([^"]+)"',
)
_SITEMAP_REF = re.compile(r"/dr/(?:detalhe|legislacao-consolidada|analise-juridica/[^/]+)/([^/]+)/([^/?#]+)")

_VIEW_HOME = "Home.home"
_VIEW_PUBLISHED = "Legislacao_Conteudos.Conteudo_Detalhe"
_VIEW_AJ = "AnaliseJuridica.AnaliseJuridica"
_VIEW_CONSOLIDATED = "LegislacaoConsolidada.LegCons_Detalhe"

# ação lógica -> (ficheiro JS do ecrã, prefixos conhecidos do nome, viewName)
ACTIONS: dict[str, tuple[str, tuple[str, ...], str]] = {
    "documents_by_date": ("dr.Home.WB_Serie1_List.mvc.js", ("DataActionGetDataAndApplicationSettings",), _VIEW_HOME),
    "published_detail": (
        "dr.Legislacao_Conteudos.Conteudo_Detalhe.mvc.js",
        ("DataActionGetAllConteudoDetalhe", "DataActionGetConteudoData"),
        _VIEW_PUBLISHED,
    ),
    "associations": ("dr.AnaliseJuridica.WB_AnaliseJuridica_Associacoes.mvc.js", ("DataActionFetchAssociacoes",), _VIEW_AJ),
    "aj_element_type": ("dr.AnaliseJuridica.AnaliseJuridica.mvc.js", ("DataActionGetElementTypeAndApplicationSettings",), _VIEW_AJ),
    "aj_data": ("dr.AnaliseJuridica.AnaliseJuridica.mvc.js", ("DataActionGetData",), _VIEW_AJ),
    "cons_header": (
        "dr.LegislacaoConsolidada.LegCons_Detalhe.mvc.js",
        ("DataActionGetDiplomaFragByIdAndApplicationSetting",),
        _VIEW_CONSOLIDATED,
    ),
    "cons_snapshot": ("dr.LegislacaoConsolidada.LegCons_Detalhe.mvc.js", ("DataActionGetData",), _VIEW_CONSOLIDATED),
    "cons_timeline": (
        "dr.LegislacaoConsolidada.AlteracoesTimelineByDiplomaLegisId.mvc.js",
        ("DataActionGetConsolidacaoByDiplomaFrag",),
        _VIEW_CONSOLIDATED,
    ),
}

# Tipos de associação da análise jurídica do DRE.
ASSOCIATION_MODIFICATIONS = "162"
ASSOCIATION_CORRECTIONS = "165"


class DreApiError(FetchError):
    """O DRE respondeu fora do contrato esperado (provável redeploy)."""


def split_sitemap_ref(ref: str) -> tuple[str, str]:
    """`/dr/detalhe/lei/29-2026-1135578391` -> (`lei`, `29-2026-1135578391`)."""
    match = _SITEMAP_REF.search(ref or "")
    if not match:
        raise DreApiError(f"Referência DRE inválida: {ref!r}. Esperado algo como /dr/detalhe/lei/29-2026-1135578391.")
    return match.group(1), match.group(2)


def dre_id_from_ref(ref: str) -> str:
    return split_sitemap_ref(ref)[1].rsplit("-", 1)[-1]


class DreSession:
    """Sessão autenticada contra os endpoints screenservices do DRE."""

    def __init__(self, http: HttpClient | None = None, *, refresh_every: int = 250) -> None:
        self.http = http or HttpClient(min_interval=1.0, max_retries=3, max_backoff=30)
        self.refresh_every = refresh_every
        self._calls = 0
        self._csrf = ""
        self._module_version = ""
        self._scripts: dict[str, str] = {}
        self._endpoints: dict[str, tuple[str, str, str]] = {}

    def handshake(self) -> None:
        """Obtém o token CSRF e a versão do módulo; os endpoints são resolvidos a pedido."""
        script = self.http.get(f"{BASE}/scripts/OutSystems.js").text
        self._csrf = next((found.group(1) for pattern in _CSRF_PATTERNS if (found := re.search(pattern, script))), "")
        if not self._csrf:
            raise DreApiError("Token CSRF não encontrado em OutSystems.js; o DRE mudou o formato.")
        version = self.http.get(f"{BASE}/moduleservices/moduleversioninfo").json()
        if isinstance(version, list) and version:
            version = version[0]
        self._module_version = (version or {}).get("versionToken", "")
        if not self._module_version:
            raise DreApiError(f"versionToken em falta em moduleversioninfo: {version!r:.200}")
        self._scripts.clear()
        self._endpoints.clear()

    def _endpoint(self, action: str) -> tuple[str, str, str]:
        if action in self._endpoints:
            return self._endpoints[action]
        script_name, prefixes, view = ACTIONS[action]
        if script_name not in self._scripts:
            self._scripts[script_name] = self.http.get(f"{BASE}/scripts/{script_name}").text
        declared = {m.group(1): (m.group(2), m.group(3)) for m in _CALL_DATA_ACTION.finditer(self._scripts[script_name])}
        for prefix in prefixes:
            # Correspondência exata primeiro: "DataActionGetData" é prefixo de outras ações.
            candidates = [prefix] if prefix in declared else sorted(name for name in declared if name.startswith(prefix))
            if candidates:
                path, api_version = declared[candidates[0]]
                self._endpoints[action] = (f"{BASE}/{path.lstrip('/')}", api_version, view)
                return self._endpoints[action]
        raise DreApiError(
            f"Nenhuma ação {prefixes} em {script_name} (ações declaradas: {sorted(declared)}). "
            f"O DRE renomeou a ação: atualizar ACTIONS[{action!r}] em sources/dre/client.py."
        )

    def call(self, action: str, variables: dict[str, Any]) -> dict[str, Any]:
        """Executa uma ação de dados e devolve o objeto `data`."""
        self._calls += 1
        if not self._csrf or (self.refresh_every and self._calls % self.refresh_every == 0):
            self.handshake()
        try:
            return self._post(action, variables)
        except DreApiError:
            # Um deploy a meio da execução invalida tokens e hashes: repetir uma vez.
            self.handshake()
            return self._post(action, variables)

    def _post(self, action: str, variables: dict[str, Any]) -> dict[str, Any]:
        url, api_version, view = self._endpoint(action)
        body = {
            "versionInfo": {"moduleVersion": self._module_version, "apiVersion": api_version},
            "viewName": view,
            "screenData": {"variables": variables},
            "clientVariables": {},
        }
        response = self.http.post(
            url, json=body, headers={"X-CSRFToken": self._csrf, "Content-Type": "application/json; charset=UTF-8"}
        )
        try:
            payload = response.json()
        except ValueError as exc:
            raise DreApiError(
                f"{action} devolveu {response.headers.get('Content-Type', '?')} em vez de JSON: {response.text[:200]!r}"
            ) from exc
        if not isinstance(payload, dict):
            raise DreApiError(f"{action} devolveu {type(payload).__name__}, esperado um objeto JSON")
        if payload.get("exception"):
            info = payload["exception"]
            raise DreApiError(f"{action}: {info.get('specificType', '?')}: {info.get('message', '?')}")
        return payload.get("data") or {}


# Estruturas vazias que os ecrãs do DRE esperam receber de volta.
_ASSOC_INVERSA_EMPTY = {
    "Data": "", "Texto": "", "Sumario": "", "Diploma": "", "TipoDiploma": "", "NumeroAJ": "",
    "NumeroDiploma": "", "LinkSitemapAnaliseJuridica": "", "DiplomaLegisId": "0", "DiplomaDGOId": "0",
    "DiplomaRegTrabId": "0", "DiplomaLegacorId": "0", "DiplomaDGAPId": "0", "ActoSocietarioId": "0",
    "AcordaoSTADiplomaId": "0", "ContratoPublicoId": "0",
}
_ASSOC_DIRETA_EMPTY = {
    "Data": "1900-01-01", "Texto": "", "AssociacaoAnaliseJuridicaId": "0", "HasLink": False,
    "HasInversa": False, "DiplomaLinkId": "0", "Numero": "", "Tipo": "",
}
_EMPTY_SEARCH: dict[str, Any] = {
    "tipoConteudo": {"List": [], "EmptyListItem": ""}, "serie": {"List": [], "EmptyListItem": ""},
    "numero": "", "ano": "0", "suplemento": "0", "dataPublicacao": "",
    "dataPublicacaoDe": "1900-01-01", "dataPublicacaoAte": "1900-01-01", "parte": "", "apendice": "",
    "fasciculo": "", "tipo": {"List": [], "EmptyListItem": ""}, "emissor": {"List": [], "EmptyListItem": ""},
    "texto": "", "sumario": "", "entidadeProponente": {"List": [], "EmptyListItem": ""}, "numeroDR": "",
    "paginaInicial": "0", "paginaFinal": "0", "dataAssinatura": "", "dataDistribuicao": "",
    "entidadePrincipal": {"List": [], "EmptyListItem": ""}, "entidadeEmitente": {"List": [], "EmptyListItem": ""},
    "docType": "", "proferido": "", "processo": "", "assunto": "", "recorrente": "", "recorrido": "",
    "relator": "", "empresa": "", "concelho": "", "nif": "", "anuncio": "", "numeroDoc": "",
    "DataAssinaturaDe": "1900-01-01", "DataAssinaturaAte": "1900-01-01", "DataDistribuicaoDe": "1900-01-01",
    "DataDistribuicaoAte": "1900-01-01", "semestre": "", "IsLegConsolidadaSelected": False, "IsFromData": False,
    "DescritorList": {"List": [], "EmptyListItem": ""},
}


def _consolidated_screen(tipo: str, ano: int, frag_id: str, legis_id: str, when: str, header: dict | None) -> dict[str, Any]:
    """Estado do ecrã LegCons_Detalhe, reduzido ao que o servidor lê.

    `DataActionGetData` lê a resposta do cabeçalho do próprio estado do ecrã
    (`GetDiplomaFragByIdAndApplicationSetting`); sem ela o DRE devolve erro. A lista
    do índice vai vazia: o pedido do site com o índice tem vários MB.
    """
    return {
        "HasJurisprudenciaAssociadaVar": True, "DiplomaLegisId": legis_id, "IsRended": True,
        "ShowFragAlteracoes": False, "ShowFragDiferencas": False, "DiplomaFragId": frag_id,
        "DataSelecionada": when, "FragmentoVersaoId": "0", "ELI_HTML": "", "hasFragIdLink": False,
        "Ano": ano, "DataAux": when, "Mensagem": {"Texto": "", "IsActive": False, "AlertId": ""},
        "TituloComFragmento": "", "Description": "", "ShowRevogados": True, "LoadFiltro": False,
        "FragVersaoIndice": "0", "ShowZoom": False, "CurrentZoom": "1", "IsPageTracked": True,
        "FragmentoVersaoIdAux": "0", "IndexLinhaToScrollId": "", "IsShowConteudoRelacionado": True,
        "ShowZoomButtons": True, "TituloAux": "",
        "TipoConteudosBools": {
            key: False
            for key in ("AcordaosSTA", "Atos1", "Atos2", "AtosSocietarios", "DGAP", "DGODOUT",
                        "DiarioRepublica", "Jurisprudencia", "Legacor", "REGTRAB")
        },
        "EmissorVar": "", "PesquisaAvancada_Struct": _EMPTY_SEARCH, "IsPrint": False,
        "IsLoadingPDFConsolidacao": False, "Comes": "", "WithConteudoRevogado": True, "ModificanteFragId": "0",
        "IndiceList": {"List": [], "EmptyListItem": {}}, "IsFiltrar": False, "WithAlteracoes": True,
        "SumarioAux": "", "Tipo": tipo, "_tipoInDataFetchStatus": 1, "Key": f"{ano}-{frag_id}",
        "_keyInDataFetchStatus": 1, "GetDiplomaFragByIdAndApplicationSetting": header or {},
    }


class DreClient:
    """Pedidos ao DRE; devolve as respostas em bruto."""

    def __init__(self, session: DreSession | None = None) -> None:
        self.session = session or DreSession()

    # ------------------------------------------------------------------ Série I

    def documents_by_date(self, iso_date: str) -> list[dict[str, Any]]:
        """Todos os documentos da 1.ª Série publicados numa data."""
        data = self.session.call("documents_by_date", {"DataSelecionada": iso_date})
        issues = (data.get("DiarioByDiaList") or {}).get("List")
        if issues is None:
            # Uma lista vazia é um dia sem Diário; a falta da lista é uma mudança do DRE.
            raise DreApiError(f"documents_by_date({iso_date}) sem DiarioByDiaList; chaves: {sorted(data)}")
        return [document for issue in issues for document in ((issue.get("DiplomaLegiList") or {}).get("List") or [])]

    def published_detail(self, ref: str) -> dict[str, Any]:
        tipo, key = split_sitemap_ref(ref)
        data = self.session.call(
            "published_detail",
            {"Tipo": tipo, "_tipoInDataFetchStatus": 1, "Key": key, "_keyInDataFetchStatus": 1,
             "ParteId": "0", "_parteIdInDataFetchStatus": 1},
        )
        detail = data.get("DetalheConteudo")
        # Uma chave desconhecida devolve um registo "por omissão" (Id 0, 1900-01-01).
        if not isinstance(detail, dict) or not any(
            str(detail.get(name) or "").strip() for name in ("Numero", "ELI", "Titulo", "Sumario", "Texto", "TextoFormatado")
        ):
            raise DreApiError(f"published_detail devolveu um registo vazio para {ref}.")
        return detail

    def associations(self, ref: str, association_id: str) -> dict[str, Any]:
        """Relações da análise jurídica: `InversasList` (este diploma foi alterado por)
        e `DiretasList` (este diploma alterou)."""
        _, key = split_sitemap_ref(ref)
        return self.session.call(
            "associations",
            {
                "MaxRecordsInversas": 1000, "MaxRecordsDiretas": 1000,
                "TableValuesInversas": {"List": [], "EmptyListItem": {"Data": "", "Diploma": "", "Link": "", "Texto": ""}},
                "TableValuesDiretas": {"List": [], "EmptyListItem": {"Data": "", "Diploma": "", "Texto": ""}},
                "StartIndex": 0, "IsListaCompleta": True, "StartIndexInversas": 0,
                "InversasAuxList": {"List": [], "EmptyListItem": _ASSOC_INVERSA_EMPTY},
                "DiretasAuxList": {"List": [], "EmptyListItem": _ASSOC_DIRETA_EMPTY},
                "IsWordExportAux": False, "IsExcelExportAux": False, "IsRendered": True, "IsDone": False,
                "ListaCompletaDiretas": False, "ListaCompletaInversas": False,
                "TipoAssociacaoId": association_id, "_tipoAssociacaoIdInDataFetchStatus": 1,
                "ConteudoId": key.rsplit("-", 1)[-1], "_conteudoIdInDataFetchStatus": 1,
                "IsFrom": "AJ", "_isFromInDataFetchStatus": 1,
                "IsWordExport": False, "_isWordExportInDataFetchStatus": 1,
                "TipoExportacao": "", "_tipoExportacaoInDataFetchStatus": 1,
                "Titulo": "", "_tituloInDataFetchStatus": 1,
                "IsExcelExport": False, "_isExcelExportInDataFetchStatus": 1,
                "Tipo": "modificacoes", "_tipoInDataFetchStatus": 1,
                "Key": key, "_keyInDataFetchStatus": 1,
                "IsPrint": False, "_isPrintInDataFetchStatus": 1,
                "DataPublicacao": "1900-01-01", "_dataPublicacaoInDataFetchStatus": 1,
            },
        )

    def descriptors(self, ref: str) -> list[str]:
        """Descritores temáticos (tesauro) da análise jurídica."""
        tipo, key = split_sitemap_ref(ref)
        parts = key.rsplit("-", 2)
        numero, ano, conteudo_id = parts if len(parts) == 3 else ("", "", key.rsplit("-", 1)[-1])
        variables: dict[str, Any] = {
            "Associacao": "informacoes-gerais", "_associacaoInDataFetchStatus": 1,
            "Tipo": tipo, "_tipoInDataFetchStatus": 1, "Key": key, "_keyInDataFetchStatus": 1,
            "ConteudoId": conteudo_id, "Numero": numero, "Year": int(ano) if ano.isdigit() else 0,
            "TipoAssociacaoIdAux": "0", "HasAssociacoesEcra": True, "DiplomaFragId": "0", "IsRended": True,
            "DiplomaLegisId": "0", "DiplomaDGOId": "0", "DiplomaRegTrabId": "0", "DiplomaLegacorId": "0",
            "DiplomaDGAPId": "0", "TipoAssociacaoId": "0", "AssociacaoAnaliseJuridicaId": "0",
            "IsWordExport": False, "IsExcelExport": False, "TipoExportacao": "", "CountEcra": 0,
            "HasJurisprudenciaAssociadaVar": False, "IsDiretaChecked": True, "IsInversaChecked": True,
            "AssociacoesCounter": 0, "IsPageTracked": True, "IsShowConteudoRelacionado": True, "Print": False,
            "TotalAssociacoes": 0, "HasAssociacoesFetched": False,
        }
        element_type = self.session.call("aj_element_type", variables)
        if element_type.get("IsNullElementType"):
            return []
        variables["GetElementTypeAndApplicationSettings"] = element_type
        variables["DiplomaLegisId"] = element_type.get("DiplomaLegisIdOut", "0")
        data = self.session.call("aj_data", variables)
        names = [(entry.get("ThesaurusElementName") or "").strip() for entry in (data.get("ThesaurusTreeList") or {}).get("List") or []]
        return list(dict.fromkeys(name for name in names if name))

    # ------------------------------------------------------- legislação consolidada

    def consolidated_sitemap(self) -> bytes:
        return self.session.http.get(SITEMAP_CONSOLIDATED).content

    def consolidated_header(self, tipo: str, ano: int, frag_id: str) -> dict[str, Any]:
        """Cabeçalho do consolidado: DiplomaLegis (Id, LinkSitemap, DataPublicacao...)."""
        data = self.session.call("cons_header", _consolidated_screen(tipo, ano, frag_id, "0", "2100-01-01", None))
        if not (data.get("ConsolidadaConteudoDetalhe") or {}).get("DiplomaLegis"):
            raise DreApiError(f"Cabeçalho consolidado vazio para {tipo}/{ano}-{frag_id}")
        return data

    def consolidated_timeline(self, legis_id: str, frag_id: str) -> list[dict[str, Any]]:
        """Atos que alteraram o diploma, cada um com as modificações e datas de vigor."""
        data = self.session.call(
            "cons_timeline",
            {
                "DiplomaLegisId": legis_id, "_diplomaLegisIdInDataFetchStatus": 1,
                "DiplomaFragId": frag_id, "_diplomaFragIdInDataFetchStatus": 1,
                "Data": "2100-01-01", "_dataInDataFetchStatus": 1,
                "ModificanteFragId": "0", "_modificanteFragIdInDataFetchStatus": 1,
                "Modificacoes": {"List": [], "EmptyListItem": {}},
                "IsRendered": True, "IsRenderingFragmentoVersao": False, "IsLoadingChangesForNewDate": False,
                "ShowAllAlteracoes": True, "SelectedDiploLegisId": "0", "SelectedDataValidacao": "1900-01-01",
                "SelectedModificanteFragId": "0", "ModificanteFragIdAux": "", "DataAux": "2100-01-01",
            },
        )
        return (data.get("ModificacoesList") or {}).get("List") or []

    def consolidated_snapshot(self, tipo: str, ano: int, frag_id: str, legis_id: str, when: str, header: dict) -> list[dict[str, Any]]:
        """Todos os fragmentos do diploma, na versão em vigor na data `when`."""
        data = self.session.call("cons_snapshot", _consolidated_screen(tipo, ano, frag_id, legis_id, when, header))
        return (data.get("LegConsBase") or {}).get("List") or []
