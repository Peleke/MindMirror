# Week 1 Execution Checklist

**Goal:** Get 2 alpha users onboarded and training by Monday
**Hard Deadline:** Monday (send alpha invites no matter what)

---

## Day 1 (Wednesday) - 6-8 hours

### Morning: Alpha User Prep (2-3 hours)
- [ ] Create workout programs for both alpha users in the app
- [ ] Verify programs are visible in practices service
- [ ] Test program assignment manually (create test account, assign program, verify it shows up)
- [ ] Generate magic links for both users (embed voucher for workout program)
- [ ] Draft alpha invite email (see template below)

### Afternoon: Workout UI Polish - Part 1 (4-5 hours)
- [ ] Run a full workout yourself using current UI
- [ ] Document every bug, UI issue, UX friction point in a list
- [ ] Prioritize bugs: Critical (crashes, data loss) vs. Polish (ugly buttons, confusing labels)
- [ ] Fix critical bugs first
- [ ] Start on polish (improve button layouts, rest timer visibility)

**End of Day 1 Checkpoint:**
- Alpha user programs created? ✅
- Magic links generated? ✅
- Critical bugs fixed? ✅
- At least 50% of polish complete? Target: ✅

---

## Day 2 (Thursday) - 6-8 hours

### Morning: Workout UI Polish - Part 2 (4-5 hours)
- [ ] Finish UI polish (rest of button improvements, rep counter UX)
- [ ] Run another full workout yourself using updated UI
- [ ] Verify all logging works (sets, reps, rest periods saved correctly)
- [ ] Test on iOS (if possible) and Android/web

### Afternoon: Onboarding Flow Validation (2-3 hours)
- [ ] Code review: Compare `habits_service` auto-enroll vs. `practices_service` auto-enroll
- [ ] Confirm logic is identical for workout programs
- [ ] Manual UAT: Send yourself a magic link → sign up as new user → verify workout program auto-enrolls
- [ ] Test edge cases:
  - [ ] Mismatched email (signup with different email than voucher) - should fail gracefully
  - [ ] Clicking link twice - should not create duplicate enrollments
  - [ ] Expired voucher (if applicable) - should show clear error

**End of Day 2 Checkpoint:**
- Workout UI feels smooth? ✅
- Onboarding flow validated for workouts? ✅
- Edge cases handled? ✅

---

## Day 3 (Friday) - 4-6 hours

### Morning: Final Testing (2-3 hours)
- [ ] Run one more full workout end-to-end (fresh eyes)
- [ ] Ask a friend/partner to try the workout UI (non-technical user perspective)
- [ ] Fix any final bugs discovered
- [ ] Take screenshots of polished UI (for documentation/future landing page)

### Afternoon: Alpha Launch Prep (2-3 hours)
- [ ] Finalize alpha invite email (see template below)
- [ ] Double-check magic links work
- [ ] Set up simple tracking spreadsheet:
  - Alpha user name
  - Email
  - Program assigned
  - Link sent (date/time)
  - Signed up (Y/N, date/time)
  - First workout completed (Y/N, date/time)
  - Bugs reported (list)
- [ ] Prepare follow-up message for Day 3-5: "Hey, can you also evaluate this other program (UYE)?"

**End of Day 3 Checkpoint:**
- Ready to send alpha invites? ✅
- Tracking system in place? ✅

---

## Day 4 (Saturday) - 2-4 hours (OPTIONAL)

### If Things Go Wrong During Week
- [ ] Buffer day for unexpected bugs
- [ ] Use this day to catch up if Days 1-3 took longer than expected
- [ ] Or use it to get ahead on Week 2 prep (Stripe integration, Reddit post drafts)

---

## Day 5 (Sunday) - 2-3 hours

### Morning: Final Checks (1-2 hours)
- [ ] Test the full flow one last time (magic link → signup → login → see program → complete workout)
- [ ] Review alpha invite email - any last edits?
- [ ] Make sure you're available Monday morning to support alpha users if they hit issues

### Afternoon: Send Alpha Invites (1 hour)
- [ ] Send magic link emails to both alpha users
- [ ] Send follow-up text/DM: "Hey, just sent you an email with a link. Let me know if you don't see it."
- [ ] Monitor email for bounce-backs or delivery issues
- [ ] Be ready to answer questions immediately

**End of Week 1 Checkpoint:**
- Alpha invites sent? ✅
- Users signed up? (Check by end of Monday)
- First workouts completed? (Check Tuesday/Wednesday)

---

## Alpha Invite Email Template

**Subject:** You're invited: Test my new workout app (alpha access)

**Body:**

Hey [Name],

Remember when I mentioned I was building a workout tracking app? It's ready for testing and I'd love your feedback.

