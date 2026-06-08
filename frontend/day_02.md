<div align="center">
  <h1>🚀 JavaScript Advanced Concepts: Day 02</h1>
  <p><i>Closures, Lexical Scoping, Prototype Chain, and ES6 Classes.</i></p>
</div>

---

Frontend Session — Functional JS
We'll go through these one by one:

Closures ← starting here
Lexical Scoping vs Dynamic Scoping
Function.prototype and the prototype chain
Object.create() vs new
hasOwnProperty vs inherited properties
class as syntactic sugar



## 1. Closures (deeper than yesterday)

You already know the definition. Today we go deeper — practical patterns built on closures.

Pattern 1 — Factory functions
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
Each call to makeUser creates a fresh closure with its own loginCount. alice and bob don't share state.

Pattern 2 — Memoization
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
cache lives in memoize's scope. The returned function closes over it — reading and writing across every call.

```
Pattern 3 — Partial application
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
firstArg is baked in. The returned function only needs the second argument. This is how libraries like Lodash implement _.partial.

```
The one thing to remember
A closure doesn't snapshot the value — it holds a live reference to the variable. This is why:
```javascript
function makeCounter() {
  let n = 0;
  return {
    increment: () => ++n,
    decrement: () => --n,
    value:     () => n
  };
}

const c = makeCounter();
c.increment(); // 1
c.increment(); // 2
c.decrement(); // 1
c.value();     // 1 — all three methods share the same live `n`
```
All three methods close over the same n — mutations from one are visible to all.


## 2. Lexical Scoping vs Dynamic Scoping

This is the rule that makes closures predictable. JavaScript uses lexical scoping — but understanding why requires knowing what the alternative looks like.

Lexical scoping — scope set at write time
The scope chain is determined by where the function is defined in the source code, not where it's called from.

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
inner was written inside outer, so it closes over outer's x. It doesn't matter that fn() is called from the global scope. The chain was fixed at write time.

```
What dynamic scoping would look like
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
Scoping rule	Result	Why
Lexical (JS)	'global'	printX written in global scope → sees global x
Dynamic (not JS)	'run'	printX called from run → would see run's x
JS always gives you 'global' here. The call location is irrelevant.

The practical implication — this is dynamic, variables are lexical
Here's where it gets interesting. JS has one thing that behaves dynamically — this. Variables follow lexical rules. this follows call-site rules.

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
Arrow functions fix this lexically — they don't get their own this, they inherit it from the surrounding scope at write time. Regular functions get this determined at call time.

Visualizing the difference
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
One rule to remember
Variables — look at where the function was written. this — look at how the function was called.

Arrow functions collapse both into one rule: always lexical.



## 3. Function.prototype and the Prototype Chain

Every object in JS has a hidden link to another object called its prototype. When you access a property that doesn't exist on the object itself, JS follows that link — and keeps following it — until it finds the property or hits null. That chain of links is the prototype chain.

The hidden link — __proto__
```javascript
const dog = { name: 'Rex' };

console.log(dog.name);       // 'Rex' — own property
console.log(dog.toString()); // '[object Object]' — where did this come from?
dog doesn't have toString. JS looks at dog.__proto__ — which points to Object.prototype — and finds it there.

dog
 │
 └── __proto__ → Object.prototype
                   ├── toString()
                   ├── hasOwnProperty()
                   ├── valueOf()
                   └── __proto__ → null  ← chain ends here
```
Functions have their own prototype chain
Every function has two things people confuse:

What it is	Used for
fn.__proto__	link to Function.prototype	gives fn methods like .call, .bind, .apply
fn.prototype	an object attached to fn	becomes __proto__ of objects created with new fn()
```javascript
function greet() {}

greet.__proto__ === Function.prototype // true — greet IS a function object
greet.prototype                        // { constructor: greet } — blueprint for instances
```
What happens with constructor functions
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
The chain for cat:

cat
 │  name: 'Cat'
 │
 └── __proto__ → Animal.prototype
                   ├── speak()
                   └── __proto__ → Object.prototype
                                     ├── toString()
                                     └── __proto__ → null
When you call cat.speak():

JS checks cat — no speak
JS checks Animal.prototype — found ✅
What new actually does
```javascript
const cat = new Animal('Cat');
```
Under the hood, new does exactly four things:

```javascript
// 1. creates a blank object
const obj = {};

