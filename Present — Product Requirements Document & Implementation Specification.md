# Present
## Product Requirements Document & Implementation Specification

**Product:** Present  
**Product type:** Web-based academic attendance management system  
**Primary users:** Lecturers and students  
**Primary technology:** Django + PostgreSQL + Django Templates + Tailwind CSS + Vanilla JavaScript  
**Document status:** MVP implementation specification  
**Version:** 1.0

---

# 1. Product Overview

## 1.1 Product concept

**Present** is a lightweight attendance management system designed for university and other educational settings.

The system allows a lecturer to:

1. Create or manage a class.
2. Add or import the students enrolled in that class.
3. Start an attendance session.
4. Have Present generate a temporary QR code.
5. Display that QR code to students.
6. Allow students to scan the QR code using their phones.
7. Verify the student's identity.
8. Verify that the student's device is physically near the lecturer's device.
9. Record the student's attendance.
10. View attendance statistics and individual attendance history.

The core principle is:

> **Students should be able to mark attendance in seconds, while the system makes it difficult to mark attendance remotely or on behalf of another student.**

---

# 2. Product Goals

## 2.1 Primary goals

Present must:

- Make attendance extremely fast for students.
- Make starting an attendance session extremely simple for lecturers.
- Maintain a persistent student roster.
- Maintain historical attendance records.
- Verify student proximity to the lecturer.
- Prevent duplicate attendance submissions.
- Discourage attendance on behalf of absent students.
- Provide lecturers with useful attendance statistics.
- Work primarily through a web browser.
- Require no native mobile application for the MVP.
- Be usable on ordinary smartphones and laptops.
- Remain simple enough to deploy and maintain by a small development team.

---

# 3. Non-Goals for MVP

The first version should NOT attempt to become a complete university management system.

The MVP should not include:

- Tuition/payment management.
- Examination management.
- Grade management.
- Course registration across an entire university.
- Learning management functionality.
- Assignment submission.
- Chat/messaging.
- Facial recognition.
- Fingerprint authentication.
- Native iOS application.
- Native Android application.
- Complex biometric verification.
- Artificial intelligence attendance prediction.
- Automatic timetable generation.
- University-wide student information system integration.

These may be considered later.

---

# 4. Target Users

Present has two primary user roles.

## 4.1 Lecturer

The lecturer is responsible for:

- Creating/managing courses.
- Managing the student roster.
- Starting attendance sessions.
- Monitoring attendance in real time.
- Ending attendance sessions.
- Reviewing attendance history.
- Viewing attendance statistics.

## 4.2 Student

The student is responsible for:

- Creating/accessing their account.
- Joining or being enrolled in courses.
- Scanning attendance QR codes.
- Granting location permission.
- Confirming attendance.
- Viewing their own attendance history.

---

# 5. Core User Journey

The intended experience should be extremely simple.

## First-time setup

```text
Lecturer creates account
        ↓
Creates course
        ↓
Imports/adds students
        ↓
Course roster is established
```

Student:

```text
Student creates account
        ↓
Student is associated with course
        ↓
Student can attend future sessions
```

## Normal attendance

```text
Lecturer opens course
        ↓
Start Attendance
        ↓
Browser requests lecturer location
        ↓
Session created
        ↓
QR code generated
        ↓
Lecturer displays QR
        ↓
Students scan
        ↓
Student identity verified
        ↓
Student location obtained
        ↓
Distance calculated
        ↓
Validation performed
        ↓
Attendance recorded
        ↓
Lecturer dashboard updates
```

---

# 6. Functional Requirements

## 6.1 Authentication

The application must support authentication.

### Lecturer authentication

A lecturer should be able to:

- Register.
- Log in.
- Log out.
- Reset password.
- View profile.
- Update profile.

### Student authentication

A student should be able to:

- Register.
- Log in.
- Log out.
- Reset password.
- View profile.
- Update profile.

The MVP should use Django's authentication system rather than implementing password authentication from scratch.

Passwords must never be stored in plaintext.

---

# 7. User Roles and Permissions

Role-based authorization must be enforced on the server.

## Lecturer permissions

A lecturer can:

- Create courses.
- Edit their courses.
- Delete/archive their courses.
- Add students.
- Import students.
- Remove students from a course.
- View their course roster.
- Start attendance sessions.
- End attendance sessions.
- View attendance records.
- View attendance statistics.

A lecturer must NOT be able to modify courses belonging to another lecturer.

## Student permissions

A student can:

- View their own profile.
- View courses they belong to.
- Scan active attendance sessions.
- View their own attendance history.

A student must NOT be able to:

- Start attendance.
- End attendance.
- Modify attendance records.
- View another student's attendance history.
- Modify course rosters.

---

# 8. Course Management

A lecturer must be able to create a course.

Required fields:

- Course code
- Course name
- Semester/academic period
- Optional description

Example:

```text
Course Code: BIOC 301
Course Name: Clinical Biochemistry
Semester: 2026/2027 First Semester
```

Each course belongs to exactly one lecturer in the MVP.

A lecturer can have multiple courses.

---

# 9. Student Roster Management

A course must have a persistent roster.

A lecturer should be able to:

### Add individual student

Fields:

- Student ID
- Full name
- Email

Optional:

- Programme
- Level
- Department

### Import students

The preferred bulk onboarding method is CSV.

Example:

```csv
student_id,full_name,email,programme,level
10982345,John Mensah,john@example.com,Biochemistry,300
10982346,Ama Boateng,ama@example.com,Biochemistry,300
10982347,Kwame Asare,kwame@example.com,Biochemistry,300
```

The import system should:

1. Validate the file.
2. Validate required columns.
3. Detect duplicate student IDs.
4. Detect malformed email addresses.
5. Display an import preview.
6. Report errors before committing valid records.
7. Allow the lecturer to confirm the import.
8. Create or associate student accounts as appropriate.
9. Create course enrollments.

The import process must not silently create corrupted records.

---

# 10. Student Identity Model

Students should have a persistent identity across courses.

The student should NOT be recreated as a completely new person every time they join a course.

For example:

```text
Student
John Mensah
Student ID: 10982345
```

may be enrolled in:

```text
BIOC 301
BIOC 401
CELL 302
```

Attendance remains attached to the student and the specific course/session.

---

# 11. Enrollment

A many-to-many relationship should exist conceptually between students and courses.

```text
Student
   │
   ├── Enrollment → BIOC 301
   ├── Enrollment → BIOC 401
   └── Enrollment → CELL 302
```

The enrollment record should contain:

- Student
- Course
- Enrollment date
- Active/inactive status

An inactive student should not be able to mark attendance for that course.

---

# 12. Attendance Session

Every attendance event is represented by an attendance session.

Example:

```text
BIOC 301
August 27, 2026
10:00 AM
```

The lecturer clicks:

**Start Attendance**

The backend creates an attendance session.

The session must contain:

- Course
- Lecturer
- Start time
- Expiration time
- Status
- Lecturer latitude
- Lecturer longitude
- Lecturer location accuracy
- Allowed radius
- Unique session token
- Creation timestamp

---

# 13. Session Lifecycle

An attendance session has three possible states:

```text
SCHEDULED / CREATED
        ↓
ACTIVE
        ↓
ENDED
```

For MVP, sessions can simply be created directly as ACTIVE.

A session automatically becomes invalid when its expiration time is reached.

The lecturer can manually end a session.

Once ended:

- New attendance submissions must be rejected.
- Existing attendance records must remain unchanged.
- The QR code must no longer produce a valid attendance transaction.

---

# 14. Session Expiration

Attendance sessions should have a short configurable duration.

Default:

```text
10 minutes
```

Possible options:

```text
5 minutes
10 minutes
15 minutes
20 minutes
30 minutes
```

The default should be 10 minutes.

The QR code must not remain valid indefinitely.

---

# 15. QR Code

When a lecturer starts a session, Present generates a unique QR code.

The QR code must contain a session-specific URL/token.

Example concept:

```text
https://present.example.com/attendance/scan/<secure-session-token>
```

The token must be:

- Cryptographically unpredictable.
- Unique.
- Associated with exactly one session.
- Invalid after session expiration.
- Invalid after the session is ended.

Do not use predictable sequential IDs as the sole QR authentication mechanism.

Bad:

```text
/session/123
/session/124
/session/125
```

Prefer a random secure token.

---

# 16. QR Code Rotation

For the MVP, the QR code may remain constant for the duration of the session.

However, the architecture should allow future implementation of rotating QR codes.

Future enhancement:

```text
QR token changes every 20–30 seconds
```

This makes screenshots and photographs of the QR code less useful.

The MVP does not require rotation.

---

# 17. Student Attendance Flow

When a student scans the QR code:

```text
QR
 ↓
Attendance page
 ↓
Determine logged-in student
 ↓
Validate session
 ↓
Validate course enrollment
 ↓
Request location
 ↓
Collect device information
 ↓
Submit attendance
 ↓
Server validates
 ↓
Attendance recorded
```

The student should see a very clear interface.

Example:

```text
BIOC 301

Attendance Session

John Mensah

We need your location to verify
that you are in the classroom.

[ Allow Location & Mark Present ]
```

---

# 18. Geolocation

Geolocation is a core feature.

The lecturer's device establishes the reference location.

When starting a session, the lecturer's browser should request location permission.

The browser Geolocation API should be used.

The lecturer location must contain:

```text
latitude
longitude
accuracy
timestamp
```

The student's device must similarly provide:

```text
latitude
longitude
accuracy
timestamp
```

---

# 19. Location Verification

The server must calculate the distance between:

```text
Lecturer location
        ↓
Student location
```

The calculation should use a geographic distance algorithm such as the Haversine formula.

Conceptually:

```text
distance = haversine(
    lecturer_latitude,
    lecturer_longitude,
    student_latitude,
    student_longitude
)
```

The result should be measured in metres.

Example:

```text
Lecturer:
5.6508, -0.1869

Student:
5.6511, -0.1872

Distance:
approximately 45 metres
```

---

# 20. Attendance Radius

The system should have a default attendance radius.

Recommended default:

```text
100 metres
```

This should be configurable.

Potential options:

```text
50 m
100 m
150 m
200 m
```

The MVP should default to 100 m.

The radius belongs to the attendance session so that historical attendance records retain the conditions under which they were recorded.

---

# 21. GPS Accuracy

GPS is not perfectly precise, especially indoors.

Therefore the system must store location accuracy.

Example:

```text
student_latitude: 5.6509
student_longitude: -0.1870
student_accuracy: 18m
distance: 42m
```

The system should not blindly treat GPS coordinates as exact.

For MVP, use the calculated distance against the configured radius while storing accuracy for auditing.

A future version can implement more sophisticated confidence rules.

---

# 22. Location Validation Rules

Attendance should be rejected when:

- Location permission is denied.
- Coordinates cannot be obtained.
- Coordinates are invalid.
- The location is clearly stale.
- The session has expired.
- The student is outside the permitted radius.

Example:

```text
Distance: 37m
Radius: 100m

→ ACCEPT
```

```text
Distance: 417m
Radius: 100m

→ REJECT
```

The UI should explain the rejection clearly without exposing unnecessary internal security information.

Example:

> You appear to be outside the attendance area. Please make sure you are in the classroom and try again.

---

# 23. Location Timestamp

The student location should be recent.

Do not accept a location reading that is hours old.

The frontend should request a fresh position when the student checks in.

The backend should validate the supplied timestamp against the current server time.

Server time must be authoritative.

Do not trust the student's device clock.

---

# 24. One Student — One Attendance

A student may only be marked present once per session.

Database-level uniqueness should enforce:

```text
UNIQUE(session_id, student_id)
```

If the student attempts to scan again:

```text
Attendance already recorded.
```

The system must not create a second record.

---

# 25. One Device — One Attendance

The MVP should also attempt to prevent multiple students from using the same device during one attendance session.

A browser-generated device identifier should be used.

The application can generate a persistent random identifier and store it in a browser cookie/local storage mechanism.

Conceptually:

```text
device_id = random UUID
```

Example:

```text
8f3a0e4d-...
```

The server records the device identifier with attendance.

A session should reject a second attendance attempt from the same device where the policy is configured as one-device-per-session.

Important:

> Browser-based device identification is not a perfect hardware identity.

Users can clear storage, switch browsers, use private browsing, or manipulate the client.

Therefore this mechanism should be considered a **deterrent**, not an absolute security guarantee.

---

# 26. Device Validation

The backend should check:

```text
Does this device already have an attendance record
for this session?
```

If yes:

```text
Reject.
```

This check must happen server-side.

Do not rely solely on JavaScript.

---

# 27. Attendance Transaction

The attendance submission should conceptually contain:

```json
{
    "session_token": "...",
    "latitude": 5.6509,
    "longitude": -0.1870,
    "accuracy": 18,
    "location_timestamp": "...",
    "device_id": "..."
}
```

The server determines the authenticated student from the authenticated session/token.

Do not trust a client-provided `student_id`.

A malicious client should not be able to submit:

```json
{
    "student_id": "someone_else"
}
```

and mark another student present.

---

# 28. Server-Side Validation Sequence

The attendance endpoint should validate in this approximate order:

```text
1. Is the user authenticated?
        ↓
2. Is the user a student?
        ↓
3. Does the session exist?
        ↓
4. Is the session active?
        ↓
5. Has the session expired?
        ↓
6. Is the student enrolled in the course?
        ↓
7. Has this student already attended?
        ↓
8. Has this device already been used?
        ↓
9. Is the location valid?
        ↓
10. Is the location timestamp acceptable?
        ↓
11. Calculate distance
        ↓
12. Is distance within allowed radius?
        ↓
13. Create attendance record
        ↓
14. Return success
```

All critical validation must happen on the server.

---

# 29. Race Conditions

The system must account for two simultaneous requests.

For example, a student could rapidly submit the attendance request twice.

The application should use:

- Database uniqueness constraints.
- Transactions where appropriate.
- Proper error handling.

The database must ultimately guarantee that:

```text
one student + one session = max one attendance record
```

---

# 30. Attendance Record

An attendance record should store sufficient information for auditing.

Recommended fields:

```text
id
session_id
student_id
timestamp
latitude
longitude
location_accuracy
distance_from_lecturer
device_id
status
created_at
```

Potential statuses:

```text
present
```

The MVP does not need complicated statuses unless required later.

---

# 31. Attendance Dashboard

The lecturer should see live attendance information.

Example:

```text
BIOC 301
Attendance Session

┌───────────────────────────────┐
│ Present                       │
│ 42 / 57                       │
└───────────────────────────────┘

Session expires in
07:32

[ QR CODE ]

Students

✓ John Mensah
✓ Ama Boateng
✓ Kwame Asare
✓ Sarah Owusu
...
```

The lecturer should not need to refresh the entire page manually.

---

# 32. Live Attendance Updates

For the MVP, use polling rather than WebSockets.

Example:

```text
Browser
   ↓
GET /attendance/sessions/<id>/status
   ↓
every 3–5 seconds
```

This is simpler and sufficient for a classroom-sized application.

Future versions may use:

- WebSockets.
- Django Channels.
- Server-Sent Events.

Do not introduce WebSockets in the MVP unless there is a demonstrated need.

---

# 33. Attendance Statistics

The course dashboard should display:

```text
Total students
Present
Absent
Attendance percentage
```

Example:

```text
Students: 57
Present: 49
Absent: 8
Attendance: 86%
```

---

# 34. Individual Student Attendance

Lecturers should be able to select a student and see their history.

Example:

```text
John Mensah

BIOC 301

Sessions: 20
Present: 18
Absent: 2
Attendance rate: 90%

Date          Status
--------------------------------
Aug 27        Present
Aug 24        Present
Aug 20        Absent
Aug 17        Present
Aug 13        Present
```

---

# 35. Course Attendance History

The lecturer should be able to view historical sessions.

Example:

```text
BIOC 301

Attendance Sessions

Date          Present    Total    Rate
----------------------------------------
Aug 27        49         57       86%
Aug 24        52         57       91%
Aug 20        48         57       84%
Aug 17        50         57       88%
```

Selecting a session should show its detailed attendance records.

---

# 36. Student Dashboard

The student dashboard should remain simple.

Example:

```text
Welcome, John

My Courses

BIOC 301
Attendance: 90%

BIOC 401
Attendance: 94%
```

Selecting a course:

```text
BIOC 301

Attendance
18 / 20

90%

Recent sessions:
✓ Aug 27
✓ Aug 24
✗ Aug 20
✓ Aug 17
```

---

# 37. User Interface Principles

Present should feel:

- Clean.
- Fast.
- Modern.
- Academic.
- Professional.
- Minimal.

Avoid:

- Excessive animations.
- Cluttered dashboards.
- Huge navigation systems.
- Unnecessary charts.
- Excessive color usage.
- Complicated forms.

The primary action should always be obvious.

---

# 38. Lecturer Navigation

Recommended navigation:

```text
Dashboard
Courses
Attendance
Students
Profile
```

Potentially:

```text
Settings
```

later.

---

# 39. Student Navigation

Recommended:

```text
Dashboard
My Courses
Attendance
Profile
```

The student should not see lecturer functionality.

---

# 40. Lecturer Dashboard

The dashboard should show:

```text
Good morning, Dr. Mensah

Your Courses

BIOC 301
Clinical Biochemistry
57 students

[ Start Attendance ]

BIOC 401
Advanced Biochemistry
42 students

[ Start Attendance ]
```

The lecturer's most common action should be immediately accessible.

---

# 41. Attendance Session Interface

When active:

```text
BIOC 301
Attendance

Session active
08:42 remaining

             ┌───────────┐
             │           │
             │ QR CODE   │
             │           │
             └───────────┘

47 / 57 Present

[ End Session ]

Recent check-ins

✓ John Mensah
✓ Ama Boateng
✓ Kwame Asare
```

---

# 42. Student Scan Interface

The student experience should be optimized for mobile.

Initial state:

```text
BIOC 301

Attendance

Checking your session...
```

Then:

```text
Location required

Present needs your location to
verify that you are attending
from the classroom.

[ Allow Location ]
```

Success:

```text
✓ You're Present

BIOC 301

Attendance recorded at 10:04 AM.
```

Failure:

```text
Attendance not recorded

You appear to be outside the
attendance area.

Please move closer to the class
and try again.
```

---

# 43. Responsive Design

The application must work well on:

- Desktop.
- Laptop.
- Tablet.
- Android phones.
- iPhones.

The QR display should be particularly optimized for:

- Laptop screen.
- Projector.
- Large classroom display.

The student scanning interface should be mobile-first.

---

# 44. Technology Stack

## Backend

**Django**

Use Django for:

- Application architecture.
- Authentication.
- Routing.
- ORM.
- Database integration.
- Server-side validation.
- Templates.
- Admin interface.

## Database

**PostgreSQL**

Use PostgreSQL for production and preferably development.

## Frontend

**Django Templates + Vanilla JavaScript**

Do not introduce React in the MVP.

## Styling

**Tailwind CSS**

Use Tailwind for the application UI.

## Client-side functionality

Vanilla JavaScript should handle:

- Geolocation.
- Attendance submission.
- QR scanning if needed.
- Countdown timers.
- Polling.
- Dynamic UI updates.
- Form interactions.

---

# 45. Recommended Django Application Structure

Use separate Django apps according to domain.

```text
present/
│
├── manage.py
│
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── accounts/
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   ├── forms.py
│   └── tests.py
│
├── courses/
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   ├── forms.py
│   └── tests.py
│
├── attendance/
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   ├── services.py
│   ├── validators.py
│   └── tests.py
│
├── templates/
│   ├── base.html
│   ├── registration/
│   ├── accounts/
│   ├── courses/
│   ├── lecturer/
│   ├── student/
│   └── attendance/
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── requirements/
│   ├── base.txt
│   ├── development.txt
│   └── production.txt
│
└── .env
```

---

# 46. Database Model

## User

Use Django's authentication system.

Recommended approach:

Use a custom user model from the beginning.

Fields:

```text
id
email
password
first_name
last_name
role
is_active
is_staff
is_superuser
date_joined
```

Role:

```text
LECTURER
STUDENT
```

Email should be unique.

---

# 47. Student Profile

Potential separate profile:

```text
StudentProfile

id
user
student_id
programme
level
department
created_at
updated_at
```

`student_id` should be unique.

---

# 48. Lecturer Profile

```text
LecturerProfile

id
user
staff_id
department
created_at
updated_at
```

Staff ID may be optional in the MVP.

---

# 49. Course Model

```text
Course

id
lecturer
code
name
description
academic_period
is_active
created_at
updated_at
```

Potential constraint:

```text
lecturer + code + academic_period
```

should not accidentally create duplicate courses.

---

# 50. Enrollment Model

```text
Enrollment

id
student
course
enrolled_at
is_active
created_at
updated_at
```

Database constraint:

```text
UNIQUE(student, course)
```

---

# 51. Attendance Session Model

```text
AttendanceSession

id
course
token
started_at
expires_at
ended_at
status
lecturer_latitude
lecturer_longitude
lecturer_accuracy
allowed_radius
created_at
```

Token must be unique.

Status:

```text
ACTIVE
ENDED
EXPIRED
```

---

# 52. Attendance Record Model

```text
AttendanceRecord

id
session
student
device_id
student_latitude
student_longitude
student_accuracy
distance_from_lecturer
recorded_at
status
created_at
```

Database constraints:

```text
UNIQUE(session, student)
```

A separate uniqueness strategy should be implemented for:

```text
session + device_id
```

if the one-device-per-session rule is enforced strictly.

---

# 53. Device Identifier

For MVP:

```text
device_id
```

should be a randomly generated UUID stored client-side.

Do not attempt to fingerprint hardware.

Do not collect:

- IMEI.
- MAC address.
- SIM number.
- Phone serial number.

The application should use the minimum device information necessary.

---

# 54. API / URL Design

Even though Django templates are being used, the application should have clean JSON endpoints for dynamic operations.

## Authentication

```text
/login/
 /logout/
/register/
/password-reset/
```

## Courses

```text
/courses/
/courses/<id>/
/courses/create/
/courses/<id>/edit/
```

## Roster

```text
/courses/<id>/students/
/courses/<id>/students/add/
/courses/<id>/students/import/
```

