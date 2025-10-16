# Alpha Validation: Week 1 Push

**Goal:** Stress test existing voucher/enrollment infrastructure with User 1, THEN onboard Users 2-3.

**Timeline:** Next 7 days

**Decision Point:** After 4 weeks, gut-check which demographic to double down on (likely combat sports).

---

## Existing Infrastructure (Already Built)

**7-Step Voucher/Magic Link System:**

1. ✅ **Link Generation** - Magic link with embedded voucher
2. ✅ **Voucher Creation** - Clicking link mints voucher (email + program ID)
   - Confirmed working for: habits_service, lessons
   - **Needs stress testing for:** practices_service (workouts)
3. ✅ **Signup Redirect** - Link → Supabase signup page
4. ✅ **Email Matching** - Signup email matches voucher recipient (Supabase validation)
5. ✅ **Auto-Enrollment on Login** - Voucher check → program assignment
   - GraphQL endpoints: `habits_service`, `practices_service`
6. ✅ **Program Visibility** - User sees assigned workout in UI
7. ⚠️ **Workout Execution** - User logs sets/reps/rest (needs polish + bug fixes)

**Key File Locations:**
- Voucher minting: `web/supabase/edge-functions/`
- Auto-enroll (workouts): `practices_service/` GraphQL endpoint
- Workout UI: `mindmirror-mobile/app/(app)/client/[id].tsx`

**Week 1 Strategy:**
- Day 1-2: Stress test Steps 1-7 with test accounts (NOT real users yet)
- Day 3: Fix critical bugs
- Day 4: Invite User 1 (knee program already built)
- Day 5: Monitor User 1's first workout, collect feedback
- Day 6-7: Build programs for Users 2-3, send invites

---

## Alpha User Profiles

### User 1: 50-year-old Female (Knee Pain)
- **Presenting Issue:** Patellofemoral pain syndrome
- **Program:** Knee rehab program (ALREADY BUILT ✅)
- **Check-in Frequency:** Daily (in-person or text)
- **Primary Goal:** Pain reduction, functional improvement
- **App Features to Test:**
  - Movement tracking
  - Pain/progress logging
  - Program progression (does it adapt as she improves?)

### User 2: Anterior Bias / AC Joint Dysfunction
- **Presenting Issue:** General anterior bias → acromioclavicular dysfunction (likely lumbopelvic origin)
- **Program:** Postural correction + shoulder/lumbar rehab (NEED TO BUILD 🔨)
- **Check-in Frequency:** Daily (in-person or text)
- **Primary Goal:** Reduce shoulder dysfunction, improve lumbar stability
- **App Features to Test:**
  - Exercise library (do videos/descriptions make sense?)
  - Movement assessment integration
  - Weekly progress tracking

### User 3: Combat Athlete (BJJ + Boxing)
- **Presenting Issue:** Needs strength & conditioning program post-skill training
- **Program:** Barbell program for combat sports (NEED TO BUILD 🔨)
- **Check-in Frequency:** Weekly in-person + text as needed
- **Primary Goal:** Build strength without interfering with skill work
- **App Features to Test:**
  - Workout logging (sets, reps, weight tracking)
  - Rest timer functionality
  - Program flexibility (can he swap exercises if needed?)

### User 4 (Optional Backup)
- **TBD** - If one of the above three drops out or doesn't engage, recruit backup user
- **Likely profile:** Another combat athlete or desk worker with shoulder/neck pain

---

## Programs to Build (Priority Order)

### 1. Anterior Bias / AC Dysfunction Program (User 2)
**Build by:** Day 2-3 of Week 1

**Program Structure:**
- **Phase 1 (Weeks 1-2):** Lumbar stability foundation
  - Dead bugs, bird dogs, planks (anti-extension/rotation)
  - Hip flexor/quad stretching (address anterior tilt)
  - Scapular retraction drills (rows, band pull-aparts)
- **Phase 2 (Weeks 3-4):** Shoulder integration
  - Face pulls, Y-T-W raises (posterior chain activation)
  - Single-arm rows (unilateral scapular stability)
  - Half-kneeling exercises (integrate lumbar stability + shoulder work)
- **Phase 3 (Weeks 5-6+):** Load progression
  - Add weight to rowing patterns
  - Progress to overhead pressing (if pain-free)
  - Farmer carries (full-body integration)

**App Requirements:**
- Video demos for each exercise
- Coaching cues (e.g., "Keep ribs down, don't flare")
- Pain tracking (shoulder pain scale 1-10 daily)

---

### 2. Combat Athlete Barbell Program (User 3)
**Build by:** Day 4-5 of Week 1