// 2. links it to Animal.prototype
obj.__proto__ = Animal.prototype;

// 3. runs the constructor with `this` = obj
Animal.call(obj, 'Cat');

// 4. returns obj (unless constructor explicitly returns an object)
return obj;
```
That's all new is. No magic.

Prototype chain lookup — the full picture
```javascript
function Vehicle(type) { this.type = type; }
Vehicle.prototype.describe = function() { return `I am a ${this.type}`; };

function Car(type, brand) {
  Vehicle.call(this, type); // borrow constructor
  this.brand = brand;
}

```
Car.prototype = Object.create(Vehicle.prototype); // link chains
Car.prototype.constructor = Car;                  // fix constructor ref

Car.prototype.honk = function() { return 'Beep!'; };

const bmw = new Car('sedan', 'BMW');

bmw.brand;      // 'BMW'       — own property
bmw.honk();     // 'Beep!'     — on Car.prototype
bmw.describe(); // 'I am a sedan' — on Vehicle.prototype
bmw.toString(); // '[object Object]' — on Object.prototype
The chain:

bmw
 └── __proto__ → Car.prototype
                   └── __proto__ → Vehicle.prototype
                                     └── __proto__ → Object.prototype
                                                       └── __proto__ → null
The one thing people get wrong
```javascript
// ❌ this breaks the chain
Car.prototype = Vehicle.prototype;
// now Car and Vehicle share the same prototype object
// adding to Car.prototype also adds to Vehicle.prototype

// ✅ this creates a proper link
Car.prototype = Object.create(Vehicle.prototype);
// creates a new object whose __proto__ is Vehicle.prototype
// Car.prototype and Vehicle.prototype are separate objects


```

## 4. Object.create() vs new

You already know what new does under the hood. Now meet Object.create() — a lower-level tool that sets up the prototype link directly, without a constructor function.

Object.create() — pure prototype linking
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
The chain:

dog
 │  name: 'Rex'
 │
 └── __proto__ → animal
                   ├── speak()
                   └── __proto__ → Object.prototype
Object.create(animal) creates a blank object whose __proto__ is set to animal. No constructor, no new, no prototype property involved.

Side by side — same result, different mechanism
Using new:

```javascript
function Animal(name) {
  this.name = name;
}
Animal.prototype.speak = function() {
  console.log(`${this.name} makes a sound`);
};

const dog = new Animal('Rex');
```
Using Object.create():

```javascript
const animalProto = {
  init(name) { this.name = name; return this; },
  speak() { console.log(`${this.name} makes a sound`); }
};

const dog = Object.create(animalProto).init('Rex');
```
Both produce the same chain — dog.__proto__ points to the prototype object containing speak. The difference is how you get there.

Key differences
new	Object.create()
Needs a constructor function	✅ yes	❌ no
Sets __proto__	✅ to Fn.prototype	✅ to whatever you pass
Runs initialization code	✅ constructor body	❌ you do it manually
Returns new object	✅ automatically	✅ automatically
Pass null for no prototype	❌	✅ Object.create(null)
Object.create(null) — a truly empty object
```javascript
const plain = Object.create(null);

plain.name = 'Alice';
plain.toString; // undefined — no Object.prototype in the chain!
```
Useful when you want a pure key-value store with zero inherited noise. No toString, no hasOwnProperty, nothing. The chain is just:

plain
 │  name: 'Alice'
 └── __proto__ → null
How Object.create() powers inheritance
This is what you used in the previous topic to link Car to Vehicle:

```javascript
Car.prototype = Object.create(Vehicle.prototype);
```
What this does step by step:

```javascript
// 1. Creates a new blank object
const obj = {};

// 2. Sets its __proto__ to Vehicle.prototype
obj.__proto__ = Vehicle.prototype;

