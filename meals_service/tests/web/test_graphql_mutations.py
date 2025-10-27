from datetime import date, datetime, timedelta, timezone
from uuid import uuid4

import pytest

# Assume 'client' fixture for httpx.AsyncClient and 'seed_db_meals' for test data setup
# from conftest import client, seed_db_meals # Adjust as per your conftest.py

# --- FoodItem Mutations --- #
CREATE_FOOD_ITEM_MUTATION = """
    mutation CreateFoodItem($input: FoodItemCreateInput!) {
      createFoodItem(input: $input) {
        id_
        name
        calories
        protein
        # other fields
      }
    }
"""

UPDATE_FOOD_ITEM_MUTATION = """
    mutation UpdateFoodItem($id: ID!, $input: FoodItemUpdateInput!) {
      updateFoodItem(id: $id, input: $input) {
        id_
        name
        calories
        # other fields
      }
    }
"""

DELETE_FOOD_ITEM_MUTATION = """
    mutation DeleteFoodItem($id: ID!) {
      deleteFoodItem(id: $id)
    }
"""

GET_FOOD_ITEM_QUERY = """ # For verifying create/delete
    query GetFoodItem($id: ID!) {
      foodItem(id: $id) {
        id_
        name
      }
    }
"""


@pytest.mark.asyncio
async def test_create_food_item(client, docker_compose_up_down, seed_db):
    unique_name = f"Test Apple {uuid4()}"
    variables = {
        "input": {
            "name": unique_name,
            "servingSize": 100.0,
            "servingUnit": "g",
            "calories": 52.0,
            "protein": 0.3,
            "carbohydrates": 14.0,
            "fat": 0.2,
            "userId": seed_db["user_goals"].user_id,  # Use a valid user ID from user_goals
        }
    }
    response = await client.post("/graphql", json={"query": CREATE_FOOD_ITEM_MUTATION, "variables": variables})
    assert response.status_code == 200
    data = response.json()
    assert data.get("errors") is None, f"GraphQL Errors: {data.get('errors')}"
    created_item = data["data"]["createFoodItem"]
    assert created_item["id_"] is not None
    assert created_item["name"] == unique_name
    assert created_item["calories"] == 52.0


@pytest.mark.asyncio
async def test_update_food_item(client, docker_compose_up_down, seed_db):
    food_item_to_update = seed_db["apple"]  # Changed from "food_item" to "apple"
    food_item_id = str(food_item_to_update.id_)
    updated_name = f"Super Banana {uuid4()}"
    variables = {
        "id": food_item_id,
        "input": {
            "name": updated_name,
            "calories": 110.0,  # Updated calories
            # Only include fields to update
        },
    }
    response = await client.post("/graphql", json={"query": UPDATE_FOOD_ITEM_MUTATION, "variables": variables})
    assert response.status_code == 200
    data = response.json()
    assert data.get("errors") is None, f"GraphQL Errors: {data.get('errors')}"
    updated_item = data["data"]["updateFoodItem"]
    assert updated_item["id_"] == food_item_id
    assert updated_item["name"] == updated_name
    assert updated_item["calories"] == 110.0


@pytest.mark.asyncio
async def test_delete_food_item(client, docker_compose_up_down, seed_db):
    # Create a new item to delete to avoid conflicts with other tests using seeded items
    name_to_delete = f"Disposable Food {uuid4()}"
    create_vars = {
        "input": {
            "name": name_to_delete,
            "calories": 10.0,
            "servingUnit": "g",
            "servingSize": 1.0,
            "protein": 1.0,
            "carbohydrates": 1.0,
            "fat": 1.0,  # Added missing required fields and ensured float for calories
            "userId": seed_db["user_goals"].user_id,
        }
    }
    response_create = await client.post("/graphql", json={"query": CREATE_FOOD_ITEM_MUTATION, "variables": create_vars})
    created_item_id = response_create.json()["data"]["createFoodItem"]["id_"]

    variables = {"id": created_item_id}
    response_delete = await client.post("/graphql", json={"query": DELETE_FOOD_ITEM_MUTATION, "variables": variables})
    assert response_delete.status_code == 200
    data = response_delete.json()
    assert data.get("errors") is None, f"GraphQL Errors: {data.get('errors')}"
    assert data["data"]["deleteFoodItem"] is True

    # Verify it's gone
    response_verify = await client.post("/graphql", json={"query": GET_FOOD_ITEM_QUERY, "variables": variables})
    assert response_verify.json()["data"]["foodItem"] is None


