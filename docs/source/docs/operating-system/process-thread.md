# Process and Thread

A program is a static entity with the potential for execution.

A process (task, job, sequential process) is the unit of execution and scheduling,
the OS abstraction for a program in execution with its dynamic execution context,
an "instance" of a program.

For a single-core machine, the illusion of running multiple processes together
is created by context switching and giving quantum of CPU time to each process.

* this is a preemptive multitasking OS
* most of today's systems do so
* non-preemptive/cooperative systems, in contrast, allows programs to run until termination or blocking on I/O

## Execution State

A process has an execution state

* Running: executes instructions on the CPU
  * has CPU control
* Ready: waits to be assigned to the CPU
  * ready to execute
  * CPU is controlled by another process
* Waiting: block on async event, e.g. I/O

|                |           |                      |                        |
| -------------- | --------- | -------------------- | ---------------------- |
| **New**        | → create  | **Ready**            |                        |
|                |           | ↓ Deschedule/Preempt | ↖ I/O done, etc.       |
|                |           | ↓ ↑                  | **Waiting**            |
|                |           | ↑ Schedule           | ↗ I/O, page fault etc. |
| **Terminated** | ← process | **Running**          |                        |

If there are multiple "ready" processes, it's the scheduler's job to decide
which one to run. See the *scheduling* section.

## Process Control Block

The data structure representing a process in OS is Process Control Block (PCB)

* contains all information about a process
* stores hardware execution states when the process is not running
  * stack pointer (SP) keeps track of the execution stack for procedure calls
  * program counter (PC) indicates the next instruction
  * values in the general-purpose registers
* the stored states are used to restore the execution

PCB typically has

* process ID (PID)
* execution state
* user ID
* PC
* register values
* address space (virtual memory mapping etc.)
* open files
* other information for scheduling, accounting ...

OS dynamically allocates and initializes PCB when creating a process, puts on ready queue,
and moves it to different state queues based on different states.
There may be multiple waiting queues for different async events (disk, console, timer, network, etc.).
PCB is de-allocated when process terminates.

The implementation is OS-dependent.

## Context Switch

For a running process, the hardware states are (naturally) in the hardware, such as PC, SP, registers.

For others, OS stores the states into PCB. When OS starts to execute such a process again,
it load the states from the PCB to the hardware.

Context switch is the process of saving and changing the hardware states from one process to another.
This usually happens very frequently.

1. run process A
2. save A's states to A's PCB
3. load states from B's PCB
4. run process B

* pure overhead
* OS tries to keep the overhead minimal
* invalidated caching etc. due to changed virtual memory mapping also causes overhead

Read more