// 3. Assigns it to Car.prototype
Car.prototype = obj;
```
Now any instance of Car walks up to Car.prototype, which walks up to Vehicle.prototype. The chain is intact without running Vehicle's constructor prematurely.

The wrong way to inherit — and why it breaks
```javascript
// ❌ common mistake
Car.prototype = new Vehicle();
```
This works accidentally in simple cases but has a hidden problem — it runs Vehicle's constructor during setup, before you have any arguments to pass. If Vehicle has side effects or required params, this breaks. Object.create() links the prototype chain without executing any constructor. Always prefer it for inheritance setup.

Mental model — one line summary
new Fn() — runs a constructor, links prototype automatically. Object.create(obj) — skips the constructor, links prototype directly.


## 3. Function.prototype and the Prototype Chain

Every object in JS has a hidden link to another object called its prototype. When you access a property that doesn't exist on the object itself, JS follows that link — and keeps following it — until it finds the property or hits null. That chain of links is the prototype chain.

The hidden link — __proto__
```javascript
const dog = { name: 'Rex' };

console.log(dog.name);       // 'Rex' — own property
console.log(dog.toString()); // '[object Object]' — where did this come from?
dog doesn't have toString. JS looks at dog.__proto__ — which points to Object.prototype — and finds it there.
dog
 │
 └── __proto__ → Object.prototype
                   ├── toString()
                   ├── hasOwnProperty()
                   ├── valueOf()
                   └── __proto__ → null  ← chain ends here

```
Functions have their own prototype chain
Every function has two things people confuse:
What it isUsed forfn.__proto__link to Function.prototypegives fn methods like .call, .bind, .applyfn.prototypean object attached to fnbecomes __proto__ of objects created with new fn()
```javascript
function greet() {}

greet.__proto__ === Function.prototype // true — greet IS a function object
greet.prototype                        // { constructor: greet } — blueprint for instances

```
What happens with constructor functions
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
The chain for cat:
cat
 │  name: 'Cat'
 │
 └── __proto__ → Animal.prototype
                   ├── speak()
                   └── __proto__ → Object.prototype
                                     ├── toString()
                                     └── __proto__ → null
When you call cat.speak():

JS checks cat — no speak
JS checks Animal.prototype — found ✅


What new actually does
```javascript
const cat = new Animal('Cat');
```
Under the hood, new does exactly four things:
```javascript
// 1. creates a blank object
const obj = {};

// 2. links it to Animal.prototype
obj.__proto__ = Animal.prototype;

// 3. runs the constructor with `this` = obj
Animal.call(obj, 'Cat');

// 4. returns obj (unless constructor explicitly returns an object)
return obj;
```
That's all new is. No magic.

Prototype chain lookup — the full picture
```javascript
function Vehicle(type) { this.type = type; }
Vehicle.prototype.describe = function() { return `I am a ${this.type}`; };

function Car(type, brand) {
  Vehicle.call(this, type); // borrow constructor
  this.brand = brand;
}

```
Car.prototype = Object.create(Vehicle.prototype); // link chains
Car.prototype.constructor = Car;                  // fix constructor ref

Car.prototype.honk = function() { return 'Beep!'; };

const bmw = new Car('sedan', 'BMW');

bmw.brand;      // 'BMW'       — own property
bmw.honk();     // 'Beep!'     — on Car.prototype
bmw.describe(); // 'I am a sedan' — on Vehicle.prototype
bmw.toString(); // '[object Object]' — on Object.prototype
The chain:
bmw
 └── __proto__ → Car.prototype
                   └── __proto__ → Vehicle.prototype
                                     └── __proto__ → Object.prototype
                                                       └── __proto__ → null

The one thing people get wrong
```javascript
// ❌ this breaks the chain
Car.prototype = Vehicle.prototype;
// now Car and Vehicle share the same prototype object
// adding to Car.prototype also adds to Vehicle.prototype

// ✅ this creates a proper link
Car.prototype = Object.create(Vehicle.prototype);
// creates a new object whose __proto__ is Vehicle.prototype
// Car.prototype and Vehicle.prototype are separate objects

```
You already know what new does under the hood. Now meet Object.create() — a lower-level tool that sets up the prototype link directly, without a constructor function.

Object.create() — pure prototype linking
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
The chain:
dog
 │  name: 'Rex'
 │
 └── __proto__ → animal
                   ├── speak()
                   └── __proto__ → Object.prototype
Object.create(animal) creates a blank object whose __proto__ is set to animal. No constructor, no new, no prototype property involved.

Side by side — same result, different mechanism
Using new:
```javascript
function Animal(name) {
  this.name = name;
}
Animal.prototype.speak = function() {
  console.log(`${this.name} makes a sound`);
};

