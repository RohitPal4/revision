<div align="center">
  <h1>🚀 JavaScript Advanced Concepts: Day 02</h1>
  <p><i>Deep dive into Functional JS, Scoping, Prototype Chains, and ES6 Classes.</i></p>
</div>

---

## 📑 Table of Contents
- [1. Closures (Deeper)](#1-closures-deeper)
- [2. Lexical vs Dynamic Scoping](#2-lexical-vs-dynamic-scoping)
- [3. Function.prototype & Prototype Chain](#3-functionprototype--prototype-chain)
- [4. Object.create() vs new](#4-objectcreate-vs-new)
- [5. hasOwnProperty vs Inherited Properties](#5-hasownproperty-vs-inherited-properties)
- [6. class as Syntactic Sugar](#6-class-as-syntactic-sugar)
- [🎯 Interview Prep & Challenges](#-interview-prep--challenges)

---

## 1. Closures (Deeper)

You already know the definition of a closure from Day 1. Today we go deeper—looking at practical patterns built entirely on closures.

### Pattern 1 — Factory Functions
A factory is a function that returns a new object with private state.

```javascript
function makeUser(name, role) {
  let loginCount = 0; // private — no way to access directly

  return {
    getName: () => name,
    getRole: () => role,
    login() {
      loginCount++;
      console.log(`${name} logged in. Total: ${loginCount}`);
    },
    getLoginCount: () => loginCount
  };
}

const alice = makeUser('Alice', 'admin');
const bob   = makeUser('Bob', 'viewer');

alice.login(); // Alice logged in. Total: 1
alice.login(); // Alice logged in. Total: 2
bob.login();   // Bob logged in. Total: 1

console.log(alice.loginCount); // undefined — truly private
```
Each call to `makeUser` creates a fresh closure with its own `loginCount`. `alice` and `bob` don't share state.

### Pattern 2 — Memoization
Closures let a function remember previous results across multiple calls.

```javascript
function memoize(fn) {
  const cache = {}; // closed over — persists across calls

  return function(n) {
    if (cache[n] !== undefined) {
      console.log('from cache');
      return cache[n];
    }
    cache[n] = fn(n);
    return cache[n];
  };
}

const slowSquare = n => n * n;
const fastSquare = memoize(slowSquare);

fastSquare(4); // computes → 16
fastSquare(4); // from cache → 16
```
`cache` lives in `memoize`'s scope. The returned function closes over it, reading and writing across every call.

### Pattern 3 — Partial Application
```javascript
function multiply(a, b) {
  return a * b;
}

function partial(fn, firstArg) {
  return function(secondArg) {
    return fn(firstArg, secondArg); // firstArg closed over
  };
}

const double = partial(multiply, 2);
const triple = partial(multiply, 3);

double(5); // 10
triple(5); // 15
```
`firstArg` is baked in. The returned function only needs the second argument. This is how libraries like Lodash implement `_.partial`.

> [!WARNING]
> **The one thing to remember:**
> A closure doesn't snapshot the value — it holds a **live reference** to the variable.
> ```javascript
> function makeCounter() {
>   let n = 0;
>   return {
>     increment: () => ++n,
>     decrement: () => --n,
>     value:     () => n
>   };
> }
> const c = makeCounter();
> c.increment(); // 1
> c.value();     // 1 — all methods share the same live `n`
> ```
> All three methods close over the same `n` — mutations from one are visible to all.

---

## 2. Lexical vs Dynamic Scoping

This is the rule that makes closures predictable. JavaScript uses **lexical scoping**, but understanding why requires knowing what the alternative looks like.

### Lexical Scoping — Scope set at write time
The scope chain is determined by *where the function is defined* in the source code, not where it's called from.

```javascript
const x = 'global';

function outer() {
  const x = 'outer';
  
  function inner() {
    console.log(x); // which x?
  }
  return inner;
}

const fn = outer();
fn(); // 'outer' — not 'global'
```
`inner` was written inside `outer`, so it closes over `outer`'s `x`. It doesn't matter that `fn()` is called from the global scope. The chain was fixed at write time.

### What dynamic scoping would look like (Not JS)
Dynamic scoping means the scope chain follows the *call stack*. JS doesn't do this, but here's the contrast:

```javascript
const x = 'global';

function printX() {
  console.log(x);
}

function run() {
  const x = 'run';
  printX(); // called from here
}

run();
```
| Scoping rule | Result | Why |
| :--- | :--- | :--- |
| **Lexical (JS)** | `'global'` | `printX` written in global scope → sees global `x` |
| **Dynamic (not JS)** | `'run'` | `printX` called from `run` → would see `run`'s `x` |

### The Practical Implication: Variables are Lexical, `this` is Dynamic
Here's where it gets interesting. JS has one thing that behaves dynamically — `this`. Variables follow lexical rules, but `this` follows call-site rules.

```javascript
const user = {
  name: 'Alice',

  greetLexical: function() {
    const getName = () => this.name; // arrow: lexical this
    return getName();
  },

  greetDynamic: function() {
    function getName() { return this.name; } // regular: dynamic this
    return getName();
  }
};

user.greetLexical(); // 'Alice' — arrow inherits this from greetLexical's call site
user.greetDynamic(); // undefined — getName() called without context, this = undefined
```

> [!TIP]
> **One rule to remember:**
> - **Variables**: Look at where the function was *written*.
> - **`this`**: Look at how the function was *called*.
> 
> Arrow functions collapse both into one rule: **always lexical**.

---

## 3. Function.prototype & Prototype Chain

Every object in JS has a hidden link to another object called its prototype. When you access a property that doesn't exist on the object itself, JS follows that link—and keeps following it—until it finds the property or hits `null`. That chain of links is the **prototype chain**.

### The hidden link — `__proto__`
```javascript
const dog = { name: 'Rex' };

console.log(dog.name);       // 'Rex' — own property
console.log(dog.toString()); // '[object Object]' — where did this come from?
```
`dog` doesn't have `toString`. JS looks at `dog.__proto__` — which points to `Object.prototype` — and finds it there.

```text
dog
 │
 └── __proto__ → Object.prototype
                   ├── toString()
                   ├── hasOwnProperty()
                   └── __proto__ → null  ← chain ends here
```

### Functions have their own prototype chain
Every function has two things people confuse:

| What it is | Used for |
| :--- | :--- |
| `fn.__proto__` | Link to `Function.prototype`. Gives `fn` methods like `.call`, `.bind`, `.apply`. |
| `fn.prototype` | An object attached to `fn`. Becomes the `__proto__` of objects created with `new fn()`. |

### What `new` actually does
```javascript
function Animal(name) { this.name = name; }
const cat = new Animal('Cat');
```
Under the hood, `new` does exactly four things:
1. Creates a blank object: `const obj = {};`
2. Links it to the constructor's prototype: `obj.__proto__ = Animal.prototype;`
3. Runs the constructor with `this` = `obj`: `Animal.call(obj, 'Cat');`
4. Returns `obj`.

### The one thing people get wrong with Inheritance
```javascript
// ❌ this breaks the chain
Car.prototype = Vehicle.prototype;
// Now Car and Vehicle share the SAME prototype object.
// Adding to Car.prototype also adds to Vehicle.prototype!

// ✅ this creates a proper link
Car.prototype = Object.create(Vehicle.prototype);
// Creates a NEW object whose __proto__ is Vehicle.prototype.
```

---

## 4. Object.create() vs new

You already know what `new` does. `Object.create()` is a lower-level tool that sets up the prototype link *directly*, without a constructor function.

### Pure prototype linking
```javascript
const animal = {
  speak() { console.log(`${this.name} makes a sound`); }
};

const dog = Object.create(animal); // dog.__proto__ = animal
dog.name = 'Rex';
dog.speak(); // 'Rex makes a sound' — found on animal (the prototype)
```

### Key Differences
| Feature | `new Constructor()` | `Object.create(proto)` |
| :--- | :---: | :---: |
| **Needs a constructor function?** | ✅ Yes | ❌ No |
| **Sets `__proto__` to...** | `Fn.prototype` | Whatever you pass |
| **Runs initialization code?** | ✅ Constructor body | ❌ Do it manually |
| **Returns new object?** | ✅ Automatically | ✅ Automatically |
| **Pass `null` for NO prototype?**| ❌ No | ✅ `Object.create(null)` |

> [!NOTE]
> **`Object.create(null)`** creates a truly empty object. It has no inherited noise. No `toString`, no `hasOwnProperty`. The chain is just `plain -> null`.

---

## 5. hasOwnProperty vs Inherited Properties

Every property lookup walks the prototype chain. But sometimes you need to know: did this object define this property *itself*, or did it inherit it?

```javascript
function Animal(name) { this.name = name; }
Animal.prototype.speak = function() {};

const dog = new Animal('Rex');

dog.hasOwnProperty('name');  // true  — lives directly on dog
dog.hasOwnProperty('speak'); // false — lives on Animal.prototype
```

### The `for...in` trap
`for...in` iterates ALL enumerable properties — own AND inherited.
```javascript
for (const key in dog) {
  console.log(key); // Prints both 'name' and any inherited enumerable properties!
}
```
**The fix:** Use `Object.keys(dog)` which never walks the chain. It strictly returns own enumerable properties.

### Safe hasOwnProperty
What if someone creates an object with `Object.create(null)`? It has no prototype, so `hasOwnProperty` doesn't exist on it!

**The safe pattern (ES2022):**
```javascript
const obj = Object.create(null);
obj.name = 'Alice';

Object.hasOwn(obj, 'name'); // ✅ true
```

### Cheat Sheet
| Method | Own? | Inherited? | Non-enumerable? |
| :--- | :---: | :---: | :---: |
| `hasOwnProperty` / `hasOwn` | ✅ | ❌ | ✅ |
| `Object.keys()` | ✅ | ❌ | ❌ |
| `Object.getOwnPropertyNames()` | ✅ | ❌ | ✅ |
| `in` operator | ✅ | ✅ | ✅ |
| `for...in` | ✅ | ✅ | ❌ |

---

## 6. class as Syntactic Sugar

`class` was introduced in ES6. It looks like classical inheritance from Java or Python — but it's not. Under the hood, it's still prototype chains, constructor functions, and `Object.create`.

### Identical Behavior, Different Syntax
```javascript
// Pre-ES6 Style
function Animal(name) { this.name = name; }
Animal.prototype.speak = function() { console.log('Sound'); };

// ES6 Class Style
class Animal {
  constructor(name) { this.name = name; }
  speak() { console.log('Sound'); }
}
```
These produce **identical prototype chains**. `speak` still lives on `Animal.prototype`, not on each instance.

### `extends` and `super`
```javascript
class Dog extends Animal {
  constructor(name, breed) {
    super(name);        // compiles to: Animal.call(this, name)
    this.breed = breed;
  }
}
```
- `extends` does the `Object.create` chain linking.
- `super()` executes the parent constructor.

### What `class` does differently (3 Real Differences)
1. **Not Hoisted:** Classes sit in the TDZ (Temporal Dead Zone) just like `let`. You cannot call `new Dog()` before the `class Dog {}` definition.
2. **Always Strict Mode:** Inside a class body, code runs in strict mode automatically.
3. **Cannot be called without `new`:** Calling a class as a regular function `Dog()` throws an error.

---

## 🎯 Interview Prep & Challenges

<details>
<summary><b>Q1: Closures and Garbage Collection</b></summary>
<br/>

What does this print? Do `add5` and `add10` share the same `x`?
```javascript
function makeAdder(x) {
  return function(y) {
    return x + y;
  };
}

const add5 = makeAdder(5);
const add10 = makeAdder(10);

console.log(add5(3));
console.log(add10(3));
console.log(add5(add10(2)));
```

**Answer:**
Output:
```text
8
13
17
```

**Do they share the same `x`?**
❌ **No.** Each call to `makeAdder()` creates a completely new execution context and a new lexical environment. The returned function forms a closure over that *specific* environment. 

Visualization:
```text
add5
  ↓
Closure A
  ↓
x = 5

add10
  ↓
Closure B
  ↓
x = 10
```
These closures are 100% independent.
</details>

<details>
<summary><b>Q2: Lexical Scoping Lookup</b></summary>
<br/>

What does this print? Why doesn't `fn()` see `runner`'s `lang`, even though it's called from inside `runner`?
```javascript
const lang = 'global';

function outer() {
  const lang = 'outer';

  function inner() {
    console.log(lang);
  }

  return inner;
}

function runner() {
  const lang = 'runner';
  const fn = outer();
  fn();
}

runner();
```

**Answer:**
Output:
```text
outer
```

**Why doesn't `fn()` see `runner`'s `lang`?**
Because JavaScript uses **Lexical (Static) Scoping**. Variables are determined by where a function is *defined*, not where it is *called*.

`inner` was created inside `outer`. Therefore its scope chain is:
`inner` → `outer` → `global`

When `fn()` (which is `inner`) executes, it searches its scope chain. It looks in `inner` (not found), then looks in `outer` (found `"outer"`). It never looks inside `runner` because the scope chain is fixed at write time.
</details>

<details>
<summary><b>Q3: Trace the Prototype Chain</b></summary>
<br/>

What does this print? Trace every property lookup.
```javascript
function Person(name) { this.name = name; }
Person.prototype.greet = function() { return `Hi, I'm ${this.name}`; };

function Developer(name, lang) {
  Person.call(this, name);
  this.lang = lang;
}

Developer.prototype = Object.create(Person.prototype);
Developer.prototype.constructor = Developer;
Developer.prototype.code = function() { return `${this.name} codes in ${this.lang}`; };

const dev = new Developer('Alice', 'JavaScript');

console.log(dev.name);
console.log(dev.code());
console.log(dev.greet());
console.log(dev.hasOwnProperty('greet'));
console.log(dev instanceof Person);
```

**Answer:**
Output:
```text
Alice
Alice codes in JavaScript
Hi, I'm Alice
false
true
```

**The Prototype Chain:**
```text
dev
│
├── name = "Alice"
├── lang = "JavaScript"
│
▼ [[Prototype]]
Developer.prototype
│
├── constructor
├── code()
│
▼ [[Prototype]]
Person.prototype
│
├── greet()
│
▼ [[Prototype]]
Object.prototype
│
├── hasOwnProperty()
│
▼
null
```

**Property Lookups:**
- `dev.name`: Found directly on `dev` (own property).
- `dev.code()`: Not on `dev`. Found on `Developer.prototype`.
- `dev.greet()`: Not on `dev` or `Developer.prototype`. Found on `Person.prototype`.
- `dev.hasOwnProperty('greet')`: Looks up the chain to `Object.prototype` to find the method `hasOwnProperty`. Executes it to check if `dev` *itself* has `greet`. Returns `false`.
- `dev instanceof Person`: Checks if `Person.prototype` exists anywhere in `dev`'s prototype chain. It does, so it returns `true`.
</details>

<details>
<summary><b>Q4: Object.create() vs new</b></summary>
<br/>

What is the difference between these two approaches, and what does `instanceof User` return for each?
```javascript
function User(name) { this.name = name; }
User.prototype.sayHi = function() { return `Hi, I'm ${this.name}`; };

// Approach A
const a = new User('Alice');

// Approach B
const proto = { sayHi() { return `Hi, I'm ${this.name}`; } };
const b = Object.create(proto);
b.name = 'Bob';
```

**Answer:**

**Prototype Chains:**
```text
a → User.prototype → Object.prototype → null
b → proto → Object.prototype → null
```

**instanceof Checks:**
- `a instanceof User` → **`true`** (Because `User.prototype` is in `a`'s prototype chain).
- `b instanceof User` → **`false`** (Because `User.prototype` is NOT in `b`'s prototype chain. `b` inherits directly from `proto`).

Both `a.hasOwnProperty('sayHi')` and `b.hasOwnProperty('sayHi')` return `false` because `sayHi` is an inherited property in both cases.
</details>

<details>
<summary><b>Q5: ES6 class internals</b></summary>
<br/>

In the following class definition, what do `extends` and `super(name)` actually compile down to in pre-ES6 terms?
```javascript
class Animal {}
class Dog extends Animal {
  constructor(name, breed) {
    super(name);
    this.breed = breed;
  }
}
```

**Answer:**

**1. What does `extends` compile down to?**
It links the prototype chains. Roughly equivalent to:
```javascript
Dog.prototype = Object.create(Animal.prototype);
Dog.prototype.constructor = Dog;
```

**2. What does `super(name)` compile down to?**
It calls the parent constructor inside the current context. Roughly equivalent to:
```javascript
Animal.call(this, name);
```

**3. What are the 3 real differences between `class` and constructor functions?**
1. **Hoisting:** Function declarations are hoisted. Classes are NOT hoisted (they sit in the Temporal Dead Zone).
2. **Strict Mode:** Code inside a `class` body automatically runs in strict mode.
3. **Execution Context:** Classes throw a `TypeError` if you try to invoke them without the `new` keyword. Constructor functions can accidentally be invoked without `new` (polluting the global object).
</details>

---
<div align="center">
  <i>Happy Coding! Keep climbing the JavaScript learning curve. 🧗‍♂️</i>
</div>
