from typing import Any, Dict
from habits_service.habits_service.app.db.uow import UnitOfWork


async def get_context() -> Dict[str, Any]:
    uow_cm = UnitOfWork()
    uow = await uow_cm.__aenter__()

    async def finalize() -> None:
        await uow_cm.__aexit__(None, None, None)

    return {"uow": uow, "_finalize": finalize}


