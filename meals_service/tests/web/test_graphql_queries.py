from datetime import date, datetime, timedelta, timezone
from uuid import uuid4

import pytest

# Assume 'client' fixture for httpx.AsyncClient and 'seed_db' or similar for test data setup
# from conftest import client, seed_db_meals # Adjust as per your conftest.py for meals


@pytest.mark.asyncio
async def test_get_food_items_list(client, seed_db, docker_compose_up_down):
    query = """
        query GetFoodItemsList {
          foodItems {
            id_
            name
            calories
            protein
            # Add other relevant fields
          }
        }
    """
    response = await client.post("/graphql", json={"query": query})
    assert response.status_code == 200
    data = response.json()
    assert "errors" not in data
    assert "foodItems" in data["data"]

    food_items_list = data["data"]["foodItems"]
    print(food_items_list)
    assert isinstance(food_items_list, list)
    # Example: check if the seeded public food item is present
    seeded_public_food_item_id = str(seed_db["oatmeal"].id_)
    found_seeded_food_item = any(fi["id_"] == seeded_public_food_item_id for fi in food_items_list)
    assert found_seeded_food_item, f"Seeded public food item with ID {seeded_public_food_item_id} not found"

    # Optionally, assert that user-specific items are NOT present
    seeded_user_food_item_id = str(seed_db["apple"].id_)
    found_user_specific_food_item = any(fi["id_"] == seeded_user_food_item_id for fi in food_items_list)
    assert (
        not found_user_specific_food_item
    ), f"User-specific food item with ID {seeded_user_food_item_id} was found in public list"

    if food_items_list:
        first_food_item = food_items_list[0]
        assert "id_" in first_food_item
        assert "name" in first_food_item
        assert "calories" in first_food_item


@pytest.mark.asyncio
async def test_get_food_item_details(client, seed_db, docker_compose_up_down):
    seeded_food_item = seed_db["apple"]
    food_item_id_to_fetch = str(seeded_food_item.id_)

    query = """
        query GetFoodItemDetails($id: ID!) {
          foodItem(id: $id) {
            id_
            name
            servingSize
            servingUnit
            calories
            protein
            carbohydrates
            fat
            # Add all fields you want to test
            createdAt
            modifiedAt
          }
        }
    """
    variables = {"id": food_item_id_to_fetch}
    response = await client.post("/graphql", json={"query": query, "variables": variables})
    assert response.status_code == 200
    data = response.json()
    assert "errors" not in data, f"GraphQL errors: {data.get('errors')}"
    assert "foodItem" in data["data"]

    food_item_details = data["data"]["foodItem"]
    assert food_item_details is not None, f"FoodItem with ID {food_item_id_to_fetch} not found."
    assert food_item_details["id_"] == food_item_id_to_fetch
    assert food_item_details["name"] == seeded_food_item.name
    assert food_item_details["calories"] == seeded_food_item.calories


@pytest.mark.asyncio
async def test_get_food_item_details_invalid_id(client, create_tables, docker_compose_up_down):
    invalid_id = str(uuid4())
    query = """
        query GetFoodItemDetails($id: ID!) {
          foodItem(id: $id) {
            id_
          }
        }
    """
    variables = {"id": invalid_id}
    response = await client.post("/graphql", json={"query": query, "variables": variables})
    assert response.status_code == 200
    data = response.json()
    assert "errors" not in data
    assert data["data"]["foodItem"] is None