const dog = new Animal('Rex');
```
Using Object.create():
```javascript
const animalProto = {
  init(name) { this.name = name; return this; },
  speak() { console.log(`${this.name} makes a sound`); }
};

const dog = Object.create(animalProto).init('Rex');
```
Both produce the same chain — dog.__proto__ points to the prototype object containing speak. The difference is how you get there.

Key differences
newObject.create()Needs a constructor function✅ yes❌ noSets __proto__✅ to Fn.prototype✅ to whatever you passRuns initialization code✅ constructor body❌ you do it manuallyReturns new object✅ automatically✅ automaticallyPass null for no prototype❌✅ Object.create(null)

Object.create(null) — a truly empty object
```javascript
const plain = Object.create(null);

plain.name = 'Alice';
plain.toString; // undefined — no Object.prototype in the chain!
```
Useful when you want a pure key-value store with zero inherited noise. No toString, no hasOwnProperty, nothing. The chain is just:
plain
 │  name: 'Alice'
 └── __proto__ → null

How Object.create() powers inheritance
This is what you used in the previous topic to link Car to Vehicle:
```javascript
Car.prototype = Object.create(Vehicle.prototype);
```
What this does step by step:
```javascript
// 1. Creates a new blank object
const obj = {};

// 2. Sets its __proto__ to Vehicle.prototype
obj.__proto__ = Vehicle.prototype;

// 3. Assigns it to Car.prototype
Car.prototype = obj;
```
Now any instance of Car walks up to Car.prototype, which walks up to Vehicle.prototype. The chain is intact without running Vehicle's constructor prematurely.

The wrong way to inherit — and why it breaks
```javascript
// ❌ common mistake
Car.prototype = new Vehicle();
```
This works accidentally in simple cases but has a hidden problem — it runs Vehicle's constructor during setup, before you have any arguments to pass. If Vehicle has side effects or required params, this breaks. Object.create() links the prototype chain without executing any constructor. Always prefer it for inheritance setup.

Mental model — one line summary

new Fn() — runs a constructor, links prototype automatically.
Object.create(obj) — skips the constructor, links prototype directly.

## 5. hasOwnProperty vs Inherited Properties

Every property lookup in JS walks the prototype chain. But sometimes you need to know: did this object define this property itself, or did it inherit it? That's exactly what hasOwnProperty answers.

The difference
```javascript
function Animal(name) {
  this.name = name;
}
Animal.prototype.speak = function() {
  console.log(`${this.name} makes a sound`);
};

const dog = new Animal('Rex');

dog.name;  // 'Rex'   — own property
dog.speak; // [Function] — inherited from Animal.prototype

dog.hasOwnProperty('name');  // true  — lives directly on dog
dog.hasOwnProperty('speak'); // false — lives on Animal.prototype
```
The chain lookup finds both — but hasOwnProperty only returns true for properties that sit directly on the object itself.

Why it matters — the for...in trap
for...in iterates all enumerable properties — own and inherited:
```javascript
function Animal(name) { this.name = name; }
Animal.prototype.type = 'mammal';

const dog = new Animal('Rex');

for (const key in dog) {
  console.log(key);
}
// 'name'  — own
// 'type'  — inherited ← you probably don't want this
```
The fix — guard with hasOwnProperty:
```javascript
for (const key in dog) {
  if (dog.hasOwnProperty(key)) {
    console.log(key); // 'name' only
  }
}

```
Object.keys() vs for...in
If you just want own enumerable properties, skip the guard entirely:
```javascript
Object.keys(dog);   // ['name'] — own enumerable only
```
Object.values(dog); // ['Rex']
Object.entries(dog);// [['name', 'Rex']]
Object.keys never walks the chain. It's the clean default when you want own properties.

The full property landscape
```javascript
const dog = new Animal('Rex');

// own + enumerable
```
Object.keys(dog);                    // ['name']

// own + enumerable + non-enumerable
Object.getOwnPropertyNames(dog);     // ['name']

// own + inherited + enumerable
for (const k in dog) console.log(k); // 'name', 'type'

// check one property
dog.hasOwnProperty('name');          // true
dog.hasOwnProperty('type');          // false
'type' in dog;                       // true  — `in` walks the chain
'type' in Animal.prototype;          // true
The in operator walks the full chain — hasOwnProperty doesn't. Know which one you need.

Safe hasOwnProperty — one edge case
What if someone creates an object with Object.create(null)? It has no prototype — so hasOwnProperty itself doesn't exist on it:
```javascript
const obj = Object.create(null);
obj.name = 'Alice';

