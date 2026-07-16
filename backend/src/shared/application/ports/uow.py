from typing import Protocol


class UoWPort[SessionType](Protocol):
    """
    Interface for the Unit of Work.
    Provides access to the transactional session.

    session is declared as a read-only property so that both the concrete
    SQLAlchemyUnitOfWork (which raises RuntimeError before __aenter__) and
    simple test mocks (which expose it as a plain attribute) satisfy the protocol.
    """

    @property
    def session(self) -> SessionType: ...
