# Present
## Product Requirements Document & Implementation Specification

**Product:** Present  
**Product type:** Web-based academic attendance presence log  
**Primary users:** Lecturers and students  
**Primary technology:** Django + PostgreSQL + Django Templates + Tailwind CSS + Vanilla JavaScript  
**Document status:** MVP implementation specification  
**Version:** 2.0

---

# 1. Product Overview

## 1.1 Product concept

**Present** is a lightweight **presence log** for university and other educational settings. It is not the official class register and it does not replace departmental enrolment lists.

The system allows a lecturer to:

1. Create and manage a course (no student roster).
2. Start an attendance session from a device that can provide GPS.
3. Display a QR code on a classroom projector (typically a second, logged-in machine).
4. Watch check-ins on their phone.
5. Optionally mark a small number of students present by hand (dead phone).
6. End the session and export who came.
7. Compare that list to the official class list they already have.

The system allows a student to:

1. Create an account with a university email and student ID.
2. Scan the QR code with the phone camera.
3. Sign in or register on that same attendance URL if needed.
4. Grant location so the server can compare them to the lecturer’s pin.
5. See that they were marked present, and later see how many sessions they have attended.

The core principle is:

> **Students should be able to mark presence in seconds. Lecturers should get a list they can reconcile. The system should make it inconvenient to check in from elsewhere — not claim it is impossible.**

## 1.2 What Present is not

Present does **not**:

- Maintain the official enrolled roster.
- Know who was absent (never-scanned official students do not exist in Present).
- Prove attendance in a way that survives a determined spoof (browser GPS and a static QR are deterrents).
- Onboard students on the lecturer’s behalf.

---

# 2. Product Goals

Present must:

- Make check-in extremely fast for students who are already signed in.
- Make starting a session simple for lecturers.
- Record who checked in, when, and (for audit) where.
- Compare student GPS to the lecturer pin at check-in so a photo of the QR sent to a friend at home usually fails.
- Prevent duplicate presence for the same student in the same session.
- Discourage two students using the same browser device in one session.
- Compile how many sessions each appearing student has attended.
- Let the lecturer export lists and reconcile against their official class list.
- Work in a web browser with no native app.
- Stay simple enough for a small team to deploy.

---

# 3. Non-Goals for MVP

Do not build:

- Lecturer-managed student roster, CSV import, or “add student to course.”
- University SIS / course-registration integration.
- Official absence registers derived from enrolment.
- Tuition, exams, grades, LMS, assignments, chat.
- Facial recognition, fingerprints, or other biometrics.
- Native iOS or Android apps.
- Rotating QR codes, Wi-Fi/Bluetooth proximity, or university SSO.
- Teaching assistants / co-lecturers on one course.
- AI prediction, automatic timetables.
- Public maps of student locations in the lecturer UI.

These may be considered later.

---

# 4. Target Users

## 4.1 Lecturer

- Registers with a **staff** email domain.
- Creates and manages their own courses.
- Starts / extends / ends attendance sessions.
- Displays the QR on a projector.
- Monitors check-ins on their own device (names, not a map).
- Adds a capped number of manual presents for dead phones.
- Archives or deletes courses.
- Exports CSV and reviews history.

## 4.2 Student

- Registers with a **student** email domain, student ID, name, and password.
- Scans attendance QR codes.
- Grants location permission.
- Views their own presence history.

A user has exactly one role in MVP: `LECTURER` or `STUDENT`.

---

# 5. Core User Journeys

## Lecturer — first-time setup

```text
Register with staff email
        ↓
Verify email / log in
        ↓
Create course (code, name, academic period)
        ↓
Course is empty — no roster
```

## Student — first-time (often at first scan)

```text
Scan QR (iOS Camera / Android Camera opens the browser)
        ↓
Land on /attendance/<token>/
        ↓
If not logged in: Login | Create account on that same page
        ↓
Account created (university email, student ID, name, password)
        ↓
Resume check-in (location → present)
```

Students may also register from `/register/` before class. The scan path must not dump them on a generic dashboard and lose the session URL.

## Normal attendance