## Attendance

```text
/courses/<id>/attendance/start/
/attendance/<session_token>/
/attendance/<session_token>/check-in/
/attendance/<session_token>/status/
/attendance/<session_token>/end/
```

## Student history

```text
/student/courses/
/student/courses/<id>/attendance/
```

---

# 55. Start Session Endpoint

Conceptually:

```text
POST /courses/<course_id>/attendance/start/
```

Server:

1. Authenticate lecturer.
2. Confirm lecturer owns course.
3. Confirm course is active.
4. Validate lecturer location.
5. Generate secure session token.
6. Create attendance session.
7. Set expiration.
8. Return session information.

Example response:

```json
{
    "success": true,
    "session_token": "...",
    "expires_at": "...",
    "allowed_radius": 100
}
```

---

# 56. Check-In Endpoint

Conceptually:

```text
POST /attendance/<session_token>/check-in/
```

Request:

```json
{
    "latitude": 5.6509,
    "longitude": -0.1870,
    "accuracy": 18,
    "location_timestamp": "2026-08-27T10:04:12Z",
    "device_id": "..."
}
```

The server determines the student through authentication.

The response should be clear.

Success:

```json
{
    "success": true,
    "status": "present",
    "message": "Attendance recorded successfully."
}
```

Failure:

```json
{
    "success": false,
    "error": "outside_attendance_radius",
    "message": "You appear to be outside the attendance area."
}
```

---

# 57. Error Codes

Use predictable internal error identifiers.

Examples:

```text
session_not_found
session_expired
session_ended
not_enrolled
already_attended
device_already_used
location_unavailable
location_stale
outside_attendance_radius
invalid_coordinates
permission_denied
```

These make frontend handling easier.

---

# 58. Security Requirements

Security is particularly important because attendance is an integrity-sensitive system.

The server must never trust:

- Student ID submitted by client.
- Course ID submitted by client.
- Attendance status submitted by client.
- Distance submitted by client.
- Lecturer identity submitted by client.
- Session ownership submitted by client.

The client should provide raw information such as coordinates.

The server calculates:

```text
student identity
course membership
session validity
distance
attendance status
```

---

# 59. CSRF Protection

Django's CSRF protection must remain enabled.

POST requests from authenticated browser sessions must use valid CSRF protection.

Do not disable CSRF globally.

---

# 60. Authentication Security

Use:

- Django password hashing.
- Secure sessions.
- HTTPS in production.
- Secure cookies.
- HttpOnly cookies.
- SameSite protection.
- CSRF protection.

Do not create a custom authentication system unless there is a compelling requirement.

---

# 61. HTTPS

Production deployment must use HTTPS.

Geolocation APIs generally require a secure context.

Therefore:

```text
HTTP
```

should not be used for production.

Use:

```text
HTTPS
```

from the beginning of deployment planning.

---

# 62. Environment Variables

Secrets must not be committed to Git.

Use environment variables for:

```text
SECRET_KEY
DEBUG
DATABASE_URL
ALLOWED_HOSTS
CSRF_TRUSTED_ORIGINS
```

Potential future variables:

```text
EMAIL_HOST
EMAIL_USER
EMAIL_PASSWORD
```

---

# 63. Django Admin

The Django admin should be configured for internal administration.

Admin should expose:

```text
Users
Student Profiles
Lecturer Profiles
Courses
Enrollments
Attendance Sessions
Attendance Records
```

Useful filters:

```text
Course
Lecturer
Student
Status
Date
```

Useful search:

```text
Student ID
Email
Course code
Course name
```

---

# 64. Auditability

Attendance records should not be casually editable.

The system should preserve:

- When attendance was recorded.
- Which session.
- Which student.
- Device identifier.
- Student location.
- Lecturer location.
- Calculated distance.
- Accuracy.

If an administrator must correct attendance later, the system should ideally maintain an audit trail.

A full audit log is a future enhancement, but the schema should not make future auditing impossible.

---

# 65. Time Handling

All timestamps should be stored in UTC.

Django timezone support should be enabled.

User-facing times should be rendered in the relevant local timezone.

The server should remain the authority for:

- Session start.
- Session expiration.
- Attendance timestamp.

Do not trust client-provided current time.

---

# 66. Attendance Accuracy

The application should distinguish:

```text
GPS coordinates
```

from:

```text
calculated attendance distance
```

The calculated distance must be generated server-side.

Example:

```text
Lecturer location
Student location

             ↓

Server calculates

             ↓

Distance = 64.3 metres
```

The client must not submit:

```text
distance = 2 metres
```

and expect the server to trust it.

---

# 67. QR Scanning

There are two separate QR-related interactions.

## Lecturer

The lecturer's browser **displays** the QR code.

## Student

The student's phone scans the QR code.

For MVP, the student can use the phone's native camera to scan the QR code.

The QR should resolve to the Present attendance URL.

This avoids requiring the student to install a QR scanner.

---

# 68. Student Enrollment UX

The preferred first-time setup is:

```text
Lecturer imports roster
       ↓
Student record exists
       ↓
Student receives/creates login
       ↓
Student account is associated with student record
```

However, the exact account activation mechanism can be simplified during MVP implementation.

Possible future mechanism:

```text
University email verification
```

---

# 69. Duplicate Student Handling

Student ID must be the primary business identifier for student records.

If an import contains:

```text
10982345,John Mensah
10982345,John Mensah
```

the import should flag the duplicate.

If a student already exists in the system:

```text
10982345
```

the application should associate the existing student rather than create a second student.

---

# 70. Attendance Percentage

For a student:

```text
attendance_rate =
sessions_present / sessions_held × 100
```

Example:

```text
18 / 20 × 100 = 90%
```

For a course session:

```text
attendance_rate =
students_present / enrolled_students × 100
```

---

# 71. Absent Students

The system does not need to create an explicit attendance record for every absent student.

Instead:

```text
Enrollment exists
Attendance record does not exist
```

means the student was absent for that session.

This reduces unnecessary writes.

However, the UI should still calculate and display:

```text
Present
Absent
```

from enrollment and attendance records.

---

# 72. Session Completion

When the lecturer ends the session:

```text
status = ENDED
ended_at = current server timestamp
```

Students can no longer check in.

The session remains available historically.

---

# 73. Expired Sessions

If the current server time exceeds:

```text
expires_at
```

the session becomes:

```text
EXPIRED
```

No new attendance records may be created.

---

# 74. Lecturer Location Failure

If the lecturer cannot provide location:

```text
Unable to determine your location.
```

The lecturer should not be able to start the attendance session.

Provide a retry mechanism.

---

# 75. Student Location Failure

If the student cannot provide location:

```text
We couldn't verify your location.

Please enable location permission
and try again.
```

Do not mark attendance.

---

# 76. Browser Compatibility

The application should target modern browsers:

- Chrome.
- Edge.
- Safari.
- Firefox.

Particular attention should be given to:

- Android Chrome.
- iOS Safari.

because students are likely to use phones.

---

# 77. Performance Requirements

For a normal university class, the system should comfortably handle:

```text
50–200 students
```

checking in around the same time.

The MVP should be designed so that a burst of requests does not produce duplicate attendance records.

PostgreSQL and proper database constraints should handle the core concurrency requirements.

---

# 78. Database Indexing

Add indexes to frequently queried fields.

Recommended:

```text
User.email
StudentProfile.student_id
Course.code
Enrollment.student
Enrollment.course
AttendanceSession.course
AttendanceSession.token
AttendanceSession.status
AttendanceRecord.session
AttendanceRecord.student
AttendanceRecord.device_id
AttendanceRecord.recorded_at
```

Do not blindly index every field.

---

# 79. Transactions

Attendance creation should be handled as a transactional operation.

Conceptually:

```text
BEGIN TRANSACTION

validate student
validate session
validate device
validate location
create attendance

COMMIT
```

Database uniqueness constraints remain the final protection against duplicates.

---

# 80. Service Layer

Business logic should not be dumped into large Django views.

Create services such as:

```text
attendance/services.py
```

Potential functions:

```text
create_attendance_session()
validate_attendance_session()
calculate_distance()
validate_student_location()
record_attendance()
end_attendance_session()
get_session_statistics()
```

This keeps the application maintainable.

---

# 81. Location Utility

Create a dedicated utility for geographic calculations.

Conceptually:

```text
calculate_distance(
    lat1,
    lon1,
    lat2,
    lon2
)
```

Return:

```text
distance in metres
```

This utility must be thoroughly tested.

---

# 82. Frontend JavaScript Modules

Avoid putting all JavaScript into one huge file.

Recommended:

```text
static/js/
    location.js
    attendance.js
    session.js
    dashboard.js
    device.js
```

Potential responsibilities:

### location.js

- Request location.
- Validate browser support.
- Return coordinates.
- Handle permission failures.

### attendance.js

- Submit attendance.
- Handle response.
- Display success/failure.

### session.js

- Countdown.
- Poll session status.
- Update attendance count.

### device.js

- Generate/retrieve device UUID.

---

# 83. UI Components

Build reusable template components for:

```text
Navbar
Sidebar
Card
Button
Badge
Modal
Alert
Table
Empty state
Loading state
QR display
Attendance status
```

Do not duplicate identical markup throughout the application.

---

# 84. Visual Language

The visual identity should communicate:

```text
Present
Verified
Academic
Reliable
Fast
```

A restrained UI is preferable.

Primary visual concepts:

- Strong typography.
- Clean cards.
- Clear status indicators.
- Generous spacing.
- High contrast.
- Mobile responsiveness.
- Minimal distractions.

---

# 85. Attendance Status Indicators

Use visually distinct states:

```text
Present
Active
Expired
Ended
Absent
Pending
Rejected
```

Do not rely on color alone.

Use:

- Icons.
- Text.
- Appropriate visual hierarchy.

This improves accessibility.

---

# 86. Accessibility

The MVP should follow basic accessibility principles:

- Semantic HTML.
- Keyboard navigation.
- Visible focus states.
- Proper form labels.
- Accessible buttons.
- Sufficient contrast.
- Clear error messages.
- Screen-reader-friendly status messages.

---

# 87. Empty States

Do not show blank dashboards.

Example:

```text
You don't have any courses yet.

Create your first course to get started.

[ Create Course ]
```

Student:

```text
You aren't enrolled in any courses yet.
```

---

# 88. Error Handling

Errors should be user-friendly.

Avoid displaying raw:

```text
500 Internal Server Error
IntegrityError
CSRF verification failed
```

to normal users.

The application should log technical errors server-side while presenting useful messages to users.

---

# 89. Logging

Production logging should capture:

- Application errors.
- Authentication failures.
- Attendance validation failures.
- Unexpected exceptions.
- Session creation.
- Session ending.

Do not log:

- Passwords.
- Authentication secrets.
- Excessive sensitive information.

---

# 90. Testing Strategy

Testing is mandatory because attendance integrity is the central product requirement.

## Unit tests

Test:

- Distance calculation.
- Session expiration.
- Attendance rate calculation.
- Token generation.
- Enrollment validation.

## Model tests

Test:

- Uniqueness constraints.
- Course ownership.
- Enrollment relationships.
- Attendance relationships.

