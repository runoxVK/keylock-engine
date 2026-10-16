# Key–Lock

**One rule, every interaction.** A grid simulation where nothing is scripted: fire, rust, trails, seekers, and chemistry that never settles all fall out of a single dot product.

```
#  #  #  #  #  #  #  #  #  #        tick 1:   s . . . . . g .     the seeker wanders
#  ~  ~  ^  ^  %  %  %  .  #        tick 8:   s s s . g . . .     it finds the trail
#  ~  ~  ^  *  *  %  %  .  #        tick 9:   S g . . . . . .     it reaches the source, and they start eating each other
#  ~  ~  ^  ^  *  %  %  .  #        tick 19:  S . . . . . . .     the seeker is gone
#  #  #  #  #  #  #  #  #  #
     fire eating a crate                     nobody wrote that part
```

---

## The idea

Most simulations are a pile of special cases: *fire burns wood*, *acid eats metal*, *the monster chases the player*. Every new thing means new rules, and every pair of things needs a decision about what happens when they meet.

Key–Lock throws all of that out. Every kind of thing in the world is a **type**, and every type is described by four things:

| | What it is | What it does |
|---|---|---|
| **key** | a vector | how this type acts on others |
| **lock** | a vector | how others act on this type |
| **product** | another type, or none | what appears when this type's lock is used in a reaction |
| **valence** | −1, 0, or +1 | whether this type pulls its bundle toward or away from things |

And there is exactly one interaction: how well one type's key lines up with another type's lock.

$$
A(q, r) = k_q \cdot l_r
$$

Lined up, the lock's owner absorbs the key's owner. Pointing opposite ways, they wear each other down. At right angles, nothing happens. A small dead zone $\varepsilon$ ignores weak alignments, leaving two numbers, the **fit** and the **clash**:

$$
A^+(q,r) = \max(0,\, A - \varepsilon) \qquad A^-(q,r) = \max(0,\, -A - \varepsilon)
$$

That's the whole vocabulary. Everything else is consequences.

---

## What one number does

The same fit does three different jobs, depending on where things are:

| Where | What the fit does | Law |
|---|---|---|
| a free amount, in a cell with things that fit its key | **grips** it, slowing its spread | flow and binding |
| two amounts not in the same bundle | **reacts:** absorption on a fit, erosion on a clash | reactions |
| two amounts in the same bundle | **holds the bundle together** | bundle structure |
| a bundle with a drive | **pulls** it toward what its lock fits | motion |

Write one number in the type table, and you've decided whether two things grip each other, eat each other, hold together, and chase each other, all at once. That's where the surprises come from.

---

## One tick

Every tick, `world.tick` runs seven steps, in order:

1. **Flow:** free amounts spread to their neighbors, slowed wherever they're gripped. A cell sends each neighbor a share of $\tfrac{D}{4} f_q \, e^{-\beta E_q}$, where $E_q$ is how strongly the cell grips $q$.
2. **Reactions:** amounts that meet react at a rate $\kappa \cdot u \cdot w \cdot (\text{fit} + \text{clash})$, clamped so nothing ever goes negative. The product always lands next to the lock, so **a bundle keeps what it absorbs**.
3. **Release:** bundled material that nothing in its bundle holds falls out and becomes free.
4. **Cleanup:** empty cells stop belonging to their bundle.
5. **Split:** cells whose connection has dropped below $\theta$ come apart, and each piece becomes its own bundle.
6. **Dissolve:** a bundle too weak to hold together crumbles back into free material.
7. **Motion:** bundles with drives step toward what they want, or push against whatever blocks them, and react across the boundary.

There's one special type, the **ambient**, which sits at exactly 1 in every cell and never changes. It's the world's only tap and drain: a type whose lock fits the ambient's key produces forever, and a type whose key fits the ambient's lock slowly fades away.

---

## Things nobody programmed

**The halo.** Put a source in the middle of the grid. It taps the ambient to make $s$, which spreads and slowly decays. They balance into a steady glow whose size, about $\sqrt{D_\text{eff} / k}$, appears nowhere in the code. With the default constants, it's about two cells.

**The seeker.** A bundle of $g$ has a drive whose lock fits $s$'s key. It wanders until the faintest trace of the trail reaches it, then climbs straight up the gradient to the source.

**Mutual consumption.** When the seeker arrives, the two eat each other. $e$'s key happens to fit $g$'s lock, and $g$'s key happens to fit $e$'s lock. That wasn't designed. The vectors were chosen so each type holds itself together; the fact that they also fit each other just *follows from the geometry*. The original design document predicted nothing would happen at contact, and the simulation proved it wrong.

**Fire.** Heat clashes with wood, wood's product is embers, embers tap the ambient for more heat. Whether a fire spreads or sputters out is a question you can answer with arithmetic: it spreads when each unit of heat makes an ember that gives off more than one unit of heat before burning out.

**Rust that builds a crust.** In the matter playground, acid eats metal into rust. Rust fits its own lock, so it holds onto itself and stays *inside* the metal, slowly building up. Inspect a corroded plate and you'll find it.

**Chemistry that never settles.** Three types where red eats green, green eats blue, and blue eats red, each turning what it eats into more of itself. Nothing is created or destroyed, nothing ever wins, and invasion fronts chase each other around the grid forever.

---

## Running it

You need Python 3, NumPy, and pygame:

```
pip install numpy pygame
```