```text
Lecturer (phone): open course → Start Attendance
        ↓
Phone requests location → pin frozen on the session
        ↓
Lecturer picks duration (default 15 min) and radius (default 150 m)
        ↓
Session ACTIVE, QR generated
        ↓
Lecturer logs into podium PC → Open display (fullscreen QR, countdown, headcount)
        ↓
Students scan with phone cameras
        ↓
Server: auth, session active, uniqueness, device, GPS vs pin
        ↓
Lecturer phone live list updates (name, student ID, email, time)
        ↓
Optional: lecturer adds up to 3 manual presents
        ↓
End session (or expiry after window + extends)
        ↓
Export CSV, reconcile with official class list
```

---

# 6. Authentication and identity

Use Django’s authentication system. Custom user model from day one. Passwords never stored in plaintext.

## 6.1 Lecturer

- Register, log in, log out, reset password, view/update profile.
- Email must match `LECTURER_EMAIL_DOMAINS` (env, e.g. `ug.edu.gh`).
- Open Gmail/Yahoo lecturer signup is not allowed.

## 6.2 Student

- Register, log in, log out, reset password, view/update profile.
- Email must match `STUDENT_EMAIL_DOMAINS` (env, e.g. `st.ug.edu.gh`).
- Student ID is unique and **immutable after registration**.
- Name may be edited.
- Email may be changed only to another address on an allowed student domain, and must remain unique.
- Password change and reset are allowed. Outbound email is **MVP**, not future work.

## 6.3 Scan-time auth

`/attendance/<token>/` must support:

- Logged-in student → continue to location / check-in.
- Anonymous → compact Login | Create account **on that page** (or with `next=` that returns to the same token URL).
- After success, do not require the student to find the course manually.

iOS Camera opens Safari. The student must be able to complete registration and check-in in that browser session. Do not assume they previously logged in on Chrome.

## 6.4 Identity honesty

First claimant of a student ID wins for registered accounts. The live list and CSV always show **student ID + name + email** so the lecturer can spot mismatches when reconciling. MVP does not require email local-part to equal student ID.

---

# 7. Roles and permissions

Enforced on the server.

## Lecturer may

- Create, edit, archive, and (with confirmation) delete their own courses.
- Start, extend, end, and update-location on their sessions.
- Open the projector display for their sessions.
- View live and historical check-ins for their courses.
- Create capped manual presents on an ACTIVE session they own.
- Export CSV for their courses/sessions.

A lecturer must not modify another lecturer’s courses.

## Student may

- View their own profile and presence history.
- Check in to an ACTIVE session via its token URL.
- View courses they have appeared in (`CourseParticipant`).

## Student must not

- Start or end sessions.
- See another student’s history.
- See raw GPS of anyone.
- Open lecturer display/live-list endpoints.
- Modify attendance records.

---

# 8. Course management

A lecturer creates a course. No students are attached up front.

Required fields:

- Course code (e.g. `BIOC 301`)
- Course name
- Academic period (e.g. `2026/2027 First Semester`)
- Optional description

Each course belongs to exactly one lecturer in MVP.

Constraint: do not accidentally duplicate `(lecturer, code, academic_period)`.

## 8.1 Dashboard filter

The lecturer dashboard **filters by academic period** (current period default).

## 8.2 Archive

Archive hides the course from the default dashboard and start-attendance list. History is kept. Unarchive is allowed.

## 8.3 Delete

Lecturer may delete a course with **typed confirmation** (e.g. type the course code). Delete **cascades**: sessions, attendance records, and participants for that course are removed.

Use delete for mistakes. Use archive at end of semester.

---

# 9. Course participation (not a roster)

There is no lecturer-managed enrolment.

`CourseParticipant` is created when:

- A registered student successfully checks in to a session of that course, or
- A manual stub row is later **merged** onto a newly registered account that matches `student_id`.

It exists so “My Courses” and “18 of 20 sessions” are cheap queries. It is not an official class list. Anyone with a valid student account who is near the pin can appear.

An inactive participant flag is not required for MVP.

---

# 10. Attendance session

Created when the lecturer starts attendance.

Must contain:

- Course
- Started at, expires at, ended at (nullable)
- Status
- Lecturer latitude, longitude, accuracy
- Allowed radius (metres)
- Unique session token (cryptographically unpredictable)
- Extend count
- Creation timestamp

## 10.1 Status

Stored statuses:

```text
ACTIVE
ENDED
EXPIRED
```

MVP creates sessions as `ACTIVE`. No scheduled/created state.

