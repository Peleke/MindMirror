begin;

-- Ensure schema
create schema if not exists meals;

-- Ensure enum type (idempotent)
do $$
begin
  if not exists (
    select 1
    from pg_type t
    join pg_namespace n on n.oid = t.typnamespace
    where t.typname = 'meal_type' and n.nspname = 'meals'
  ) then
    create type meals.meal_type as enum ('breakfast','lunch','dinner','snack');
  end if;
end$$;

-- Tables

create table if not exists meals.food_items (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default clock_timestamp(),
  modified_at timestamptz not null default clock_timestamp(),
  name varchar(256) not null,
  serving_size double precision not null,
  serving_unit varchar(64) not null,
  calories double precision not null default 0,
  protein double precision not null default 0,
  carbohydrates double precision not null default 0,
  fat double precision not null default 0,
  saturated_fat double precision,
  monounsaturated_fat double precision,
  polyunsaturated_fat double precision,
  trans_fat double precision,
  cholesterol double precision,
  fiber double precision,
  sugar double precision,
  sodium double precision,
  vitamin_d double precision,
  calcium double precision,
  iron double precision,
  potassium double precision,
  zinc double precision,
  user_id text,
  notes text
);

create table if not exists meals.user_goals (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default clock_timestamp(),
  modified_at timestamptz not null default clock_timestamp(),
  user_id text not null unique,
  daily_calorie_goal double precision not null default 2000,
  daily_water_goal double precision not null default 2000,
  daily_protein_goal double precision,
  daily_carbs_goal double precision,
  daily_fat_goal double precision
);

create table if not exists meals.meals (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default clock_timestamp(),
  modified_at timestamptz not null default clock_timestamp(),
  name varchar(256) not null,
  type meals.meal_type not null,
  date timestamptz not null,
  notes text,
  user_id text not null
);

create table if not exists meals.meal_foods (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default clock_timestamp(),
  modified_at timestamptz not null default clock_timestamp(),
  meal_id uuid not null references meals.meals(id) on delete cascade,
  food_item_id uuid not null references meals.food_items(id),
  quantity double precision not null,
  serving_unit varchar(64) not null
);

create table if not exists meals.water_consumption (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default clock_timestamp(),
  modified_at timestamptz not null default clock_timestamp(),
  user_id text not null,
  quantity double precision not null,
  consumed_at timestamptz not null
);

-- Helpful indexes
create index if not exists ix_meals_food_items_user_id_name on meals.food_items(user_id, name);
create index if not exists ix_meals_meals_user_date on meals.meals(user_id, date desc);
create index if not exists ix_meals_meal_foods_meal_id on meals.meal_foods(meal_id);
create index if not exists ix_meals_meal_foods_food_item_id on meals.meal_foods(food_item_id);
create index if not exists ix_meals_water_user_time on meals.water_consumption(user_id, consumed_at desc);

commit;