@pytest.mark.asyncio
async def test_get_meals_by_user_and_date_range(client, seed_db, docker_compose_up_down):
    user_id_to_fetch = seed_db["user_goals"].user_id  # Assuming user_goals has the user_id
    # Using seeded meal's date
    start_date_str = (datetime.now(timezone.utc).date() - timedelta(days=1)).isoformat()
    end_date_str = datetime.now(timezone.utc).date().isoformat()

    query = """
        query GetMeals($userId: String!, $startDate: String!, $endDate: String!) {
          mealsByUserAndDateRange(userId: $userId, startDate: $startDate, endDate: $endDate) {
            id_
            name
            type
            date
            mealFoods {
              quantity
              servingUnit
              foodItem {
                id_
                name
                calories
              }
            }
          }
        }
    """
    variables = {"userId": user_id_to_fetch, "startDate": start_date_str, "endDate": end_date_str}
    response = await client.post("/graphql", json={"query": query, "variables": variables})
    assert response.status_code == 200
    data = response.json()
    print(f"Meals by user and date range data: {data}")
    assert "errors" not in data, f"GraphQL errors: {data.get('errors')}"
    assert "mealsByUserAndDateRange" in data["data"]

    meals_list = data["data"]["mealsByUserAndDateRange"]
    assert isinstance(meals_list, list)
    # Check if the seeded meal is present
    seeded_meal_id = str(seed_db["test_meal"].id_)
    found_seeded_meal = any(m["id_"] == seeded_meal_id for m in meals_list)
    assert found_seeded_meal, f"Seeded meal with ID {seeded_meal_id} not found for user {user_id_to_fetch} in range"

    if meals_list:
        first_meal = meals_list[0]
        assert "id_" in first_meal
        assert "name" in first_meal
        assert "mealFoods" in first_meal
        if first_meal["mealFoods"]:
            assert "foodItem" in first_meal["mealFoods"][0]


@pytest.mark.asyncio
async def test_get_meal_details(client, seed_db, docker_compose_up_down):
    seeded_meal = seed_db["test_meal"]
    meal_id_to_fetch = str(seeded_meal.id_)

    query = """
        query GetMealDetails($id: ID!) {
          meal(id: $id) {
            id_
            name
            type
            date
            notes
            createdAt
            modifiedAt
            mealFoods {
              id_
              quantity
              servingUnit
              foodItem {
                id_
                name
                calories
              }
            }
          }
        }
    """
    variables = {"id": meal_id_to_fetch}
    response = await client.post("/graphql", json={"query": query, "variables": variables})
    assert response.status_code == 200
    data = response.json()
    assert "errors" not in data, f"GraphQL errors: {data.get('errors')}"
    assert "meal" in data["data"]

    meal_details = data["data"]["meal"]
    assert meal_details is not None, f"Meal with ID {meal_id_to_fetch} not found."
    assert meal_details["id_"] == meal_id_to_fetch
    assert meal_details["name"] == seeded_meal.name
    # Compare datetime strings, ensuring consistent ISO format and timezone handling
    # Parse both to datetime objects for robust comparison if formats might differ slightly
    # or if one might lack timezone information that the other has.
    # For now, assuming the seeded_meal.date is also a datetime object.
    expected_date_iso = seeded_meal.date.isoformat()
    assert meal_details["date"] == expected_date_iso
    assert len(meal_details["mealFoods"]) == len(seeded_meal.meal_foods)


@pytest.mark.asyncio
async def test_get_meal_details_invalid_id(client, create_tables, docker_compose_up_down):
    invalid_id = str(uuid4())
    query = """
        query GetMealDetails($id: ID!) {
          meal(id: $id) {
            id_
          }
        }
    """
    variables = {"id": invalid_id}
    response = await client.post("/graphql", json={"query": query, "variables": variables})
    assert response.status_code == 200
    data = response.json()
    assert "errors" not in data
    assert data["data"]["meal"] is None


@pytest.mark.asyncio
async def test_get_user_goals(client, seed_db, docker_compose_up_down):
    seeded_user_goals = seed_db["user_goals"]
    user_id_to_fetch = seeded_user_goals.user_id

    query = """
        query GetUserGoals($userId: String!) {
          userGoals(userId: $userId) {
            id_
            userId
            dailyCalorieGoal
            dailyWaterGoal
            # Add other fields
            createdAt
            modifiedAt
          }
        }
    """
    variables = {"userId": user_id_to_fetch}
    response = await client.post("/graphql", json={"query": query, "variables": variables})
    assert response.status_code == 200
    data = response.json()
    assert "errors" not in data, f"GraphQL errors: {data.get('errors')}"
    assert "userGoals" in data["data"]

    user_goals_details = data["data"]["userGoals"]
    assert user_goals_details is not None, f"UserGoals for user ID {user_id_to_fetch} not found."
    assert user_goals_details["userId"] == user_id_to_fetch
    assert user_goals_details["dailyCalorieGoal"] == seeded_user_goals.daily_calorie_goal