- Lecturer **End** → `ENDED`, `ended_at` = server now. No new check-ins (scan or manual).
- Server time ≥ `expires_at` and not already `ENDED` → treat as `EXPIRED` (store or derive consistently; either is fine if check-in always uses server time vs `expires_at` / `ended_at`).
- Historical sessions remain visible.

Once ended or expired, existing records are not changed by new check-ins.

## 10.2 One active session

At most **one ACTIVE session per course**. Starting another is rejected until the current one is ended or expired. Sequential sessions the same day (lecture then lab) are allowed.

## 10.3 Duration and extend

- Lecturer picks duration at start: **5 / 10 / 15 / 20 / 30 minutes**.
- **Default: 15 minutes.**
- While ACTIVE, **+5 minutes**, maximum **3 extends**.
- End always wins immediately.

## 10.4 Radius

Belongs to the session so history keeps the rule that applied.

- Options: **50 / 100 / 150 / 200 / 300 metres**.
- **Default: 150 metres.**

## 10.5 Lecturer pin

The pin is why a friend at home should fail: check-in compares **student GPS to this pin**, not to a campus centroid.

- Frozen when the session starts. Lecturer cannot start without a location (retry UI).
- **Update location** on the lecturer phone replaces the pin. **New** check-ins use the new pin. Already-present rows stay as recorded (original distance kept).

Do not continuously stream lecturer GPS. Do not require GPS from the projector PC.

---

# 11. QR code and projector display

QR encodes a session-specific URL:

```text
https://present.example.com/attendance/<secure-session-token>/
```

Token: unique, unguessable, invalid after end/expiry. Do not use sequential `/session/123` as the only secret.

MVP: QR is **static** for the session. Rotating QR is future.

## 11.1 Two-device classroom

Typical hall: GPS-capable phone vs podium PC on HDMI.

1. Lecturer starts the session **on the phone** (location + live name list).
2. Lecturer **logs into Present on the podium PC** and opens **Open display** for this session.
3. Display is **fullscreen**: large QR, countdown, **headcount only**.
4. **No names, student IDs, or emails on the projector.**

The live name list stays on the phone.

If they leave the podium PC logged in, the projector still must not have shown the class list. Prefer a dedicated display URL that cannot render names even for a logged-in lecturer.

Students use the **phone’s native camera**. No in-app scanner in MVP.

---

# 12. Student check-in

```text
QR → attendance page → authenticated student
  → session exists, ACTIVE, not expired
  → not already present (as this user)
  → device_id not already used this session
  → fresh browser geolocation
  → POST coordinates
  → server Haversine vs lecturer pin
  → within radius → AttendanceRecord (scan)
  → CourseParticipant if needed
```

Student UI: course name, their name, location prompt, success or a clear retry. No course search. No typing a code.

### Success

```text
You're Present
BIOC 301
Attendance recorded at 10:04 AM
```

### Outside radius

```text
Attendance not recorded
You appear to be outside the attendance area.
Please move closer to the class and try again.
```

Do not explain Haversine, pin coordinates, or other internals.

### Location denied / unavailable

Do not mark present. Ask them to enable location and retry.

---

# 13. Geolocation (anti remote-scan)

**Purpose:** make “send a photo of the QR to a friend at home” fail for ordinary students.

**Mechanism:** at check-in, the **server** computes distance between lecturer pin and student-supplied coordinates. If distance > session radius, reject.

**Honesty:** the client chooses the numbers. Mock location, DevTools, and shared logins still work. Present records **presence with friction**, not cryptographic proof someone stood in the room.

## 13.1 What is stored vs what is shown

Store on the scan record:

- Student latitude, longitude, accuracy
- Distance from lecturer pin (server-calculated)
- Lecturer pin is already on the session

Lecturer UI and CSV for lecturers: **name, student ID, email, time, source (scan/manual)**. Not coordinates, not a map, not accuracy.

Admin (Django admin) may see coordinates for audit.

## 13.2 Rules

Reject check-in when:

- Location permission denied / coordinates missing / invalid
- Session ended or expired
- Distance > allowed radius

Store accuracy; **do not** add accuracy into the pass/fail formula in MVP (no `distance <= radius + accuracy` buffer, no reject-on-poor-accuracy). Gate is Haversine vs radius.