# --- Meal Mutations --- #
CREATE_MEAL_MUTATION = """
    mutation CreateMeal($input: MealCreateInput!) {
      createMeal(input: $input) {
        id_
        name
        type
        date
        notes
        mealFoods {
          quantity
          servingUnit
          foodItem {
            id_
            name
          }
        }
      }
    }
"""

UPDATE_MEAL_MUTATION = """
    mutation UpdateMeal($id: ID!, $input: MealUpdateInput!) {
      updateMeal(id: $id, input: $input) {
        id_
        name
        notes
        type
        date
      }
    }
"""

DELETE_MEAL_MUTATION = """
    mutation DeleteMeal($id: ID!) {
      deleteMeal(id: $id)
    }
"""

GET_MEAL_QUERY = """
    query GetMeal($id: ID!) {
      meal(id: $id) {
        id_
        name
        mealFoods { id_ }
      }
    }
"""


@pytest.mark.asyncio
async def test_create_meal(client, docker_compose_up_down, seed_db):
    user_id = seed_db["user_goals"].user_id
    food_item1_id = str(seed_db["apple"].id_)
    food_item2_id = str(seed_db["oatmeal"].id_)

    meal_name = f"Test Lunch {uuid4()}"
    now_iso = datetime.now(timezone.utc).isoformat()

    variables = {
        "input": {
            "userId": user_id,
            "name": meal_name,
            "type": "LUNCH",
            "date": now_iso,
            "notes": "A healthy test lunch.",
            "mealFoodsData": [
                {"foodItemId": food_item1_id, "quantity": 150.0, "servingUnit": "g"},
                {"foodItemId": food_item2_id, "quantity": 1.0, "servingUnit": "slice"},
            ],
        }
    }
    response = await client.post("/graphql", json={"query": CREATE_MEAL_MUTATION, "variables": variables})
    assert response.status_code == 200
    data = response.json()
    print(f"Create Meal Response: {data}")
    assert data.get("errors") is None, f"GraphQL Errors: {data.get('errors')}"
    created_meal = data["data"]["createMeal"]
    assert created_meal["id_"] is not None
    assert created_meal["name"] == meal_name
    assert created_meal["type"] == "LUNCH"
    assert created_meal["date"] == now_iso
    assert len(created_meal["mealFoods"]) == 2
    assert created_meal["mealFoods"][0]["foodItem"]["id_"] == food_item1_id
    assert created_meal["mealFoods"][1]["foodItem"]["id_"] == food_item2_id


@pytest.mark.asyncio
async def test_update_meal(client, docker_compose_up_down, seed_db):
    meal_to_update = seed_db["test_meal"]
    meal_id = str(meal_to_update.id_)
    updated_notes = f"Updated meal notes {uuid4()}"
    new_datetime_iso = (datetime.now(timezone.utc) - timedelta(days=5)).isoformat()

    variables = {"id": meal_id, "input": {"notes": updated_notes, "type": "DINNER", "date": new_datetime_iso}}
    response = await client.post("/graphql", json={"query": UPDATE_MEAL_MUTATION, "variables": variables})
    assert response.status_code == 200
    data = response.json()
    assert data.get("errors") is None, f"GraphQL Errors: {data.get('errors')}"
    updated_meal = data["data"]["updateMeal"]
    assert updated_meal["id_"] == meal_id
    assert updated_meal["notes"] == updated_notes
    assert updated_meal["type"] == "DINNER"
    assert updated_meal["date"] == new_datetime_iso


