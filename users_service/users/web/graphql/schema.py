from typing import Any, List, Optional

import strawberry

from users.repository.models import DomainModel

from .resolvers import Mutation, Query
from .scalars import UUID, DomainScalar
from .types import (
    AssociationStatusGQL,
    CoachClientAssociationGQL,
    DomainGQL,
    RoleGQL,
    SchedulableTypeGQL,
    ServiceTypeGQL,
    ServiceTypeGQL_Type,
    UserRoleTypeGQL,
    UserServiceLinkTypeGQL,
    UserTypeGQL,
)


def get_schema(extensions: Optional[List[Any]] = None):
    return strawberry.federation.Schema(
        query=Query,
        mutation=Mutation,
        types=[
            UserTypeGQL,
            ServiceTypeGQL_Type,
            SchedulableTypeGQL,
            UserServiceLinkTypeGQL,
            UserRoleTypeGQL,
            CoachClientAssociationGQL,
        ],
        enable_federation_2=True,
        extensions=extensions or [],
    )


schema = get_schema()

__all__ = ["schema", "get_schema"]