* [Evolution of the x86 context switch in Linux MaiZure's Projects](https://www.maizure.org/projects/evolution_x86_context_switch_linux/)

## Typical Memory Space

A typical memory layout for a process address space:

| high address         |
| -------------------- |
| stack                |
| ↓ (growth direction) |
|                      |
|                      |
|                      |
| ↑ (growth direction) |
| heap                 |
| bss                  |
| data                 |
| text                 |
| **low address**      |

* `stack` usually stores the information for procedure calls
* `heap` usually is not tied to specific procedures
* `bss` (block starting symbol) is uninitialized global variables, some OS initializes to zero before execution
* `data` contains the initialized data, stored in the program
* `text` contains the code, stored in the program

The `bss`, `data`, and `text` sections have fixed-sizes that are stored in the program.

Processes have isolated private address space

* each process can access "any address" in the virtual memory
* the mapping to physical memory is managed by OS
* no direct way to access other process's memory

See the *memory* section.

### Stack Frame (optional)

The `stack` typically stores stack frames, aks activation records

* one for each procedure call (function call)
* each stack frame stores
  * return address
  * caller's stack frame address
  * local variables
  * function arguments
  * ...

Calling conventions depend on architectures, machines...

One example:

* caller-saved registers
  * function called can change freely
* callee-saved registers
  * restore to original value after returning from a function
* SP, stack pointer, points to the stack base
  * recall stack grows downwards
  * next function call's stack starts from SP
* FP, frame pointer, points to the old SP
  * almost the "head" of current stack frame
* "above" FP
  * function arguments
  * return address
  * old FP
* "between" FP and SP
  * callee-saved registers (to restore later)
  * local variables

Again, details depends.

## Manage a Process

Few examples for process-related syscalls.

Creation: the parent defines or donates resources and privileges to its children; parent can wait for the children processes or continue in parallel.

* Windows [CreateProcess()](https://docs.microsoft.com/en-us/windows/win32/procthread/creating-processes) creates a new process
  * creates and initializes a PCB
  * creates and initializes an address space
  * loads the program specified by a function argument to the address space
  * copies command arguments to the address space
  * initializes the saved hardware states to start execution, usually at main
  * places the PCB on ready queue
  * returns a struct to the parent
* Unix fork() creates a copy of current process
  * creates and initializes a PCB
  * creates a new address space
  * copy entire of current address space to it
  * initializes the kernel resources with a copy, such as file descriptors
    * they are the same opened files, but independent
  * places the PCB on ready queue
  * returns 0 to the child
  * returns the child's PID to the parent
  * see [clone()](https://man7.org/linux/man-pages/man2/clone.2.html) for more

Exec

* Unix exec() replaces current process with another
  * stops the current process
  * loads the program to current address space
  * initializes the hardware states and arguments
  * places the PCB on ready queue

Exit

* Unix exit(int status), Windows ExitProcess(int status)
* free resources and terminate
  * terminate threads
  * close files/connections
  * de-allocate memory (and clean up paged out memory)
  * delete PCB
* conventionally, `status = 0` means success, and failure otherwise

Wait

* Unix wait()
  * Suspends the current process until any child process terminates
* Unix waitpid(), Windows WaitForSingleObject()
  * suspends until the specified child process terminates

## Inter-Process Communication (IPC)

Processes can interact via

* shared files
  * just write and read the same file; most basic
* passing messages through kernel
  * e.g. [pipe](https://man7.org/linux/man-pages/man2/pipe.2.html), [fifo (named pipe)](https://man7.org/linux/man-pages/man7/fifo.7.html), [socket](https://man7.org/linux/man-pages/man7/unix.7.html)
* shared memory
  * e.g. [linux shm](https://man7.org/linux/man-pages/man7/shm_overview.7.html)
* signals etc.
  * e.g. [send signal](https://man7.org/linux/man-pages/man2/kill.2.html), [signal actions](https://man7.org/linux/man-pages/man2/sigaction.2.html)

## Thread

A process can be either single-threaded, or multi-threaded,
and its address space, file descriptors etc. are shared by its threads.

A thread has a stack, registers, and a PC. Threads' stacks can be accessed by the others within same process.
It's a sequential execution flow within a process, a unit of scheduling (a process is now a container of threads).
The data structure representing a thread is thread control block (TCB).

Multi-threading can help

* handle concurrent events
  * `concurrency`: tasks running in an overlapping manner, may or may not at the same time
  * overlap I/O with computation
* run parallel programs
  * `parallelism`: tasks running at the same time
  * requiring multiple CPUs or cores
* make certain programming easier
* switching among threads may be cheaper than among processes

Kernel-level threads (native or non-green threads) are managed by the OS

* informed scheduling: integrated with the OS
  * both user- and kernel-space stacks
  * thread management needs trapping into the kernel: overhead
  * needs to be generic to support general needs
    * usually comes with heavy features, potential overhead
  * slower to create, manipulate, synchronize
  * real parallelism capability, better for I/O
* Windows: threads
* Solaris: light process (LWP)
* POSIX: pthreads PTHREAD_SCOPE_SYSTEM

(terminology: `kernel thread` can literally mean the threads in the kernel that typically is a native thread)

User-level threads (green threads) are managed by the runtime, namely the user-level library

* uninformed scheduling
  * use procedure calls to create, switch between, synchronize threads
  * faster to create, manipulate, synchronize
  * invisible to the OS
    * appears as one thread
    * cannot use multiprocessors and thus no parallelism
  * runtime thread manager needs to communicate with the kernel
    * may ask OS for periodical interrupts
  * fate-sharing
    * commonly use non-blocking syscalls to avoid blocking other threads
    * page faulting blocks all threads
  * much less overhead than kernel-level threads, typically 100 times faster
    * can have specifically optimized scheduling policy
* POSIX: pthreads PTHREAD_SCOPE_PROCESS

n:m threading

* n user threads for m k-threads
* kernel-level threading is 1:1
* user-level threading is n:1
* hybrid: multiplexing n user threads on m kthreads
  * combine for the benefits (parallelism and self-management)
  * old problems: blocking, overhead...
  * difficult to ensure m kthreads running on separate processors/cores
    * runtime scheduler doesn't know exactly if one kthread runs
  * difficult to ensure relative priority
    * Linux has dynamic priority by default
    * need to work with OS interface and policies

Non-preemptive threads must voluntarily give up CPU.
Preemptive scheduling uses interrupts for involuntary context switches.

Because threads can access the same memory, the execution is out of program's control and switching happens arbitrarily,
program needs to use synchronization to control cooperation, usually by restricting interleaving executions.
See `synchronization` section.

Read more

* [An Introduction to programming with threads - Andrew D. Birrell](https://www.hpl.hp.com/techreports/Compaq-DEC/SRC-RR-35.pdf)
