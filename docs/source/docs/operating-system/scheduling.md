# Scheduling

OS needs to determine which jobs to run, which ones to delay.

## Goals

Scheduling algorithms can have many different goals, sometimes conflicting:

* utilization: maximize useful CPU usage
* throughput: maximize the number of jobs completed per unit time
* turnaround: minimize the turnaround time of each job
  * $turnaround = t_{waiting} + t_{running} = t_{complete} - t_{arrive}$
* waiting: minimize the average time on waiting queues
* response: minimize the average time on ready queue
* fairness: no starvation
  * a job starves when it can't progress: others has resources it needs thus blocking it
* priority: some processes are more critical

For batch systems like supercomputers, they usually prefer better job throughput and turnaround time.
For interactive systems like desktops, they usually focus on responsiveness to user interactions.

(Starvation is usually a side effect of scheduling or synchronization,
such as when a high priority process prevents another from running,
or one thread can't acquire a lock)

A CPU-bound process uses the full quantum while an IO-bound process uses a part of a quantum:
it issues the I/O request and blocks.

CPU utilization is the fraction of useful work. Context switching is not useful work.
Simply speaking, the OS should schedule the CPU-bound process to use the time when the
IO-bound ones are blocked, so that the work (computation and I/O) overlaps.

## Scheduler

Scheduling usually happens when

* job changes from running to waiting (see `process and thread` section for process states)
* job changes from running to ready, e.g. interrupt
* job is created or exited

For preemptive systems, scheduler can change the current running job via involuntary context switching.
For non-preemptive/cooperative systems, scheduler can only schedule when a job terminates or explicitly blocks (e.g. I/O),
which is voluntary context switch.

An OS can have multiple levels of schedulers.

* long-term scheduler: which jobs to admit/keep in the memory
  * relatively infrequent
  * large overhead of swapping a process in/out memory
* short-term scheduler: which job to context switch after end of CPU quantum
  * relatively frequent
  * must minimize the overhead of context switching and queue manipulation

## Policies

There are different scheduling policies/principles.
No best policy to achieve all goals.

`First-come first-served (FCFS), first-in first-out (FIFO)`

* run the jobs in the order of arrival
* no starvation

Problems

* potentially large average waiting time
  * one long job will delay all jobs after

`Shortest job first (SJF)`

* run the job with the smallest expected CPU burst
* minimize the average waiting time (and **often** the turnaround time, not always)
* preemptive SJF is called shortest remaining time first
  * if a new job comes with shorter CPU burst than the current one, switch to it

Problems

* potential starvation
* can't know CPU burst exactly in advance in practice

`Round Robin (RR)`

* run each job with equal time slice (CPU quantum) and then preempt
  * or until it exits or blocks
  * circular FIFO
* fair, no starvation

Problems

* many bad cases, such as
  * 100 jobs requiring 101 unit time, but each time slice is 100
  * 2 jobs requiring 100 unit time, while each time slice is 10
* unnecessarily increasing waiting time (and turnaround time)
* wasted time on frequent context switches

`Priority`

* run the next job with highest priority
* both preemptive and non-preemptive
* "age" the jobs
  * increase priority for waiting jobs
* can also decrease priority with high CPU consumption

Problems

* potential starvation without "age"

`Multiple-level feedback queues (MLFQ)`

* combine different algorithms
* multiple queues with different priorities
* use RR on the same queue
* moves jobs among queues, namely computes the priorities, based on feedback
  * such as CPU consumption, job type changes (interactive jobs become I/O intensive ones)

## Scheduling in Practice

With multiprocessors, affinity scheduling happens when the scheduler tries to assign one job
to one processor, because of the low possibility of cache missing and so on.
But strict affinity may hurt load balancing.

In real-time systems, the scheduler also needs to ensure it meets all the deadlines.

* earliest deadline first scheduling (EDF)
* least slack time scheduling (LST)

Linux uses [CFS scheduler](https://kernel.org/doc/html/latest/scheduler/sched-design-CFS.html), which is based on `virtual runtime`.

Read More

* [Processor affinity - Wikipedia](https://en.wikipedia.org/wiki/Processor_affinity)
* [Borrowed-virtual-time (BVT) scheduling: supporting latency-sensitive threads in a general-purpose scheduler: ACM SIGOPS Operating Systems Review: Vol 33, No 5](https://dl.acm.org/doi/10.1145/319344.319169)