## 13.3 Timestamps

Request a fresh position on the client. **Server time** is authoritative for `recorded_at` and session expiry.

Do not trust client `location_timestamp` as a security control. If sent, it may be stored for debugging; it must not be what makes a location “fresh.”

---

# 14. Uniqueness and devices

## 14.1 One student, one session

For a linked user:

```text
UNIQUE(session_id, student_id) WHERE student_id IS NOT NULL
```

Rescan → “Attendance already recorded.”

## 14.2 One device, one session (scan path)

Persistent random UUID in cookie/localStorage (`device.js`). Server stores it on scan records.

If this `device_id` already has a scan record for the session → reject. Clear, non-technical error.

This is a **deterrent**. Private browsing, cleared storage, and another browser bypass it.

`device_id` must be a non-empty UUID on scan submissions. Missing/empty must not collapse everyone into one key.

Manual presents have no device check.

Do not collect IMEI, MAC, SIM, or serial.

## 14.3 Race conditions

Two parallel submits: uniqueness constraints + transactions. One success, one duplicate error. Never two rows.

---

# 15. Manual present (dead phone)

Only the course owner, only while the session is **ACTIVE**.

- Lecturer types **student ID + full name**.
- Record is `source = manual`, **no student GPS**.
- **Cap: 3 per session.**
- CSV and UI mark them as manual.

### Matching

1. If a registered student already has this `student_id`:
   - If they already have a record this session → reject.
   - Else create a linked manual record (`student` FK set).
2. If nobody is registered with that ID:
   - Create a **stub row** on this session: `stub_student_id`, `stub_name`, `student` null.
   - Do **not** create a User. Do **not** reserve the ID globally.

Same ID may be stubbed in another course’s session.

### Merge

When a student **registers** with a `student_id` that matches existing stub rows, attach those rows (`student` FK) and create `CourseParticipant` as needed. Name on the stub is not a merge key.

Typos do not lock anyone out of Present. An impostor can still first-claim an ID at registration (same as any self-serve ID).

Lecturers cannot delete check-ins in MVP (no crasher-remove). Extra names stay; ignore them on the official list.

---

# 16. Server-side validation (scan)

Approximate order:

```text
1. Authenticated
2. Role is student
3. Session exists
4. Session ACTIVE and not past expires_at / ended_at
5. This user has not already attended
6. device_id valid and not already used this session
7. Coordinates present and valid
8. Haversine vs current lecturer pin
9. Distance ≤ allowed_radius
10. Create record (transaction)
11. Ensure CourseParticipant
12. Return success
```

Never trust client `student_id`, distance, attendance status, or lecturer identity.

Manual path: lecturer auth, owns course, session ACTIVE, cap, ID/name validation, uniqueness, no GPS.

---

# 17. Attendance record

```text
id
session
student (nullable)
stub_student_id (nullable)
stub_name (nullable)
source          scan | manual
device_id       (scan; nullable for manual)
student_latitude / longitude / accuracy  (scan; null for manual)
distance_from_lecturer                   (scan; null for manual)
recorded_at
created_at
```

Constraints:

- Scan: `student` required, coords required, `source=scan`.
- Manual linked: `student` set, coords null, `source=manual`.
- Manual stub: `student` null, stub fields set, `source=manual`.
- At most one linked record per `(session, student)`.
- At most one stub per `(session, stub_student_id)`.

Failed scan attempts are **not** stored as records. Log them server-side. Lecturer does not see a reject list.

Status on the record is unnecessary in MVP: existence means present.

---

# 18. Lecturer live session (phone)

```text
BIOC 301
Session active
08:42 remaining   [ +5 min ]  (if extends remain)
[ Update location ]

47 present

[ Open display instructions / link ]

Students (newest first)
✓ John Mensah    10982345    john@st.ug.edu.gh    10:04
✓ Ama Boateng    10982346    ama@st.ug.edu.gh     10:04   Manual

[ Add manual present ]   (if under cap)
[ End session ]
```

Polling every **3–5 seconds** (`GET` session status, **lecturer-auth only**). No WebSockets in MVP.

The QR **token must not** authorize this name list. Projector display endpoint returns QR payload + count + remaining time only.

---

# 19. Statistics

There is no enrolled denominator. Do not show `49/57` or class `%` against a roster.

