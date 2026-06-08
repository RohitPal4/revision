<div align="center">
  <h1>🚀 JavaScript Advanced Concepts: Day 01</h1>
  <p><i>A deep dive into Execution Contexts, Hoisting, Closures, and more.</i></p>
</div>

---

## 📑 Table of Contents
- [1. Execution Context](#1-execution-context)
- [2. Call Stack](#2-call-stack)
- [3. Hoisting](#3-hoisting)
- [4. var vs let vs const](#4-var-vs-let-vs-const)
- [5. Scope Chains](#5-scope-chains)
- [6. Closures](#6-closures)
- [🎯 Interview Prep & Challenges](#-interview-prep--challenges)

---

## 1. Execution Context

Every time JavaScript runs, it needs a place to keep track of: what variables exist, what `this` refers to, and what code is currently running. That place is called an Execution Context (EC).

Two phases happen before any code runs:

**Phase 1 — Creation phase**
- JS scans the code
- Allocates memory for variables and functions
- Sets up the scope chain
- Determines the value of `this`

**Phase 2 — Execution phase**
- Code runs line by line
- Variables get assigned actual values

### Three types of EC:
- **Global EC** — created once when the script loads. In browsers, this = `window`. There is always exactly one.
- **Function EC** — created every time a function is called (not defined — called). Each call gets its own fresh EC.
- **Eval EC** — ignore this one, you'll never use it.

Each EC contains three things:
```text
Execution Context
├── Variable Environment   ← where var declarations live
├── Lexical Environment    ← where let/const + function declarations live
└── this binding           ← depends on how the function was called
```

### Quick example:
```javascript
const name = 'Alice';       // in Global EC

function greet() {
  const msg = 'Hello';      // in greet's Function EC
  console.log(msg + name);  // walks scope chain to find `name`
}

greet();
```
When `greet()` is called, a brand-new Function EC is created with its own variable environment. When it needs `name`, it doesn't find it locally, so it looks up the scope chain to the Global EC — and finds it there.

---

## 2. Call Stack

The Call Stack is JavaScript's mechanism for tracking which execution context is currently active. It's a classic stack (LIFO — Last In, First Out).

> [!TIP]
> **Simple rule**: EC created → pushed on stack. EC finished → popped off stack.

### Visualizing it:
```javascript
function multiply(a, b) {
  return a * b;           // 3️⃣ runs here
}

function square(n) {
  return multiply(n, n);  // 2️⃣ calls multiply
}

square(4);                // 1️⃣ starts here
```

Here's exactly what the stack looks like at each moment:

**1️⃣ `square(4)` called**
```text
     ┌─────────────┐
     │  square EC  │  ← top (active)
     ├─────────────┤
     │  Global EC  │
     └─────────────┘
```

**2️⃣ `multiply(4, 4)` called inside square**
```text
     ┌──────────────┐
     │ multiply EC  │  ← top (active)
     ├──────────────┤
     │  square EC   │  ← waiting
     ├──────────────┤
     │  Global EC   │
     └──────────────┘
```

**3️⃣ multiply returns 16 → popped**
```text
     ┌─────────────┐
     │  square EC  │  ← top again (resumes)
     ├─────────────┤
     │  Global EC  │
     └─────────────┘
```

**4️⃣ square returns 16 → popped**
```text
     ┌─────────────┐
     │  Global EC  │  ← only this remains
     └─────────────┘
```

### Stack Overflow
This is literally what causes the error — infinite recursion fills the stack until the engine gives up:
```javascript
function infinite() {
  return infinite(); // keeps pushing, never pops
}

infinite(); // ❌ Uncaught RangeError: Maximum call stack size exceeded
```

### Key insight — JS is single-threaded
There is one call stack. Only one EC is ever running at a time — the one on top. This is why JS can't do two things simultaneously. (Async/await and the event loop work around this — but that's a later topic.)

| Concept | One-liner |
| :--- | :--- |
| **Call Stack** | Tracks which EC is active |
| **Push** | Happens when a function is called |
| **Pop** | Happens when a function returns |
| **Stack overflow** | Too many nested calls, stack runs out of space |

---

## 3. Hoisting

Remember Phase 1 (Creation phase) from Execution Context? That's where hoisting happens. Before any code runs, JS scans the file and allocates memory for declarations. It looks like variables and functions "move to the top" — but nothing physically moves. The engine just knows about them early.

### var hoisting — declared AND initialized
```javascript
console.log(name); // ✅ undefined  (not an error!)
var name = 'Alice';
console.log(name); // ✅ 'Alice'
```
What JS actually sees internally:
```javascript
var name = undefined; // ← hoisted + initialized to undefined
console.log(name);    // undefined
name = 'Alice';       // assignment stays in place
console.log(name);    // 'Alice'
```

### let / const hoisting — declared but NOT initialized (TDZ)
```javascript
console.log(age); // ❌ ReferenceError: Cannot access 'age' before initialization
let age = 25;
```
`let` and `const` are hoisted — the engine knows they exist — but they sit in the **Temporal Dead Zone (TDZ)** from the start of the block until their line is reached. Touching them inside the TDZ throws an error.

```text
Start of scope
│
│  ← TDZ: engine knows `age` exists but won't let you touch it
│
let age = 25;  ← TDZ ends here, `age` is now accessible
│
End of scope
```

### Function declarations — fully hoisted
```javascript
greet(); // ✅ 'Hello!'  — works before the definition

function greet() {
  console.log('Hello!');
}
```
The entire function body is hoisted. You can call it anywhere in the file.

### Function expressions — NOT fully hoisted
```javascript
greet(); // ❌ TypeError: greet is not a function

var greet = function() {
  console.log('Hello!');
};
```
Here `greet` is a `var` — so it's hoisted as `undefined`. Calling `undefined()` throws a `TypeError`.

### Side-by-side cheat sheet
|  | Hoisted? | Initialized? | Usable before declaration? |
| :--- | :---: | :---: | :--- |
| **`var`** | ✅ Yes | ✅ `undefined` | ✅ Yes (gives `undefined`) |
| **`let`** | ✅ Yes | ❌ No (TDZ) | ❌ `ReferenceError` |
| **`const`** | ✅ Yes | ❌ No (TDZ) | ❌ `ReferenceError` |
| **`function` declaration** | ✅ Yes | ✅ Full body | ✅ Yes |
| **`function` expression (var)**| ✅ Yes | ✅ `undefined` | ❌ `TypeError` |

### The one thing people get wrong
*"let and const are not hoisted."*

**Wrong.** They are hoisted — the TDZ proves it. If they weren't hoisted at all, this would print the outer value instead of throwing:
```javascript
let x = 'outer';

function test() {
  console.log(x); // ❌ ReferenceError (not 'outer'!)
  let x = 'inner';
}

test();
```
The inner `let x` was hoisted to the top of `test()`'s scope, putting `x` in TDZ — which is why it doesn't reach up to find `'outer'`.

---

## 4. var vs let vs const

You already know hoisting behavior. Now let's layer in the remaining differences — scope, redeclaration, and reassignment. After this, the three will never blur together again.

### Scope — the biggest difference
**`var` is function-scoped**
```javascript
function test() {
  if (true) {
    var x = 10;
  }
  console.log(x); // ✅ 10 — x leaked out of the if block!
}
```
`var` doesn't care about `{ }` blocks — only function boundaries contain it.

**`let` and `const` are block-scoped**
```javascript
function test() {
  if (true) {
    let y = 10;
    const z = 20;
  }
  console.log(y); // ❌ ReferenceError — y is locked inside the if block
  console.log(z); // ❌ ReferenceError — same for z
}
```
A "block" is anything between `{ }` — `if`, `for`, `while`, standalone braces.

### The classic var trap in loops
```javascript
for (var i = 0; i < 3; i++) {
  setTimeout(() => console.log(i), 100);
}
// prints: 3, 3, 3  ❌
```
`var i` leaks out of the loop. By the time `setTimeout` fires, the loop is done and `i` is already `3`.

```javascript
for (let i = 0; i < 3; i++) {
  setTimeout(() => console.log(i), 100);
}
// prints: 0, 1, 2  ✅
```
`let` creates a fresh binding of `i` for each iteration. Each closure captures its own copy.

### Redeclaration
```javascript
var a = 1;
var a = 2; // ✅ fine — no error

let b = 1;
let b = 2; // ❌ SyntaxError: Identifier 'b' has already been declared

const c = 1;
const c = 2; // ❌ SyntaxError
```

### Reassignment & mutation
```javascript
var a = 1;   a = 2;  // ✅
let b = 1;   b = 2;  // ✅
const c = 1; c = 2;  // ❌ TypeError: Assignment to constant variable
```
But `const` doesn't mean immutable — it means the binding can't be reassigned:
```javascript
const user = { name: 'Alice' };
user.name = 'Bob';  // ✅ mutating the object is fine
user = {};          // ❌ reassigning the binding is not
```

### Full comparison table
| | `var` | `let` | `const` |
| :--- | :---: | :---: | :---: |
| **Scope** | function | block | block |
| **Hoisted** | ✅ `undefined` | ✅ TDZ | ✅ TDZ |
| **Redeclarable** | ✅ Yes | ❌ No | ❌ No |
| **Reassignable** | ✅ Yes | ✅ Yes | ❌ No |
| **Global property (top-level)** | ✅ `window.x` | ❌ No | ❌ No |

> [!TIP]
> **The rule going forward:**
> `const` by default
> ↓ only switch to `let` if you need to reassign
> ↓ never use `var` in modern code

---

## 5. Scope Chains

Every execution context has access to its own variables — but also to variables in all its parent environments. The chain of these linked environments is the **scope chain**. When JS can't find a variable locally, it walks up the chain, one level at a time, until it finds it or hits the global scope and throws a `ReferenceError`.

### Lexical scoping — the chain is set at write time
The scope chain is determined by *where you write the function in the code*, not where you call it from. This is called lexical (or static) scoping.

```javascript
const a = 'global';

function outer() {
  const b = 'outer';

  function inner() {
    const c = 'inner';
    console.log(c); // ✅ found locally
    console.log(b); // ✅ found in outer's scope
    console.log(a); // ✅ found in global scope
  }

  inner();
}

outer();
```
The chain for `inner` looks like this:
`inner EC`  →  `outer EC`  →  `Global EC`  →  ❌ `(ReferenceError)`

JS checks each level left to right, stops the moment it finds the variable.

### Call location doesn't matter — write location does
This is where most people get tripped up:
```javascript
const x = 'global';

function getX() {
  console.log(x); // which x?
}

function run() {
  const x = 'local';
  getX(); // called from here — but does it see 'local'?
}

run(); // prints 'global'  ← not 'local'
```
`getX` was written inside the global scope, so its scope chain links to global — not to `run`'s scope. Calling it from inside `run` doesn't change that chain.

### Shadowing — inner wins over outer
```javascript
const msg = 'outer';

function show() {
  const msg = 'inner'; // shadows the outer `msg`
  console.log(msg);    // ✅ 'inner' — found locally, stops here
}

show();
console.log(msg); // ✅ 'outer' — show's `msg` never touched this
```

### The full picture so far
```text
                        ┌─────────────────┐
                        │    Global EC    │  ← a, x, msg, getX, outer...
                        └────────┬────────┘
                                 │ scope chain
                        ┌────────┴────────┐
                        │    outer EC     │  ← b
                        └────────┬────────┘
                                 │ scope chain
                        ┌────────┴────────┐
                        │    inner EC     │  ← c
                        └─────────────────┘
```
Each arrow points to the parent environment. The chain is fixed the moment the function is defined.

**One-line summary:** JS looks for a variable starting in the current scope, then walks up through parent scopes — following the chain set at write time — until it finds it or runs out of scopes.

---

## 6. Closures

A closure is what happens when a function retains access to its lexical scope even after the outer function has finished executing and its execution context has been popped off the call stack.

This isn't a special feature you opt into — it's just how scope chains work. **Every function in JS is a closure.**

### The basic case
```javascript
function makeCounter() {
  let count = 0;        // lives in makeCounter's scope

  return function() {
    count++;            // still accessing count — even after makeCounter returns
    console.log(count);
  };
}

const counter = makeCounter(); // makeCounter's EC is gone
counter(); // 1
counter(); // 2
counter(); // 3
```
`makeCounter` has returned and its EC is off the stack — but `count` is still alive because the inner function holds a reference to the environment where `count` lives. The garbage collector won't clean it up as long as `counter` exists.

### What's actually being "closed over"
The inner function doesn't copy the value of `count` — it holds a live reference to the variable itself. So mutations are reflected:
```javascript
function makeAdder(x) {
  return function(y) {
    return x + y; // x is closed over — not copied
  };
}

const add5 = makeAdder(5);
const add10 = makeAdder(10);

add5(3);  // 8
add10(3); // 13
```
Each call to `makeAdder` creates a fresh scope with its own `x`. `add5` and `add10` close over different environments — they don't share `x`.

### Closures + the var loop bug — now fully explained
You saw this earlier:
```javascript
for (var i = 0; i < 3; i++) {
  setTimeout(() => console.log(i), 100);
}
// 3, 3, 3
```
All three callbacks close over the same `i` — because `var` is function-scoped, there's only one `i` shared across all iterations. By the time they run, it's 3.

With `let`:
```javascript
for (let i = 0; i < 3; i++) {
  setTimeout(() => console.log(i), 100);
}
// 0, 1, 2
```
`let` creates a new binding per iteration — each callback closes over its own separate `i`.

### Practical use: data privacy
Closures are how you create private variables in JS — no `class` needed:
```javascript
function makeWallet(initial) {
  let balance = initial; // private — unreachable from outside

  return {
    deposit(amount)  { balance += amount; },
    withdraw(amount) { balance -= amount; },
    getBalance()     { return balance; }
  };
}

const wallet = makeWallet(100);
wallet.deposit(50);
wallet.getBalance(); // 150
wallet.balance;      // undefined — can't access directly
```

### The mental model
```text
makeCounter() called
│
├── count = 0  created in makeCounter's environment
│
└── inner function returned
        │
        └── carries a backpack 🎒 containing a reference to:
                └── makeCounter's environment (where count lives)
```
`makeCounter`'s EC popped off stack — but environment survives because the inner function's backpack still points to it.

### All 6 topics — how they connect
```text
Execution Context    → the container where code runs
       ↓
Call Stack           → tracks which EC is active
       ↓
Hoisting             → happens inside EC creation phase
       ↓
var / let / const    → differ in scope, TDZ, redeclaration
       ↓
Scope Chain          → how ECs link to parent environments
       ↓
Closures             → functions remembering their scope chain
                       long after the outer EC is gone
```

---

## 🎯 Interview Prep & Challenges

<details>
<summary><b>Q1: Execution Context</b></summary>

What gets created before any code runs when JS encounters this file?

```javascript
const x = 10;

function greet(name) {
  const msg = 'Hello ' + name;
  return msg;
}

greet('Alice');
```

What ECs are created, in what order, and what does each contain in the creation phase?

**Answer:**

**Execution Contexts created in order:**

1. **Global Execution Context (GEC)**
   - Created when the file starts.
   - **Creation Phase:**
     - `x` → hoisted and uninitialized (TDZ).
     - `greet` → entire function object stored in memory.
   - **Execution Phase:**
     - `x` becomes 10.
     - `greet('Alice')` is invoked.

2. **Function Execution Context (FEC) for `greet`**
   - Created when `greet('Alice')` is called.
   - **Creation Phase:**
     - Parameter `name` initialized immediately with `"Alice"`. *(Note: `name` is a parameter binding, not "hoisted" in the traditional sense like body declarations)*.
     - `msg` hoisted but uninitialized (TDZ).
   - **Execution Phase:**
     - `msg` becomes `"Hello Alice"`.
     - Function returns `"Hello Alice"`.

After the function returns, the Function Execution Context is destroyed, leaving only the Global Execution Context.
</details>

<details>
<summary><b>Q2: Call Stack</b></summary>

What does the call stack look like at the moment `multiply` is executing? And what order do things get popped?

```javascript
function multiply(a, b) {
  return a * b;
}

function square(n) {
  return multiply(n, n);
}

function printSquare(n) {
  const result = square(n);
  console.log(result);
}

printSquare(3);
```

**Answer:**

**Deepest Point of the Stack**
This is the moment when `multiply` is executing, which is the maximum stack depth:

```text
┌─────────────────┐
│ multiply EC     │  a=3, b=3
├─────────────────┤
│ square EC       │  n=3
├─────────────────┤
│ printSquare EC  │  n=3
├─────────────────┤
│ Global EC       │
└─────────────────┘
```

**Return Phase (Popping Order)**
Because the call stack follows **LIFO (Last In, First Out)**:
1. `multiply EC`  ← popped first
2. `square EC`
3. `printSquare EC`
4. `Global EC` (when program ends)

The contexts are popped in this order:
`multiply` → `square` → `printSquare` → `Global`
</details>

<details>
<summary><b>Q3: Hoisting</b></summary>

What does this print? Don't run it — reason through it.

```javascript
console.log(a);
console.log(b);
console.log(c);

var a = 1;
let b = 2;

function c() {
  return 3;
}
```

**Answer:**

**Trick Question 🚨**
Execution actually halts at `console.log(b)`.

1. **First Line:** `console.log(a);`
   - Output: `undefined` (because `var` is hoisted and initialized with `undefined`).
2. **Second Line:** `console.log(b);`
   - Output: `ReferenceError: Cannot access 'b' before initialization`. `let` is hoisted but stays in the Temporal Dead Zone (TDZ).
3. **Third Line:** `console.log(c);`
   - This line is **never reached**. JavaScript does not continue after an uncaught error.

*If `console.log(b)` were removed:*
The output would be:
```text
undefined
[Function: c]
```
Because function declarations are fully hoisted and initialized as the entire function object.
</details>

<details>
<summary><b>Q4: var vs let vs const</b></summary>

What does this print, and why?

```javascript
function test() {
  console.log(i);

  for (var i = 0; i < 3; i++) {
    // nothing
  }

  console.log(i);
}

test();
```

**Answer:**

**Original Code (var)**
Output:
```text
undefined
3
```
Because `var` is function-scoped and hoisted with an initial value of `undefined`. The loop updates the same variable, leaving its final value as `3`.

**If you replace var with let:**
Output:
```text
ReferenceError: i is not defined
```
Because `let` is block-scoped. The variable `i` exists only inside the `for` loop block and cannot be accessed before or after the loop.

*Important:* With `let`, the error is "i is not defined" (not "cannot access before initialization") because `let i` never existed in the outer scope at all. Two different errors, two different causes!
</details>

<details>
<summary><b>Q5: Closures (the hardest one)</b></summary>

What does this print? Reason through it carefully. Then explain: after `makeMultiplier(2)` returns, is `x` garbage collected? Why or why not?

```javascript
function makeMultiplier(x) {
  return function(y) {
    return x * y;
  };
}

const double = makeMultiplier(2);
const triple = makeMultiplier(3);

double(5);
triple(5);
triple(double(4));
```

**Answer:**

**Final Results:**
```javascript
double(5);          // 10
triple(5);          // 15
triple(double(4));  // 24
```

**Is `x` garbage collected?**
❌ **No.**

Normally, when a function finishes, its Function Execution Context is removed from the Call Stack, and its local variables become eligible for Garbage Collection (GC).

However, in this case, the returned function still uses `return x * y;`. Therefore, JavaScript keeps the outer lexical environment alive. 

Conceptually:
```text
double
   ↓
Function
   ↓
Closure
   ↓
{x : 2}
```
Since `double` still references `x`, GC cannot remove it.

**When can x be garbage collected?**
Only when no references remain. If you later do:
`double = null;`
There are no more references to the closure, so the Garbage Collector can reclaim the memory.
</details>

---
<div align="center">
  <i>Happy Coding! Keep climbing the JavaScript learning curve. 🧗‍♂️</i>
</div>