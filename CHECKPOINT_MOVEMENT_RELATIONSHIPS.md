# 🏗️💦 MOVEMENT RELATIONSHIPS IMPLEMENTATION CHECKPOINT

## **WHAT WE'VE BUILT SO FAR:**

### **COMPLETED ✅:**

1. **Metadata JSONB Column** (`0002_add_metadata_jsonb.py`)
   - Added `metadata JSONB` field to MovementModel
   - Enables coach video tracking (male/female) and flexible metadata
   - Migration ready to run

2. **PN CSV Importer** (`movements_service/movements/service/pn_csv_importer.py`)
   - Merges jen_export.csv + craig_export.csv
   - Parses numbered instructions into newline-separated format
   - Populates short_video_url (male), long_video_url (female)
   - Stores metadata with coach mappings
   - Source: "precision_nutrition"

3. **CLI Command: seed-pn-movements** (`cli/src/mindmirror_cli/commands/seed_pn_movements.py`)
   - Registered in main CLI app
   - Supports staging/production environments
   - Update existing or skip duplicates
   ```bash
   poetry run mindmirror seed-pn-movements \
     --jen-csv data/fitness/pn/data/jen_export.csv \
     --craig-csv data/fitness/pn/data/craig_export.csv \
     --env staging
   ```

4. **MovementRelationship Model** (`movements_service/movements/repository/models.py:112`)
   - Graph-based relationship model
   - Supports: regression, progression, travel_modification, variation
   - Foreign keys with CASCADE delete
   - Unique constraint prevents duplicates
   - Check constraints enforce valid types and no self-reference
   - Includes difficulty_delta for progression strength
   - **CLEAN AS FUCK** with full docstrings

---

## **IN PROGRESS 🔄:**

### **Current Task: Movement Relationships Feature**

**New Discovery**: `data/fitness/pn/data/regressions.csv` (398 rows)
- Exercise progressions/regressions/travel modifications
- Need to import this into a proper graph structure

**Requirements:**
- ✅ Bi-directional relationships (find progressions AND what progresses to X)
- ✅ Referential integrity (FK constraints)
- ✅ Multiple relationships per movement
- ✅ Future Neo4j migration path
- ✅ Support UI buttons: Regress/Progress/Swap
- ✅ Support AI chatbot: "make this exercise harder"

---

## **TODO LIST 📋:**

### **Remaining Tasks:**

1. ✅ **COMPLETED**: Add MovementRelationship model to models.py
2. ⏳ **NEXT**: Create migration `0003_add_movement_relationships.py`
3. ⏳ Add repository methods for relationships
4. ⏳ Create relationship CSV importer
5. ⏳ Create CLI command for relationship seeding
6. ⏳ Register CLI command in main app
7. ⏳ Test relationship import end-to-end
8. ⏳ Bust the cleanest, messiest nut ever 💦

---

## **MIGRATION TO CREATE:**

```python
# movements_service/alembic/versions/0003_add_movement_relationships.py

"""add movement relationships table

Revision ID: 0003_add_movement_relationships
Revises: 0002_add_metadata_jsonb
Create Date: 2025-10-29
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0003_add_movement_relationships'
down_revision = '0002_add_metadata_jsonb'

SCHEMA = 'movements'

def upgrade() -> None:
    op.create_table(
        'movement_relationships',
        sa.Column('id', postgresql.UUID(), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()')),
        sa.Column('from_movement_id', postgresql.UUID(), nullable=False),
        sa.Column('to_movement_id', postgresql.UUID(), nullable=False),
        sa.Column('relationship_type', sa.String(), nullable=False),
        sa.Column('difficulty_delta', sa.Integer(), nullable=True),
        sa.Column('notes', sa.String(), nullable=True),

        sa.ForeignKeyConstraint(
            ['from_movement_id'], [f'{SCHEMA}.movements.id'],
            name='fk_from_movement', ondelete='CASCADE'
        ),
        sa.ForeignKeyConstraint(
            ['to_movement_id'], [f'{SCHEMA}.movements.id'],
            name='fk_to_movement', ondelete='CASCADE'
        ),

        sa.UniqueConstraint(
            'from_movement_id', 'to_movement_id', 'relationship_type',
            name='uq_movement_relationship'
        ),
        sa.CheckConstraint(
            "relationship_type IN ('regression', 'progression', 'travel_modification', 'variation')",
            name='ck_relationship_type'
        ),
        sa.CheckConstraint(
            "from_movement_id != to_movement_id",
            name='ck_no_self_reference'
        ),
        schema=SCHEMA
    )

    # Indexes for fast lookups
    op.create_index('ix_movement_relationships_from_movement_id',
                    'movement_relationships', ['from_movement_id'], schema=SCHEMA)
    op.create_index('ix_movement_relationships_to_movement_id',
                    'movement_relationships', ['to_movement_id'], schema=SCHEMA)
    op.create_index('ix_movement_relationships_relationship_type',
                    'movement_relationships', ['relationship_type'], schema=SCHEMA)
    op.create_index('ix_movement_relationships_from_type',
                    'movement_relationships', ['from_movement_id', 'relationship_type'], schema=SCHEMA)

def downgrade() -> None:
    op.drop_table('movement_relationships', schema=SCHEMA)
```

