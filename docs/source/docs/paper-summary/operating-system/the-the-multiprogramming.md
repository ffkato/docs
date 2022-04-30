# The structure of the "THE"-multiprogramming system Summary

[The structure of the “THE”-multiprogramming system](https://dl.acm.org/doi/10.1145/800001.811672)

[pdf](https://www.eecs.ucf.edu/~eurip/papers/dijkstra-the68.pdf)

## Overview

With a publication date of 01 January 1967, this is an old paper before the introduction of UNIX.
Its style, from today's perspective, is more like a "work progress report" than a "research paper".

"THE" is the single-user multiprogramming operating system that the author's team was working on.
By designing and building "THE", they contributed:

* paging for virtual memory abstraction
* semaphore for "mutual synchronization"
* hierarchy for software, which dramatically helps testing/verification
* (provable logical soundness and testable implementation, regarded as the "main contribution" by the author)
  * Dijkstra's fear of debugging with interrupting led to the hierarchy design

## Building Objectives

Dijkstra wrote the following objectives for their design:

1. short turnaround time for short programs
2. economic use of peripheral devices
3. automatic control of backing store, combined with economic use of the processor
4. economic feasibility of applications requiring flexibility of a general purpose computer

## Storage and Memory

This paper introduced "pages" for memory units, and "segments" for information units.
There are "core pages" and "drum pages".

A segment identifier can be used to access "segment variable", which indicates
if a segment it empty and (if not empty) the pages storing it.

* pages can be allocated without strict mapping to segments
* pages correspond to "physical pages" and segments correspond to "virtual pages" today

## Processor and Processes

"THE" uses abstract sequential processes, without speed assumptions, representing
user programs and input/output devices. They use semaphores to cooperate.

## Hierarchy

"THE" has 6 levels.

* Level 0: processor allocation; real-time clock. similar to today's scheduler
  * hides the actual processor
* Level 1: "segment controller", segment -> pages. similar to today's virtual memory
* Level 2: "message interpreter"; keyboards, console
  * as if each process owns "its private conversion console" (achieved via semaphore)
  * the set of commands may be huge, needs level 1 to page out
* Level 3: processes managing "logical communication units" for I/O
  * must name a device to use it
* Level 4: user program
* Level 5: operator (may be a joke)

The specific levels are outdated but the idea of layering is particularly useful for testing.

## Semaphore

This paper invented semaphores.

### P operation

"passering" in Dutch ("passing")

P decreases the value by 1

* potential delay
* if resulting value is $>=0$, continue
* if resulting value is $<0$, wait on this semaphore

### V operation

"vrijgave" in Dutch ("release")

V increases the value by 1

* if resulting value is $<=0$, a blocked process continues
  * order undefined

## Discussion

### Writing Style

It's doubted if a paper written in the same way today would be appreciated.
But there is no "right" or "wrong" way to write a paper. While the researchers
are staying up to running the experiments one day before the deadline, no wonder
the complicated rhetorical devices are skipped.

### Performance Concern

As it was still a work in progress, there was no performance evaluation.

But even in today, the cost of layer crossing is still one of the most expensive
performance overhead.

* Is that number of layers really necessary? How much does it cost to cross all layers?
* How to generalize after introducing multi-users?
* ...
