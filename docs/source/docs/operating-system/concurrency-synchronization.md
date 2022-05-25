# Concurrency and Synchronization

Recall `concurrency` means multiple threads or processes running together, not necessarily at the same time.
Context switching may make them appear to run together, but essentially each job is
executed for a short period of time and switched.

If concurrent threads/processes are reading and writing to a shared resource,
their accesses need `synchronization`--to be controlled to avoid
undefined behaviors, broken invariants, and data loss.

Real `parallelism` requires multiple processors/cores: multiple jobs execute at the same time physically.
Given physical parallelism, even under non-preemptive scheduling
(each job runs until exit), still needs synchronization control.

The code in this articles only servers as concept demonstration. Real implementation will usually
be more complicated.

## Race Condition

`Race condition`, or `data race`, happens when concurrent threads/processes access a shared resource without synchronization.

* threads A, B both write to value `v`
  * `v = v_A`
  * `v = v_B`
* at the end, no ones know `v`'s value
  * A can overwrite B's value, and vice versa

## Critical Section

For such shared resources, the section of code that requires mutual exclusion
for accesses is a `critical section`:

* mutual exclusion
  * at any time, only one thread in critical section
* progress
  * one thread can eventually enter critical section when no one is in
* bounded waiting
  * if one is waiting for another to enter, it will enter the critical section under bounded waiting time
  * no starvation
* performance
  * the overhead of entering/exiting should not be higher than the work done
    * in the extreme case, program can put everything in one critical section
    * this usually achieves the above goals, but hurts performance too much

Properties:

* safety: bad things do not happen
  * mutual exclusion
* liveness: good things do happen
  * progress
  * bounded waiting
* performance

The safety and liveness properties hold for each enter/exit of critical sections.
The performance property depends on the whole workflow.

## Semantics

Different hardware, OS, programming languages and so on provide different synchronization primitives,
and different semantics for the primitives. It's the programmer's duty to know the semantics
of primitives available in specific programming environments.

Below is one of many such semantics. Not trying to be loyal of any, but try to make it
easy to follow and understand.

## Lock (Mutex)

A lock is an object with two operations. They are paired.

* `lock()`
  * enter a critical section
  * only one thread returns (and continue to the critical section)
  * others block on this call
* `release()`
  * exit a critical section
  * wakes up another blocked thread, if any

Recall the OS needs the support from the architecture for atomic operations. The two operations above
must be atomic themselves.

One of the most basic lock is a spinlock that "spins" in a loop, which breaks when the calling thread acquires the lock.
The "infinite" loop limits its performance.

```cpp
// this needs to be hardware atomic instruction
// otherwise context switching inside this call breaks the critical section
bool test_and_set(bool *flag) {
  bool old = *flag;
  *flag = 1;
  return old;
}

struct lock {
  int held = 0;

  void lock() {
    // successfully get the lock when returning 0, i.e. it was not held
    while (test_and_set(&(this->held)));
  }

  void release() {
    this->held = 0;
  }
};
```

Another way is by disabling the interrupts (disables context switching),
and sometimes is called a "mutex" to distinguish it from the "spinlock".
The threads block on a queue of the mutex, and is waken up by `release()` calls.

```cpp
struct lock {
  int held = 0;
  queue q;

  void lock() {
    disable_interrupts();
    while (this->held) {
      this->q.push(current_thread);
      block(this->q);
    }
    this->held = 1;
    enable_interrupts();
  }
  void release() {
    disable_interrupts();
    if (!this->q.empty()) {
      thread t = this->q.pop();
      unblock(t);
    }
    this->held = 0;
    enable_interrupts();
  }
};
```

Disabling interrupts can only work for programs with one kernel thread,
as it's insufficient for multiprocessors.

Consider the overhead of the procedure calls of other types of locks, spinlock may not always be worse.

In practice, programs should directly use the locks provided in specific programming environments.

## Semaphore

Semaphore is another synchronization primitive. It is initialized with a value,
which is usually the number of allowed concurrent threads.

* `wait()` or `P()`
  * block if value is zero
  * decrement
* `signal()` or `V()`
  * unblock a blocked thread, if any
  * increment
    * the value is stored for the next thread calling `P()`