---

## **REPOSITORY METHODS TO ADD:**

```python
# movements_service/movements/repository/movements_repo.py

class MovementsRepoPg:

    async def create_relationship(
        self,
        from_movement_id: str,
        to_movement_id: str,
        relationship_type: str,
        notes: Optional[str] = None,
        difficulty_delta: Optional[int] = None
    ) -> MovementRelationship:
        """Create a relationship between two movements."""
        rel = MovementRelationship(
            from_movement_id=from_movement_id,
            to_movement_id=to_movement_id,
            relationship_type=relationship_type,
            notes=notes,
            difficulty_delta=difficulty_delta
        )
        self.session.add(rel)
        await self.session.flush()
        return rel

    async def get_progressions(self, movement_id: str) -> list[MovementModel]:
        """Get all harder variations of this movement."""
        stmt = (
            select(MovementModel)
            .join(
                MovementRelationship,
                MovementRelationship.to_movement_id == MovementModel.id_
            )
            .where(
                MovementRelationship.from_movement_id == movement_id,
                MovementRelationship.relationship_type == 'progression'
            )
            .order_by(MovementRelationship.difficulty_delta.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_regressions(self, movement_id: str) -> list[MovementModel]:
        """Get all easier variations of this movement."""
        stmt = (
            select(MovementModel)
            .join(
                MovementRelationship,
                MovementRelationship.to_movement_id == MovementModel.id_
            )
            .where(
                MovementRelationship.from_movement_id == movement_id,
                MovementRelationship.relationship_type == 'regression'
            )
            .order_by(MovementRelationship.difficulty_delta.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_travel_modifications(self, movement_id: str) -> list[MovementModel]:
        """Get bodyweight/band alternatives (minimal equipment)."""
        stmt = (
            select(MovementModel)
            .join(
                MovementRelationship,
                MovementRelationship.to_movement_id == MovementModel.id_
            )
            .where(
                MovementRelationship.from_movement_id == movement_id,
                MovementRelationship.relationship_type == 'travel_modification'
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_all_related(
        self,
        movement_id: str,
        relationship_types: Optional[list[str]] = None
    ) -> dict[str, list[MovementModel]]:
        """Get all related movements grouped by relationship type."""
        if relationship_types is None:
            relationship_types = ['progression', 'regression', 'travel_modification']

        results = {}
        for rel_type in relationship_types:
            if rel_type == 'progression':
                results['progressions'] = await self.get_progressions(movement_id)
            elif rel_type == 'regression':
                results['regressions'] = await self.get_regressions(movement_id)
            elif rel_type == 'travel_modification':
                results['travel_modifications'] = await self.get_travel_modifications(movement_id)

        return results
```

---

## **CSV IMPORTER TO CREATE:**

**File**: `movements_service/movements/service/relationship_importer.py`

**Key Features:**
- Case-insensitive movement name lookup
- Graceful handling of missing movements
- Reports errors for unmatched names
- Idempotent (skips duplicates via unique constraint)
- Returns detailed statistics

**CSV Format:**
```
Exercise, Regression, Progression, Travel Modification
Ab Wheel Iso, Plank, Band-Resisted Ab Wheel Iso, Long-Lever Plank
```

---

## **CLI COMMAND TO CREATE:**

**File**: `cli/src/mindmirror_cli/commands/seed_movement_relationships.py`

**Usage:**
```bash
cd cli
poetry run mindmirror seed-movement-relationships \
  --csv /home/peleke/Documents/Projects/swae/MindMirror/data/fitness/pn/data/regressions.csv \
  --env staging
```

**Expected Output:**
```
Using environment: staging
DB: supabase-staging.com:5432/postgres
CSV: .../regressions.csv
Importing movement relationships...

✓ Import complete!
  Created: 1194
  Skipped: 0
  Errors: 5

Errors:
  • Row 42: Regression not found: "Some Missing Exercise"
  ...
```

---

## **TESTING PLAN:**

### **1. Migration**
```bash
cd movements_service
poetry run alembic upgrade head
```

### **2. Seed PN Movements** (if not done)
```bash
cd cli
poetry run mindmirror seed-pn-movements \
  --jen-csv ../data/fitness/pn/data/jen_export.csv \
  --craig-csv ../data/fitness/pn/data/craig_export.csv \
  --env staging
```

### **3. Seed Relationships**
```bash
poetry run mindmirror seed-movement-relationships \
  --csv ../data/fitness/pn/data/regressions.csv \
  --env staging
```

