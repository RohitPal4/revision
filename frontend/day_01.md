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

Every time JavaScript runs, it needs a place to keep track of variables, `this`, and executing code. That container is the **Execution Context (EC)**.

### The Two Phases
1. **Phase 1 — Creation Phase**
   - Scans the code.
   - Allocates memory for variables and functions.
   - Sets up the scope chain and determines `this`.
2. **Phase 2 — Execution Phase**
   - Code runs line by line.
   - Variables get assigned their actual values.

### Types of EC
- **Global EC**: Created once when the script loads. In browsers, `this = window`.
- **Function EC**: Created *every time* a function is called (not when it is defined).

> [!NOTE]
> **Inside an Execution Context:**
> - **Variable Environment**: Where `var` declarations live.
> - **Lexical Environment**: Where `let`, `const`, and `function` declarations live.
> - **`this` Binding**: Depends on how the function was called.

---

## 2. Call Stack

The Call Stack tracks which execution context is currently active. It follows the **LIFO (Last In, First Out)** principle.

> [!TIP]
> **Simple Rule**: EC Created → Pushed to stack. EC Finished → Popped off stack.

```javascript
function multiply(a, b) {
  return a * b;           // 3️⃣ runs here
}

function square(n) {
  return multiply(n, n);  // 2️⃣ calls multiply
}

square(4);                // 1️⃣ starts here
```

> [!WARNING]
> **Stack Overflow** occurs when you have infinite recursion. The call stack runs out of memory because contexts keep getting pushed but never popped!

---

## 3. Hoisting

Before code runs (during the Creation Phase), JS scans the file and allocates memory. It *feels* like variables and functions "move to the top," but nothing physically moves.

| Concept | Hoisted? | Initialized? | Usable before declaration? |
| :--- | :---: | :---: | :--- |
| `var` | ✅ Yes | `undefined` | ✅ Yes (gives `undefined`) |
| `let` / `const` | ✅ Yes | ❌ No (TDZ) | ❌ `ReferenceError` |
| `function` | ✅ Yes | ✅ Full body | ✅ Yes |
| `const myFunc = () => {}`| ✅ Yes | ❌ No (TDZ) | ❌ `ReferenceError` |

> [!IMPORTANT]
> **The Temporal Dead Zone (TDZ):** `let` and `const` *are* hoisted, but they sit in the TDZ until their actual line of code executes. Accessing them inside the TDZ throws a `ReferenceError`.

---

## 4. var vs let vs const

Never blur them together again. 

| Feature | `var` | `let` | `const` |
| :--- | :---: | :---: | :---: |
| **Scope** | Function-scoped | Block-scoped (`{}`) | Block-scoped (`{}`) |
| **Hoisted?** | ✅ (`undefined`) | ✅ (TDZ) | ✅ (TDZ) |
| **Redeclarable?** | ✅ Yes | ❌ No | ❌ No |
| **Reassignable?** | ✅ Yes | ✅ Yes | ❌ No |

### The Classic Loop Trap
```javascript
// ❌ Using var leaks the variable globally!
for (var i = 0; i < 3; i++) {
  setTimeout(() => console.log(i), 100); // Prints: 3, 3, 3
}

// ✅ Using let creates a fresh binding per iteration
for (let i = 0; i < 3; i++) {
  setTimeout(() => console.log(i), 100); // Prints: 0, 1, 2
}
```

---

## 5. Scope Chains

When JS can't find a variable locally, it walks up the **Scope Chain**, one level at a time, until it hits the Global Scope.

- **Lexical Scoping:** The scope chain is determined by *where you write the code*, not where the function is called!
- **Shadowing:** An inner variable will block access to an outer variable with the same name.

```javascript
const msg = 'outer';

function show() {
  const msg = 'inner'; // Shadows the outer `msg`
  console.log(msg);    // ✅ 'inner'
}

show();
console.log(msg);      // ✅ 'outer'
```

---

## 6. Closures

A **closure** is what happens when a function retains access to its lexical scope *even after the outer function has finished executing*.

> [!NOTE]
> Every function in JavaScript is technically a closure. It's not a special feature you opt into—it's just how scope chains work.

### Practical Use: Data Privacy
```javascript
function makeWallet(initial) {
  let balance = initial; // Private variable

  return {
    deposit(amount)  { balance += amount; },
    withdraw(amount) { balance -= amount; },
    getBalance()     { return balance; }
  };
}

const wallet = makeWallet(100);
wallet.deposit(50);
console.log(wallet.getBalance()); // 150
console.log(wallet.balance);      // undefined (Private!)
```

---

## 🎯 Interview Prep & Challenges

<details>
<summary><b>Q1: What gets created before any code runs when JS encounters a file?</b></summary>
<br/>

**Answer:**
The **Global Execution Context (GEC)** is created.
During the **Creation Phase**:
- Memory is allocated for variables (hoisted).
- Function declarations are fully loaded into memory.
</details>

<details>
<summary><b>Q2: What is the output of the following code and why?</b></summary>
<br/>

```javascript
console.log(a);
console.log(b);
var a = 1;
let b = 2;
```

**Answer:**
1. `console.log(a)` prints `undefined` because `var` is hoisted and initialized with `undefined`.
2. `console.log(b)` throws a `ReferenceError` because `let` is in the Temporal Dead Zone (TDZ). Execution stops completely at this error.
</details>

<details>
<summary><b>Q3: Explain the `var` loop issue and how `let` fixes it.</b></summary>
<br/>

**Answer:**
When using `var` inside a loop with an asynchronous callback (like `setTimeout`), `var` is function-scoped. There is only *one* shared `i` variable. By the time the async callbacks run, the loop has already finished, and they all read the final value of `i`.

Using `let` fixes this because `let` is block-scoped. It creates a brand-new, separate binding of `i` for *every single iteration* of the loop, meaning each callback closes over its own unique value.
</details>

<details>
<summary><b>Q4: After `const double = makeMultiplier(2)` returns, is the variable garbage collected?</b></summary>
<br/>

**Answer:**
**❌ No, it is not garbage collected.**

Because the inner function returned by `makeMultiplier(2)` still references the outer variables, a **closure** is formed. The JavaScript engine keeps the outer lexical environment alive in memory as long as the returned `double` function still exists. Memory is only reclaimed once `double` is no longer referenced (e.g., set to `null`).
</details>

---
<div align="center">
  <i>Happy Coding! Keep climbing the JavaScript learning curve. 🧗‍♂️</i>
</div>