# Week 1 Stress Testing Framework

**Goal:** Validate EVERY step of the voucher/enrollment/workout flow BEFORE inviting real alpha users.

**Timeline:** Day 1-2 of Week 1

**Success Criteria:** All 8 test rounds pass OR all P0 bugs are documented and fixed by Day 3.

---

## Pre-Test Setup

### 1. Environment Preparation

**Required Access:**
- [ ] Local development environment running (`make demo`)
- [ ] Database access (PostgreSQL + Supabase dashboard)
- [ ] Qdrant access (http://localhost:6333/dashboard)
- [ ] Flower UI for Celery monitoring (http://localhost:5555)

**Test Accounts:**
Create disposable email addresses for testing:
```
test+alpha1@yourdomain.com
test+alpha2@yourdomain.com
test+alpha3@yourdomain.com
```

### 2. Verify Test Program Exists

**User 1's Knee Program:**
```bash
# Check practices_service database
psql $DATABASE_URL -c "SELECT id_, title FROM practice_templates WHERE title ILIKE '%knee%';"
```

**Expected Output:**
```
 id_  | title
------+------------------------
 123  | Knee Rehab Program
```

If program doesn't exist, create it before testing.

### 3. Database Query Helpers

Create `scripts/test-helpers/verify-voucher.sql`:
```sql
-- Check if voucher was created
SELECT
  id,
  email,
  program_id,
  created_at,
  redeemed
FROM vouchers
WHERE email LIKE 'test+alpha%'
ORDER BY created_at DESC
LIMIT 5;
```

Create `scripts/test-helpers/verify-enrollment.sql`:
```sql
-- Check if user was auto-enrolled
SELECT
  u.email,
  e.program_id,
  e.enrolled_at,
  e.status
FROM users u
JOIN program_enrollments e ON u.id = e.user_id
WHERE u.email LIKE 'test+alpha%'
ORDER BY e.enrolled_at DESC
LIMIT 5;
```

Create `scripts/test-helpers/reset-test-data.sql`:
```sql
-- Clean up test data (DANGER: only run on local/staging)
DELETE FROM workout_logs WHERE user_id IN (
  SELECT id FROM users WHERE email LIKE 'test+alpha%'
);
DELETE FROM program_enrollments WHERE user_id IN (
  SELECT id FROM users WHERE email LIKE 'test+alpha%'
);
DELETE FROM vouchers WHERE email LIKE 'test+alpha%';
DELETE FROM users WHERE email LIKE 'test+alpha%';
```

---

## Test Round 1: Happy Path (Everything Works)

**Estimated Time:** 45 minutes

**Goal:** Verify full end-to-end flow works with zero errors.

### Step-by-Step Procedure

#### Step 1: Generate Magic Link

**How to generate:**
```bash
# Option A: Use Supabase edge function
curl -X POST https://your-project.supabase.co/functions/v1/create-voucher \
  -H "Authorization: Bearer YOUR_SERVICE_ROLE_KEY" \
  -d '{
    "email": "test+alpha1@yourdomain.com",
    "program_id": "123",
    "program_type": "practice"
  }'

# Option B: Generate manually via admin UI (if exists)
# Option C: Generate via CLI tool (if exists)
```

**Expected Response:**
```json
{
  "magic_link": "https://yourapp.com/signup?voucher=abc123xyz",
  "voucher_id": "v_abc123",
  "expires_at": "2024-10-27T00:00:00Z"
}
```

**Checklist:**
- [ ] Magic link generated successfully
- [ ] Link contains `?voucher=` parameter
- [ ] Link is valid (not expired)

---

#### Step 2: Click Magic Link → Verify Voucher Mints

**Actions:**
1. Copy magic link from Step 1
2. Open in incognito browser window
3. Click the link

**Expected Behavior:**
- Redirected to Supabase signup page
- Email field pre-filled with `test+alpha1@yourdomain.com`
- No error messages

**Database Verification:**
```bash
psql $DATABASE_URL -f scripts/test-helpers/verify-voucher.sql
```

**Expected Output:**
```
 id       | email                          | program_id | created_at          | redeemed
----------+--------------------------------+------------+---------------------+---------
 v_abc123 | test+alpha1@yourdomain.com     | 123        | 2024-10-20 10:00:00 | false
```

**Checklist:**
- [ ] Voucher row exists in database
- [ ] Email matches test account
- [ ] `program_id` is correct (123 = knee program)
- [ ] `redeemed = false` (not yet redeemed)

---

#### Step 3: Complete Supabase Signup

**Actions:**
1. On Supabase signup page, enter:
   - Email: `test+alpha1@yourdomain.com` (should be pre-filled)
   - Password: `TestPassword123!`
2. Click "Sign Up"

**Expected Behavior:**
- Account created successfully
- Redirected to app (mobile or web depending on environment)
- No "email mismatch" errors

**Checklist:**
- [ ] Signup completed without errors
- [ ] Confirmation email received (check test email inbox)
- [ ] Redirected to app homepage

---

#### Step 4: Verify Email Matches Voucher

**This is handled automatically by Supabase validation**

**Database Verification:**
```bash
psql $DATABASE_URL -c "SELECT email, email_confirmed FROM auth.users WHERE email = 'test+alpha1@yourdomain.com';"
```

**Expected Output:**
```
 email                          | email_confirmed
--------------------------------+-----------------
 test+alpha1@yourdomain.com     | true
```

**Checklist:**
- [ ] User exists in `auth.users` table
- [ ] `email_confirmed = true`

---

#### Step 5: Login → Verify Auto-Enrollment

**Actions:**
1. If not automatically logged in, login with test account credentials
2. Navigate to "Home" or "Workouts" tab in app

**Expected Behavior:**
- User is auto-enrolled in knee program on first login
- Program appears in UI (workout card visible)

**Database Verification:**
```bash
psql $DATABASE_URL -f scripts/test-helpers/verify-enrollment.sql
```

**Expected Output:**
```
 email                          | program_id | enrolled_at         | status
--------------------------------+------------+---------------------+--------
 test+alpha1@yourdomain.com     | 123        | 2024-10-20 10:05:00 | active
```

**Checklist:**
- [ ] Enrollment row exists
- [ ] `program_id = 123` (knee program)
- [ ] `status = active`
- [ ] Voucher `redeemed = true` (check vouchers table)

---

#### Step 6: Navigate to Program → Verify Workout Displays

**Actions:**
1. In app, tap on knee program workout card
2. Navigate to today's workout

**Expected Behavior:**
- Workout detail screen loads
- Exercise list visible
- Sets/reps data displays correctly
- Videos/descriptions load (if available)

**Visual Verification:**
- [ ] Workout title: "Knee Rehab - Day 1" (or similar)
- [ ] Exercises listed: 3-5 exercises visible
- [ ] Each exercise shows:
  - [ ] Exercise name (e.g., "Quad Sets")
  - [ ] Target sets/reps (e.g., "3 × 10")
  - [ ] Video preview or placeholder
  - [ ] Description (collapsible)

**Checklist:**
- [ ] Workout loads without errors
- [ ] No missing data (all exercises render)
- [ ] UI is readable (text not cut off)

---

#### Step 7: Complete Full Workout

**Actions:**
1. **Exercise 1 (3 sets × 10 reps):**
   - Tap reps input, enter `10`
   - Tap load input, enter `0` (bodyweight)
   - Tap ✓ button
   - Rest timer should appear (60 seconds)
   - Wait for timer to finish OR tap "Skip"
   - Repeat for sets 2 and 3

2. **Exercise 2 (3 sets × 12 reps):**
   - Tap reps input, enter `12`
   - Tap load input, enter `5` (light weight)
   - Tap ✓ button
   - Use rest timer
   - Repeat for all sets

3. **Complete remaining exercises** (repeat pattern)

4. **Mark workout complete:**
   - Scroll to bottom
   - Tap "Complete Workout" button

**Expected Behavior During Logging:**
- [ ] Input fields accept numeric values
- [ ] Rest timer modal appears prominently (centered, not hidden)
- [ ] Timer counts down correctly
- [ ] Tapping "Skip" closes timer and marks set complete
- [ ] Completed sets show visual feedback (green checkmark, strikethrough, etc.)
- [ ] No lag or freezing when tapping through sets rapidly

**Expected Behavior After Completion:**
- [ ] "Workout Complete" confirmation appears
- [ ] Redirected to home screen
- [ ] Workout card shows "Completed" badge or checkmark

**Database Verification:**
```sql
-- Check workout completion
SELECT
  w.id,
  w.workout_date,
  w.completed,
  w.duration_seconds,
  COUNT(s.id) as total_sets
FROM workout_sessions w
LEFT JOIN set_logs s ON s.workout_session_id = w.id
WHERE w.user_id = (SELECT id FROM users WHERE email = 'test+alpha1@yourdomain.com')
GROUP BY w.id
ORDER BY w.workout_date DESC
LIMIT 1;
```

**Expected Output:**
```
 id  | workout_date | completed | duration_seconds | total_sets
-----+--------------+-----------+------------------+-----------
 456 | 2024-10-20   | true      | 1234             | 9
```

**Checklist:**
- [ ] Workout session exists in database
- [ ] `completed = true`
- [ ] `total_sets = 9` (or expected count based on program)
- [ ] Each set has `reps`, `load_value`, `load_unit` values

---

#### Step 8: Logout, Login Again → Verify Persistence

**Actions:**
1. Logout of app
2. Login again with same credentials
3. Navigate to workout history or completed workouts view

**Expected Behavior:**
- [ ] Previously completed workout appears in history
- [ ] Set data is still visible (reps/weight saved)
- [ ] No data loss

**Checklist:**
- [ ] Workout history loads
- [ ] Completed workout shows correct date
- [ ] Set details are accurate (reps/weight match what was logged)

---

### Test Round 1 Success Criteria

**PASS if:**
- ✅ All 8 steps completed without errors
- ✅ Voucher created → User enrolled → Workout completed → Data persisted

**FAIL if:**
- ❌ Any step crashes the app
- ❌ Voucher doesn't mint
- ❌ User not auto-enrolled
- ❌ Workout data doesn't save
- ❌ Data lost after logout/login

**If FAIL:** Document bug in tracking spreadsheet (see Bug Tracking Template below)

---

## Test Round 2: Duplicate Magic Link Click

**Estimated Time:** 20 minutes

**Goal:** Verify system handles duplicate link clicks gracefully (no duplicate vouchers/enrollments).

### Procedure

1. **Clean up previous test data:**
   ```bash
   psql $DATABASE_URL -f scripts/test-helpers/reset-test-data.sql
   ```

2. **Generate new magic link** (same as Round 1 Step 1)

3. **Click link in TWO browser tabs simultaneously:**
   - Open incognito tab 1, paste link, press Enter
   - Open incognito tab 2, paste SAME link, press Enter

4. **Check database for duplicate vouchers:**
   ```bash
   psql $DATABASE_URL -f scripts/test-helpers/verify-voucher.sql
   ```

5. **Expected Output:**
   ```
   id       | email                      | program_id | created_at          | redeemed
   ---------+----------------------------+------------+---------------------+---------
   v_abc456 | test+alpha1@yourdomain.com | 123        | 2024-10-20 11:00:00 | false
   ```
   **Only ONE voucher should exist** (not two)

6. **Complete signup** (same as Round 1)

7. **Check for duplicate enrollments:**
   ```bash
   psql $DATABASE_URL -f scripts/test-helpers/verify-enrollment.sql
   ```

8. **Expected Output:**
   ```
   email                      | program_id | enrolled_at         | status
   ---------------------------+------------+---------------------+--------
   test+alpha1@yourdomain.com | 123        | 2024-10-20 11:05:00 | active
   ```
   **Only ONE enrollment should exist**

### Success Criteria

**PASS if:**
- ✅ Only 1 voucher created (no duplicates)
- ✅ Only 1 enrollment created
- ✅ System deduplicates based on email + program_id

**FAIL if:**
- ❌ 2 vouchers created
- ❌ 2 enrollments created
- ❌ App crashes when clicking link twice

**Bug Severity:** Critical (P0) - Duplicate enrollments could break program scheduling

---

## Test Round 3: Email Mismatch

**Estimated Time:** 15 minutes

**Goal:** Verify system prevents unauthorized access if signup email differs from voucher email.

### Procedure

1. **Clean up previous test data**

2. **Generate magic link for** `test+alpha1@yourdomain.com`

3. **Click link** (voucher mints for `test+alpha1@yourdomain.com`)

4. **Attempt signup with DIFFERENT email:**
   - Email: `test+alpha2@yourdomain.com` (DIFFERENT from voucher)
   - Password: `TestPassword123!`

5. **Expected Behavior:**
   - **Option A:** Supabase rejects signup with error: "Email does not match voucher"
   - **Option B:** Signup succeeds BUT user does NOT get auto-enrolled

6. **Verify enrollment table:**
   ```bash
   psql $DATABASE_URL -f scripts/test-helpers/verify-enrollment.sql
   ```

7. **Expected Output:**
   ```
   (0 rows)
   ```
   **No enrollment should exist for `test+alpha2@yourdomain.com`**

### Success Criteria

**PASS if:**
- ✅ System blocks enrollment (email mismatch = no access to program)
- ✅ Error message is clear (user knows what went wrong)

**FAIL if:**
- ❌ User gets enrolled despite email mismatch (SECURITY ISSUE)
- ❌ No error message (user confused)

**Bug Severity:** Critical (P0) - Security vulnerability if mismatched emails can access programs

---

## Test Round 4: Mid-Workout Exit

**Estimated Time:** 20 minutes

**Goal:** Verify partial workout progress persists if user exits mid-workout.

### Procedure

1. **Start new test account** (Round 1 setup)

2. **Navigate to workout, start logging:**
   - Exercise 1: Complete Set 1 (10 reps, 0 kg)
   - Exercise 1: Complete Set 2 (10 reps, 0 kg)
   - **STOP HERE** (do NOT complete Exercise 1 Set 3)

3. **Exit app abruptly:**
   - **Mobile:** Close app (swipe up to kill)
   - **Web:** Close browser tab

4. **Re-open app, navigate back to workout**

5. **Expected Behavior:**
   - Sets 1 and 2 are still marked complete (green checkmarks)
   - Set 3 is still pending (not lost)
   - Data persists across app restart

6. **Database Verification:**
   ```sql
   SELECT
     s.set_number,
     s.reps,
     s.load_value,
     s.completed
   FROM set_logs s
   JOIN workout_sessions w ON s.workout_session_id = w.id
   WHERE w.user_id = (SELECT id FROM users WHERE email = 'test+alpha1@yourdomain.com')
   ORDER BY s.set_number;
   ```

7. **Expected Output:**
   ```
   set_number | reps | load_value | completed
   -----------+------+------------+-----------
   1          | 10   | 0          | true
   2          | 10   | 0          | true
   ```
   **Sets 1-2 saved, Set 3 not yet created**

8. **Complete rest of workout** (verify final completion works)

### Success Criteria

**PASS if:**
- ✅ Partial progress persists
- ✅ User can resume where they left off
- ✅ No data loss

**FAIL if:**
- ❌ All progress lost (sets reset to empty)
- ❌ Workout crashes when re-opened

**Bug Severity:** Critical (P0) - Users will rage-quit if they lose progress

---

## Test Round 5: Offline Mode

**Estimated Time:** 25 minutes

**Goal:** Verify app handles offline mode gracefully (no crash, syncs when reconnected).

### Procedure

1. **Start workout** (new test account)

2. **Log Exercise 1 (3 sets) while ONLINE:**
   - Complete Set 1, Set 2, Set 3
   - Verify sets save (check database)

3. **Turn OFF internet:**
   - **Mobile:** Enable Airplane Mode
   - **Web:** Disable WiFi or use browser DevTools (Network → Offline)

4. **Attempt to log Exercise 2:**
   - Enter reps for Set 1
   - Tap ✓ button
   - **Expected Behavior:**
     - **Option A:** App shows error: "Offline. Changes will sync when reconnected."
     - **Option B:** App queues mutation, shows optimistic update (set appears complete, syncs later)
     - **Option C:** App freezes/crashes (FAIL)

5. **Log 2-3 more sets while offline**

6. **Turn internet back ON**

7. **Expected Behavior:**
   - App detects reconnection
   - Queued mutations upload to server
   - Database updates with offline-logged sets

8. **Database Verification:**
   ```sql
   -- Check if offline sets synced
   SELECT COUNT(*) FROM set_logs WHERE workout_session_id = [session_id];
   ```

9. **Expected Output:**
   ```
   count
   -------
   6
   ```
   **(3 online sets + 3 offline sets = 6 total)**

### Success Criteria

**PASS if:**
- ✅ App doesn't crash when offline
- ✅ Error message is clear OR optimistic updates work
- ✅ Data syncs when reconnected

**FAIL if:**
- ❌ App crashes
- ❌ Data lost (offline sets disappear)
- ❌ No feedback to user (they don't know if data saved)

**Bug Severity:** High (P1) - Users may work out in gyms with poor signal

---

## Test Round 6: Workout History Navigation

**Estimated Time:** 15 minutes

**Goal:** Verify users can view past workouts and drill into details.

### Procedure

1. **Complete 2-3 workouts** (using test account)
   - Workout 1: Knee Rehab Day 1 (today)
   - Workout 2: Knee Rehab Day 2 (tomorrow, manually create or advance date)
   - Workout 3: Knee Rehab Day 3

2. **Navigate to workout history view:**
   - **Expected location:** "Home" tab → "Past Workouts" section
   - **Or:** "Workouts" tab → "History" view

3. **Expected Behavior:**
   - All 3 completed workouts listed
   - Sorted by date (most recent first)
   - Each workout shows:
     - Title (e.g., "Knee Rehab Day 1")
     - Date (e.g., "Oct 20, 2024")
     - Completion badge (green checkmark or "Completed" label)

4. **Tap on Workout 1 (oldest):**
   - Should navigate to workout detail view
   - Sets/reps/weight should display (read-only)
   - Data should match what was logged

5. **Verify data integrity:**
   - Check Exercise 1 Set 1: `10 reps, 0 kg` (or whatever was logged)
   - Check Exercise 2 Set 1: `12 reps, 5 kg`

### Success Criteria

**PASS if:**
- ✅ Workout history accessible
- ✅ All completed workouts listed
- ✅ Past workout details viewable
- ✅ Data matches original logs

**FAIL if:**
- ❌ History view empty (workouts missing)
- ❌ Tapping workout crashes app
- ❌ Data incorrect (reps/weight don't match)

**Bug Severity:** High (P1) - Users need to track progress over time

---

## Test Round 7: Rapid Logging Stress Test

**Estimated Time:** 10 minutes

**Goal:** Verify app handles rapid tapping without data loss or UI bugs.

### Procedure

1. **Start new workout**

2. **Log sets RAPIDLY (as fast as possible):**
   - Exercise 1: Tap reps input, enter `10`, tap ✓
   - Exercise 1: Tap reps input, enter `10`, tap ✓
   - Exercise 1: Tap reps input, enter `10`, tap ✓
   - **Skip rest timer** (tap "Skip" immediately)
   - Repeat for 3 exercises × 3 sets = **9 sets in under 1 minute**

3. **Mark workout complete**

4. **Database Verification:**
   ```sql
   SELECT COUNT(*) FROM set_logs WHERE workout_session_id = [session_id];
   ```

5. **Expected Output:**
   ```
   count
   -------
   9
   ```
   **All 9 sets should be saved**

6. **Check for duplicate sets:**
   ```sql
   SELECT set_number, COUNT(*) as duplicates
   FROM set_logs
   WHERE workout_session_id = [session_id]
   GROUP BY set_number
   HAVING COUNT(*) > 1;
   ```

7. **Expected Output:**
   ```
   (0 rows)
   ```
   **No duplicates**

### Success Criteria

**PASS if:**
- ✅ All 9 sets saved
- ✅ No duplicates
- ✅ No UI freezing/lag
- ✅ No crashes

**FAIL if:**
- ❌ Sets missing (only 7/9 saved)
- ❌ Duplicate sets created
- ❌ App freezes or crashes

**Bug Severity:** Critical (P0) - Users will tap quickly, system must handle concurrency

---

## Test Round 8: UX Friction Audit

**Estimated Time:** 30 minutes

**Goal:** Document EVERY moment of confusion or friction, even if app technically works.

### Procedure

1. **Run through full flow ONE more time** (magic link → signup → workout)

2. **Document friction points:**

   **Signup Flow:**
   - [ ] Is magic link obvious? (Does user know what to click?)
   - [ ] Is signup page clear? (Do they know what to enter?)
   - [ ] Are error messages helpful? (If password too weak, does it say why?)

   **Program UI:**
   - [ ] Can user find today's workout easily? (Within 3 taps?)
   - [ ] Is workout title descriptive? ("Knee Rehab Day 1" vs. "Workout #123")
   - [ ] Are exercise names clear? (Jargon-free or explained?)

   **Workout Logging:**
   - [ ] Is it obvious how to log a set? (Do buttons have clear labels?)
   - [ ] Are input fields easy to tap? (44px touch targets?)
   - [ ] Does rest timer grab attention? (Not hidden in corner?)
   - [ ] Is "Complete Workout" button prominent? (Easy to find when done?)

   **Error Handling:**
   - [ ] What if user enters invalid data? (e.g., `-5` reps)
   - [ ] What if GraphQL mutation fails? (Does user see error or silent failure?)
   - [ ] What if video doesn't load? (Placeholder or broken image?)

3. **Create list of 5-10 UX improvements:**

   Example output:
   ```
   1. "Video" button label unclear → Change to "Watch Demo"
   2. Rest timer bottom sheet hard to see → Convert to centered modal
   3. Completed sets have minimal visual feedback → Add green checkmark
   4. "Complete Workout" button small → Make full-width, prominent color
   5. Error messages generic → Add specific actions ("Check internet, then retry")
   ```

### Success Criteria

**This round ALWAYS passes** (it's a discovery exercise, not pass/fail)

**Deliverable:** List of UX improvements ranked by severity (P0/P1/P2)

---

## Bug Tracking Template

**File:** Create `docs/week-1-bug-tracker.csv` or Google Sheet

**Columns:**

| Test Round | Bug Description | Severity | Steps to Reproduce | Expected Behavior | Actual Behavior | Status | Fix Notes |
|------------|-----------------|----------|-------------------|-------------------|-----------------|--------|-----------|
| Round 2 | Duplicate vouchers created | P0 | Click magic link twice in separate tabs | 1 voucher created | 2 vouchers created | Open | Need deduplication logic |
| Round 4 | Mid-workout progress lost | P0 | Exit app mid-workout, re-open | Sets persist | Sets disappeared | Open | Add auto-save on blur |
| Round 8 | Rest timer not visible | P1 | Complete set | Prominent modal | Hidden bottom sheet | Open | Convert to centered modal |
| Round 8 | "Complete Workout" button small | P2 | Scroll to bottom | Full-width button | Small 120px button | Open | Increase width |

**Severity Levels:**
- **P0 (Critical):** Blocks user from completing core flow (crashes, data loss, signup broken)
- **P1 (High):** Major friction but workaround exists (confusing UI, error messages unclear)
- **P2 (Medium):** Minor annoyance (ugly layout, typos, small visual bugs)
- **P3 (Low):** Polish / nice-to-have (animations, advanced features)

**Day 3 Priority:** Fix ALL P0 bugs before inviting User 1. P1/P2/P3 can wait for Week 2.

---

## Post-Test Checklist

After completing all 8 rounds:

- [ ] Bug tracker populated with all discovered issues
- [ ] Bugs prioritized (P0 vs P1 vs P2)
- [ ] P0 bugs assigned to Day 3-4 fix schedule
- [ ] UX improvement list shared with team
- [ ] Test results documented (8/8 passed OR X bugs found)
- [ ] Decision made: "Ready to invite User 1" OR "Need more fixes"

---

## Day 3-4: Bug Fix Execution

### P0 Bug Fix Process

1. **Triage P0 bugs:**
   - Estimate fix time (each bug 30min - 3hr)
   - Prioritize by impact (data loss > crashes > enrollment broken)

2. **Fix bugs sequentially:**
   - Fix Bug #1
   - Re-run failed test round
   - Verify fix works
   - Move to Bug #2

3. **Re-run ALL test rounds after fixes:**
   - Don't assume fix didn't break something else
   - Full regression test (all 8 rounds)

4. **Document fixes:**
   - Update bug tracker: `Status: Fixed` + `Fix Notes: "Added deduplication check in voucher service"`

### Success Criteria for Day 4

**Ready to invite User 1 if:**
- ✅ All P0 bugs fixed
- ✅ Re-ran all 8 test rounds, all passed
- ✅ No new P0 bugs discovered during regression

**NOT ready if:**
- ❌ Any P0 bugs remain
- ❌ Regression tests revealed new critical issues
- ❌ Fix requires backend changes that aren't deployed

---

*This framework ensures we catch showstoppers BEFORE real users see them. Better to find bugs in controlled testing than during User 1's first workout.*
