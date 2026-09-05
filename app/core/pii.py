from functools import lru_cache

from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine


@lru_cache
def _analyzer() -> AnalyzerEngine:
    # en_core_web_sm (not Presidio's default en_core_web_lg) to keep the
    # worker image small - lower NER recall on names/addresses is an accepted
    # trade-off for now; upgrade the model here if that proves insufficient.
    provider = NlpEngineProvider(
        nlp_configuration={
            "nlp_engine_name": "spacy",
            "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}],
        }
    )
    return AnalyzerEngine(nlp_engine=provider.create_engine())


@lru_cache
def _anonymizer() -> AnonymizerEngine:
    return AnonymizerEngine()


def mask_pii(text: str) -> str:
    """Replace detected PII (names, emails, phone numbers, SSNs, credit cards,
    addresses, etc.) with type placeholders (e.g. "<PERSON>", "<EMAIL_ADDRESS>")
    before the text is embedded/indexed - the searchable vector store should
    never hold raw PII, per GDPR data-minimization."""
    if not text.strip():
        return text
    results = _analyzer().analyze(text=text, language="en")
    return _anonymizer().anonymize(text=text, analyzer_results=results).text
