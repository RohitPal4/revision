<div align="center">
  <h1>🚀 Node.js Core: Day 01</h1>
  <p><i>A deep dive into the native `http` module, routing, and streams.</i></p>
</div>

---

## 📑 Table of Contents
- [1. The Mental Model](#1-the-mental-model)
- [2. Building the Server — Line by Line](#2-building-the-server--line-by-line)
- [3. Routing & Error Handling](#3-routing--error-handling)
- [4. Testing without a Browser](#4-testing-without-a-browser)

---

## 1. The Mental Model

In the browser, JS runs in a tab. In Node.js, JS runs on your machine — with access to the file system, network, and OS. The `http` module is Node's built-in way to open a TCP port and listen for incoming HTTP requests.

*No Express. No framework. Just this:*

```text
Client                        Node.js
  │                              │
  │  GET /users HTTP/1.1         │
  │ ─────────────────────────►   │
  │                              │  ← your callback runs
  │                              │  ← req = incoming message
  │                              │  ← res = your response handle
  │  HTTP/1.1 200 OK             │
  │ ◄─────────────────────────   │
```

Every request triggers your callback with two objects:
- **`req`** — what the client sent (method, url, headers, body)
- **`res`** — what you send back (status, headers, body)

---

## 2. Building the Server — Line by Line

```javascript
const http = require('http'); // 1

const server = http.createServer((req, res) => { // 2
  res.writeHead(200, { 'Content-Type': 'text/plain' }); // 3
  res.end('Hello World'); // 4
});

server.listen(3000, () => { // 5
  console.log('Server running on http://localhost:3000');
});
```

### Breakdown:
1. **`require('http')`**: Pulls in Node's native `http` module. No `npm install` needed.
2. **`createServer`**: Creates a server. The callback fires on *every* incoming request.
3. **`res.writeHead`**: Writes the status line + headers. `200 = OK`. Must be called before `res.end()`.
4. **`res.end`**: Sends the response body and signals the response is complete. **Always required** — without it the client hangs forever waiting.
5. **`server.listen`**: Binds to port 3000 and starts listening. The callback fires once when ready.

---

## 3. Routing & Error Handling

Here is a real server with basic routing and POST body parsing.

```javascript
const http = require('http');

const server = http.createServer((req, res) => {
  const { method, url } = req; // destructure what we need

  // route: GET /
  if (method === 'GET' && url === '/') {
    res.writeHead(200, { 'Content-Type': 'text/plain' });
    res.end('Home page');
    return;
  }

  // route: GET /users
  if (method === 'GET' && url === '/users') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ users: ['Alice', 'Bob'] }));
    return;
  }

  // route: POST /users
  if (method === 'POST' && url === '/users') {
    let body = '';

    req.on('data', chunk => { body += chunk; }); // collect chunks
    req.on('end', () => {                        // body fully received
      const parsed = JSON.parse(body);
      res.writeHead(201, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ created: parsed }));
    });
    return;
  }

  // fallthrough: 404
  res.writeHead(404, { 'Content-Type': 'text/plain' });
  res.end('Not found');
});

server.listen(3000, () => {
  console.log('listening on :3000');
});
```

### Three things worth understanding deeply:

> [!IMPORTANT]
> **Why return after each route?**
> Without it, execution falls through to the next `if` — and you'd try to call `res.writeHead` twice, which throws an error.

> [!NOTE]
> **Why chunked body reading for POST?**
> HTTP bodies arrive as a stream — not all at once. `req.on('data')` collects pieces, `req.on('end')` fires when the full body is assembled. This is why Express's `req.body` feels magical — it does this for you under the hood.

> [!WARNING]
> **Why does `res.end()` matter?**
> `res.end()` flushes and closes the response. Skip it and the browser spins forever. Every single code path must call it exactly once.

---

## 4. Testing without a Browser

You can use `curl` to test all routes straight from your terminal.

```bash
# GET home
curl http://localhost:3000/

# GET users
curl http://localhost:3000/users

# POST users
curl -X POST http://localhost:3000/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice"}'

# 404 Not Found
curl http://localhost:3000/unknown
```

---
<div align="center">
  <i>Happy Coding! Build that backend muscle. 💪</i>
</div>