from pathlib import Path

BASE = Path(__file__).parent

class intent:
    @staticmethod
    def build(history: str, nl_query: str) -> str:
        return (BASE / "intent_router.txt").read_text().replace("{history}", history).replace("{nl_query}", nl_query)

class plan:
    @staticmethod
    def build(nl_query: str, schema_hint: str) -> str:
        return (BASE / "plan_sql.txt").read_text().replace("{nl_query}", nl_query).replace("{schema_hint}", schema_hint)

class repair:
    @staticmethod
    def build(sql: str, error: str, schema_hint: str) -> str:
        return (BASE / "repair_sql.txt").read_text().replace("{sql}", sql).replace("{error}", error).replace("{schema_hint}", schema_hint)

class rewrite:
    @staticmethod
    def build(history: str, followup: str) -> str:
        return (BASE / "rewrite_followup.txt").read_text().replace("{history}", history).replace("{followup}", followup)

class clarify:
    @staticmethod
    def build(history: str, nl_query: str) -> str:
        return (BASE / "clarify.txt").read_text().replace("{history}", history).replace("{nl_query}", nl_query)