obj.hasOwnProperty('name'); // ❌ TypeError: obj.hasOwnProperty is not a function
```
The safe pattern used in libraries:
```javascript
Object.prototype.hasOwnProperty.call(obj, 'name'); // ✅ true
```
Or in modern JS:
```javascript
Object.hasOwn(obj, 'name'); // ✅ true — ES2022, cleaner

```
Cheat sheet
MethodOwn?Inherited?Non-enumerable?hasOwnProperty✅❌✅Object.keys()✅❌❌Object.getOwnPropertyNames()✅❌✅in operator✅✅✅for...in✅✅❌


## 6. class as Syntactic Sugar
class was introduced in ES6. It looks like classical inheritance from Java or Python — but it's not. Under the hood it's still prototype chains, constructor functions, and Object.create. The keyword just makes it look cleaner.

Side by side — identical behavior, different syntax
Pre-ES6 prototype style:

```javascript
function Animal(name) {
  this.name = name;
}

Animal.prototype.speak = function() {
  console.log(`${this.name} makes a sound`);
};
```
ES6 class style:

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
These produce identical prototype chains. The class version is just a cleaner way to write the same thing. speak still lives on Animal.prototype, not on each instance.

```javascript
const dog = new Animal('Rex');
dog.hasOwnProperty('speak'); // false — it's on Animal.prototype
extends and super — prototype chaining with clean syntax
```
Pre-ES6:

```javascript
function Dog(name, breed) {
  Animal.call(this, name);   // borrow constructor
  this.breed = breed;
}
```
Dog.prototype = Object.create(Animal.prototype); // link chain
Dog.prototype.constructor = Dog;

Dog.prototype.bark = function() {
  console.log('Woof!');
};
ES6 class:

```javascript
class Dog extends Animal {
  constructor(name, breed) {
    super(name);        // calls Animal's constructor
    this.breed = breed;
  }

  bark() {
    console.log('Woof!');
  }
}
extends does the Object.create chain linking. super() does the Animal.call(this, name). Same result, far less ceremony.

```
```javascript
const rex = new Dog('Rex', 'Labrador');

rex.name;              // 'Rex'       — own (set by Animal constructor via super)
rex.breed;             // 'Labrador'  — own (set by Dog constructor)
rex.bark();            // 'Woof!'     — on Dog.prototype
rex.speak();           // 'Rex makes a sound' — on Animal.prototype
rex instanceof Dog;    // true
rex instanceof Animal; // true
```
What class does NOT change

## 1. Methods are still on the prototype — not the instance:


```javascript
const a = new Animal('Cat');
const b = new Animal('Dog');

a.speak === b.speak; // true — same function reference on Animal.prototype
2. typeof a class is still function:

```
```javascript
typeof Animal; // 'function'
```

## 3. The prototype chain is identical:


rex
 └── __proto__ → Dog.prototype
                   └── __proto__ → Animal.prototype
                                     └── __proto__ → Object.prototype
                                                       └── null
What class does differently — two real differences

## 1. Not hoisted like function declarations:


```javascript
const d = new Dog(); // ❌ ReferenceError
class Dog {}
```
Function constructors are hoisted. Classes are not — they sit in the TDZ just like let.


## 2. Always strict mode:


```javascript
class Animal {
  speak() {
    console.log(this); // always strict — `this` won't default to global
  }
}
```
Inside a class body, code runs in strict mode automatically. In a regular constructor function, it only does if you explicitly write 'use strict'.

The complete picture — all 6 topics unified
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



---

## 🎯 Interview Prep & Challenges

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
Then answer: do add5 and add10 share the same x? Why or why not?

Step 1: Create add5
const add5 = makeAdder(5);

When makeAdder(5) runs:

x = 5

It returns:

function(y) {
  return x + y;
}

The returned function forms a closure over:

x = 5

Conceptually:

add5
  ↓
function(y) {
   return x + y;
}
  ↓
Closure
  ↓
x = 5
Step 2: Create add10
const add10 = makeAdder(10);

A completely new execution context is created.

x = 10

Another function is returned.

add10
  ↓
function(y) {
   return x + y;
}
  ↓
Closure
  ↓
x = 10
Step 3: Evaluate add5(3)
console.log(add5(3));

Inside add5:

x = 5  (from closure)
y = 3  (parameter)

Calculation:

5 + 3 = 8

Output:

8
Step 4: Evaluate add10(3)
console.log(add10(3));

Inside add10:

x = 10
y = 3

Calculation:

10 + 3 = 13

Output:

13
Step 5: Evaluate add5(add10(2))

Work from the inside out.

First
add10(2)

Inside add10:

x = 10
y = 2

Calculation:

10 + 2 = 12

Returns:

12

Now the expression becomes:

add5(12)

Inside add5:

x = 5
y = 12

Calculation:

5 + 12 = 17

Output:

17
Final Output
8
13
17
Do add5 and add10 share the same x?
Answer:

❌ No.

They do not share the same x.

Why?

Each call to makeAdder() creates a new execution context and a new lexical environment.

First Call
makeAdder(5)

creates:

Environment A

x = 5
Second Call
makeAdder(10)

creates:

Environment B

x = 10

These are completely separate.

Visualization:

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

So when:

add5(3)

runs, it always uses:

x = 5

and when:

add10(3)

runs, it always uses:

x = 10
Interview Answer

The output is:

8
13
17

add5 and add10 do not share the same x. Each call to makeAdder() creates a new lexical environment, and the returned function closes over that specific environment. Therefore add5 remembers x = 5, while add10 remembers x = 10. These closures are independent of each other.


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
Then answer: why doesn't fn() see runner's lang, even though it's called from inside runner?
Step 1: Global Scope
const lang = 'global';

Global scope contains:

lang = "global"
outer = function
runner = function
Step 2: Call runner()
runner();

Inside runner:

const lang = 'runner';

Runner scope:

lang = "runner"

Then:

const fn = outer();

calls outer().

Step 3: Execute outer()

Inside outer:

const lang = 'outer';

Outer scope:

lang = "outer"

Then:

return inner;

returns the function:

function inner() {
  console.log(lang);
}

Important:

When inner is created, it remembers its surrounding lexical environment.

inner
  ↓
Closure
  ↓
outer scope
  ↓
lang = "outer"

Now:

const fn = outer();

So:

fn = inner function

with a closure over outer's environment.

Step 4: Call fn()
fn();

This executes:

console.log(lang);

JavaScript looks for lang.

Search Process
Current Scope (inner)
No lang
Parent Scope (outer)
lang = "outer"

Found!

So it stops searching.

Output:

outer
Final Output
outer
Which Scope Does lang Resolve To?

Inside:

function inner() {
  console.log(lang);
}

Lookup happens like this:

inner scope
   ↓
outer scope   ← FOUND HERE
   ↓
global scope

Therefore:

lang → outer scope
value → "outer"
Why Doesn't fn() See Runner's lang?

Many developers initially think:

fn() is called inside runner
so it should see runner's lang

But JavaScript does not work that way.

JavaScript uses:

Lexical (Static) Scoping

Meaning:

Variables are determined by where a function is defined, not where it is called.

Where was inner defined?
function outer() {
  const lang = 'outer';

  function inner() {
    console.log(lang);
  }
}

inner was created inside outer.

Therefore its scope chain is:

inner
  ↓
outer
  ↓
global

Not:

inner
  ↓
runner
  ↓
global
Visual Diagram
Global Scope
│
├── lang = "global"
│
├── outer()
│     │
│     ├── lang = "outer"
│     │
│     └── inner()
│
└── runner()
      │
      └── lang = "runner"

When inner() executes:

inner
  ↓
outer
  ↓
global

It never looks inside runner.

Interview Answer

The output is:

outer

The lang variable inside inner resolves to the lang declared in outer, because JavaScript uses lexical scoping. A function remembers the scope where it was defined, not where it is called. Even though fn() is invoked inside runner, inner was created inside outer, so its scope chain is:

inner → outer → global

and not:

inner → runner → global

Therefore console.log(lang) prints "outer".


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
Draw the prototype chain for dev and explain where each property is found.

Step 1: Person Constructor
function Person(name) {
  this.name = name;
}

Creates objects like:

{
  name: "Alice"
}
Step 2: Add greet to Person.prototype
Person.prototype.greet = function() {
  return `Hi, I'm ${this.name}`;
};

