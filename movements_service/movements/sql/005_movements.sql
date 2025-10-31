-- Create movements schema and tables for Supabase
create schema if not exists movements;

-- Movements table
create table if not exists movements.movements (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  modified_at timestamptz not null default now(),
  slug text not null unique,
  name text not null,
  difficulty text,
  body_region text,
  target_muscle_group text,
  prime_mover_muscle text,
  posture text,
  arm_mode text,
  arm_pattern text,
  grip text,
  load_position text,
  leg_pattern text,
  foot_elevation text,
  combo_type text,
  mechanics text,
  laterality text,
  primary_classification text,
  force_type text,
  archetype text,
  description text,
  short_video_url text,
  long_video_url text,
  gif_url text,
  source text,
  external_id text,
  is_public boolean not null default true,
  user_id text
);

create index if not exists ix_movements_name on movements.movements (name);
create index if not exists ix_movements_body_region on movements.movements (body_region);
create index if not exists ix_movements_user_id on movements.movements (user_id);
create index if not exists ix_movements_external_id on movements.movements (external_id);

-- Aliases
create table if not exists movements.movement_aliases (
  id uuid primary key default gen_random_uuid(),
  movement_id uuid not null,
  alias text not null unique,
  created_at timestamptz not null default now()
);
create index if not exists ix_alias_movement_id on movements.movement_aliases (movement_id);

-- Muscle links
create table if not exists movements.movement_muscle_links (
  movement_id uuid not null,
  muscle_name text not null,
  role text not null,
  primary key (movement_id, muscle_name, role)
);
create index if not exists ix_muscle_movement_id on movements.movement_muscle_links (movement_id);

-- Equipment links
create table if not exists movements.movement_equipment_links (
  movement_id uuid not null,
  equipment_name text not null,
  role text not null,
  item_count integer,
  primary key (movement_id, equipment_name, role)
);
create index if not exists ix_equipment_movement_id on movements.movement_equipment_links (movement_id);

-- Pattern links
create table if not exists movements.movement_pattern_links (
  movement_id uuid not null,
  pattern_name text not null,
  position integer not null default 1,
  primary key (movement_id, pattern_name)
);
create index if not exists ix_pattern_movement_id on movements.movement_pattern_links (movement_id);

-- Plane links
create table if not exists movements.movement_plane_links (
  movement_id uuid not null,
  plane_name text not null,
  position integer not null default 1,
  primary key (movement_id, plane_name)
);
create index if not exists ix_plane_movement_id on movements.movement_plane_links (movement_id);

-- Tags
create table if not exists movements.movement_tag_links (
  movement_id uuid not null,
  tag_name text not null,
  primary key (movement_id, tag_name)
);
create index if not exists ix_tag_movement_id on movements.movement_tag_links (movement_id);

-- Instructions
create table if not exists movements.movement_instructions (
  movement_id uuid not null,
  position integer not null,
  text text not null,
  primary key (movement_id, position)
);
create index if not exists ix_instr_movement_id on movements.movement_instructions (movement_id);
