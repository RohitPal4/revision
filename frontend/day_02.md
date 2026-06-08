<div align="center">
  <h1>🚀 Frontend Day 02: Functional JS & Prototypes</h1>
  <p><i>Closures, Lexical Scoping, Prototype Chains, and Class Syntactic Sugar</i></p>
</div>

---

## 📑 Topics Covered
1. [Closures (deeper than yesterday)](#1-closures-deeper-than-yesterday)
2. [Lexical Scoping vs Dynamic Scoping](#2-lexical-scoping-vs-dynamic-scoping)
3. [Function.prototype and the Prototype Chain](#3-functionprototype-and-the-prototype-chain)
4. [Object.create() vs new](#4-objectcreate-vs-new)
5. [hasOwnProperty vs inherited properties](#5-hasownproperty-vs-inherited-properties)
6. [class as syntactic sugar](#6-class-as-syntactic-sugar)

---

## 1. Closures (deeper than yesterday)

You already know the definition. Today we go deeper — practical patterns built on closures.

<details>
<summary><b>View Practical Closure Patterns</b></summary>
<br/>

### Pattern 1 — Factory functions
A factory is a function that returns a new object with private state:
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

alice.loginCount; // undefined — truly private
```
Each call to `makeUser` creates a fresh closure with its own `loginCount`. `alice` and `bob` don't share state.

### Pattern 2 — Memoization
Closures let a function remember previous results:
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
fastSquare(5); // computes → 25
```
`cache` lives in `memoize`'s scope. The returned function closes over it — reading and writing across every call.

### Pattern 3 — Partial application
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

> [!IMPORTANT]
> **The one thing to remember:** A closure doesn't snapshot the value — it holds a **live reference** to the variable.
> ```javascript
> function makeCounter() {
>   let n = 0;
>   return {
>     increment: () => ++n,
>     decrement: () => --n,
>     value:     () => n
>   };
> }
> 
> const c = makeCounter();
> c.increment(); // 1
> c.increment(); // 2
> c.decrement(); // 1
> c.value();     // 1 — all three methods share the same live `n`
> ```
> All three methods close over the same `n` — mutations from one are visible to all.

</details>

---

## 2. Lexical Scoping vs Dynamic Scoping

This is the rule that makes closures predictable. JavaScript uses **lexical scoping** — but understanding why requires knowing what the alternative looks like.

<details>
<summary><b>View Scoping Deep Dive</b></summary>
<br/>

### Lexical scoping — scope set at write time
The scope chain is determined by **where the function is defined** in the source code, not where it's called from.
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
Dynamic scoping means the scope chain follows the call stack — the function uses variables from wherever it was called. JS doesn't do this, but here's the contrast:
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
| **Dynamic** | `'run'` | `printX` called from `run` → would see `run`'s `x` |

JS always gives you `'global'` here. The call location is irrelevant.

### The practical implication — `this` is dynamic, variables are lexical
Here's where it gets interesting. JS has one thing that behaves dynamically — `this`. Variables follow lexical rules. `this` follows call-site rules.
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
Arrow functions fix `this` lexically — they don't get their own `this`, they inherit it from the surrounding scope at write time. Regular functions get `this` determined at call time.

### Visualizing the difference
```text
LEXICAL (variables in JS)
─────────────────────────
Source code structure defines the chain:

  global
  └── outer()
      └── inner()   ← inner sees outer's vars, always

DYNAMIC (how `this` works in JS)
─────────────────────────────────
Call stack at runtime defines the context:

  run() calls printX()
  → this inside printX = whatever called it
```

> [!NOTE]
> **One rule to remember:**
> - **Variables** — look at where the function was *written*.
> - **`this`** — look at how the function was *called*.
> - **Arrow functions** collapse both into one rule: *always lexical*.

</details>

---

## 3. Function.prototype and the Prototype Chain

Every object in JS has a hidden link to another object called its prototype. When you access a property that doesn't exist on the object itself, JS follows that link — and keeps following it — until it finds the property or hits `null`. That chain of links is the prototype chain.

<details>
<summary><b>View Prototype Deep Dive</b></summary>
<br/>

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
                   ├── valueOf()
                   └── __proto__ → null  ← chain ends here
```

### Functions have their own prototype chain
Every function has two things people confuse:
| Property | Used for |
| :--- | :--- |
| `fn.__proto__` | link to `Function.prototype` (gives fn methods like `.call`, `.bind`, `.apply`) |
| `fn.prototype` | an object attached to `fn` (becomes `__proto__` of objects created with `new fn()`) |

```javascript
function greet() {}
greet.__proto__ === Function.prototype // true — greet IS a function object
greet.prototype                        // { constructor: greet } — blueprint for instances
```

### What happens with constructor functions
```javascript
function Animal(name) {
  this.name = name;
}

Animal.prototype.speak = function() {
  console.log(`${this.name} makes a sound`);
};

const cat = new Animal('Cat');

cat.name;    // 'Cat'    — own property (set by constructor)
cat.speak(); // 'Cat makes a sound' — found on Animal.prototype
```
The chain for `cat`:
```text
cat
 │  name: 'Cat'
 │
 └── __proto__ → Animal.prototype
                   ├── speak()
                   └── __proto__ → Object.prototype
                                     ├── toString()
                                     └── __proto__ → null
```

### What `new` actually does
Under the hood, `new` does exactly four things:
```javascript
// 1. creates a blank object
const obj = {};

// 2. links it to Animal.prototype
obj.__proto__ = Animal.prototype;

// 3. runs the constructor with `this` = obj
Animal.call(obj, 'Cat');

// 4. returns obj
return obj;
```

### The one thing people get wrong
```javascript
// ❌ this breaks the chain
Car.prototype = Vehicle.prototype;
// now Car and Vehicle share the same prototype object!

// ✅ this creates a proper link
Car.prototype = Object.create(Vehicle.prototype);
// creates a new object whose __proto__ is Vehicle.prototype
```

</details>

---

## 4. Object.create() vs new

You already know what `new` does under the hood. Now meet `Object.create()` — a lower-level tool that sets up the prototype link directly, without a constructor function.

<details>
<summary><b>View Object.create() Deep Dive</b></summary>
<br/>

### Object.create() — pure prototype linking
```javascript
const animal = {
  speak() {
    console.log(`${this.name} makes a sound`);
  }
};

const dog = Object.create(animal); // dog.__proto__ = animal
dog.name = 'Rex';

dog.speak(); // 'Rex makes a sound' — found on animal (the prototype)
```
`Object.create(animal)` creates a blank object whose `__proto__` is set to `animal`. No constructor, no `new`, no prototype property involved.

### Key differences
| Feature | `new` | `Object.create()` |
| :--- | :--- | :--- |
| Needs a constructor function | ✅ yes | ❌ no |
| Sets `__proto__` | ✅ to Fn.prototype | ✅ to whatever you pass |
| Runs initialization code | ✅ constructor body | ❌ you do it manually |
| Returns new object | ✅ automatically | ✅ automatically |
| Pass null for no prototype | ❌ | ✅ `Object.create(null)` |

### Object.create(null) — a truly empty object
```javascript
const plain = Object.create(null);

plain.name = 'Alice';
plain.toString; // undefined — no Object.prototype in the chain!
```
Useful when you want a pure key-value store with zero inherited noise. No `toString`, no `hasOwnProperty`, nothing.

> [!WARNING]
> **The wrong way to inherit — and why it breaks**
> ```javascript
> // ❌ common mistake
> Car.prototype = new Vehicle();
> ```
> This runs `Vehicle`'s constructor during setup, before you have any arguments to pass. If `Vehicle` has side effects or required params, this breaks. `Object.create()` links the prototype chain without executing any constructor.

</details>

---

## 5. hasOwnProperty vs Inherited Properties

Every property lookup in JS walks the prototype chain. But sometimes you need to know: did this object define this property itself, or did it inherit it? That's exactly what `hasOwnProperty` answers.

<details>
<summary><b>View Properties Deep Dive</b></summary>
<br/>

### The difference
```javascript
function Animal(name) { this.name = name; }
Animal.prototype.speak = function() { console.log(`${this.name} makes a sound`); };

const dog = new Animal('Rex');

dog.name;  // 'Rex'   — own property
dog.speak; // [Function] — inherited from Animal.prototype

dog.hasOwnProperty('name');  // true  — lives directly on dog
dog.hasOwnProperty('speak'); // false — lives on Animal.prototype
```

### Why it matters — the `for...in` trap
`for...in` iterates **all** enumerable properties — own and inherited.
```javascript
for (const key in dog) {
  if (dog.hasOwnProperty(key)) {
    console.log(key); // 'name' only, skips inherited 'type'
  }
}
```

### `Object.keys()` vs `for...in`
If you just want own enumerable properties, skip the guard entirely:
```javascript
Object.keys(dog);   // ['name'] — own enumerable only
```
`Object.keys` never walks the chain. It's the clean default.

### Cheat sheet
| Method | Own? | Inherited? | Non-enumerable? |
| :--- | :---: | :---: | :---: |
| `hasOwnProperty` | ✅ | ❌ | ✅ |
| `Object.keys()` | ✅ | ❌ | ❌ |
| `Object.getOwnPropertyNames()` | ✅ | ❌ | ✅ |
| `in` operator | ✅ | ✅ | ✅ |
| `for...in` | ✅ | ✅ | ❌ |

</details>

---

## 6. class as Syntactic Sugar

`class` was introduced in ES6. It looks like classical inheritance from Java or Python — but it's not. Under the hood it's still prototype chains, constructor functions, and `Object.create`. The keyword just makes it look cleaner.

<details>
<summary><b>View Class Syntax Deep Dive</b></summary>
<br/>

### Side by side — identical behavior, different syntax
**Pre-ES6 prototype style:**
```javascript
function Animal(name) { this.name = name; }
Animal.prototype.speak = function() { console.log(`${this.name} makes a sound`); };
```
**ES6 class style:**
```javascript
class Animal {
  constructor(name) {
    this.name = name;
  }
  speak() {
    console.log(`${this.name} makes a sound`);
  }
}
```
These produce identical prototype chains. `speak` still lives on `Animal.prototype`, not on each instance.

### `extends` and `super`
**Pre-ES6:**
```javascript
function Dog(name, breed) {
  Animal.call(this, name);   // borrow constructor
  this.breed = breed;
}
Dog.prototype = Object.create(Animal.prototype); // link chain
Dog.prototype.constructor = Dog;
```
**ES6 class:**
```javascript
class Dog extends Animal {
  constructor(name, breed) {
    super(name);        // calls Animal's constructor
    this.breed = breed;
  }
}
```
`extends` does the `Object.create` chain linking. `super()` does the `Animal.call(this, name)`. Same result, far less ceremony.

### What `class` does NOT change
1. Methods are still on the prototype.
2. `typeof` a class is still `'function'`.
3. The prototype chain is identical.

### What `class` does differently — two real differences
1. **Not hoisted:** Function constructors are hoisted. Classes sit in the TDZ (Temporal Dead Zone) just like `let` variables.
2. **Always strict mode:** Inside a class body, code runs in strict mode automatically.

### The complete picture — all 6 topics unified
```text
Closures
└── functions remember their lexical scope
      │
      └── Lexical Scoping
            └── scope chain fixed at write time, not call time
                  │
                  └── Prototype Chain
                        └── property lookup walks __proto__ links
                              │
                              ├── Object.create()  — links chain directly
                              ├── new              — links chain via constructor
                              │
                              └── hasOwnProperty
                                    └── tells you where in the chain a property lives
                                          │
                                          └── class syntax
                                                └── cleaner API over the same prototype chain
```

</details>

---

## 🎯 Interview Practice
*Expand the sections below to test your understanding!*


                                                <details>
<summary><b>Q1 — Closures</b></summary>
<br/>

What does this print? Reason through every line.
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
Then answer: do `add5` and `add10` share the same `x`? Why or why not?

**Answer:**

### Step-by-Step Execution
1. **Create add5**: `makeAdder(5)` creates a closure over `x = 5`. It returns a function expecting `y`.
2. **Create add10**: `makeAdder(10)` creates a completely new execution context and closure over `x = 10`.
3. **Evaluate add5(3)**: Uses closure `x = 5`, argument `y = 3`. `5 + 3 = 8`. Output: **8**.
4. **Evaluate add10(3)**: Uses closure `x = 10`, argument `y = 3`. `10 + 3 = 13`. Output: **13**.
5. **Evaluate add5(add10(2))**:
   - Work inside out: `add10(2)` computes `10 + 2 = 12`.
   - Now evaluate `add5(12)`: computes `5 + 12 = 17`.
   - Output: **17**.

### Do they share the same x?
**❌ No. They do not share the same `x`.**

Each call to `makeAdder()` creates a new execution context and a new lexical environment. Therefore, `add5` remembers `x = 5`, while `add10` remembers `x = 10`. These closures are completely independent of each other.

</details>

<details>
<summary><b>Q2 — Lexical Scoping</b></summary>
<br/>

What does this print? Before answering, identify which scope each variable resolves to.
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
Then answer: why doesn't `fn()` see `runner`'s `lang`, even though it's called from inside `runner`?

**Answer:**

### Execution Flow
1. **Global Scope**: `lang = "global"`.
2. **Call runner()**: Inside `runner`, `lang = "runner"`. It calls `outer()`.
3. **Execute outer()**: Inside `outer`, `lang = "outer"`. It returns the `inner` function. Crucially, `inner` forms a closure over `outer`'s lexical environment.
4. **Call fn()**: `fn()` is invoked. It looks for `lang`. It checks its own scope (none), then its parent scope (`outer`), finds `lang = "outer"`, and prints it.

**Final Output:**
**outer**

### Why Doesn't fn() See Runner's lang?
JavaScript uses **Lexical (Static) Scoping**, meaning variables are determined by where a function is defined, not where it is called.

Since `inner` was created inside `outer`, its scope chain is fixed at creation time:
`inner → outer → global`

It does *not* look at the call stack (`inner → runner → global`). Therefore, it never looks inside `runner`, and resolves `lang` to "outer".

</details>

<details>
<summary><b>Q3 — Prototype Chain</b></summary>
<br/>

What does this print? Trace every property lookup.
```javascript
function Person(name) {
  this.name = name;
}

Person.prototype.greet = function() {
  return `Hi, I'm ${this.name}`;
};

function Developer(name, lang) {
  Person.call(this, name);
  this.lang = lang;
}

Developer.prototype = Object.create(Person.prototype);
Developer.prototype.constructor = Developer;

Developer.prototype.code = function() {
  return `${this.name} codes in ${this.lang}`;
};

const dev = new Developer('Alice', 'JavaScript');

console.log(dev.name);
console.log(dev.lang);
console.log(dev.code());
console.log(dev.greet());
console.log(dev.hasOwnProperty('name'));
console.log(dev.hasOwnProperty('greet'));
console.log(dev instanceof Developer);
console.log(dev instanceof Person);
```

**Answer:**

### Prototype Chain
After setup, the `dev` object has the following chain:
```text
dev
├── name = "Alice"
├── lang = "JavaScript"
▼ [[Prototype]]
Developer.prototype
├── constructor
├── code()
▼ [[Prototype]]
Person.prototype
├── greet()
▼ [[Prototype]]
Object.prototype
├── hasOwnProperty()
├── toString()
▼
null
```

### Property Lookups & Output
| Expression | Found Where? | Output |
| :--- | :--- | :--- |
| `dev.name` | Directly on `dev` | **"Alice"** |
| `dev.lang` | Directly on `dev` | **"JavaScript"** |
| `dev.code()` | `Developer.prototype` | **"Alice codes in JavaScript"** |
| `dev.greet()` | `Person.prototype` | **"Hi, I'm Alice"** |
| `hasOwnProperty('name')` | `Object.prototype` | **true** (exists on `dev`) |
| `hasOwnProperty('greet')` | `Object.prototype` | **false** (exists on `Person.prototype`) |
| `dev instanceof Developer` | `Developer.prototype` in chain | **true** |
| `dev instanceof Person` | `Person.prototype` in chain | **true** |

The actual chain walk for `hasOwnProperty` is `dev → Developer.prototype → Person.prototype → Object.prototype`. JavaScript checks the object itself, then walks up the prototype chain until it finds the property or reaches null.

</details>


Q4 — Object.create() vs new
What is the difference between these two, and what does each produce?
jsfunction User(name) {
  this.name = name;
}
User.prototype.sayHi = function() {
  return `Hi, I'm ${this.name}`;
};

// Approach A
const a = new User('Alice');

// Approach B
const proto = {
  sayHi() { return `Hi, I'm ${this.name}`; }
};
const b = Object.create(proto);
b.name = 'Bob';
Answer these three:

Draw the prototype chain for both a and b
What does a.hasOwnProperty('sayHi') return? What about b.hasOwnProperty('sayHi')?
What does a instanceof User return? What about b instanceof User? Why?

This question tests the difference between constructor functions (new) and prototype-based object creation (Object.create).

Approach A — Using new
function User(name) {
  this.name = name;
}

User.prototype.sayHi = function() {
  return `Hi, I'm ${this.name}`;
};

const a = new User('Alice');

What new User('Alice') does internally:

Step 1

Creates an empty object

{}
Step 2

Sets its prototype

newObject.[[Prototype]]
      ↓
User.prototype
Step 3

Calls:

User.call(newObject, 'Alice')

which adds:

name = 'Alice'
Step 4

Returns the object.

Result:

a
│
└── name = "Alice"
Approach B — Using Object.create
const proto = {
  sayHi() {
    return `Hi, I'm ${this.name}`;
  }
};

const b = Object.create(proto);
b.name = 'Bob';
Step 1
Object.create(proto)

creates:

b
│
▼
proto
Step 2
b.name = 'Bob';

Result:

b
│
└── name = "Bob"
1. Prototype Chains
For a
a
│
├── name = "Alice"
│
▼ [[Prototype]]

User.prototype
│
├── sayHi()
│
▼ [[Prototype]]

Object.prototype
│
▼

null
For b
b
│
├── name = "Bob"
│
▼ [[Prototype]]

proto
│
├── sayHi()
│
▼ [[Prototype]]

Object.prototype
│
▼

null

Notice:

a → User.prototype
b → proto

Different prototype chains.

2. hasOwnProperty('sayHi')
For a
a.hasOwnProperty('sayHi')

Check only properties directly on a.

Own properties:

name

sayHi is on:

User.prototype

Therefore:

false
For b
b.hasOwnProperty('sayHi')

Own properties:

name

sayHi is on:

proto

Therefore:

false
Answers
a.hasOwnProperty('sayHi') // false
b.hasOwnProperty('sayHi') // false
3. instanceof User
For a
a instanceof User

JavaScript checks:

Is User.prototype
inside a's prototype chain?

Chain:

a
↓
User.prototype

Found.

Result:

true
For b
b instanceof User

JavaScript checks:

Is User.prototype
inside b's prototype chain?

Chain:

b
↓
proto
↓
Object.prototype
↓
null

No User.prototype.

Result:

false
Why?

Because instanceof works by checking the prototype chain.

Conceptually:

obj instanceof Constructor

means:

Does Constructor.prototype
exist somewhere in obj's prototype chain?
Quick Comparison
Feature	new User()	Object.create(proto)
Calls constructor?	✅ Yes	❌ No
Sets prototype automatically?	✅ User.prototype	✅ proto
Creates instance of User?	✅ Yes	❌ No
instanceof User	✅ true	❌ false
Can access sayHi()	✅ Yes	✅ Yes
Final Answers
Prototype Chains
a
a
↓
User.prototype
↓
Object.prototype
↓
null
b
b
↓
proto
↓
Object.prototype
↓
null
hasOwnProperty
a.hasOwnProperty('sayHi') // false
b.hasOwnProperty('sayHi') // false

Because sayHi is inherited in both cases.

instanceof
a instanceof User // true
b instanceof User // false

Because only a has User.prototype in its prototype chain. b inherits from proto, not from User.prototype.

<details>
<summary><b>Q4 — Object.create() vs new</b></summary>
<br/>

What is the difference between these two, and what does each produce?

```javascript
function User(name) {
  this.name = name;
}
User.prototype.sayHi = function() {
  return `Hi, I'm ${this.name}`;
};

// Approach A
const a = new User('Alice');

// Approach B
const proto = {
  sayHi() { return `Hi, I'm ${this.name}`; }
};
const b = Object.create(proto);
b.name = 'Bob';
```

Answer these three:
1. Draw the prototype chain for both `a` and `b`
2. What does `a.hasOwnProperty('sayHi')` return? What about `b.hasOwnProperty('sayHi')`?
3. What does `a instanceof User` return? What about `b instanceof User`? Why?

**Answer:**

This question tests the difference between constructor functions (`new`) and prototype-based object creation (`Object.create`).

**Approach A — Using `new`**
```javascript
function User(name) {
  this.name = name;
}

User.prototype.sayHi = function() {
  return `Hi, I'm ${this.name}`;
};

const a = new User('Alice');
```
What `new User('Alice')` does internally:
1. **Step 1:** Creates an empty object `{}`
2. **Step 2:** Sets its prototype (`newObject.[[Prototype]]` → `User.prototype`)
3. **Step 3:** Calls `User.call(newObject, 'Alice')`, adding `name = 'Alice'`
4. **Step 4:** Returns the object `a`.

**Approach B — Using `Object.create`**
```javascript
const proto = {
  sayHi() {
    return `Hi, I'm ${this.name}`;
  }
};

const b = Object.create(proto);
b.name = 'Bob';
```
1. **Step 1:** `Object.create(proto)` creates `b` with `proto` as its prototype.
2. **Step 2:** `b.name = 'Bob'` assigns the name property.

### 1. Prototype Chains
**For a:**
```text
a
├── name = "Alice"
▼ [[Prototype]]
User.prototype
├── sayHi()
▼ [[Prototype]]
Object.prototype
▼
null
```

**For b:**
```text
b
├── name = "Bob"
▼ [[Prototype]]
proto
├── sayHi()
▼ [[Prototype]]
Object.prototype
▼
null
```
*Notice:* `a` → `User.prototype`, while `b` → `proto`. Different prototype chains.

### 2. hasOwnProperty('sayHi')
- `a.hasOwnProperty('sayHi')` // **false** (sayHi is on User.prototype)
- `b.hasOwnProperty('sayHi')` // **false** (sayHi is on proto)

Because `sayHi` is inherited in both cases.

### 3. instanceof User
- `a instanceof User` // **true** (User.prototype is in a's chain)
- `b instanceof User` // **false** (b inherits from proto, not User.prototype)

Because `instanceof` works by checking if `Constructor.prototype` exists anywhere in the object's prototype chain.

### Quick Comparison
| Feature | `new User()` | `Object.create(proto)` |
| :--- | :---: | :---: |
| Calls constructor? | ✅ Yes | ❌ No |
| Sets prototype automatically? | ✅ `User.prototype` | ✅ `proto` |
| Creates instance of User? | ✅ Yes | ❌ No |
| `instanceof User` | ✅ true | ❌ false |
| Can access `sayHi()` | ✅ Yes | ✅ Yes |

</details>

<details>
<summary><b>Q5 — class as syntactic sugar (the hardest one)</b></summary>
<br/>

What does this print? Then answer the questions below.

```javascript
class Animal {
  constructor(name) {
    this.name = name;
  }
  speak() {
    return `${this.name} makes a sound`;
  }
}

class Dog extends Animal {
  constructor(name, breed) {
    super(name);
    this.breed = breed;
  }
  bark() {
    return `${this.name} barks`;
  }
}

const d = new Dog('Rex', 'Labrador');

console.log(d.name);
console.log(d.breed);
console.log(d.bark());
console.log(d.speak());
console.log(d.hasOwnProperty('bark'));
console.log(d.hasOwnProperty('name'));
console.log(typeof Dog);
console.log(d instanceof Dog);
console.log(d instanceof Animal);
```

Then answer these three:
1. What does `extends` compile down to in pre-ES6 prototype terms?
2. What does `super(name)` compile down to?
3. What are the two real differences between `class` and a regular constructor function?

**Answer:**

`class` is mostly syntactic sugar over JavaScript's prototype-based inheritance.

### Step-by-Step Execution
Internally (roughly), the classes compile down to:
```javascript
function Animal(name) { this.name = name; }
Animal.prototype.speak = function() { return `${this.name} makes a sound`; };

function Dog(name, breed) {
  Animal.call(this, name);
  this.breed = breed;
}
Dog.prototype = Object.create(Animal.prototype);
Dog.prototype.constructor = Dog;
Dog.prototype.bark = function() { return `${this.name} barks`; };
```

When creating `const d = new Dog('Rex', 'Labrador')`, the prototype chain is:
```text
d
├── name = "Rex"
├── breed = "Labrador"
▼ [[Prototype]]
Dog.prototype
├── bark()
▼ [[Prototype]]
Animal.prototype
├── speak()
▼ [[Prototype]]
Object.prototype
▼
null
```

### Outputs
- `d.name` → **"Rex"** (Found directly on d)
- `d.breed` → **"Labrador"** (Found directly on d)
- `d.bark()` → **"Rex barks"** (Found on Dog.prototype)
- `d.speak()` → **"Rex makes a sound"** (Found on Animal.prototype)
- `d.hasOwnProperty('bark')` → **false** (It's on Dog.prototype)
- `d.hasOwnProperty('name')` → **true** (It's directly on d)
- `typeof Dog` → **"function"** (Classes are actually functions)
- `d instanceof Dog` → **true** (Dog.prototype is in the chain)
- `d instanceof Animal` → **true** (Animal.prototype is in the chain)

### Question Answers

**1. What does `extends` compile down to?**
Roughly equivalent to linking the prototypes:
```javascript
Dog.prototype = Object.create(Animal.prototype);
Dog.prototype.constructor = Dog;
```

**2. What does `super(name)` compile down to?**
Roughly equivalent to borrowing the constructor:
```javascript
Animal.call(this, name);
```
Which executes `this.name = name` inside the child object's context.

**3. Two real differences between classes and constructor functions:**
1. **Classes cannot be called without `new`**. A regular constructor function like `function User(){}` can be called as `User()`, but `class User{}` will throw a TypeError if called without `new`.
2. **Class methods are automatically strict mode**. Code inside a `class` body automatically runs in strict mode, preventing global variable leaks and `this` defaulting to `window`.

</details>
User() → error
new User() → works
Class methods run in strict mode automatically
Constructor functions do not automatically enforce strict mode.

Everything else—instances, prototypes, inheritance, instanceof, method lookup—is still built on JavaScript's prototype system.

You mentioned two differences correctly — but there's a third worth knowing for interviews: classes are not hoisted like function declarations. new Dog() before the class Dog {} line throws a ReferenceError (TDZ, just like let). A constructor function declaration would work fine before its definition. You covered this in the teaching session — just make sure it's in your interview answer too.