**Session:** headcount of present rows (scan + manual).

**Student who has appeared on this course** (via `CourseParticipant` or records):

```text
attendance_rate = sessions_attended / sessions_held × 100
```

`sessions_held` = **all completed** (`ENDED` or `EXPIRED`) sessions for that **course**, including those before the student first appeared. A week-6 first appearance shows `1/6`.

`sessions_attended` = distinct sessions with a record linked to that student (after merge, stubs count).

**Course history table:** date, headcount (not rate-vs-enrolment).

---

# 20. CSV export (MVP)

Required. Without export, “reconcile with the class list” is not a product.

**One session**

```text
student_id, full_name, email, recorded_at, source
```

`email` empty for unmerged stubs. `source` is `scan` or `manual`.

**Course rollup**

```text
student_id, full_name, email, sessions_attended, sessions_held, rate
```

Unmerged stubs appear on session CSV; they appear on rollup only after merge (or as stub ID/name with attended count of stubbed sessions — implement session CSV first; rollup of unmerged stubs: include them as ID/name, email blank, attended = sessions they were stubbed in).

No PDF/Excel required.

---

# 21. Student dashboard

```text
My Courses   (CourseParticipant only)

BIOC 301
18 / 20 sessions
```

Course detail: their check-ins (dates, scan vs manual). No other students. No GPS.

Empty state if they have never appeared in a course.

---

# 22. Navigation and UI

## Lecturer

```text
Dashboard | Courses | Attendance | Profile
```

Dashboard: greeting, period filter, courses with **Start Attendance** (disabled if an ACTIVE session already exists — show **Open session** instead).

## Student

```text
Dashboard | My Courses | Profile
```

No lecturer controls.

Principles: clean, fast, academic, obvious primary action. Minimal animation and colour. Empty states with a next action. Errors in plain language (never raw `IntegrityError` / CSRF dumps). Do not rely on colour alone for status (text + hierarchy). Basic a11y: semantic HTML, labels, focus, contrast, keyboard.

Visual language: Present, academic, reliable, fast. Strong type, cards, spacing, high contrast, mobile-first student flows, projector-optimized QR.

Reusable template pieces: navbar, cards, buttons, badges, modal, alert, table, empty/loading, QR display, status.

---

# 23. Technology

**Backend:** Django (auth, ORM, templates, admin, validation).  
**Database:** PostgreSQL (dev and production).  
**Frontend:** Django Templates + vanilla JS. No React in MVP.  
**CSS:** Tailwind CSS.

JS modules (do not one-file):

```text
static/js/
  location.js     geolocation, permission failures
  attendance.js   check-in POST, messages
  session.js      countdown, poll, extend/end UI hooks
  device.js       UUID get-or-create
  display.js      projector QR page
```

Business logic in `attendance/services.py`, not fat views. Distance helper thoroughly unit-tested.

---

# 24. Project structure

```text
present/
├── manage.py
├── config/                 settings, urls, asgi, wsgi
├── accounts/               custom user, profiles, domain-gated auth
├── courses/                Course, CourseParticipant
├── attendance/             sessions, records, services, validators
├── templates/
├── static/
├── requirements/           base, development, production
└── .env                    not committed
```

---

# 25. Data models

## User (custom)

```text
id, email (unique), password, first_name, last_name
role                  LECTURER | STUDENT
is_active, is_staff, is_superuser, date_joined
```

Email is the username.

## StudentProfile

```text
id, user (OneToOne), student_id (unique, immutable in app logic)
programme, level, department   optional
created_at, updated_at
```

## LecturerProfile

```text
id, user (OneToOne)
staff_id               optional
department             optional
created_at, updated_at
```

## Course

```text
id, lecturer, code, name, description
academic_period
is_archived
is_active
created_at, updated_at
```

Unique together: `(lecturer, code, academic_period)`.

## CourseParticipant

```text
id, student, course, first_seen_at
UNIQUE(student, course)
```

## AttendanceSession

```text
id, course, token (unique)
started_at, expires_at, ended_at
status
lecturer_latitude, lecturer_longitude, lecturer_accuracy
allowed_radius
extend_count
created_at
```

## AttendanceRecord

As section 17.

---

# 26. URL design

## Auth

```text
/login/
/logout/
/register/                  role-specific; enforce domain by chosen role
/password-reset/
```