**Program Structure:**
- **Training Frequency:** 2-3x/week (post-skill training)
- **Focus:** Strength without mass gain, injury prevention
- **Weekly Template:**
  - **Day 1 (Lower):** Squat variation (goblet, front squat), RDL, single-leg work
  - **Day 2 (Upper):** Bench or overhead press, horizontal row, chin-ups
  - **Day 3 (Optional Power/Conditioning):** Trap bar deadlift, push press, sled work
- **Key Constraints:**
  - Keep volume moderate (2-3 sets per exercise, don't fry CNS)
  - Avoid exercises that interfere with skill work (e.g., no heavy grip work before grappling)
  - Emphasize neck strength, posterior chain, anti-rotation core

**App Requirements:**
- Weight/rep tracking (progressive overload)
- Rest timer between sets (2-3 minutes for strength work)
- Exercise swap options (e.g., "Gym doesn't have trap bar? Do conventional deadlift instead")

---

## Feature Validation Checklist

**Core Features to Test:**

### Onboarding & Enrollment
- [ ] Magic link signup works (User 1, 2, 3 can create accounts)
- [ ] Program auto-assigns after signup (voucher system works)
- [ ] Users can see their assigned program on first login

### Program Viewing & Navigation
- [ ] Users can view program overview (see all weeks/phases)
- [ ] Users can see today's workout
- [ ] Exercise descriptions are clear (text + video if available)
- [ ] Users can navigate between past/future workouts

### Workout Logging
- [ ] Users can log sets, reps, weight (for barbell program)
- [ ] Users can mark exercises as complete
- [ ] Rest timer works and is visible during workout
- [ ] Workout data saves correctly (doesn't disappear on refresh)

### Progress Tracking
- [ ] Users can see workout history (past sessions)
- [ ] Pain/progress notes can be added (text field for subjective feedback)
- [ ] Progress charts/graphs display (if feature exists)

### Edge Cases
- [ ] What happens if user skips a workout? (Does program adjust or just move to next day?)
- [ ] Can users restart a workout if they exit mid-session?
- [ ] What if internet drops mid-workout? (Does data sync when reconnected?)

### UX Polish
- [ ] App feels smooth (no janky animations or slow loading)
- [ ] Buttons are intuitive (users don't ask "how do I log this?")
- [ ] Error messages are clear (e.g., "Workout failed to save. Retry?")

---

## Week 1 Execution Timeline

**PRIORITY: Stress test existing infrastructure BEFORE building new programs**

### Day 1-2: Stress Test Existing System (User 1 Only)
- [ ] **Confirm User 1's knee program exists in app** (already built)
- [ ] **Generate magic link for User 1** (embed voucher for knee program)
- [ ] **Test Step 1-2:** Click magic link → verify voucher mints (check database or logs)
- [ ] **Test Step 3-4:** Complete Supabase signup → verify email matches voucher
- [ ] **Test Step 5:** Login → verify auto-enrollment (knee program assigned)
- [ ] **Test Step 6:** Navigate to program → verify UI displays workout correctly
- [ ] **Test Step 7:** Complete full workout → log sets/reps/rest → verify data saves
- [ ] **Repeat end-to-end flow 2-3 times** (delete test account, re-test from scratch)
- [ ] **Document ALL bugs/edge cases discovered** (spreadsheet or doc)

**Critical Infrastructure Tests:**
- [ ] What happens if user clicks magic link twice? (duplicate vouchers?)
- [ ] What if signup email differs from voucher email? (should fail gracefully)
- [ ] What if user exits mid-workout? (does progress save or reset?)
- [ ] What if internet drops during workout logging? (does data sync when reconnected?)
- [ ] Can user navigate back to previous workouts? (history view works?)

### Day 3: Fix Critical Bugs
- [ ] Prioritize bugs: **Critical** (crashes, data loss, enrollment breaks) vs. **Polish** (ugly UI, confusing labels)
- [ ] **Fix ALL critical bugs** before inviting User 1
- [ ] Re-test end-to-end flow after fixes
- [ ] Document remaining polish items for Week 2

### Day 4: Invite User 1 (Knee Program)
- [ ] Send magic link to User 1 via email/text
- [ ] Follow up immediately: "Link sent, let me know if you have issues"
- [ ] Monitor signup (check database or admin panel)
- [ ] **Be available for support** if User 1 hits issues during signup/first workout

### Day 5: User 1 First Workout + Daily Check-in
- [ ] User 1 completes first knee rehab session
- [ ] Check in: "How was the workout? Anything broken or confusing?"
- [ ] Track pain level: "Knee pain today? 1-10 scale"
- [ ] Note any bugs or UX friction
- [ ] **Fix urgent bugs immediately** (if User 1 is blocked)

### Day 6-7: Build Programs for Users 2 & 3
**ONLY proceed if User 1's flow worked smoothly**

- [ ] Create User 2's anterior bias/AC program in app
- [ ] Create User 3's barbell program in app
- [ ] Verify both programs display correctly in practices service
- [ ] Generate magic links for Users 2 & 3 (embed voucher for correct program)
- [ ] Send invites to Users 2 & 3 (same process as User 1)

**End of Week 1 Success Criteria:**
- [ ] User 1 signed up and completed 1-2 workouts successfully
- [ ] No critical bugs in voucher/enrollment/workout flow
- [ ] Programs built for Users 2 & 3 (ready to invite)
- [ ] ALL three users invited by end of Week 1 (User 1 by Day 4, Users 2-3 by Day 7)

---

## Weeks 2-4: Ongoing Validation

**Weekly Cadence:**

### Week 2
- **User 1 (50+ Knee):** Daily check-ins, track pain levels (1-10 scale), adjust program if needed
- **User 2 (AC Dysfunction):** Daily check-ins, monitor shoulder pain + lumbar stability improvements
- **User 3 (Combat Athlete):** Weekly in-person session + mid-week text check-in ("How was Tuesday's lift?")
- **Focus:** Fix bugs discovered in Week 1, polish UX based on feedback

### Week 3
- **User 1:** Should see measurable improvement in knee pain (8/10 → 5/10 target)
- **User 2:** Should notice reduced shoulder dysfunction, better posture awareness
- **User 3:** Should be comfortable with workout logging, able to track progressive overload
- **Focus:** Test program progression (does app automatically advance users to next phase?)

### Week 4
- **User 1:** Gut-check - is she still engaged? Would she pay $25/month for this?
- **User 2:** Gut-check - does he see value? Would he recommend to friends?
- **User 3:** Gut-check - is this better than a generic workout app? Would other fighters use this?
- **Focus:** Decision point - which demographic showed strongest engagement?

---

## Feedback Collection (Lightweight)

**For Users 1 & 2 (Daily Check-ins):**
- Quick text: "How was today's workout? Anything broken or confusing?"
- Track pain levels: "Knee pain today? 1-10 scale"
- Note any bugs/UX friction in a simple spreadsheet or note

**For User 3 (Weekly Check-ins):**
- In-person or video call: "Walk me through your last 2 workouts. What sucked?"
- Ask about specific features: "Did the rest timer work? Was weight tracking easy?"
- Note any feature requests: "What would make this app way better for you?"

**Simple Tracking Spreadsheet:**

| User | Date | Workout Completed | Pain Level (1-10) | Bugs Reported | Feature Requests | Would Recommend? |
|------|------|-------------------|-------------------|---------------|------------------|------------------|
| User 1 | 10/20 | Knee Rehab Day 1 | 8/10 | None | - | TBD |
| User 2 | 10/20 | Posture Day 1 | 6/10 (shoulder) | Rest timer didn't show | Video demos | TBD |
| User 3 | 10/21 | Barbell Day 1 | N/A | Can't edit weight mid-set | Exercise swap option | TBD |

---

## Decision Framework (End of Week 4)

**Question:** Which demographic should we double down on?

**Gut-Check Indicators:**

### Combat Athletes (User 3 + potential gym referrals)
- **Strong signal:** User 3 enthusiastic, brings training partners to test app
- **Strong signal:** User 3 willing to pay $25/month, sees clear value over YouTube
- **Strong signal:** Easy to recruit more testers (gym has 50+ members, tight community)
- **Weak signal:** User 3 completes workouts but doesn't engage deeply
- **Weak signal:** Hard to recruit more testers (gym members aren't interested)

### 50+ Demographic (User 1)
- **Strong signal:** User 1 sees measurable pain reduction (8/10 → 3/10 in 4 weeks)
- **Strong signal:** User 1 tells friends about app, volunteers testimonial
- **Strong signal:** Willing to pay because "it's cheaper than physical therapy"
- **Weak signal:** User 1 drops off after 2 weeks, says "I forgot to use it"
- **Weak signal:** Pain didn't improve (program didn't work or adherence was low)

### Desk Workers / Posture Dysfunction (User 2)
- **Strong signal:** User 2 sees shoulder pain reduction + functional improvement
- **Strong signal:** User 2 refers coworkers or gym friends with similar issues
- **Strong signal:** Large addressable market (everyone has desk job pain)
- **Weak signal:** User 2 completes workouts but doesn't see results
- **Weak signal:** Hard to recruit more testers (desk workers don't prioritize movement)

**Expected Outcome (Your Gut Feel):**
- **Likely winner:** Combat athletes
- **Reasoning:** Easier to access (gym community), intrinsically motivated (already train 3-6x/week), willing to pay for expertise
- **Next steps if combat wins:** Build 3-5 more combat-specific programs (striker conditioning, BJJ strength, shoulder health for boxers), recruit 10-20 beta testers from local gyms

**Backup plan if combat doesn't hit:**
- Test 50+ demographic next (recruit via Facebook, doctor referrals, senior centers)
- Build 2-3 joint-friendly programs (hip mobility, balance/fall prevention, bone density)

---

## Red Flags (Stop and Fix Immediately)

**If any of these happen in Week 1, PAUSE alpha push and fix:**

- [ ] **Voucher system breaks** - Users sign up but program doesn't auto-assign
- [ ] **Data doesn't save** - Users complete workouts but app loses their progress
- [ ] **App crashes mid-workout** - Critical UX failure, will kill engagement
- [ ] **Magic links don't work** - Users can't even sign up

**These are showstoppers. Fix before continuing.**

---

## Success Metrics (Simple)

**Minimum Success (Week 1):**
- [ ] 3/3 users signed up
- [ ] 3/3 completed at least 1 workout
- [ ] 0 critical bugs (crashes, data loss)

**Good Success (Week 4):**
- [ ] 3/3 users still engaged (completed 8+ workouts)
- [ ] Positive feedback ("I'd actually use this regularly")
- [ ] 1-2 users willing to pay $25/month
- [ ] Clear signal on which demographic is strongest

**Great Success (Week 4):**
- [ ] 3/3 users enthusiastic (volunteered testimonials without asking)
- [ ] User 3 (combat athlete) recruited 2-3 training partners to test app
- [ ] Measurable results (User 1's knee pain down 50%+, User 2's shoulder dysfunction improved)
- [ ] Clear decision to double down on combat sports niche

---

## Next Steps After Week 4

**If combat sports shows strongest signal:**
1. Build 3-5 more combat-specific programs (striker S&C, grappler strength, injury prevention)
2. Recruit 10-20 beta testers from local gyms (offer free access for 3 months)
3. Create content marketing assets (blog post: "Why Boxers Get Shoulder Impingement," free PDF lead magnets)
4. Start Reddit outreach (r/MuayThai, r/amateur_boxing, r/bjj)

**If 50+ demographic shows strongest signal:**
1. Build 3-5 joint-friendly programs (hip mobility, balance, bone density)
2. Recruit 10-20 beta testers via Facebook ads or doctor referrals
3. Create educational content (menopause + movement, fall prevention, healthy aging)
4. Test pricing ($20-30/month, position as healthcare expense)

**If both show weak signal:**
1. Re-evaluate product-market fit (maybe movement-first isn't right positioning?)
2. Test nutrition-first angle (Unfuck Your Eating program with User 1-3)
3. Consider pivoting to general wellness dashboard (broader appeal, less niche-specific)

---

## Infrastructure Stress Testing Checklist (Day 1-2)

**Goal:** Validate EVERY step of the voucher/enrollment/workout flow BEFORE inviting real users.

### Setup
- [ ] Create test email account (e.g., `test+alpha1@yourdomain.com`)
- [ ] Confirm User 1's knee program exists in practices_service
- [ ] Have database access ready (to verify voucher creation, enrollment status)
- [ ] Have admin panel or logs access (to monitor flow in real-time)

### Test Round 1: Happy Path (Everything Works)
- [ ] **Step 1:** Generate magic link for test email + knee program ID
- [ ] **Step 2:** Click magic link → verify voucher mints (check database: voucher table should have new row with email + program_id)
- [ ] **Step 3:** Complete Supabase signup with SAME email as voucher
- [ ] **Step 4:** Verify email matches (Supabase should accept signup, no error)
- [ ] **Step 5:** Login to app → verify auto-enrollment (check database: user should be enrolled in knee program)
- [ ] **Step 6:** Navigate to program in UI → verify workout displays (exercises, sets, reps visible)
- [ ] **Step 7:** Complete full workout:
  - [ ] Log first exercise (3 sets × 10 reps)
  - [ ] Use rest timer between sets (verify it counts down)
  - [ ] Log second exercise (different rep scheme)
  - [ ] Mark workout as complete
  - [ ] Verify data saves (check database: workout_logs table should have entries)
- [ ] **Step 8:** Logout, login again → verify workout history shows (progress persists)

**Expected result:** All steps work, no errors, data saves correctly.

---

### Test Round 2: Edge Case - Duplicate Magic Link Click
- [ ] **Delete test account** from database (clean slate)
- [ ] Generate new magic link
- [ ] Click link TWICE (in two different browser tabs)
- [ ] Check database: are there TWO vouchers or ONE? (should be ONE, deduplication logic)
- [ ] Complete signup
- [ ] Verify only ONE enrollment (not duplicated)

**Expected result:** System handles duplicate clicks gracefully (no duplicate vouchers/enrollments).

---

### Test Round 3: Edge Case - Email Mismatch
- [ ] Generate magic link for `test+alpha1@yourdomain.com`
- [ ] Click link (voucher mints)
- [ ] Try to sign up with DIFFERENT email (`test+alpha2@yourdomain.com`)
- [ ] **Expected behavior:** System should either:
  - Reject signup with error: "Email doesn't match voucher"
  - OR allow signup but DON'T auto-enroll (no program assigned)
- [ ] Verify user doesn't get access to program (security check)

**Expected result:** System prevents unauthorized access (email mismatch = no enrollment).

---

### Test Round 4: Edge Case - Mid-Workout Exit
- [ ] Start workout (log 1-2 exercises)
- [ ] Exit app mid-workout (close browser/app, don't mark complete)
- [ ] Re-open app, navigate back to workout
- [ ] **Check:** Does progress persist? (Are logged sets still there?)
- [ ] Complete rest of workout, mark as done
- [ ] Verify full workout saves correctly

**Expected result:** Partial progress saves (user doesn't lose data if they exit mid-workout).

---

### Test Round 5: Edge Case - Offline Mode
- [ ] Start workout
- [ ] Log 1 exercise (3 sets)
- [ ] Turn OFF internet (airplane mode or disable WiFi)
- [ ] Try to log next exercise
- [ ] **Check:** Does app crash or show graceful error?
- [ ] Turn internet back ON
- [ ] **Check:** Does data sync? (Logged sets should upload)

**Expected result:** App handles offline mode gracefully (no crash, syncs when reconnected).

---

### Test Round 6: Edge Case - Workout History Navigation
- [ ] Complete 2-3 workouts (different days)
- [ ] Navigate to workout history view
- [ ] **Check:** Can user see past workouts?
- [ ] Click on past workout → **Check:** Can user view details (sets, reps, notes)?
- [ ] Try to edit past workout (if feature exists)

**Expected result:** Workout history is accessible and displays correctly.

---

### Test Round 7: Stress Test - Rapid Logging
- [ ] Start workout
- [ ] Log sets RAPIDLY (tap through 3 sets × 3 exercises = 9 logs in <1 minute)
- [ ] Mark workout complete
- [ ] Check database: Are ALL 9 sets logged correctly? (no data loss due to rapid taps)

**Expected result:** App handles rapid logging without data loss or UI bugs.

---

### Test Round 8: Polish Check - UX Friction Points
- [ ] Run through full flow ONE more time (magic link → signup → workout)
- [ ] Document EVERY moment of confusion:
  - [ ] Is signup flow clear? (Do you know what to click next?)
  - [ ] Is program UI intuitive? (Can you find today's workout easily?)
  - [ ] Is workout logging obvious? (Do buttons make sense?)
  - [ ] Are rest timers visible and easy to use?
  - [ ] Are error messages helpful? (If something breaks, do you know what to do?)

**Expected result:** List of 5-10 UX improvements (even if app works, note what's confusing).

---

### Bug Tracking Template

**Use this format to document bugs during stress testing:**

| Test Round | Bug Description | Severity | Steps to Reproduce | Expected Behavior | Actual Behavior |
|------------|-----------------|----------|-------------------|-------------------|-----------------|
| Round 2 | Duplicate vouchers created | Critical | Click magic link twice | 1 voucher created | 2 vouchers created |
| Round 4 | Mid-workout progress lost | Critical | Exit app mid-workout, re-open | Sets persist | Sets disappeared |
| Round 8 | Rest timer not visible | Polish | Start workout, complete set | Timer shows prominently | Timer hidden in corner |

**Severity levels:**
- **Critical:** Blocks user (crashes, data loss, can't signup, can't complete workout)
- **High:** Major friction (confusing UX, error messages unclear, feature doesn't work as expected)
- **Medium:** Minor annoyance (ugly UI, small layout bugs, typos)
- **Low:** Polish (nice-to-have improvements, feature requests)

**Day 3 Priority:** Fix ALL Critical bugs before inviting User 1. High/Medium/Low can wait for Week 2.

---

*This plan is designed to be lightweight, action-oriented, and gut-feel driven. No overthinking. Just build, ship, learn, iterate.*