## Attendance service tests

Test:

```text
Valid attendance → success
Expired session → rejection
Ended session → rejection
Student not enrolled → rejection
Duplicate student → rejection
Duplicate device → rejection
Outside radius → rejection
Invalid location → rejection
```

---

# 91. Integration Tests

Test complete flows.

### Lecturer

```text
Login
→ Create course
→ Add students
→ Start session
→ End session
```

### Student

```text
Login
→ Open QR URL
→ Submit location
→ Attendance recorded
```

### Security

```text
Student attempts to access another student's data
→ 403/404
```

---

# 92. Concurrency Test

Simulate two requests from the same student arriving almost simultaneously.

Expected result:

```text
Request 1 → attendance created
Request 2 → rejected as duplicate
```

Do not allow:

```text
Request 1 → attendance created
Request 2 → second attendance created
```

---

# 93. Security Testing

Test:

- CSRF.
- Authentication bypass.
- Authorization bypass.
- Session token guessing.
- Duplicate requests.
- Student ID manipulation.
- Course ID manipulation.
- Location manipulation.
- Expired QR codes.
- Ended sessions.
- Unauthorized attendance modifications.

---

# 94. Deployment Architecture

Recommended initial production architecture:

```text
                    Internet
                       │
                       ▼
                    Nginx
                       │
                       ▼
                  Gunicorn
                       │
                       ▼
                    Django
                       │
                       ▼
                 PostgreSQL
```

Static files should be served efficiently by Nginx.

---

# 95. Production Infrastructure

Minimum:

```text
VPS
Ubuntu Linux
Nginx
Gunicorn
Django
PostgreSQL
HTTPS
```

The application should run under a non-root service account.

---

# 96. Environment Separation

Maintain:

```text
development
staging
production
```

At minimum, development and production configuration must be separated.

Never use:

```text
DEBUG=True
```

in production.

---

# 97. Git Workflow

Repository:

```text
present/
```

Recommended branches:

```text
main
develop
feature/*
fix/*
```

Example:

```text
feature/authentication
feature/course-management
feature/attendance-session
feature/geolocation
```

Pull requests should be used before merging significant features.

---

# 98. Commit Strategy

Use meaningful commits.

Good:

```text
feat: add custom user authentication
feat: add course enrollment
feat: implement attendance sessions
feat: add geolocation validation
fix: prevent duplicate attendance
test: add attendance concurrency tests
```

Avoid:

```text
update
changes
stuff
final
final2
```

---

# 99. Implementation Phases

The project should be built incrementally.

## Phase 1 — Project Foundation

Implement:

- Django project.
- PostgreSQL connection.
- Environment configuration.
- Custom user model.
- Base templates.
- Tailwind.
- Authentication.
- Django admin.

Deliverable:

```text
Users can register and log in.
```

---

## Phase 2 — Course Management

Implement:

- Course model.
- Course creation.
- Course editing.
- Course listing.
- Lecturer ownership.
- Course dashboard.

Deliverable:

```text
Lecturer can create and manage courses.
```

---

## Phase 3 — Student Management

Implement:

- Student profile.
- Student IDs.
- Enrollment.
- Individual student addition.
- CSV import.
- Roster page.

Deliverable:

```text
Lecturer can establish a complete class roster.
```

---

## Phase 4 — Attendance Sessions

Implement:

- Session model.
- Secure token generation.
- Session creation.
- Expiration.
- End session.
- QR generation.
- QR display.

Deliverable:

```text
Lecturer can start an attendance session
and display a QR code.
```

---

## Phase 5 — Student Check-In

Implement:

- QR URL.
- Student authentication.
- Session validation.
- Enrollment validation.
- Attendance record.
- Duplicate protection.

Deliverable:

```text
Student can scan and mark attendance.
```

Initially implement attendance without geolocation if necessary so the core transaction can be tested independently.

---

## Phase 6 — Geolocation

Implement:

- Lecturer location capture.
- Student location capture.
- Location accuracy.
- Haversine calculation.
- Radius validation.
- Location timestamps.
- Failure states.

Deliverable:

```text
Only students within the configured
attendance radius can check in.
```

---

## Phase 7 — Device Protection

Implement:

- Device UUID generation.
- Persistent client storage.
- Device/session validation.
- Duplicate device handling.

Deliverable:

```text
One device cannot be used to
record multiple students in one session.
```

---

## Phase 8 — Live Dashboard

Implement:

- Attendance count.
- Present student list.
- Polling.
- Countdown.
- Session status.
- End session.

Deliverable:

```text
Lecturer can watch attendance happen in real time.
```

---

## Phase 9 — History & Analytics

Implement:

- Course attendance history.
- Individual student history.
- Attendance percentages.
- Session statistics.
- Student dashboard.

Deliverable:

```text
Present becomes a useful semester-long attendance system.
```

---

## Phase 10 — Hardening & Deployment

Implement:

- Security review.
- Automated tests.
- Error handling.
- Logging.
- HTTPS.
- Production configuration.
- PostgreSQL production database.
- Backup strategy.
- Deployment scripts.

Deliverable:

```text
Production-ready MVP.
```

---

# 100. MVP Definition of Done

The MVP is complete when the following scenario works from beginning to end.

## Lecturer

1. Registers/logs in.
2. Creates BIOC 301.
3. Imports 57 students.
4. Opens BIOC 301.
5. Clicks **Start Attendance**.
6. Grants browser location permission.
7. Present creates an active session.
8. Present generates a QR code.
9. Lecturer displays QR code.

## Student

1. Student logs in.
2. Student scans QR code.
3. Student's course membership is validated.
4. Browser requests location.
5. Student grants location permission.
6. Present receives coordinates.
7. Server calculates distance.
8. Distance is within permitted radius.
9. Device has not been used for another student.
10. Student has not already attended.
11. Attendance is recorded.