@pytest.mark.asyncio
async def test_delete_meal(client, docker_compose_up_down, seed_db):
    user_id = seed_db["user_goals"].user_id
    food_item_id = str(seed_db["apple"].id_)
    meal_name_to_delete = f"Temporary Meal {uuid4()}"
    now_iso_for_delete = datetime.now(timezone.utc).isoformat()
    create_vars = {
        "input": {
            "userId": user_id,
            "name": meal_name_to_delete,
            "type": "SNACK",
            "date": now_iso_for_delete,
            "mealFoodsData": [{"foodItemId": food_item_id, "quantity": 1.0, "servingUnit": "item"}],
        }
    }
    response_create = await client.post("/graphql", json={"query": CREATE_MEAL_MUTATION, "variables": create_vars})
    created_meal_id = response_create.json()["data"]["createMeal"]["id_"]

    delete_vars = {"id": created_meal_id}
    response_delete = await client.post("/graphql", json={"query": DELETE_MEAL_MUTATION, "variables": delete_vars})
    assert response_delete.status_code == 200
    data = response_delete.json()
    assert data.get("errors") is None, f"GraphQL Errors: {data.get('errors')}"
    assert data["data"]["deleteMeal"] is True

    # Verify it's gone
    response_verify = await client.post("/graphql", json={"query": GET_MEAL_QUERY, "variables": delete_vars})
    assert response_verify.json()["data"]["meal"] is None


# --- UserGoals Mutations --- #

# CREATE_USER_GOALS_MUTATION already exists via upsert logic, so we test upsert.
UPSERT_USER_GOALS_MUTATION = """
    mutation UpsertUserGoals($userId: String!, $input: UserGoalsCreateInput!) {
      upsertUserGoals(userId: $userId, input: $input) {
        id_
        userId
        dailyCalorieGoal
        dailyWaterGoal
        # other fields
      }
    }
"""

UPDATE_USER_GOALS_MUTATION = """
    mutation UpdateUserGoals($userId: String!, $input: UserGoalsUpdateInput!) {
      updateUserGoals(userId: $userId, input: $input) {
        id_
        userId
        dailyCalorieGoal
        dailyProteinGoal
      }
    }
"""

DELETE_USER_GOALS_MUTATION = """
    mutation DeleteUserGoals($userId: String!) {
      deleteUserGoals(userId: $userId)
    }
"""

GET_USER_GOALS_QUERY = """ # For verifying create/delete
    query GetUserGoals($userId: String!) {
      userGoals(userId: $userId) {
        id_
        dailyCalorieGoal
      }
    }
"""


@pytest.mark.asyncio
async def test_upsert_user_goals_create(client, docker_compose_up_down, seed_db):
    user_id_new = f"test-user-{uuid4()}@example.com"
    variables = {
        "userId": user_id_new,
        "input": {
            "userId": user_id_new,  # Input also needs userId
            "dailyCalorieGoal": 2500.0,
            "dailyWaterGoal": 3000.0,
            "dailyProteinGoal": 180.0,
            "dailyCarbsGoal": 300.0,
            "dailyFatGoal": 80.0,
        },
    }
    response = await client.post("/graphql", json={"query": UPSERT_USER_GOALS_MUTATION, "variables": variables})
    assert response.status_code == 200
    data = response.json()
    assert data.get("errors") is None, f"GraphQL Errors: {data.get('errors')}"
    goals = data["data"]["upsertUserGoals"]
    assert goals["id_"] is not None
    assert goals["userId"] == user_id_new
    assert goals["dailyCalorieGoal"] == 2500.0

    # Clean up by deleting
    await client.post("/graphql", json={"query": DELETE_USER_GOALS_MUTATION, "variables": {"userId": user_id_new}})


@pytest.mark.asyncio
async def test_upsert_user_goals_update(client, docker_compose_up_down, seed_db):
    existing_user_id = seed_db["user_goals"].user_id
    variables = {
        "userId": existing_user_id,
        "input": {
            "userId": existing_user_id,
            "dailyCalorieGoal": 2600.0,  # Updated value
            "dailyWaterGoal": 3100.0,  # Updated value
            # Include other fields from UserGoalsCreateInput as they are required by input type
            "dailyProteinGoal": (
                seed_db["user_goals"].daily_protein_goal
                if seed_db["user_goals"].daily_protein_goal is not None
                else 150.0
            ),
            "dailyCarbsGoal": (
                seed_db["user_goals"].daily_carbs_goal if seed_db["user_goals"].daily_carbs_goal is not None else 250.0
            ),
            "dailyFatGoal": (
                seed_db["user_goals"].daily_fat_goal if seed_db["user_goals"].daily_fat_goal is not None else 70.0
            ),
        },
    }
    response = await client.post("/graphql", json={"query": UPSERT_USER_GOALS_MUTATION, "variables": variables})
    assert response.status_code == 200
    data = response.json()
    assert data.get("errors") is None, f"GraphQL Errors: {data.get('errors')}"
    goals = data["data"]["upsertUserGoals"]
    assert goals["userId"] == existing_user_id
    assert goals["dailyCalorieGoal"] == 2600.0
    assert goals["dailyWaterGoal"] == 3100.0


