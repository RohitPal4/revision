<div align="center">
  <h1>🚀 Node.js Core: Day 02</h1>
  <p><i>Express Setup, Routing, Path Variables, and Error Middleware.</i></p>
</div>

---

## 📑 Table of Contents
- [1. Express Setup + Basic Routing](#1-express-setup--basic-routing)
- [2. Path Variables — req.params](#2-path-variables--reqparams)
- [3. Query Parameters — req.query](#3-query-parameters--reqquery)
- [4. Strict JSON Schemas + Error Middleware](#4-strict-json-schemas--error-middleware)

---

## 1. Express Setup + Basic Routing

### Setup
```bash
mkdir api && cd api
npm init -y
npm install express
touch server.js
```

### Minimal server
```javascript
const express = require('express');
const app = express();

app.use(express.json()); // parses incoming JSON bodies into req.body

app.get('/', (req, res) => {
  res.json({ message: 'API is running' });
});

app.listen(3000, () => {
  console.log('listening on :3000');
});
```

### Three things happening here:
1. `express()` — creates the app instance. Think of it as your configured HTTP server.
2. `app.use(express.json())` — middleware that reads the raw request body and parses it into `req.body`. Without this, `req.body` is `undefined` on POST/PUT requests.
3. `app.get(path, handler)` — registers a route. Express matches method + path, then runs your handler.

### Route methods map directly to HTTP verbs
```javascript
app.get('/users', handler);     // READ
app.post('/users', handler);    // CREATE
app.put('/users/:id', handler); // REPLACE
app.patch('/users/:id',handler);// UPDATE
app.delete('/users/:id',handler)// DELETE
```

---

## 2. Path Variables — `req.params`

Path variables are dynamic segments in the URL, prefixed with `:`.

```javascript
app.get('/users/:id', (req, res) => {
  const { id } = req.params;

  res.json({
    userId: id,
    name: 'Alice'
  });
});
```

**Test:**
```bash
curl http://localhost:3000/users/42
# { "userId": "42", "name": "Alice" }
```

> [!WARNING]
> `req.params.id` is always a string — even if you pass a number in the URL. Always parse it:

```javascript
const id = parseInt(req.params.id, 10);

if (isNaN(id)) {
  return res.status(400).json({ error: 'id must be a number' });
}
```

### Multiple path variables
```javascript
app.get('/users/:userId/posts/:postId', (req, res) => {
  const { userId, postId } = req.params;
  res.json({ userId, postId });
});
```

**Test:**
```bash
curl http://localhost:3000/users/5/posts/12
# { "userId": "5", "postId": "12" }
```

---

## 3. Query Parameters — `req.query`

Query params come after `?` in the URL — used for filtering, sorting, pagination.

```javascript
app.get('/users', (req, res) => {
  const { role, sort, limit } = req.query;

  res.json({
    filters: {
      role:  role  || 'all',
      sort:  sort  || 'asc',
      limit: limit ? parseInt(limit, 10) : 20
    }
  });
});
```

**Test:**
```bash
curl "http://localhost:3000/users?role=admin&sort=desc&limit=5"
# { "filters": { "role": "admin", "sort": "desc", "limit": 5 } }
```

> [!NOTE]
> Same rule as params — all query values arrive as strings. Always coerce types explicitly.

---

## 4. Strict JSON Schemas + Error Middleware

### Strict JSON response schema
Every route should return a consistent shape — success and error alike:

```javascript
// success shape
res.status(200).json({
  success: true,
  data: { userId: 1, name: 'Alice' }
});

// error shape
res.status(404).json({
  success: false,
  error: 'User not found'
});
```

Consistency matters — the frontend always knows what shape to expect.

### Putting it all together — a complete API

```javascript
const express = require('express');
const app = express();

app.use(express.json());

const users = [
  { id: 1, name: 'Alice', role: 'admin' },
  { id: 2, name: 'Bob',   role: 'viewer' },
  { id: 3, name: 'Carol', role: 'admin' }
];

// GET /users?role=admin
app.get('/users', (req, res) => {
  const { role } = req.query;
  const result = role
    ? users.filter(u => u.role === role)
    : users;

  res.status(200).json({ success: true, data: result });
});

// GET /users/:id
app.get('/users/:id', (req, res) => {
  const id = parseInt(req.params.id, 10);

  if (isNaN(id)) {
    return res.status(400).json({ success: false, error: 'id must be a number' });
  }

  const user = users.find(u => u.id === id);

  if (!user) {
    return res.status(404).json({ success: false, error: 'User not found' });
  }

  res.status(200).json({ success: true, data: user });
});

// POST /users
app.post('/users', (req, res) => {
  const { name, role } = req.body;

  if (!name || !role) {
    return res.status(400).json({ success: false, error: 'name and role are required' });
  }

  const newUser = { id: users.length + 1, name, role };
  users.push(newUser);

  res.status(201).json({ success: true, data: newUser });
});

// 404 — unmatched routes
app.use((req, res) => {
  res.status(404).json({ success: false, error: 'Route not found' });
});

// error middleware — exactly 4 arguments
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ success: false, error: 'Internal server error' });
});

app.listen(3000, () => console.log('listening on :3000'));
```

### Three things worth burning into memory

> [!IMPORTANT]
> **Middleware order matters.** Express runs middleware top to bottom. Your 404 handler must come after all routes — otherwise it catches everything.

> [!WARNING]
> **Error middleware needs exactly 4 args.** Express identifies it as an error handler *only* because of the `err` as the first parameter. Write 3 args and it becomes a regular middleware — errors silently pass through.

> [!NOTE]
> **Return on early responses.** Without `return`, execution continues after `res.json()` and you'll try to send a second response — Express throws a "headers already sent" error.

---

### Test the full API

```bash
# all users
curl http://localhost:3000/users

# filter by role
curl "http://localhost:3000/users?role=admin"

# single user
curl http://localhost:3000/users/1

# user not found
curl http://localhost:3000/users/99

# create user
curl -X POST http://localhost:3000/users \
  -H "Content-Type: application/json" \
  -d '{"name":"Dave","role":"viewer"}'

# bad id
curl http://localhost:3000/users/abc

# unknown route
curl http://localhost:3000/unknown
```

## 💡 Interview Q&A

### Q1 — Setup + Basic Routing
What is this line doing, and what happens if you remove it?
```javascript
app.use(express.json());
```
Then answer: if you remove it and send this request —
```bash
curl -X POST http://localhost:3000/users \
  -H "Content-Type: application/json" \
  -d '{"name":"Alice","role":"admin"}'
```
— what does `req.body` contain inside your route handler?

**Answer:**

**What does this line do?**
`app.use(express.json());`
This is middleware in Express that parses incoming requests with a JSON body and converts the JSON into a JavaScript object.

For example, if the client sends:
```json
{
  "name": "Alice",
  "role": "admin"
}
```
then Express automatically makes it available as:
```javascript
req.body = {
  name: "Alice",
  role: "admin"
};
```

**What happens if you remove it?**
Suppose your route is:
```javascript
app.post("/users", (req, res) => {
  console.log(req.body);
  res.send("OK");
});
```
and you send:
```bash
curl -X POST http://localhost:3000/users \
  -H "Content-Type: application/json" \
  -d '{"name":"Alice","role":"admin"}'
```
Without `app.use(express.json());`, Express does not parse the JSON body.
So inside the route: `console.log(req.body);` you will get: `undefined` because `req.body` was never populated.

**Summary**
| | With `express.json()` | Without `express.json()` |
|---|---|---|
| **JSON body** | is parsed | is not parsed |
| **`req.body`** | `= { name: "Alice", role: "admin" }` | `= undefined` |
| **Data access** | Easy access to request data | Cannot access JSON data directly |

> **If you remove `app.use(express.json())`, then for the given curl request, `req.body` will be `undefined` inside the route handler.**

---

### Q2 — Path Variables
What is wrong with this code? Find all the bugs.
```javascript
app.get('/users/:id', (req, res) => {
  const id = req.params.id;

  const user = users.find(u => u.id === id);

  if (!user) {
    res.status(404).json({ success: false, error: 'User not found' });
  }

  res.status(200).json({ success: true, data: user });
});
```
The users array is:
```javascript
const users = [
  { id: 1, name: 'Alice' },
  { id: 2, name: 'Bob' }
];
```
There are two bugs. Find both, explain why each is a bug, and write the fixed version.

**Answer:**

#### Bug 1: Type Mismatch
**Problem:** `req.params.id` is always a string.
```javascript
const id = req.params.id;
```
If the request is `GET /users/1`, then `id === "1"`. But in the array, the `id` is a number (`1`). So `1 === "1"` is `false`. Therefore, `users.find(u => u.id === id);` returns `undefined` even though the user exists.

**Fix:** Convert the route parameter to a number:
```javascript
const id = Number(req.params.id);
// or
const id = parseInt(req.params.id, 10);
```

#### Bug 2: Missing `return` After 404 Response
**Problem:** After sending the 404 response, the function continues executing:
```javascript
if (!user) {
  res.status(404).json({
    success: false,
    error: 'User not found'
  });
}
// ... Execution continues ...
res.status(200).json({ success: true, data: user });
```
Now Express tries to send two responses for one request. This causes an error like: `Error [ERR_HTTP_HEADERS_SENT]: Cannot set headers after they are sent to the client`

**Fix:** Return immediately:
```javascript
if (!user) {
  return res.status(404).json({
    success: false,
    error: 'User not found'
  });
}
```

#### Fixed Version
```javascript
app.get('/users/:id', (req, res) => {
  const id = Number(req.params.id);

  const user = users.find(u => u.id === id);

  if (!user) {
    return res.status(404).json({
      success: false,
      error: 'User not found'
    });
  }

  res.status(200).json({
    success: true,
    data: user
  });
});
```

> **Interview Answer (Short)**
> - **Bug 1:** `req.params.id` is a string, while `users.id` is a number. Convert `req.params.id` using `Number()` or `parseInt()` before comparison.
> - **Bug 2:** After sending the 404 response, execution continues and attempts to send a second response. Add `return` before `res.status(404).json(...)` to stop further execution.

---

### Q3 — Query Parameters
What does this route return for each of these three requests? Trace through the logic for each one.
```javascript
app.get('/users', (req, res) => {
  const users = [
    { id: 1, name: 'Alice', role: 'admin' },
    { id: 2, name: 'Bob',   role: 'viewer' },
    { id: 3, name: 'Carol', role: 'admin' }
  ];

  const { role, limit } = req.query;

  const filtered = role
    ? users.filter(u => u.role === role)
    : users;

  const limited = limit
    ? filtered.slice(0, parseInt(limit, 10))
    : filtered;

  res.status(200).json({ success: true, data: limited });
});
```
**Request A:** `curl http://localhost:3000/users`
**Request B:** `curl "http://localhost:3000/users?role=admin"`
**Request C:** `curl "http://localhost:3000/users?role=admin&limit=1"`

**Answer:**

#### Request A: `curl http://localhost:3000/users`
- **Step 1:** `req.query` is `{}`. So `role = undefined`, `limit = undefined`.
- **Step 2:** `role` is undefined (falsy), so `filtered = users;`.
- **Step 3:** `limit` is undefined, so `limited = filtered;`.
- **Response:** All 3 users.

#### Request B: `curl "http://localhost:3000/users?role=admin"`
- **Step 1:** `req.query` is `{ role: "admin" }`. So `role = "admin"`, `limit = undefined`.
- **Step 2:** Filter admins (`Alice` and `Carol`). Result: `filtered = [{ Alice }, { Carol }]`.
- **Step 3:** `limit` is undefined, so `limited = filtered;`.
- **Response:** Alice and Carol.

#### Request C: `curl "http://localhost:3000/users?role=admin&limit=1"`
- **Step 1:** `req.query` is `{ role: "admin", limit: "1" }`. So `role = "admin"`, `limit = "1"`.
- **Step 2:** Filter admins. Result: `filtered = [{ Alice }, { Carol }]`.
- **Step 3:** `parseInt("1", 10)` becomes `1`. Then `filtered.slice(0, 1)` returns only the first element: `[{ Alice }]`.
- **Response:** Alice.

#### Quick Summary
| Request | Filter Applied | Limit Applied | Result |
|---|---|---|---|
| `/users` | No | No | Alice, Bob, Carol |
| `/users?role=admin` | Admin only | No | Alice, Carol |
| `/users?role=admin&limit=1` | Admin only | First 1 user | Alice |

> **Interview Takeaway**
> - `req.query` values are **always strings**.
> - `role=admin` filters users by role.
> - `limit=1` is converted from `"1"` to `1` using `parseInt()`.
> - `slice(0, n)` returns the first `n` elements.

---

### Q4 — Error Middleware
What is wrong with this error handler?
```javascript
app.use((err, req, res) => {
  res.status(500).json({
    success: false,
    error: 'Something went wrong'
  });
});
```

**Answer:**

**Problem:**
Express recognizes error-handling middleware only if it has **exactly 4 parameters**: `(err, req, res, next)`.
Your middleware has only 3 parameters: `(err, req, res)`. So Express treats it as normal middleware, not error middleware.
As a result:
- Errors are not routed to it.
- It never gets called when an error occurs.
- It appears to "silently fail."

**Fix:** Add the fourth parameter `next`.
```javascript
app.use((err, req, res, next) => {
  res.status(500).json({
    success: false,
    error: 'Something went wrong'
  });
});
```
*Even if you don't use `next`, it must be present.*

**Why does Express require 4 parameters?**
Express identifies middleware by its function signature:
- Normal Middleware: `(req, res, next)`
- Error Middleware: `(err, req, res, next)`
The first parameter (`err`) tells Express: "This middleware is intended to handle errors." Without all four parameters, Express doesn't recognize it as an error handler.

**What is `next` used for?**
`next` passes control to the next middleware.
- Normal middleware: `next()`
- Error middleware: `next(err)` forwards the error to another error handler.

**How do you trigger this error handler from a route?**
- **Method 1: `next(err)` (Recommended)**
  ```javascript
  app.get('/users/:id', (req, res, next) => {
    // ...
    if (!user) return next(new Error('User not found'));
  });
  ```
- **Method 2: Throw an Error (Sync Code)**
  ```javascript
  app.get('/test', (req, res) => {
    throw new Error('Something broke');
  });
  ```
- **Method 3: Async Route**
  ```javascript
  app.get('/test', async (req, res, next) => {
    try {
      throw new Error('Database failed');
    } catch (err) {
      next(err);
    }
  });
  ```

> **Interview Answer (Short)**
> - The error handler is missing the fourth parameter `next`.
> - Express only treats middleware with signature `(err, req, res, next)` as error-handling middleware.
> - `next` is used to pass control or forward errors to the next middleware/error handler.
> - Trigger the error handler by calling `next(new Error('Something went wrong'))` inside a route, or by throwing an error in synchronous code.

<div align="center">
  <i>Happy Coding! Express yourself! 🚂</i>
</div>