Now:

Person.prototype
│
└── greet()
Step 3: Developer Constructor
function Developer(name, lang) {
  Person.call(this, name);
  this.lang = lang;
}

When called:

new Developer('Alice', 'JavaScript')

Inside:

Person.call(this, 'Alice');

sets:

this.name = "Alice"

Then:

this.lang = "JavaScript";

Object becomes:

{
  name: "Alice",
  lang: "JavaScript"
}
Step 4: Set Up Inheritance
Developer.prototype = Object.create(Person.prototype);

This means:

Developer.prototype
       ↓
Person.prototype

Inheritance is established.

Step 5: Fix Constructor
Developer.prototype.constructor = Developer;

Now:

Developer.prototype.constructor
     ↓
Developer
Step 6: Add code()
Developer.prototype.code = function() {
  return `${this.name} codes in ${this.lang}`;
};

Now:

Developer.prototype
│
├── constructor
└── code()
Step 7: Create Object
const dev = new Developer('Alice', 'JavaScript');

Result:

dev
│
├── name = "Alice"
└── lang = "JavaScript"
Prototype Chain
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
├── toString()
└── ...
│
▼

null
Property Lookup 1
console.log(dev.name);

Search:

dev
└── name found

Output:

Alice
Property Lookup 2
console.log(dev.lang);

Search:

dev
└── lang found

Output:

JavaScript
Property Lookup 3
console.log(dev.code());

Search:

dev
↓
Developer.prototype
↓
code found

Execute:

return `${this.name} codes in ${this.lang}`;

this = dev

Alice codes in JavaScript

Output:

Alice codes in JavaScript
Property Lookup 4
console.log(dev.greet());

Search:

dev
↓
Developer.prototype
↓
Person.prototype
↓
greet found

Execute:

return `Hi, I'm ${this.name}`;

this = dev

Hi, I'm Alice

Output:

Hi, I'm Alice
Property Lookup 5
console.log(dev.hasOwnProperty('name'));

Search:

dev
↓
Object.prototype
↓
hasOwnProperty found

Checks whether name exists directly on dev.

name = own property

Output:

true
Property Lookup 6
console.log(dev.hasOwnProperty('greet'));

Checks:

Does dev itself contain greet?

No.

greet lives on:

Person.prototype

Output:

false
instanceof Check 1
console.log(dev instanceof Developer);

JavaScript checks:

Is Developer.prototype
inside dev's prototype chain?

Chain:

dev
↓
Developer.prototype

Found.

Output:

true
instanceof Check 2
console.log(dev instanceof Person);

JavaScript checks:

Is Person.prototype
inside dev's prototype chain?

Chain:

dev
↓
Developer.prototype
↓
Person.prototype

Found.

Output:

true
Final Output
Alice
JavaScript
Alice codes in JavaScript
Hi, I'm Alice
true
false
true
true
Interview Summary
Expression	Found Where?	Result
dev.name	dev	"Alice"
dev.lang	dev	"JavaScript"
dev.code()	Developer.prototype	"Alice codes in JavaScript"
dev.greet()	Person.prototype	"Hi, I'm Alice"
hasOwnProperty	Object.prototype	method call
dev instanceof Developer	Developer.prototype in chain	true
dev instanceof Person	Person.prototype in chain	true

The key idea is that JavaScript first checks the object itself, then walks up the prototype chain until it finds the property or reaches null.

You skipped one level on hasOwnProperty lookup. The actual chain walk is dev → Developer.prototype → Person.prototype → Object.prototype — hasOwnProperty is found at Object.prototype, not directly after dev. You got the result right, just compress the search path accurately when explaining in interviews.


</details>

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

</details>

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

What does extends compile down to in pre-ES6 prototype terms?
What does super(name) compile down to?
What are the two real differences between class and a regular constructor function?

This is one of the most important advanced JavaScript interview questions.

The key idea:

class is mostly syntactic sugar over JavaScript's prototype-based inheritance.

Step 1: Create Classes
class Animal {
  constructor(name) {
    this.name = name;
  }