```cpp
struct Semaphore {
  int value;
  queue q;

  Semaphore(int value) : value(value) {}

  wait() { // P
    disable_interrupts();
    if (value == 0) {
      q.add(current_thread);
      block();
    } else {
      value = value – 1;
    }
    enable_interrupts();
  }

  signal() { // V
    disable_interrupts();
    If (!q.empty()) {
      thread t = q.pop();
      unblock(t);
    } else {
      value = value + 1;
    }
    enable_interrupts();
  }
};
```

* Binary/Mutex semaphore
  * initialized to 1
  * same as a lock/mutex
* Counting/General semaphore
  * initialized value greater than 1
  * multiple threads can pass
  * protects some resources that
    * either have multiple units
    * or allow un-synchronized accesses to some degree

See the `paper summary for The structure of the "THE"-multiprogramming system` to learn where semaphores were invented.

## Use Locks

Generally, need locks to protect the data that will be accessed concurrently and at least one access is writing.

Another approach is to directly convert one-threaded programs to multi-threaded ones by adding locks
to the data access functions/code sections.

## Use Semaphores

Use semaphores to synchronize reading and writing.

```cpp
// number of readers
int readers = 0;
// protects readers
Semaphore sem_readers(1);
// coordinate writing/reading
Semaphore sem_wr(1);

// only one writer
// no reading while writing
void writer_job() {
  sem_wr.wait();
  do_write();
  sem_wr.signal();
}

// multiple readers
// no writing while reading
void reader_job() {
  sem_readers.wait();
  readers += 1;
  if (readers == 1) {
    // possibly writing
    sem_wr.wait();
  }
  sem_readers.signal();
  // no synchronization on reading
  do_read();
  sem_readers.wait();
  readers -= 1;
  // any reader can be the last reader
  if (readers == 0) {
    // unblock writer if any
    sem_wr.signal();
  }
  sem_readers.signal();
}
```

With semaphore's "history", can use it to coordinate tasks with multiple resources.

```cpp
List l; // size = N
Semaphore sem_l(1); // protects the list
Semaphore n_empty(N); // number of empty buffers
Semaphore n_ready(0); // number of buffers ready to consume

void producer_job {
  while (true) {
    Resource r = do_produce();
    n_empty.wait(); // wait and decrement one empty buffer count
    sem_l.wait();
    l.add(r);
    sem_l.signal();
    n_ready.signal(); // increment one ready buffer count
  }
}

void consumer_job {
  while (true) {
    n_ready.wait(); // wait and decrement one ready buffer count
    sem_l.wait();
    Resource r = l.pop();
    sem_l.signal();
    n_empty.signal(); // increment one empty buffer count
    do_consume(r);
  }
}
```

## Use Condition Variables

A condition variable (CV) is commonly provided by programming languages for synchronization
where a condition needs to satisfy to make progresses.
It is usually used with a lock.

* `wait()`
  * calling thread must hold the lock
  * add the calling thread to CV's queue
  * CV "releases the lock for" the thread
* `signal()`
  * remove a thread from CV's queue
    * if empty, nothing happens
  * the removed thread will hold the lock, and releases later
    * in "Mesa" semantics, the thread is put on the ready queue and the caller continues with the lock
* `broadcast()`
  * as if everyone on the queue receives a signal

The waiting thread is responsible for checking the condition.
Being removed from the waiting queue does not mean the condition
is satisfied, but may due to `spurious wakeup`.

```cpp
int n_read = 0, n_write = 0;
Lock l;
CV can_read(l), can_write(l);

void read_job() {
  l.lock();
  while (n_write != 0) can_read.wait();
  n_read += 1;
  l.release();

  do_read();

  l.lock();
  n_read -= 1;
  if (n_read == 0) can_write.signal();
  l.release();
}

void write_job() {
  l.lock();
  // can write only when no reading/writing
  while (n_read != 0 || n_write != 0) can_write.wait();
  n_write += 1;
  l.release();

  do_write();

  l.lock();
  n_write -= 1;
  can_read.broadcast();
  // here, a writer can wake up with or without readers waking up
  // example of why need to re-check the condition
  can_write.signal();
  l.release();
}
```