@pytest.mark.asyncio
async def test_get_user_goals_invalid_user_id(client, create_tables, docker_compose_up_down):
    invalid_user_id = "non-existent-user-" + str(uuid4())
    query = """
        query GetUserGoals($userId: String!) {
          userGoals(userId: $userId) {
            id_
          }
        }
    """
    variables = {"userId": invalid_user_id}
    response = await client.post("/graphql", json={"query": query, "variables": variables})
    assert response.status_code == 200
    data = response.json()
    assert "errors" not in data  # Service returns null for not found
    assert data["data"]["userGoals"] is None


@pytest.mark.asyncio
async def test_get_water_consumptions_by_user_and_date_range(client, seed_db, docker_compose_up_down):
    user_id_to_fetch = seed_db["water1"].user_id
    # Using seeded water consumption's date
    start_date_str = (seed_db["water1"].consumed_at.date() - timedelta(days=1)).isoformat()
    end_date_str = (seed_db["water1"].consumed_at.date() + timedelta(days=1)).isoformat()

    query = """
        query GetWaterConsumptions($userId: String!, $startDate: String!, $endDate: String!) {
          waterConsumptionsByUserAndDateRange(userId: $userId, startDate: $startDate, endDate: $endDate) {
            id_
            quantity
            consumedAt
            # Add other relevant fields
          }
        }
    """
    variables = {"userId": user_id_to_fetch, "startDate": start_date_str, "endDate": end_date_str}
    response = await client.post("/graphql", json={"query": query, "variables": variables})
    assert response.status_code == 200
    data = response.json()
    assert "errors" not in data, f"GraphQL errors: {data.get('errors')}"
    assert "waterConsumptionsByUserAndDateRange" in data["data"]

    wc_list = data["data"]["waterConsumptionsByUserAndDateRange"]
    assert isinstance(wc_list, list)
    seeded_wc_id = str(seed_db["water1"].id_)
    found_seeded_wc = any(wc["id_"] == seeded_wc_id for wc in wc_list)
    assert found_seeded_wc, f"Seeded water consumption {seeded_wc_id} not found for user {user_id_to_fetch}"

    if wc_list:
        first_wc = wc_list[0]
        assert "id_" in first_wc
        assert "quantity" in first_wc
        assert "consumedAt" in first_wc


@pytest.mark.asyncio
async def test_get_water_consumption_details(client, seed_db, docker_compose_up_down):
    seeded_wc = seed_db["water1"]
    wc_id_to_fetch = str(seeded_wc.id_)

    query = """
        query GetWaterConsumptionDetails($id: ID!) {
          waterConsumption(id: $id) {
            id_
            userId
            quantity
            consumedAt
            createdAt
            modifiedAt
          }
        }
    """
    variables = {"id": wc_id_to_fetch}
    response = await client.post("/graphql", json={"query": query, "variables": variables})
    assert response.status_code == 200
    data = response.json()
    assert "errors" not in data, f"GraphQL errors: {data.get('errors')}"
    assert "waterConsumption" in data["data"]

    wc_details = data["data"]["waterConsumption"]
    assert wc_details is not None, f"WaterConsumption with ID {wc_id_to_fetch} not found."
    assert wc_details["id_"] == wc_id_to_fetch
    assert wc_details["quantity"] == seeded_wc.quantity


