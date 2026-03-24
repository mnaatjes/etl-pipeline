# Slalom v1.0: Design Autopsy & Post-Mortem

**Date:** March 24, 2026  
**Subject:** Architectural Analysis of the Slalom Stream Orchestration Framework  
**Objective:** Identify alternate planning strategies to reduce cognitive load and accelerate system discovery.

---

## 1. Executive Summary
The Slalom framework successfully achieved a "High-Fidelity" Hexagonal Architecture. However, the development process suffered from **Architectural Sprawl**, where the sheer number of abstractions (Ports, Adapters, Managers, Registries) outpaced the developer's working memory. This document explores how we could have built the same system with less "fog."

---

## 2. The Modularization Debate: Monolith vs. Micro-Packages

### Current State:
We used a **Integrated Monorepo**. Everything is in one `src/` tree.
*   **Pros:** Immediate visibility, easy refactoring across layers.
*   **Cons:** High cognitive load; impossible to "forget" a subsystem because it's always one directory away.

### Recommendation: The "Dependency Wall"
Should we have broken subsystems into their own modules? **Yes, but internally.**
Instead of a separate repository (which adds too much overhead for a solo dev), a better approach is **Strict Local Packaging**:
*   **Module A (`slalom-identity`):** Only handles `Address` -> `Coordinate`.
*   **Module B (`slalom-core`):** Only handles the `Gateway` and `StreamManager`.
*   **Benefit:** By treating Identity as a "library" that you import into Core, you force your brain to stop thinking about *how* it works and start only thinking about *what* it returns.

---

## 3. Directionality: Top-Down vs. Bottom-Up

### Our Path: Bottom-Up (Infrastructure-First)
We started with `PosixFileStream`, then moved to `ResourceManager`, and finally built the `Gateway`.
*   **The Problem:** We built "Holes" into the system because we didn't know exactly what the Gateway would need until the very end. This led to the massive Identity Refactor in week 2.

### The Alternate: Top-Down (API-First / RDD)
**Readme-Driven Development (RDD)**: 
1.  Write the `README.md` first. Write the exact code you *wish* you could run: `slalom.read("registry://...")`.
2.  Define the `Gateway` interface methods with `pass`.
3.  **Backfill the "Muscle":** Only build an abstraction when the Gateway literally cannot function without it.
*   **Benefit:** This ensures every line of code has a "User Story" attached to it. You avoid building "just-in-case" features.

---

## 4. Requirement Discovery: The "Spike" Method

### How to better understand "What I Wanted":
You felt overwhelmed because you were **Designing while Coding**. These are two different brain modes.

**The "Spike" Pattern:**
*   **Step 1 (The Spike):** Write a 50-line "spaghetti" script that downloads a file, decompresses it, and prints JSON. No classes, no ports, no hexagonal anything.
*   **Step 2 (The Distillation):** Look at the script and ask: "Which part of this will change if I use S3 instead of HTTP?" -> That becomes an **Adapter**.
*   **Step 3 (The Formalization):** Move only the distilled logic into the Slalom framework.
*   **Benefit:** You prove the *possibility* of the feature before you pay the "Abstraction Tax" to make it permanent.

---

## 5. Simplifying the "Abstraction Tax"

We jumped straight to **High-Fidelity Packets** (Identity, Context, Lineage).
*   **Alternative:** Start with **Primitive Streams** (iterators of raw bytes).
*   Add the `SessionContext` (The Passport) only when you need multi-step tracing.
*   Add the `Identity` (The Lineage) only when you need to prove audit trails.
*   **Lesson:** Abstractions are like debts; only take them out when you know you can pay for them with the value they provide.

---

## 6. Closing Recommendations for "Slalom 2.0"

If you were to start over today, I would recommend this sequence:

1.  **Define the "Golden Path" (Top-Down):** Write 5 test cases that represent the perfect user experience.
2.  **Use ADRs (Architecture Decision Records):** Create a folder `docs/adr/`. Every time you make a big choice (like "Let's use ijson"), write a 3-sentence markdown file explaining *why*.
3.  **Skeleton First:** Implement the `Gateway` and `StreamManager` with complete type-hints but zero logic. Ensure the "Plumbing" works (DI Container) before adding the "Water" (Data).
4.  **Defer Genericness:** Don't build a `ResourceRegistry` until you have at least three protocols. Patterns are easier to see in groups of three.

### Final Verdict
**The Slalom v1.0 build was not a mistake; it was a "Prototype-in-Production."** The complexity you feel is the result of solving hard problems. The next time you feel this "fog," it’s a signal to stop coding and start **Readme-Driven Design.**