## Lecturer

The lecturer immediately sees:

```text
1 / 57 Present
```

Then:

```text
2 / 57 Present
```

and eventually:

```text
49 / 57 Present
```

When the lecturer ends the session:

```text
49 Present
8 Absent
86% Attendance
```

The session becomes immutable from the normal lecturer interface.

---

# 101. Important Product Decisions

The following decisions should remain fixed unless there is a strong reason to change them:

### Decision 1

**Django over Flask**

Reason:

- Authentication.
- Admin.
- ORM.
- Forms.
- Security.
- Structured application architecture.

### Decision 2

**PostgreSQL over SQLite**

Reason:

- Concurrent attendance submissions.
- Relational data.
- Production reliability.
- Strong constraints.

### Decision 3

**Django Templates + Vanilla JS over React**

Reason:

- Lower complexity.
- Faster MVP development.
- No need for a separate frontend application.
- Attendance interaction is relatively contained.
- React can be introduced later if the dashboard becomes sufficiently complex.

### Decision 4

**QR + geolocation**

QR establishes:

```text
Which attendance session?
```

Geolocation establishes:

```text
Is the student physically near the session?
```

Authentication establishes:

```text
Which student?
```

Device identification establishes:

```text
Has this device already been used?
```

Together:

```text
Identity
+
Session
+
Location
+
Device
=
Verified Attendance
```

---

# 102. Future Enhancements

These should NOT block MVP development.

Potential future versions could include:

## Rotating QR

QR changes every few seconds.

## Wi-Fi verification

Verify that the device is connected to the classroom/institution network.

## Bluetooth proximity

Use Bluetooth beacons or other proximity mechanisms.

## University SSO

Integrate with institutional authentication.

## Email verification

Require university email addresses.

## Timetable integration

Automatically create sessions based on scheduled classes.

## Attendance reports

Export:

```text
CSV
Excel
PDF
```

## Attendance warnings

Automatically identify students below a threshold.

Example:

```text
John Mensah
Attendance: 62%
⚠ Below 75% threshold
```

## Multiple lecturers

Allow co-teaching.

## Course assistants

Allow authorized teaching assistants to start sessions.

## Advanced analytics

Track:

- Attendance trends.
- Session-level attendance.
- Student attendance patterns.
- Course comparisons.

## Progressive Web App

Allow Present to behave more like a mobile application without requiring native apps.

---

# 103. Critical Security Principle

The most important implementation principle is:

> **The frontend is never trusted.**

A user can modify JavaScript.

A user can inspect network requests.

A user can manipulate request payloads.

Therefore:

```text
Frontend
    ↓
provides information
    ↓
Backend
    ↓
validates everything
    ↓
Database
    ↓
enforces integrity
```

The server must determine whether attendance is valid.

---

# 104. Critical UX Principle

The most important UX principle is:

> **Attendance should take seconds, not minutes.**

The ideal student flow is:

```text
Scan QR
   ↓
Location check
   ↓
✓ Present
```

No lengthy form.

No searching for a course.

No manually entering a student number.

No typing a code.

No unnecessary confirmation steps.

Once authenticated and onboarded, the student's normal attendance interaction should be almost frictionless.

---

# 105. Product Philosophy

Present should not feel like an administrative database with an attendance feature.

It should feel like:

> **A simple "I'm here" button backed by serious verification.**

The complexity should exist behind the scenes.

For the lecturer:

```text
Start → Display → Watch → End
```

For the student:

```text
Scan → Verify → Present
```

Everything else exists to make those two experiences reliable.

---

# 106. Final Architecture

The final MVP architecture should look approximately like this:

```text
                         PRESENT
                            │
             ┌──────────────┴──────────────┐
             │                             │
         LECTURER                       STUDENT
             │                             │
             ▼                             ▼
      Django Templates              Django Templates
             │                             │
             └──────────────┬──────────────┘
                            │
                     Vanilla JavaScript
                            │
                 ┌──────────┴──────────┐
                 │                     │
             Geolocation              QR
                 │                     │
                 └──────────┬──────────┘
                            │
                         Django
                            │
             ┌──────────────┼──────────────┐
             │              │              │
         Accounts         Courses       Attendance
             │              │              │
             └──────────────┼──────────────┘
                            │
                       Django ORM
                            │
                            ▼
                       PostgreSQL
```

---

# 107. Core Data Relationship

The central relationship is:

```text
LECTURER
    │
    │ owns
    ▼
 COURSE
    │
    │ has
    ▼
ENROLLMENTS
    │
    │ connect
    ▼
 STUDENTS
    │
    │ attend
    ▼
ATTENDANCE SESSIONS
    │
    │ generate
    ▼
ATTENDANCE RECORDS
```

More precisely:

```text
Lecturer
   │
   ├───────────────┐
   ▼               ▼
Courses          Profile
   │
   ▼
Enrollments
   │
   ▼
Students
   │
   ▼
Attendance Records
   ▲
   │
Attendance Sessions
```

---

# 108. Final MVP Success Criteria

Present succeeds if a lecturer can walk into a classroom and accomplish this:

```text
Open Present
      ↓
Select BIOC 301
      ↓
Start Attendance
      ↓
QR appears
      ↓
Project QR
      ↓
Students scan
      ↓
Location verified
      ↓
Attendance appears live
      ↓
End session
```

without requiring technical knowledge.

A student should be able to:

```text
Scan
 ↓
Verify location
 ↓
See "You're Present"
```

in a matter of seconds.

That simplicity should remain the defining characteristic of Present even as the system grows.