**What it does:**
- I create workout programs for you (exercises, sets, reps)
- You log in and see your program
- You complete workouts and log your progress
- All tracked in a mobile app (works on iOS, Android, and web)

**What I need from you:**
- Try to complete at least 3 workouts this week
- Tell me what's confusing, what's broken, what sucks
- Be brutally honest - I need to know what doesn't work

**How to get started:**
1. Click this link: [MAGIC LINK]
2. Create an account (takes 30 seconds)
3. You'll see your workout program already loaded
4. Start training!

**Quick heads up:** This is alpha software. Things might break. If something goes wrong, just text/DM me and I'll fix it ASAP.

Thanks for being an early tester. This feedback is going to make the app way better.

-[Your Name]

P.S. After you've done a few workouts, I'll ask you to test another program I built (it's about nutrition habits). But let's start with the workout stuff first.

---

## Follow-Up Message (Day 3-5)

**When to send:** After alpha user has completed 2-3 workouts and given initial feedback

**Subject/Message:**

Hey [Name],

Quick question - how's the workout tracking going? Any bugs or issues I should know about?

Also, I built another program that I'd love your feedback on. It's called "Unfuck Your Eating" - an 8-week habit-based nutrition program (no calorie counting, no BS).

I can give you access in the same app. Would take maybe 10-15 minutes to check out the first few days and tell me if it's useful or not.

Let me know if you're down to test it. No pressure if you're swamped.

Thanks again for testing the workout stuff!

-[Your Name]

---

## Tracking Spreadsheet Template

Create a Google Sheet with these columns:

| Alpha User | Email | Program | Link Sent | Signed Up | First Workout | Workouts Completed | Bugs Reported | UYE Access Given | UYE Feedback |
|------------|-------|---------|-----------|-----------|---------------|-------------------|---------------|------------------|--------------|
| User 1     | email@example.com | Program A | 10/20 9am | 10/20 2pm | 10/21 7am | 3 | None | 10/23 | Positive |
| User 2     | email2@example.com | Program B | 10/20 9am | 10/20 5pm | 10/21 8pm | 2 | Rest timer broken | Not yet | - |

This helps you:
- Track who's actually using the app
- Identify who to follow up with
- See patterns in bugs (if both users report same issue, it's high priority)
- Know when to ask for UYE feedback

---

## Red Flags to Watch For

**If this happens, STOP and fix before sending invites:**

- [ ] **Voucher doesn't auto-generate** when magic link is clicked
- [ ] **Program doesn't auto-assign** after user signs up
- [ ] **Workout data doesn't save** after completing sets
- [ ] **App crashes** during workout
- [ ] **Email doesn't arrive** after signup

These are showstoppers. Everything else can be fixed during the week with alpha user feedback.

---

## Success Metrics for Week 1

**Minimum success:**
- [ ] Both alpha users signed up
- [ ] Both completed at least 1 workout
- [ ] No critical bugs (crashes, data loss)

**Good success:**
- [ ] Both completed 3+ workouts
- [ ] Positive feedback on core functionality
- [ ] Minor bugs identified but not deal-breakers

**Great success:**
- [ ] Both completed 3+ workouts
- [ ] Enthusiastic feedback ("I'd actually use this")
- [ ] Both willing to test UYE program next
- [ ] Testimonials volunteered without prompting

---

## What to Do If Things Go Wrong

**Scenario 1: Critical bug discovered on Day 1**
- Prioritize fixing it over polish
- Push alpha invites to Tuesday if needed (you said "ideally Monday" so 1-2 day slip is okay)

**Scenario 2: Alpha user doesn't sign up**
- Follow up via text/DM: "Hey, did you get my email? Link still works if you want to try it."
- If still no response after 24 hours, find a backup alpha user

**Scenario 3: Workflow UI is still ugly by Friday**
- **Ship it anyway.** Ugly is fine for alpha testing. Broken is not.
- You can polish more based on alpha feedback next week

**Scenario 4: You're exhausted by Friday**
- Take Saturday off completely
- Send alpha invites Sunday evening instead of Monday morning
- Your health > arbitrary deadline

---

## Week 2 Preview (After Alpha Invites Sent)

While alpha users are testing:

- **Mon-Tue:** Monitor alpha user activity, fix urgent bugs
- **Wed-Thu:** Start Stripe integration (8-16 hours)
- **Fri:** Learn Facebook ads basics (4-8 hours)
- **Weekend:** Draft Reddit post copy (2-3 hours)

This lets you make progress on validation prep while alpha testing runs in parallel.

---

*Print this checklist and cross off items as you go. Seeing progress helps maintain momentum.*