| Command | What it does |
|---|---|
| `python main.py` | the tiny world: a source and a seeker, drawn one type at a time |
| `python seeker.py` | the seeker story on a single row, printed tick by tick |
| `python playground.py` | the **matter playground**: fire, water, wood, metal, ice, acid, oil, and more |
| `python playground.py cycle` | the **cycle chemistry**: three colours that eat each other forever |

In `main.py`, **Space** pauses, the **right arrow** steps one tick while paused, **R** restarts, and the **number keys** pick which type to draw.

### The playground

The playground runs the real `world.tick` on a different type table, and gives you tools to see *why* things happen, not just *what*.

| Key | View | What it shows |
|---|---|---|
| `1` | matter | every cell's main type: big glyph for bundled, small for free |
| `2` | bundles | every bundle in its own colour, with borders where ownership changes |
| `3` | one type | how much of the selected type is in each cell |
| `4` | binding | where the selected type would be gripped and held |
| `5` | reactions | how much raw reaction is about to happen in each cell |
| `6` | bonds | connections between a bundle's cells; red ones split next tick |

Point at any cell and the side panel shows everything about it: every free and bundled amount, each free type's binding and how much of it is free to leave, its cohesion, the reactions about to start there, and the bundle it belongs to, including whether it's about to dissolve. Every kind of reaction gets logged the first time it happens, written in the model's own terms.

**Left-drag** paints, **right-drag** erases, the **mouse wheel** picks a type, **B** changes the brush, **Space** pauses, the **right arrow** steps, **N** cycles scenes, **R** reloads, and **C** clears.

---

## Writing your own world

Everything a world does lives in its type table. Here's the tiny world from `type_table.py`:

```python
NAMES = ["ambient", "e", "s", "g"]

KEYS = np.array([
    [0.0, 1.0],   # ambient
    [0.0, 1.0],   # e - lines up with its own lock, so it holds itself together
    [1.0, 0.0],   # s - lines up weakly with the ambient's lock, so it slowly decays
    [0.0, 1.0],   # g - lines up with the second part of its own lock
])

LOCKS = np.array([
    [0.3, 0.0],   # ambient
    [0.0, 0.6],   # e - lines up with the ambient's key, so it produces s
    [0.0, 0.0],   # s - fits nothing
    [1.0, 0.6],   # g - its first part fits s, so it absorbs s and is drawn toward it
])

PRODUCTS = np.array([NONE, 2, NONE, NONE])   # e produces s
VALENCES = np.array([0, 0, 0, 1])            # g is a drive
```

Change one arrow and predict what happens before you run it. That's the best way to learn the system.

**Design tips, learned the hard way:**

- **Fit means grip, absorb, and sense, all at once.** A type can't sense something without also holding onto it and consuming it. A seeker whose lock grips its own trail too strongly will trap the scent in its own cell and never move.
- **Each type has one product,** whatever reacts with it. If water's product is steam, then *anything* water absorbs turns into steam.
- **Signed axes couple opposites.** If hot and cold are two ends of one axis, anything that clashes with heat automatically fits cold. Give opposites separate axes unless you want that.
- **Like interacts with like.** Bundles hold together because their contents fit each other, so two bundles of the same stuff also react when they touch.
- **A product that fits itself never leaves.** It stays bundled inside whatever made it. Sometimes that's a bug, and sometimes it's rust.
- **Loops have gains.** Whether a process runs away or dies out is computable from the table. Compute it.

---

## What it can't do yet

Being honest about the edges is part of the project:

- **Nothing forms.** Bundles only move, shrink, split, and dissolve. Water never freezes, and nothing is ever born.
- **Nothing is contained.** Free material passes straight through walls; a wall can only slow what it grips.
- **Nothing multiplies fast.** Every reaction converts one-for-one, so explosions aren't possible.
- **Nothing falls.** Flow is the same in every direction, so liquids spread like fog instead of pooling.
- **Closed worlds wind down.** Without a source, everything heads toward stillness. That's a theorem, not a bug.

Each of these is a candidate law, and prototypes of containment, product yield, and same-type exclusion have already been tried in the browser.

---

## Files

| File | What's in it |
|---|---|
| `config.py` | grid size, display settings, and the constants $D$, $\beta$, $\kappa$, $\varepsilon$, $\theta$ |
| `type_table.py` | the tiny world's types, and the fit and clash tables computed from them |
| `world.py` | the laws: flow, reactions, release, cleanup, split, dissolve, motion |
| `checks.py` | invariants checked after every tick: the ambient never changes, nothing goes negative, unowned cells hold nothing bundled |
| `render.py`, `main.py` | the tiny world's window |
| `seeker.py` | the seeker story, in text |
| `matter_types.py`, `cycle_types.py` | the playground's type tables, laid out exactly like `type_table.py` |
| `lens.py` | the playground's tools for looking inside the world |
| `playground.py` | the playground itself |

The playground swaps its own table in place of `type_table.py` before importing `world.py`, so the laws run completely unchanged.

The full mathematics, with axioms, definitions, and proofs, is in *The Key–Lock Model*. *Applying the Key–Lock Model to Emergent Simulation* covers where it's headed: a roguelike set in a breached containment facility, where every anomaly is a chemistry and every breach is a chain reaction nobody wrote.

---

*Inspired by Dwarf Fortress, Brogue, Noita, and the stubborn belief that a world should be able to surprise the person who made it.*