@pytest.mark.asyncio
async def test_get_water_consumption_details_invalid_id(client, create_tables, docker_compose_up_down):
    invalid_id = str(uuid4())
    query = """
        query GetWaterConsumptionDetails($id: ID!) {
          waterConsumption(id: $id) {
            id_
          }
        }
    """
    variables = {"id": invalid_id}
    response = await client.post("/graphql", json={"query": query, "variables": variables})
    assert response.status_code == 200
    data = response.json()
    assert "errors" not in data
    assert data["data"]["waterConsumption"] is None


@pytest.mark.asyncio
async def test_get_total_water_consumption_by_user_and_date(client, seed_db, docker_compose_up_down):
    user_id_to_fetch = seed_db["user_goals"].user_id
    # Use a date for which we know there's data from the seeder
    # Ensure water1 and water2 consumed_at dates fall on this date_str
    date_str = seed_db["water1"].consumed_at.date().isoformat()

    query = """
        query GetTotalWaterConsumption($userId: String!, $dateStr: String!) {
          totalWaterConsumptionByUserAndDate(userId: $userId, dateStr: $dateStr)
        }
    """
    variables = {"userId": user_id_to_fetch, "dateStr": date_str}
    response = await client.post("/graphql", json={"query": query, "variables": variables})
    assert response.status_code == 200
    data = response.json()
    print(f"Total water consumption data: {data}")
    assert "errors" not in data, f"GraphQL errors: {data.get('errors')}"
    assert "totalWaterConsumptionByUserAndDate" in data["data"]

    total_water = data["data"]["totalWaterConsumptionByUserAndDate"]

    # Sum quantities of water entries for the specific user and date from seed_db
    expected_total = 0
    if seed_db["water1"].user_id == user_id_to_fetch and seed_db["water1"].consumed_at.date().isoformat() == date_str:
        expected_total += seed_db["water1"].quantity
    if seed_db["water2"].user_id == user_id_to_fetch and seed_db["water2"].consumed_at.date().isoformat() == date_str:
        expected_total += seed_db["water2"].quantity

    assert (
        total_water == expected_total
    ), f"Total water consumption {total_water} did not match expected sum {expected_total} from seeded data for date {date_str}."


@pytest.mark.asyncio
async def test_get_total_water_consumption_no_data(client, create_tables, docker_compose_up_down):
    user_id_to_fetch = "user-with-no-water-" + str(uuid4())
    date_str = date.today().isoformat()

    query = """
        query GetTotalWaterConsumption($userId: String!, $dateStr: String!) {
          totalWaterConsumptionByUserAndDate(userId: $userId, dateStr: $dateStr)
        }
    """
    variables = {"userId": user_id_to_fetch, "dateStr": date_str}
    response = await client.post("/graphql", json={"query": query, "variables": variables})
    assert response.status_code == 200
    data = response.json()
    assert "errors" not in data
    assert data["data"]["totalWaterConsumptionByUserAndDate"] == 0.0


@pytest.mark.asyncio
async def test_food_items_autocomplete_local_only(client, seed_db, docker_compose_up_down, monkeypatch):
    # Disable OFF in context by monkeypatching app module's _off_client to None
    from meals.web import app as meals_app

    monkeypatch.setattr(meals_app, "_off_client", None)

    query = """
        query Autocomplete($q: String!) {
          foodItemsAutocomplete(query: $q, limit: 5) {
            source
            id_
            name
          }
        }
    """
    variables = {"q": "Oat"}
    response = await client.post("/graphql", json={"query": query, "variables": variables})
    assert response.status_code == 200
    data = response.json()
    assert "errors" not in data
    results = data["data"]["foodItemsAutocomplete"]
    # Should contain local items, not OFF
    assert any(r["source"] == "local" for r in results)