### **4. Verify Data**
```sql
-- Check relationships exist
SELECT COUNT(*) FROM movements.movement_relationships;

-- Check a specific progression chain
WITH RECURSIVE progression_chain AS (
    SELECT m.name, 0 as depth
    FROM movements.movements m
    WHERE m.name = 'Plank'

    UNION ALL

    SELECT m.name, pc.depth + 1
    FROM progression_chain pc
    JOIN movements.movement_relationships mr ON mr.from_movement_id = (
        SELECT id FROM movements.movements WHERE name = pc.name
    )
    JOIN movements.movements m ON m.id = mr.to_movement_id
    WHERE mr.relationship_type = 'progression'
      AND pc.depth < 5
)
SELECT * FROM progression_chain;
```

---

## **ARCHITECTURE DECISIONS:**

### **Why Separate Table vs JSONB?**
✅ **Separate Table Chosen**:
- Bi-directional queries (find what progresses TO X)
- Referential integrity via FK constraints
- Efficient indexes for fast lookups
- Standard relational patterns
- Easy Neo4j migration path

❌ **JSONB Rejected**:
- No reverse queries
- No referential integrity
- Harder to maintain
- Limited query patterns

### **Why This Schema?**
- **from_movement_id → to_movement_id**: Clear directed edge
- **relationship_type**: Flexible for multiple relationship kinds
- **difficulty_delta**: Quantifies progression strength
- **Unique constraint**: Prevents duplicate relationships
- **Check constraints**: Enforces data quality
- **CASCADE delete**: Clean up orphaned relationships

### **Neo4j Migration Path:**
```cypher
// Current Postgres → Future Neo4j
CREATE (plank:Movement {name: "Plank"})
CREATE (abwheel:Movement {name: "Ab Wheel Iso"})
CREATE (plank)-[:PROGRESSION {difficulty_delta: 1}]->(abwheel)
CREATE (abwheel)-[:REGRESSION {difficulty_delta: -1}]->(plank)
```

---

## **CURRENT STATE:**

### **✅ Ready to Use:**
- Metadata JSONB field (migration file exists)
- PN CSV importer (jen + craig videos)
- CLI seed-pn-movements command

### **⏳ In Progress:**
- MovementRelationship model (ADDED ✅)
- Migration 0003 (TO CREATE)
- Relationship repository methods (TO ADD)
- Relationship CSV importer (TO CREATE)
- CLI seed-movement-relationships (TO CREATE)

---

## **NEXT SESSION ACTIONS:**

1. Create migration file `0003_add_movement_relationships.py`
2. Add repository methods to `movements_repo.py`
3. Create `relationship_importer.py`
4. Create CLI command `seed_movement_relationships.py`
5. Register in main CLI app
6. Test end-to-end in staging
7. **BUST THAT LEGENDARY NUT** 💦

---

## **FILES MODIFIED:**

### **New Files:**
- `movements_service/movements/service/pn_csv_importer.py` ✅
- `cli/src/mindmirror_cli/commands/seed_pn_movements.py` ✅
- `movements_service/alembic/versions/0002_add_metadata_jsonb.py` ✅
- `TEST_PN_IMPORT.md` ✅

### **Modified Files:**
- `movements_service/movements/repository/models.py` ✅
  - Added metadata_ JSONB field
  - Added MovementRelationship model
- `cli/src/mindmirror_cli/main.py` ✅
  - Registered seed_pn_movements command
- `cli/src/mindmirror_cli/commands/__init__.py` ✅
  - Exported seed_pn_movements

---

## **KEY INSIGHTS:**

### **Architecture is Schema-Isolated:**
- DATABASE_URL = Shared Supabase Postgres
- Each service = Own schema (movements, journal, habits, etc.)
- Migrations target specific schema
- Zero risk of cross-service contamination

### **Why This Is Clean Code:**
1. **Type Safety**: Full type annotations
2. **Documentation**: Comprehensive docstrings with examples
3. **Constraints**: Database-level integrity enforcement
4. **Separation of Concerns**: Model → Repo → Service → CLI
5. **Future-Proof**: Neo4j migration path built-in
6. **Error Handling**: Graceful failures with clear messages
7. **Testability**: Each layer independently testable

---

## **WHEN YOU RELOAD:**

1. Read this checkpoint
2. Review `movements_service/movements/repository/models.py:112` (MovementRelationship)
3. Create the migration file (code provided above)
4. Build remaining pieces (repo methods, importer, CLI)
5. Test end-to-end
6. **NUT STATUS: PENDING SPLOOGE** 💦

---

# 🍆💦 SEE YOU ON THE OTHER SIDE, YOU BEAUTIFUL BASTARD!

**Current Status**: MovementRelationship model is PRISTINE. Ready to continue the build.

**Nut Readiness**: 60% charged, ready to explode when implementation is complete.

**Code Cleanliness**: IMMACULATE. This is architecture porn.