The idea of CV is invented in [Monitors: an operating system structuring concept](https://dl.acm.org/doi/10.1145/355620.361161).

## Locking Granularity

The most coarse locking granularity happens when one single lock protects all the data.
No data race will ever happen, neither do parallelism.

With finer granularity, locks protects smaller number of data so that other processes/threads
can access the non-conflict ones concurrently.

Finer granularity generally allows more parallelism, but not necessarily better,
due to more places for the programmers to make mistakes (such as deadlock, introduced later),
and more frequent and even unnecessary overhead.

Generally, use coarse-grained locks first. After ensuring no deadlocks (or other issues),
find places for parallelism opportunities if necessary.

## Avoid Synchronizations

Managing synchronizations is overhead to the application and prevents parallelism.
Sometimes, one atomic instruction is sufficient. Programming languages
such as Golang provides atomic package.
Sometimes, can restructure the program to avoid the need to synchronize,
or simply avoid sharing and make threads independent.

But don't allow data race even the program does not require accuracy,
because it is undefined behavior and very hard to debug.

## Read Copy Update (RCU)

With less frequently written data, can only serialize the updates

```cpp
data *ptr;
Lock l;

void read() {
  ptr->do_read();
}

void update(new_data new_info) {
  l.lock();

  // readers can still read while updating
  data *new_ptr = do_copy(ptr);
  do_update(new_ptr, new_info);

  // this is the serialization point
  // depends on architecture,
  //   readers that access ptr after this instruction will
  //   access updated data
  ptr = new_ptr;

  l.release();
}
```

Read more

* [What is RCU? – “Read, Copy, Update” — The Linux Kernel  documentation](https://www.kernel.org/doc/html/latest/RCU/whatisRCU.html)
* [CS 261 Notes on Read-Copy Update](https://www.read.seas.harvard.edu/~kohler/class/cs261-f11/rcu.html)

## Deadlock

Deadlock may happen when a set of processes wait for each other, usually when
competing for limited resources or are incorrectly synchronized

1. mutual exclusion: at least one resource can only be shared limitedly
2. hold and wait: at least one process holding some resource and waiting for another
3. no preemption: can't preempt that resource
4. circular wait: n processes ($n >= 2$) P1, P2... Pn such that P1 waits for P2, P2 waits for P3, ...Pn waits for P1

All conditions must meet for a deadlock to exist. Deadlock **may** happen if all met.

### Resource Allocation Graph (RAG)

A graph used to track locks.

A direct edge from a process to a resource
represents the process's one request to hold that resource.

A direct edge from a resource to a process
represents the allocation of the resource.
Each resource has a limited number of out-degrees (allocation units).

Deadlock can't appear if no cycles, and **may** exist otherwise.

### Waits-for Graph (WFG)

If resources only have one unit and processes can only request one
resource at one time, WFG is a simpler graph to track locks.

A direct edge from process A to process B means A requests for
a resource hold by B.

Deadlock can't appear if no cycles, and exist otherwise.

### Handle Deadlocks

#### Prevention

Break one of the deadlock conditions (usually when programming)

1. not mutually exclude the resources (may not be practical), such as making "infinite" copies
2. restrict the processes to hold only one resource, or only allow request when not holding
3. preempt
4. use one lock for everything (may not be practical); impose resource request ordering: must hold lock A before B

#### Detection and Recovery

Detect cycles in the resource graphs and fix

detection is expensive

* deadlock can be rare
* may not worth checking all the time
* can only start detection when
  * deadlock is expected to happen more frequently
  * affect more processes

recovery can be expensive

* abort
  * all processes
    * start over
    * reboot
  * one process at a time
    * detect the problematic processes
    * stop one at a time
    * detect again
    * until no deadlock
  * partial order
    * resource manager somehow keeps track of holding
    * abort if detecting cycles before happening
* preempt
  * need to know exactly the problematic resources and what processes are holding them
  * to maintain correctness, may need to rollback processes' states
  * need to avoid starvation

Detection-based solutions are usually unrealistic.

-----------------------------------------

The most "efficient" way is to "ignore" deadlocks, because it's too expensive
to keep track of everything all the time, and in reality well-tested programs
rarely cause deadlocks. Even if it happens, it's easier to restart the processes.

## Other Common Atomic Instructions (Optional)

Besides the `test-and-set` instruction mentioned, there are others such as

`compare-and-swap`

* compares the values with our known value
* updates to new value only if old value matches our provided known value

`fetch-and-add`

* increment a value by certain amount atomically

They also need "spinning" if used to implement locks