@pytest.mark.asyncio
async def test_food_items_autocomplete_barcode_hit(client, seed_db, docker_compose_up_down, monkeypatch):
    # Monkeypatch OffClient.get_product_by_barcode to return a fake product
    class FakeOff:
        def get_product_by_barcode(self, code, fields=None):
            return {
                "code": code,
                "product_name": "Nutella",
                "brands": "Ferrero",
                "image_url": "https://img.example/nutella.jpg",
                "nutrition_grades": "e",
                "nutriments": {"energy-kcal_100g": 539, "proteins_100g": 6.0, "carbohydrates_100g": 57.5, "fat_100g": 30.9},
            }

        def search_fulltext(self, query, page_size=10):
            return []

    from meals.web import app as meals_app

    monkeypatch.setattr(meals_app, "_off_client", FakeOff())

    query = """
        query Autocomplete($q: String!) {
          foodItemsAutocomplete(query: $q, limit: 5) {
            source
            externalId
            name
            brand
          }
        }
    """
    variables = {"q": "3017624010701"}
    response = await client.post("/graphql", json={"query": query, "variables": variables})
    assert response.status_code == 200
    data = response.json()
    assert "errors" not in data
    results = data["data"]["foodItemsAutocomplete"]
    # Should contain an OFF result
    assert any(r["source"] == "off" and r["externalId"] == "3017624010701" for r in results)


@pytest.mark.asyncio
async def test_import_off_product_creates_food_item(client, create_tables, docker_compose_up_down, monkeypatch):
    # Fake OFF product detail for import
    class FakeOff:
        def get_product_by_barcode(self, code, fields=None):
            return {
                "code": code,
                "product_name": "Orange Juice",
                "brands": "Generic",
                "image_url": "https://img.example/oj.jpg",
                "nutrition_grades": "c",
                "nutriments": {
                    "energy-kcal_100g": 45,
                    "proteins_100g": 0.7,
                    "carbohydrates_100g": 10.4,
                    "fat_100g": 0.2,
                    "sodium_100g": 0.005,
                },
                "serving_size": "240 ml",
            }

    from meals.web import app as meals_app

    monkeypatch.setattr(meals_app, "_off_client", FakeOff())

    mutation = """
        mutation Import($code: String!) {
          importOffProduct(code: $code) {
            id_
            name
            brand
            source
            externalSource
            externalId
            thumbnailUrl
            calories
            protein
            carbohydrates
            fat
            sodium
          }
        }
    """
    variables = {"code": "0000000001234"}
    response = await client.post("/graphql", json={"query": mutation, "variables": variables})
    assert response.status_code == 200
    data = response.json()
    assert "errors" not in data, data.get("errors")
    item = data["data"]["importOffProduct"]
    assert item["name"] == "Orange Juice"
    assert item["brand"] == "Generic"
    assert item["source"] == "off"
    assert item["externalSource"] == "openfoodfacts"
    assert item["externalId"] == "0000000001234"
    assert item["calories"] > 0


@pytest.mark.asyncio
async def test_import_off_product_idempotent(client, create_tables, docker_compose_up_down, monkeypatch):
    # Reuse the same FakeOff
    class FakeOff:
        def __init__(self):
            self.calls = 0

        def get_product_by_barcode(self, code, fields=None):
            self.calls += 1
            return {
                "code": code,
                "product_name": "OJ",
                "brands": "BrandX",
                "image_url": "https://img.example/oj.jpg",
                "nutriments": {"energy-kcal_100g": 45, "proteins_100g": 1.0, "carbohydrates_100g": 9.0, "fat_100g": 0.1},
            }

    from meals.web import app as meals_app

    fake = FakeOff()
    monkeypatch.setattr(meals_app, "_off_client", fake)

    mutation = """
        mutation Import($code: String!) {
          importOffProduct(code: $code) { id_ name externalId }
        }
    """
    variables = {"code": "0000000002222"}
    # First call creates
    resp1 = await client.post("/graphql", json={"query": mutation, "variables": variables})
    assert resp1.status_code == 200
    data1 = resp1.json()["data"]["importOffProduct"]
    # Second call should return existing (still OK)
    resp2 = await client.post("/graphql", json={"query": mutation, "variables": variables})
    assert resp2.status_code == 200
    data2 = resp2.json()["data"]["importOffProduct"]
    assert data1["id_"] == data2["id_"]
