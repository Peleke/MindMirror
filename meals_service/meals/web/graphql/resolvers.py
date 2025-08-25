from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

import strawberry
from strawberry.types import Info

from meals.domain.models import (
    DomainFoodItem,
    DomainMeal,
    DomainMealFood,
    DomainUserGoals,
    DomainWaterConsumption,
)
from meals.repository.repositories import (
    FoodItemRepository,
    MealRepository,
    UserGoalsRepository,
    WaterConsumptionRepository,
)
from meals.repository.uow import UnitOfWork
from meals.service.services import (
    FoodItemService,
    MealService,
    UserGoalsService,
    WaterConsumptionService,
)
from meals.service.off_mapping import map_off_product_to_autocomplete, map_off_product_to_food_create

from .types import MealFoodInput  # For MealCreateInput
from .types import MealTypeGQLEnum  # Use the renamed Python enum
from .types import (
    FoodAutocompleteResult,
    FoodItemCreateInput,
    FoodItemTypeGQL,
    FoodItemUpdateInput,
    MealCreateInput,
    MealFoodTypeGQL,
    MealTypeGQL,
    MealUpdateInput,
    UserGoalsCreateInput,
    UserGoalsTypeGQL,
    UserGoalsUpdateInput,
    WaterConsumptionCreateInput,
    WaterConsumptionTypeGQL,
    WaterConsumptionUpdateInput,
)

# Conversion functions (Domain Model -> GQL Type)


def convert_food_item_to_gql(domain_food_item: DomainFoodItem) -> FoodItemTypeGQL:
    return FoodItemTypeGQL(
        id_=strawberry.ID(str(domain_food_item.id_)),
        created_at=domain_food_item.created_at,
        modified_at=domain_food_item.modified_at,
        name=domain_food_item.name,
        serving_size=domain_food_item.serving_size,
        serving_unit=domain_food_item.serving_unit,
        calories=domain_food_item.calories,
        protein=domain_food_item.protein,
        carbohydrates=domain_food_item.carbohydrates,
        fat=domain_food_item.fat,
        saturated_fat=domain_food_item.saturated_fat,
        monounsaturated_fat=domain_food_item.monounsaturated_fat,
        polyunsaturated_fat=domain_food_item.polyunsaturated_fat,
        trans_fat=domain_food_item.trans_fat,
        cholesterol=domain_food_item.cholesterol,
        fiber=domain_food_item.fiber,
        sugar=domain_food_item.sugar,
        sodium=domain_food_item.sodium,
        potassium=domain_food_item.potassium,
        calcium=domain_food_item.calcium,
        iron=domain_food_item.iron,
        vitamin_d=domain_food_item.vitamin_d,
        zinc=domain_food_item.zinc,
        notes=domain_food_item.notes,
        user_id=domain_food_item.user_id,
        brand=domain_food_item.brand,
        thumbnail_url=domain_food_item.thumbnail_url,
        source=domain_food_item.source,
        external_source=domain_food_item.external_source,
        external_id=domain_food_item.external_id,
    )


def convert_meal_food_to_gql(domain_meal_food: DomainMealFood) -> MealFoodTypeGQL:
    return MealFoodTypeGQL(
        id_=strawberry.ID(str(domain_meal_food.id_)),
        created_at=domain_meal_food.created_at,
        modified_at=domain_meal_food.modified_at,
        meal_id=strawberry.ID(str(domain_meal_food.meal_id)),
        food_item_id=strawberry.ID(str(domain_meal_food.food_item_id)),
        quantity=domain_meal_food.quantity,
        serving_unit=domain_meal_food.serving_unit,
        food_item=convert_food_item_to_gql(domain_meal_food.food_item),
    )