@pytest.mark.asyncio
async def test_update_user_goals(client, docker_compose_up_down, seed_db):
    user_id_to_update = seed_db["user_goals"].user_id
    updated_protein_goal = 200.0
    variables = {
        "userId": user_id_to_update,
        "input": {
            # Only include fields to update for UserGoalsUpdateInput
            "dailyProteinGoal": updated_protein_goal,
            "dailyCalorieGoal": 2250.0,  # Example of another field update
        },
    }
    response = await client.post("/graphql", json={"query": UPDATE_USER_GOALS_MUTATION, "variables": variables})
    assert response.status_code == 200
    data = response.json()
    assert data.get("errors") is None, f"GraphQL Errors: {data.get('errors')}"
    updated_goals = data["data"]["updateUserGoals"]
    assert updated_goals["userId"] == user_id_to_update
    assert updated_goals["dailyProteinGoal"] == updated_protein_goal
    assert updated_goals["dailyCalorieGoal"] == 2250.0


@pytest.mark.asyncio
async def test_delete_user_goals(client, docker_compose_up_down, seed_db):
    # Create a new user goal to delete
    user_id_to_delete = f"delete-me-user-{uuid4()}@example.com"
    create_vars = {
        "userId": user_id_to_delete,
        "input": {"userId": user_id_to_delete, "dailyCalorieGoal": 1000.0, "dailyWaterGoal": 1000.0},
    }
    await client.post("/graphql", json={"query": UPSERT_USER_GOALS_MUTATION, "variables": create_vars})

    delete_vars = {"userId": user_id_to_delete}
    response_delete = await client.post(
        "/graphql", json={"query": DELETE_USER_GOALS_MUTATION, "variables": delete_vars}
    )
    assert response_delete.status_code == 200
    data = response_delete.json()
    assert data.get("errors") is None, f"GraphQL Errors: {data.get('errors')}"
    assert data["data"]["deleteUserGoals"] is True

    # Verify it's gone
    response_verify = await client.post("/graphql", json={"query": GET_USER_GOALS_QUERY, "variables": delete_vars})
    assert response_verify.json()["data"]["userGoals"] is None


# --- WaterConsumption Mutations --- #
CREATE_WATER_CONSUMPTION_MUTATION = """
    mutation CreateWaterConsumption($input: WaterConsumptionCreateInput!) {
      createWaterConsumption(input: $input) {
        id_
        userId
        quantity
        consumedAt
      }
    }
"""

UPDATE_WATER_CONSUMPTION_MUTATION = """
    mutation UpdateWaterConsumption($id: ID!, $input: WaterConsumptionUpdateInput!) {
      updateWaterConsumption(id: $id, input: $input) {
        id_
        quantity
        consumedAt
      }
    }
"""

DELETE_WATER_CONSUMPTION_MUTATION = """
    mutation DeleteWaterConsumption($id: ID!) {
      deleteWaterConsumption(id: $id)
    }
"""

GET_WATER_CONSUMPTION_QUERY = """
    query GetWaterConsumption($id: ID!) {
      waterConsumption(id: $id) {
        id_
        quantity
      }
    }
"""


@pytest.mark.asyncio
async def test_create_water_consumption(client, docker_compose_up_down, seed_db):
    user_id = seed_db["user_goals"].user_id
    consumed_at_iso = datetime.now(timezone.utc).isoformat()
    variables = {"input": {"userId": user_id, "quantity": 500.0, "consumedAt": consumed_at_iso}}
    response = await client.post("/graphql", json={"query": CREATE_WATER_CONSUMPTION_MUTATION, "variables": variables})
    assert response.status_code == 200
    data = response.json()
    assert data.get("errors") is None, f"GraphQL Errors: {data.get('errors')}"
    created_wc = data["data"]["createWaterConsumption"]
    assert created_wc["id_"] is not None
    assert created_wc["userId"] == user_id
    assert created_wc["quantity"] == 500.0
    assert created_wc["consumedAt"] is not None  # Check presence, exact match can be tricky with timezones/precision