## Courses (lecturer)

```text
/courses/
/courses/create/
/courses/<id>/
/courses/<id>/edit/
/courses/<id>/archive/
/courses/<id>/delete/
/courses/<id>/export/
```

## Attendance

```text
POST /courses/<id>/attendance/start/
GET  /attendance/<token>/                      student check-in page (scan-time auth)
POST /attendance/<token>/check-in/
GET  /attendance/sessions/<id>/live/           lecturer names + count (lecturer auth)
POST /attendance/sessions/<id>/end/
POST /attendance/sessions/<id>/extend/
POST /attendance/sessions/<id>/location/
POST /attendance/sessions/<id>/manual/
GET  /attendance/sessions/<id>/display/        QR + count + timer only (lecturer auth)
GET  /attendance/sessions/<id>/export/
```

Do not put the name list on a URL that is guessable from the QR token alone.

## Student

```text
/student/courses/
/student/courses/<id>/
```

---

# 27. Endpoint notes

## Start

Lecturer owns course, course not archived, no other ACTIVE session, valid location, generate token, set `expires_at`, return token, `expires_at`, radius, display URL.

## Check-in

Body:

```json
{
  "latitude": 5.6509,
  "longitude": -0.1870,
  "accuracy": 18,
  "device_id": "<uuid>"
}
```

Student from the auth session only.

## Errors (stable codes)

```text
session_not_found
session_expired
session_ended
already_attended
device_already_used
location_unavailable
outside_attendance_radius
invalid_coordinates
permission_denied
not_authenticated
not_student
domain_not_allowed
student_id_taken
manual_cap_reached
manual_duplicate
active_session_exists
extend_cap_reached
```

User `message` is friendly. `error` is for the frontend.

---

# 28. Security

The frontend is never trusted. Server decides identity, session validity, distance, and whether to write a row. Database enforces uniqueness.

- CSRF stays enabled.
- Django password hashing, secure/HttpOnly/SameSite cookies, HTTPS in production.
- Geolocation requires a secure context; production is HTTPS from first deploy plan.
- Rate-limit login and check-in reasonably (implementation detail; do not leave unlimited brute force).
- Do not log passwords or secrets. Do log auth failures, session start/end, and validation failures.

**Environment (not in git):**

```text
SECRET_KEY
DEBUG
DATABASE_URL
ALLOWED_HOSTS
CSRF_TRUSTED_ORIGINS
STUDENT_EMAIL_DOMAINS
LECTURER_EMAIL_DOMAINS
EMAIL_HOST
EMAIL_USER
EMAIL_PASSWORD
```

`DEBUG=True` is forbidden in production.

---

# 29. Time

Store timestamps in UTC. `USE_TZ = True`. Render in local timezone for humans. Server is authority for start, expiry, extend, and `recorded_at`.

---

# 30. Admin

Django admin: users, profiles, courses, participants, sessions, records. Filters: course, lecturer, student, status, date. Search: student ID, email, course code/name.

Attendance should not be casually edited. MVP has no full audit log; do not make records impossible to audit later (keep coords on scan rows).

---

# 31. Indexing (do not index everything)

```text
User.email
StudentProfile.student_id
Course (lecturer, academic_period)
CourseParticipant (course, student)
AttendanceSession.token
AttendanceSession (course, status)
AttendanceRecord (session, student)
AttendanceRecord (session, stub_student_id)
AttendanceRecord.device_id
AttendanceRecord.recorded_at
```

---

# 32. Testing (mandatory with check-in, not only at deploy)

**Unit:** Haversine, expiry/extend math, attendance rate (`attended / course sessions held`), token uniqueness/entropy smoke, email domain allowlist.

**Model:** uniqueness (student/session, stub/session, device/session), course ownership, one ACTIVE session.

**Service:**

```text
Valid scan in radius → success
Outside radius → reject, no row
Expired / ended → reject
Duplicate student → reject
Duplicate device → reject
Invalid/missing location → reject
Manual under cap → success
Manual over cap → reject
Stub merge on register → FK attached
Second ACTIVE session on same course → reject
```

**Integration:** lecturer start → display → student scan-time register → check-in → live count; student cannot read another student’s pages (403/404).

**Concurrency:** two parallel check-ins from same student → one row.