def convert_meal_to_gql(domain_meal: DomainMeal) -> MealTypeGQL:
    return MealTypeGQL(
        id_=strawberry.ID(str(domain_meal.id_)),
        created_at=domain_meal.created_at,
        modified_at=domain_meal.modified_at,
        user_id=domain_meal.user_id,
        name=domain_meal.name,
        type=MealTypeGQLEnum(domain_meal.type.value),  # Ensure this uses the renamed enum
        date=domain_meal.date,
        notes=domain_meal.notes,
        meal_foods=[convert_meal_food_to_gql(mf) for mf in domain_meal.meal_foods],
    )


def convert_user_goals_to_gql(domain_user_goals: DomainUserGoals) -> UserGoalsTypeGQL:
    return UserGoalsTypeGQL(
        id_=strawberry.ID(str(domain_user_goals.id_)),
        created_at=domain_user_goals.created_at,
        modified_at=domain_user_goals.modified_at,
        user_id=domain_user_goals.user_id,
        daily_calorie_goal=domain_user_goals.daily_calorie_goal,
        daily_water_goal=domain_user_goals.daily_water_goal,
        daily_protein_goal=domain_user_goals.daily_protein_goal,
        daily_carbs_goal=domain_user_goals.daily_carbs_goal,
        daily_fat_goal=domain_user_goals.daily_fat_goal,
    )


def convert_water_consumption_to_gql(domain_wc: DomainWaterConsumption) -> WaterConsumptionTypeGQL:
    return WaterConsumptionTypeGQL(
        id_=strawberry.ID(str(domain_wc.id_)),
        created_at=domain_wc.created_at,
        modified_at=domain_wc.modified_at,
        user_id=domain_wc.user_id,
        quantity=domain_wc.quantity,
        consumed_at=domain_wc.consumed_at,
    )