  speak() {
    return `${this.name} makes a sound`;
  }
}

Internally (roughly):

function Animal(name) {
  this.name = name;
}

Animal.prototype.speak = function() {
  return `${this.name} makes a sound`;
};
class Dog extends Animal {
  constructor(name, breed) {
    super(name);
    this.breed = breed;
  }

  bark() {
    return `${this.name} barks`;
  }
}

Roughly becomes:

function Dog(name, breed) {
  Animal.call(this, name);
  this.breed = breed;
}

Dog.prototype = Object.create(Animal.prototype);
Dog.prototype.constructor = Dog;

Dog.prototype.bark = function() {
  return `${this.name} barks`;
};
Step 2: Create Object
const d = new Dog('Rex', 'Labrador');

After construction:

d
├── name = "Rex"
└── breed = "Labrador"
Prototype Chain
d
│
├── name
├── breed
│
▼ [[Prototype]]

Dog.prototype
│
├── bark()
│
▼ [[Prototype]]

Animal.prototype
│
├── speak()
│
▼ [[Prototype]]

Object.prototype
│
▼

null
Output 1
console.log(d.name);

Found directly on d.

Output:

Rex
Output 2
console.log(d.breed);

Found directly on d.

Output:

Labrador
Output 3
console.log(d.bark());

Lookup:

d
↓
Dog.prototype
↓
bark found

Returns:

Rex barks

Output:

Rex barks
Output 4
console.log(d.speak());

Lookup:

d
↓
Dog.prototype
↓
Animal.prototype
↓
speak found

Returns:

Rex makes a sound

Output:

Rex makes a sound
Output 5
console.log(d.hasOwnProperty('bark'));

Does d directly contain bark?

No

It's on:

Dog.prototype

Output:

false
Output 6
console.log(d.hasOwnProperty('name'));

name exists directly on d.

Output:

true
Output 7
console.log(typeof Dog);

Classes are actually functions.

Output:

function
Output 8
console.log(d instanceof Dog);

Checks whether:

Dog.prototype

exists in d's prototype chain.

Yes.

Output:

true
Output 9
console.log(d instanceof Animal);

Checks whether:

Animal.prototype

exists in the chain.

Yes.

Output:

true
Final Output
Rex
Labrador
Rex barks
Rex makes a sound
false
true
function
true
true
Question 1
What does extends compile down to?
class Dog extends Animal {}

Roughly becomes:

Dog.prototype = Object.create(Animal.prototype);

Dog.prototype.constructor = Dog;

This creates the prototype chain:

Dog.prototype
      ↓
Animal.prototype

So methods on Animal.prototype become available to Dog instances.

Question 2
What does super(name) compile down to?
super(name);

Roughly becomes:

Animal.call(this, name);

Meaning:

Animal.call(this, 'Rex');

which executes:

this.name = 'Rex';

inside the child object's context.

Question 3
What are the two real differences between class and constructor functions?

Many people say:

"Classes are just syntax sugar."

Mostly true, but there are some real differences.

Difference 1: Classes cannot be called without new

Constructor function:

function User() {}

User(); // allowed

Class:

class User {}

User();

Output:

TypeError:
Class constructor User cannot be invoked without 'new'

Classes must use:

new User();
Difference 2: Class methods are automatically strict mode
class User {
  sayHi() {
    // strict mode automatically
  }
}

Class bodies run in strict mode.

Constructor functions do not automatically do this.

Interview Answer
extends

Roughly equivalent to:

Dog.prototype = Object.create(Animal.prototype);
Dog.prototype.constructor = Dog;
super(name)

Roughly equivalent to:

Animal.call(this, name);
Two real differences between classes and constructor functions
Classes cannot be called without new
User() → error
new User() → works
Class methods run in strict mode automatically
Constructor functions do not automatically enforce strict mode.

Everything else—instances, prototypes, inheritance, instanceof, method lookup—is still built on JavaScript's prototype system.

You mentioned two differences correctly — but there's a third worth knowing for interviews: classes are not hoisted like function declarations. new Dog() before the class Dog {} line throws a ReferenceError (TDZ, just like let). A constructor function declaration would work fine before its definition. You covered this in the teaching session — just make sure it's in your interview answer too.

</details>