@pytest.mark.asyncio
async def test_update_water_consumption(client, docker_compose_up_down, seed_db):
    water_to_update = seed_db["water1"]
    water_id = str(water_to_update.id_)
    new_consumed_at_iso = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()

    variables = {"id": water_id, "input": {"quantity": 750.0, "consumedAt": new_consumed_at_iso}}
    response = await client.post("/graphql", json={"query": UPDATE_WATER_CONSUMPTION_MUTATION, "variables": variables})
    assert response.status_code == 200
    data = response.json()
    assert data.get("errors") is None, f"GraphQL Errors: {data.get('errors')}"
    updated_wc = data["data"]["updateWaterConsumption"]
    assert updated_wc["id_"] == water_id
    assert updated_wc["quantity"] == 750.0
    assert updated_wc["consumedAt"] == new_consumed_at_iso


@pytest.mark.asyncio
async def test_delete_water_consumption(client, docker_compose_up_down, seed_db):
    user_id = seed_db["user_goals"].user_id
    consumed_at_iso = datetime.now(timezone.utc).isoformat()
    create_vars = {"input": {"userId": user_id, "quantity": 100.0, "consumedAt": consumed_at_iso}}
    response_create = await client.post(
        "/graphql", json={"query": CREATE_WATER_CONSUMPTION_MUTATION, "variables": create_vars}
    )
    created_wc_id = response_create.json()["data"]["createWaterConsumption"]["id_"]

    delete_vars = {"id": created_wc_id}
    response_delete = await client.post(
        "/graphql", json={"query": DELETE_WATER_CONSUMPTION_MUTATION, "variables": delete_vars}
    )
    assert response_delete.status_code == 200
    data = response_delete.json()
    assert data.get("errors") is None, f"GraphQL Errors: {data.get('errors')}"
    assert data["data"]["deleteWaterConsumption"] is True

    # Verify it's gone
    response_verify = await client.post(
        "/graphql", json={"query": GET_WATER_CONSUMPTION_QUERY, "variables": delete_vars}
    )
    assert response_verify.json()["data"]["waterConsumption"] is None


# Example of more complex mutation: Add Food to Meal (if this was a direct mutation)
# For this project, adding/removing food is part of Meal create/update or separate resolver.
# If `addFoodToMeal` and `removeFoodFromMeal` were top-level mutations, they'd be tested here.
# Since they are methods on the Meal service, their logic is implicitly tested via Meal create/update.
# Let's assume there is an `addFoodToMeal` mutation for demonstration

ADD_FOOD_TO_MEAL_MUTATION = """
    mutation AddFoodToMeal($mealId: ID!, $foodItemId: ID!, $quantity: Float!, $servingUnit: String!) {
        addFoodToMeal(mealId: $mealId, foodItemId: $foodItemId, quantity: $quantity, servingUnit: $servingUnit) {
            id_ # Meal ID
            mealFoods {
                id_
                quantity
                foodItem {
                    id_
                    name
                }
            }
        }
    }
"""


@pytest.mark.asyncio
async def test_add_food_to_meal(client, docker_compose_up_down, seed_db):
    meal_id = str(seed_db["test_meal"].id_)  # Changed from "meal"
    # Assuming food_item3 is available in seed_db and not already in the meal
    food_to_add_id = str(seed_db["chicken_breast"].id_)  # Changed from "food_item3" to "chicken_breast"

    variables = {"mealId": meal_id, "foodItemId": food_to_add_id, "quantity": 75.0, "servingUnit": "g"}

    response = await client.post("/graphql", json={"query": ADD_FOOD_TO_MEAL_MUTATION, "variables": variables})
    assert response.status_code == 200
    data = response.json()
    print(f"Add Food to Meal Response: {data}")
    assert data.get("errors") is None, f"GraphQL Errors: {data.get('errors')}"

    updated_meal = data["data"]["addFoodToMeal"]
    assert updated_meal["id_"] == meal_id

    found_added_food = False
    for mf in updated_meal["mealFoods"]:
        if mf["foodItem"]["id_"] == food_to_add_id:
            assert mf["quantity"] == 75.0
            found_added_food = True
            break
    assert found_added_food, f"Food item {food_to_add_id} not found in meal {meal_id} after addFoodToMeal mutation"

    # To make this test more robust, you might want to fetch the meal before adding,
    # count mealFoods, add, then fetch again and assert the count and content has changed as expected.