**Security:** CSRF, authz, token guessing, student_id in body ignored, location spoof still “accepted if coords inside radius” is expected (document as deterrent), ended QR fails.

---

# 33. Deployment

```text
Internet → Nginx → Gunicorn → Django → PostgreSQL
```

Nginx serves static files. Ubuntu VPS, non-root service user, HTTPS. Separate development and production settings. Backups of PostgreSQL in the hardening phase.

Git: `main`, `develop`, `feature/*`, `fix/*`. Conventional commits (`feat:`, `fix:`, `test:`). PRs for significant features.

---

# 34. Implementation phases

## Phase 1 — Foundation

Django, PostgreSQL, env, custom user, Tailwind, base templates, domain-gated register/login, password reset email, admin.

Deliverable: staff/student can register only with allowed domains and log in.

## Phase 2 — Courses

CRUD, period filter, archive, typed cascade delete, ownership.

Deliverable: lecturer manages courses with no roster.

## Phase 3 — Sessions and display

Session model, token, start (GPS + radius + duration), one ACTIVE, QR, podium **display page** (QR/count/timer), end, extend (+5 × 3), update location.

Deliverable: lecturer starts on phone and projects QR without names.

## Phase 4 — Check-in

Scan URL, scan-time auth resume, record, uniqueness, device UUID, live poll on lecturer phone. **No GPS gate yet** optional internally only if needed to test the transaction; do not ship without Phase 5.

Deliverable: logged-in student can scan and appear on the list.

## Phase 5 — Geolocation

Lecturer pin, student GPS, Haversine, radius, store coords, hide coords from lecturer UI, failure messages.

Deliverable: home coordinates fail; nearby succeed (ordinary devices).

## Phase 6 — Manual presents and merge

Capped manual, stubs, merge on register, CSV (session + rollup).

Deliverable: dead-phone path and export for reconciliation.

## Phase 7 — History

Course session list, per-student `attended / held`, student dashboard.

Deliverable: semester-long presence log.

## Phase 8 — Hardening

Tests from phases 3–6 already written; security pass; logging; HTTPS; production config; backups.

Deliverable: production-ready MVP.

---

# 35. MVP definition of done

## Lecturer

1. Registers with staff email and logs in.
2. Creates BIOC 301 for the current academic period.
3. On phone: Start Attendance, grants location, default 15 min / 150 m.
4. On podium PC: logs in, opens display — large QR, countdown, headcount, **no names**.
5. Phone shows names as students scan (ID, name, email, time).
6. Can +5 min up to three times, update location, add up to 3 manuals, End.
7. Exports CSV and ticks against their official class list.
8. Sees headcount, not `49/57`.

## Student

1. Scans QR (including first-time in Safari from Camera).
2. Registers with student email + student ID on that page if needed.
3. Grants location; inside radius → You’re Present.
4. Friend at home with the same QR and real GPS → outside radius (unless they spoof coords).
5. Can see `18 / 20` style history for courses they have appeared in.

The session is immutable from the lecturer UI except: extend and update-location while ACTIVE, and manuals while ACTIVE. No row deletes.

---

# 36. Product decisions (fixed unless there is a strong reason)

**Django** — auth, admin, ORM, forms, structure.  
**PostgreSQL** — concurrent check-ins and constraints.  
**Templates + vanilla JS** — no separate SPA for MVP.  
**QR + GPS as deterrent** — QR selects the session; GPS (server Haversine vs pin) raises the cost of checking in from elsewhere; auth selects the person; device UUID raises the cost of pass-the-phone. Together they produce a **presence record with friction**, not a verified-attendance certificate.  
**Presence log, not register** — lecturers already have a class list; Present does not duplicate it.

---

# 37. Future (must not block MVP)

- Rotating QR
- Wi-Fi / Bluetooth proximity
- University SSO
- Email local-part == student ID (if campus mail actually works that way)
- Co-lecturers / TAs
- Remove/correct a check-in with audit
- Lecturer map of check-ins
- Excel/PDF reports, at-risk thresholds
- PWA
- Roster import / SIS sync if a department later wants Present to *be* the register

---

# 38. UX principle

> **Attendance should take seconds, not minutes.**

Ideal repeat student: Scan → location → You’re Present.

Ideal lecturer: Start → project QR → watch the phone → End → export.

Complexity stays behind the server.
