import fnmatch

from pytest_archon import archrule


def test_domain_independence():
    """Domain layer must not depend on any other layers (Application, Presentation, Infrastructure, etc.) or external frameworks."""

    def check_direct_imports(module, direct_imports, all_imports):
        forbidden = [
            "src.modules.*application*",
            "src.modules.*presentation*",
            "src.modules.*infrastructure*",
            "src.modules.*adapters*",
            "src.shared.application",
            "src.shared.presentation",
            "src.shared.infrastructure",
            "src.shared.infrastructure.adapters",
            "fastapi*",
            "sqlalchemy*",
            "celery*",
            "redis*",
            "httpx*",
            "pydantic*",
            "resend*",
        ]
        for imp in direct_imports:
            for pat in forbidden:
                if fnmatch.fnmatch(imp, pat):
                    return False
        return True

    (
        archrule("domain_independence")
        .match("src.modules.*domain*")
        .should(check_direct_imports)
        .check("src")
    )


def test_application_independence():
    """Application layer can depend on Domain, but not on Presentation, Infrastructure, Adapters, or external frameworks like FastAPI."""

    def check_direct_imports(module, direct_imports, all_imports):
        forbidden = [
            "src.modules.*presentation*",
            "src.modules.*infrastructure*",
            "src.modules.*adapters*",
            "src.shared.presentation",
            "src.shared.infrastructure",
            "src.shared.infrastructure.adapters",
            "fastapi*",
            "sqlalchemy*",
            "celery*",
            "redis*",
        ]
        for imp in direct_imports:
            for pat in forbidden:
                if fnmatch.fnmatch(imp, pat):
                    return False
        return True

    (
        archrule("application_independence")
        .match("src.modules.*application*")
        .should(check_direct_imports)
        .check("src")
    )


def test_presentation_does_not_depend_on_infrastructure():
    """Presentation layer should interact with Infrastructure ONLY via Application interfaces.
    Exception: dependencies.py acts as the DI composition root and is allowed to instantiate infrastructure.
    """

    def check_direct_imports(module, direct_imports, all_imports):
        forbidden = [
            "src.modules.*infrastructure*",
            "src.modules.*adapters*",
            "src.shared.infrastructure",
        ]

        # FastAPI dependencies are the Composition Root for the presentation layer,
        # they must import infrastructure to bind it.
        if "presentation.api.dependencies" in module:
            return True
        if "shared.presentation.api.dependencies" in module:
            return True

        for imp in direct_imports:
            for pat in forbidden:
                if fnmatch.fnmatch(imp, pat):
                    return False
        return True

    (
        archrule("presentation_infrastructure_isolation")
        .match("src.modules.*presentation*")
        .should(check_direct_imports)
        .check("src")
    )


def test_infrastructure_does_not_depend_on_presentation():
    """Infrastructure layer should not know about HTTP / Presentation layer concepts."""

    def check_direct_imports(module, direct_imports, all_imports):
        forbidden = [
            "src.modules.*presentation*",
            "src.shared.presentation",
            "src.api",
        ]
        for imp in direct_imports:
            for pat in forbidden:
                if fnmatch.fnmatch(imp, pat):
                    return False
        return True

    (
        archrule("infrastructure_presentation_isolation")
        .match("src.modules.*infrastructure*")
        .should(check_direct_imports)
        .check("src")
    )