@strawberry.type
class Query:
    @strawberry.field
    async def food_item(self, info: Info, id: strawberry.ID) -> Optional[FoodItemTypeGQL]:
        uow: UnitOfWork = info.context["uow"]
        async with uow:
            repo = FoodItemRepository(uow.session)
            service = FoodItemService(repo)
            item = await service.get_food_item_by_id(UUID(str(id)))
            return convert_food_item_to_gql(item) if item else None

    @strawberry.field
    async def food_items(
        self,
        info: Info,
        user_id: Optional[str] = None,
        search_term: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[FoodItemTypeGQL]:
        uow: UnitOfWork = info.context["uow"]
        async with uow:
            repo = FoodItemRepository(uow.session)
            service = FoodItemService(repo)

            if user_id:
                items = await service.list_food_items_by_user(
                    user_id=user_id, search_term=search_term, limit=limit, offset=offset
                )
            else:
                items = await service.list_food_items(search_term=search_term, limit=limit, offset=offset)
            return [convert_food_item_to_gql(item) for item in items]

    @strawberry.field
    async def food_items_for_user_with_public(
        self,
        info: Info,
        user_id: str,
        search_term: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[FoodItemTypeGQL]:
        """Get both public food items AND user's personal food items."""
        uow: UnitOfWork = info.context["uow"]
        async with uow:
            repo = FoodItemRepository(uow.session)
            service = FoodItemService(repo)
            items = await service.list_food_items_for_user_with_public(
                user_id=user_id, search_term=search_term, limit=limit, offset=offset
            )
            return [convert_food_item_to_gql(item) for item in items]

    @strawberry.field
    async def food_items_autocomplete(
        self,
        info: Info,
        query: str,
        user_id: Optional[str] = None,
        limit: int = 10,
    ) -> List[FoodAutocompleteResult]:
        """Merge local fuzzy results with OFF suggestions.
        - If query is barcode-like: fetch OFF product detail and surface as a single OFF hit
        - Else: try Search-a-licious (if enabled); otherwise return only local
        """
        try:
            print(f"[Meals] autocomplete query='{query}' user_id={user_id} limit={limit}", flush=True)
        except Exception:
            pass
        uow: UnitOfWork = info.context["uow"]
        off_client = info.context.get("off")
        results: List[FoodAutocompleteResult] = []

        # Local results first
        async with uow:
            repo = FoodItemRepository(uow.session)
            service = FoodItemService(repo)
            local_items = await service.list_food_items_for_user_with_public(
                user_id=user_id or "", search_term=query, limit=limit
            )
            for item in local_items:
                results.append(
                    FoodAutocompleteResult(
                        source="local",
                        id_=strawberry.ID(str(item.id_)),
                        external_id=item.external_id,
                        name=item.name,
                        brand=item.brand,
                        thumbnail_url=item.thumbnail_url,
                        nutrition_grades=(item.external_metadata or {}).get("nutrition_grades") if item.external_metadata else None,
                    )
                )

        # If we already have enough, return
        # Do not return early; always attempt to enrich with OFF results, then trim at the end

        # Barcode-like query: digits and length >= 8
        is_barcode_like = query.isdigit() and len(query) >= 8
        off_hits: List[FoodAutocompleteResult] = []
        if off_client and is_barcode_like:
            fields = [
                "code",
                "product_name",
                "brands",
                "image_url",
                "nutrition_grades",
                "nutriments",
                "nutriscore_data",
                "serving_size",
                "serving_quantity",
            ]
            product = off_client.get_product_by_barcode(query, fields=fields)
            if product:
                mapped = map_off_product_to_autocomplete(product)
                off_hits.append(FoodAutocompleteResult(**mapped))
        elif off_client:
            # Try full-text if enabled (async). Request a fixed number to avoid zero-size queries.
            off_page_size = max(1, min(8, limit or 8))
            for prod in await off_client.search_fulltext(query, page_size=off_page_size):
                mapped = map_off_product_to_autocomplete(prod)
                off_hits.append(FoodAutocompleteResult(**mapped))

        # De-dupe by name+brand
        seen = {(r.name.lower(), (r.brand or "").lower()) for r in results}
        for r in off_hits:
            key = (r.name.lower(), (r.brand or "").lower())
            if key not in seen:
                results.append(r)
                seen.add(key)
            if len(results) >= limit:
                break

        return results[:limit]

    @strawberry.field
    async def meal(self, info: Info, id: strawberry.ID) -> Optional[MealTypeGQL]:
        uow: UnitOfWork = info.context["uow"]
        async with uow:
            repo = MealRepository(uow.session)
            service = MealService(repo)
            item = await service.get_meal_by_id(UUID(str(id)))
            return convert_meal_to_gql(item) if item else None

    @strawberry.field
    async def meals_by_user_and_date_range(
        self,
        info: Info,
        user_id: str,
        start_date: str,
        end_date: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[MealTypeGQL]:
        uow: UnitOfWork = info.context["uow"]
        async with uow:
            repo = MealRepository(uow.session)
            service = MealService(repo)
            # The service expects date objects, Strawberry passes strings
            parsed_start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            parsed_end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
            items = await service.list_meals_by_user_and_date_range(
                user_id=user_id, start_date=parsed_start_date, end_date=parsed_end_date, limit=limit, offset=offset
            )
            return [convert_meal_to_gql(item) for item in items]

    @strawberry.field
    async def search_meals_by_user(
        self,
        info: Info,
        user_id: str,
        search_term: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[MealTypeGQL]:
        """Search meals by user with optional search term filtering."""
        uow: UnitOfWork = info.context["uow"]
        async with uow:
            repo = MealRepository(uow.session)
            service = MealService(repo)
            items = await service.list_meals_by_user(
                user_id=user_id, search_term=search_term, limit=limit, offset=offset
            )
            return [convert_meal_to_gql(item) for item in items]

    @strawberry.field
    async def user_goals(self, info: Info, user_id: str) -> Optional[UserGoalsTypeGQL]:
        uow: UnitOfWork = info.context["uow"]
        async with uow:
            repo = UserGoalsRepository(uow.session)
            service = UserGoalsService(repo)
            item = await service.get_user_goals_by_user_id(user_id)
            return convert_user_goals_to_gql(item) if item else None

    @strawberry.field
    async def water_consumption(self, info: Info, id: strawberry.ID) -> Optional[WaterConsumptionTypeGQL]:
        uow: UnitOfWork = info.context["uow"]
        async with uow:
            repo = WaterConsumptionRepository(uow.session)
            service = WaterConsumptionService(repo)
            item = await service.get_water_consumption_by_id(UUID(str(id)))
            return convert_water_consumption_to_gql(item) if item else None

    @strawberry.field
    async def water_consumptions_by_user_and_date_range(
        self,
        info: Info,
        user_id: str,
        start_date: str,
        end_date: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[WaterConsumptionTypeGQL]:
        uow: UnitOfWork = info.context["uow"]
        async with uow:
            repo = WaterConsumptionRepository(uow.session)
            service = WaterConsumptionService(repo)
            parsed_start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            parsed_end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
            items = await service.list_water_consumption_by_user_and_date_range(
                user_id=user_id, start_date=parsed_start_date, end_date=parsed_end_date, limit=limit, offset=offset
            )
            return [convert_water_consumption_to_gql(item) for item in items]

    @strawberry.field
    async def total_water_consumption_by_user_and_date(self, info: Info, user_id: str, date_str: str) -> float:
        uow: UnitOfWork = info.context["uow"]
        async with uow:
            repo = WaterConsumptionRepository(uow.session)
            service = WaterConsumptionService(repo)
            parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            total = await service.get_total_water_consumption_by_user_and_date(user_id, parsed_date)
            return total


@strawberry.type
class Mutation:
    @strawberry.field
    async def create_food_item(self, info: Info, input: FoodItemCreateInput) -> FoodItemTypeGQL:
        uow: UnitOfWork = info.context["uow"]
        async with uow:
            repo = FoodItemRepository(uow.session)
            service = FoodItemService(repo)
            # Convert Strawberry input to dict for service
            item_data = strawberry.asdict(input)
            created_item = await service.create_food_item(item_data)
            await uow.commit()
            return convert_food_item_to_gql(created_item)

    @strawberry.field
    async def import_off_product(self, info: Info, code: str, user_id: Optional[str] = None) -> Optional[FoodItemTypeGQL]:
        """Import an OFF product by barcode into our DB, idempotently."""
        uow: UnitOfWork = info.context["uow"]
        off_client = info.context.get("off")
        if not off_client:
            return None

        fields = [
            "code",
            "product_name",
            "brands",
            "image_url",
            "nutrition_grades",
            "nutriments",
            "nutriscore_data",
            "serving_size",
            "serving_quantity",
        ]
        product = off_client.get_product_by_barcode(code, fields=fields)
        if not product:
            return None

        async with uow:
            repo = FoodItemRepository(uow.session)
            service = FoodItemService(repo)

            # Check if already imported
            existing = await repo.search_food_items_by_name(product.get("product_name", ""), limit=50)
            for item in existing:
                if item.external_source == "openfoodfacts" and item.external_id == product.get("code"):
                    return convert_food_item_to_gql(item)

            # Map and create
            create_dict = map_off_product_to_food_create(product)
            if user_id:
                create_dict["user_id"] = user_id
            created = await service.create_food_item(create_dict)
            return convert_food_item_to_gql(created)

    @strawberry.field
    async def update_food_item(
        self, info: Info, id: strawberry.ID, input: FoodItemUpdateInput
    ) -> Optional[FoodItemTypeGQL]:
        uow: UnitOfWork = info.context["uow"]
        async with uow:
            repo = FoodItemRepository(uow.session)
            service = FoodItemService(repo)
            update_data = strawberry.asdict(input)
            # Filter out None values, so service layer can handle partial updates
            update_data_filtered = {k: v for k, v in update_data.items() if v is not None}
            updated_item = await service.update_food_item(UUID(str(id)), update_data_filtered)
            if updated_item:
                return convert_food_item_to_gql(updated_item)
            return None

    @strawberry.field
    async def delete_food_item(self, info: Info, id: strawberry.ID) -> bool:
        uow: UnitOfWork = info.context["uow"]
        async with uow:
            repo = FoodItemRepository(uow.session)
            service = FoodItemService(repo)
            result = await service.delete_food_item(UUID(str(id)))
            return result

    @strawberry.field
    async def create_meal(self, info: Info, input: MealCreateInput) -> MealTypeGQL:
        uow: UnitOfWork = info.context["uow"]
        async with uow:
            repo = MealRepository(uow.session)
            service = MealService(repo)
            item_data = strawberry.asdict(input)
            # Convert MealFoodInput list within meal_foods_data
            if "meal_foods_data" in item_data and item_data["meal_foods_data"] is not None:
                item_data["meal_foods_data"] = [strawberry.asdict(mf_input) for mf_input in input.meal_foods_data]

            created_item = await service.create_meal(item_data)
            return convert_meal_to_gql(created_item)

    @strawberry.field
    async def update_meal(self, info: Info, id: strawberry.ID, input: MealUpdateInput) -> Optional[MealTypeGQL]:
        uow: UnitOfWork = info.context["uow"]
        async with uow:
            repo = MealRepository(uow.session)
            service = MealService(repo)
            update_data = strawberry.asdict(input)
            update_data_filtered = {k: v for k, v in update_data.items() if v is not None}
            updated_item = await service.update_meal(UUID(str(id)), update_data_filtered)
            if updated_item:
                await uow.commit()
                return convert_meal_to_gql(updated_item)
            return None

    @strawberry.field
    async def delete_meal(self, info: Info, id: strawberry.ID) -> bool:
        uow: UnitOfWork = info.context["uow"]
        async with uow:
            repo = MealRepository(uow.session)
            service = MealService(repo)
            result = await service.delete_meal(UUID(str(id)))
            if result:
                await uow.commit()
            return result

    @strawberry.field
    async def add_food_to_meal(
        self, info: Info, meal_id: strawberry.ID, food_item_id: strawberry.ID, quantity: float, serving_unit: str
    ) -> Optional[MealTypeGQL]:
        uow: UnitOfWork = info.context["uow"]
        async with uow:
            repo = MealRepository(uow.session)
            service = MealService(repo)
            updated_meal = await service.add_food_to_meal(
                meal_id=UUID(str(meal_id)),
                food_item_id=UUID(str(food_item_id)),
                quantity=quantity,
                serving_unit=serving_unit,
            )
            if updated_meal:
                await uow.commit()
                return convert_meal_to_gql(updated_meal)
            return None

    @strawberry.field
    async def remove_food_from_meal(
        self, info: Info, meal_id: strawberry.ID, food_item_id: strawberry.ID
    ) -> Optional[MealTypeGQL]:
        uow: UnitOfWork = info.context["uow"]
        async with uow:
            repo = MealRepository(uow.session)
            service = MealService(repo)
            updated_meal = await service.remove_food_from_meal(UUID(str(meal_id)), UUID(str(food_item_id)))
            if updated_meal:
                await uow.commit()
                return convert_meal_to_gql(updated_meal)
            return None

    @strawberry.field
    async def create_user_goals(self, info: Info, input: UserGoalsCreateInput) -> UserGoalsTypeGQL:
        uow: UnitOfWork = info.context["uow"]
        async with uow:
            repo = UserGoalsRepository(uow.session)
            service = UserGoalsService(repo)
            item_data = strawberry.asdict(input)
            created_item = await service.create_user_goals(item_data)
            await uow.commit()
            return convert_user_goals_to_gql(created_item)

    @strawberry.field
    async def update_user_goals(
        self, info: Info, user_id: str, input: UserGoalsUpdateInput
    ) -> Optional[UserGoalsTypeGQL]:
        uow: UnitOfWork = info.context["uow"]
        async with uow:
            repo = UserGoalsRepository(uow.session)
            service = UserGoalsService(repo)
            update_data = strawberry.asdict(input)
            update_data_filtered = {k: v for k, v in update_data.items() if v is not None}
            # The service layer expects to update by user_id for UserGoals
            updated_item = await service.update_user_goals_by_user_id(user_id, update_data_filtered)
            if updated_item:
                await uow.commit()
                return convert_user_goals_to_gql(updated_item)
            return None

    @strawberry.field
    async def upsert_user_goals(
        self, info: Info, user_id: str, input: UserGoalsCreateInput
    ) -> UserGoalsTypeGQL:  # Upsert uses CreateInput for all fields
        uow: UnitOfWork = info.context["uow"]
        async with uow:
            repo = UserGoalsRepository(uow.session)
            service = UserGoalsService(repo)
            item_data = strawberry.asdict(input)  # Input should contain all necessary fields for create or update
            # Ensure user_id from path is used, not from input if present, though UserGoalsCreateInput has user_id
            item_data["user_id"] = user_id
            upserted_item = await service.upsert_user_goals(user_id, item_data)
            await uow.commit()
            return convert_user_goals_to_gql(upserted_item)

    @strawberry.field
    async def delete_user_goals(self, info: Info, user_id: str) -> bool:  # UserGoals are deleted by user_id in service
        uow: UnitOfWork = info.context["uow"]
        async with uow:
            repo = UserGoalsRepository(uow.session)
            service = UserGoalsService(repo)
            # The service delete_user_goals_by_user_id takes user_id
            # Assuming there's a get_user_goals_by_user_id to get the ID first, or service handles deletion by user_id directly
            # For now, let's assume the service can delete by user_id or we get the ID first.
            # Simpler: if service.delete_user_goals expects an ID, we need to fetch it first.
            # Let's adjust to a more direct approach if service allows direct delete by user_id
            # Or, if the GQL schema is to delete by the UserGoals specific ID (UUID)
            # The current UserGoalsService delete method expects the specific goal ID (UUID), not user_id.
            # We need to get the goal ID from user_id first.
            goals_to_delete = await service.get_user_goals_by_user_id(user_id)
            if goals_to_delete:
                result = await service.delete_user_goals(goals_to_delete.id_)
                if result:
                    await uow.commit()
                return result
            return False

    @strawberry.field
    async def create_water_consumption(self, info: Info, input: WaterConsumptionCreateInput) -> WaterConsumptionTypeGQL:
        uow: UnitOfWork = info.context["uow"]
        async with uow:
            repo = WaterConsumptionRepository(uow.session)
            service = WaterConsumptionService(repo)
            item_data = strawberry.asdict(input)
            created_item = await service.create_water_consumption(item_data)
            await uow.commit()
            return convert_water_consumption_to_gql(created_item)

    @strawberry.field
    async def update_water_consumption(
        self, info: Info, id: strawberry.ID, input: WaterConsumptionUpdateInput
    ) -> Optional[WaterConsumptionTypeGQL]:
        uow: UnitOfWork = info.context["uow"]
        async with uow:
            repo = WaterConsumptionRepository(uow.session)
            service = WaterConsumptionService(repo)
            update_data = strawberry.asdict(input)
            update_data_filtered = {k: v for k, v in update_data.items() if v is not None}
            updated_item = await service.update_water_consumption(UUID(str(id)), update_data_filtered)
            if updated_item:
                await uow.commit()
                return convert_water_consumption_to_gql(updated_item)
            return None

    @strawberry.field
    async def delete_water_consumption(self, info: Info, id: strawberry.ID) -> bool:
        uow: UnitOfWork = info.context["uow"]
        async with uow:
            repo = WaterConsumptionRepository(uow.session)
            service = WaterConsumptionService(repo)
            result = await service.delete_water_consumption(UUID(str(id)))
            if result:
                await uow.commit()
            return result

