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

---
<div align="center">
  <i>Happy Coding! Express yourself! 🚂</i>
</div>