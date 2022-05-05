# Operating System Introduction

The operating system (OS) is a program that runs programs,
a layer between the applications and the hardware.
It abstracts the resources and provides protection,
so that users and programs can

* safely share resources
* be isolated
* cooperate

An operating system

* must protect programs from each other
* must protect OS from programs
* may protect programs from OS

An OS usually has a scheduler, memory management, file systems, networking stacks, device drivers.

A kernel is

* a subset of operating system
* the software that provides the most critical OS services

For example, UI can be part of the OS, but not in the kernel.

For the purpose of this discussion, the word "kernel" and "OS"
will be used in an un-confusing, interchangeable way.

The key job of OS is providing illusions.

* portable and well-defined environments
  * reality: there are run on machines with different architectures, hardware...
* unlimited processors
  * reality: context switching and scheduling, see `process and thread` section
* unlimited memory
  * reality: virtual memory, see `memory` section

All the illusions hide the underlying complexities.

> Note: the words "usually" and "typically" may appear many times
> throughout the discussion, because there are many "non-standard"
> operating systems, often from academic researches, which
> are quite different from the common ones today

## Architecture Supports OS

Commonly, OS uses supports from the architecture to

* manipulate privileged machine state
  * operation modes
* generate and handle events
  * interrupts, exceptions
* implement concurrency
  * atomic instructions

The discussion on architectures is beyond the scope.
For simplicity, can treat CPU as a state machine that
interacts with other hardware based on its states
(such as the values in the registers) and the
byte-code instructions.

## Kernel Mode

Architecture supports at least two operation modes: kernel and user mode

* kernel mode is also called privileged mode
* a status bit in a protected control register indicates the current mode
* setting the bit is a protected instruction

Protected CPU instructions can only execute in kernel mode. Examples:

* direct I/O access
* setting timers
* memory management
* manipulate protected registers
* halt
* ...

## Events

> Note: The [terms are confusing](https://en.wikipedia.org/wiki/Interrupt#Terminology),
> and they are different for different OS, different versions of the same OS, and different under different contexts.
> Below is one of many definitions.

An event is an unnatural control flow change that stops the execution and may change one of or both context and mode.

* interrupts are caused by an external event, e.g. timer expires, I/O finishes.
* exceptions are caused by executing instructions. CPU requires software to handle exceptions.

Expected events are requested/scheduled by the OS or the programs.

| Events             | Unexpected | Expected           |
| ------------------ | ---------- | ------------------ |
| Exception (sync)   | Fault      | Syscall trap       |
| Interrupts (async) | Interrupt  | Software interrupt |

* exceptions are *kind of* synchronous as the current program will block on faults and the syscalls
* interrupts are *kind of* asynchronous as the kernel can do other work while waiting for interrupts

**Fault**: Hardware detects and reports exceptional conditions, such as page fault, unaligned access, divide by zero.

* must save execution context to restart the faulting process later
* modern OS uses faults for several functionalities, such as debugging, copy-on-write
* fault exceptions are a performance optimization
  * alternatively, detect exceptional conditions by inserting extra instructions
  * harms the performance
* examples:
  * page faults. *see the memory section*
  * program faults with no registered handler
  * dereference null, divide by zero, undefined instruction

**Syscall trap**: *syscall will be explained later*. For example, when a program in user mode executes `SYSCALL` instruction
(where CPU ISA supports `SYSCALL`), it's trapped to the kernel.

**Interrupt**: as above. Interrupts signal asynchronous events coming from hardware or (both software and hardware) timers.
Modern CPU have precise interrupts. They transfers control only on instruction boundaries.

**Software interrupt**: asynchronous system trap ([AST](https://en.wikipedia.org/wiki/Asynchronous_System_Trap)),
asynchronous or deferred procedure call ([APC](https://en.wikipedia.org/wiki/Asynchronous_procedure_call) or [DPC](https://en.wikipedia.org/wiki/Deferred_Procedure_Call)). Can be used to defer work until interrupts resolve...

The machine defines what events it supports, and the kernel defines handlers accordingly.
The handlers execute in kernel mode.

* after booting the system, entry to kernel is a result of an event
* the kernel becomes an "event handler"

When an exception or interrupt happens

* the processor switches to kernel mode, saves the program counter, transfers execution control to the handler
* control (usually) transfers back to user mode and the original context after the handler returns
* for x86 machines, the kernel defines "interrupt" handlers in an Interrupt Descriptor Table (IDT).
  * IDT stores handlers for both exceptions and interrupts
  * each entry, a `gate descriptor`, stores information for all possible "interrupts", including the handler address

### Fault recovery

Sometimes, "fixing" the exceptional condition

* page faults are usually handled by bringing in the missing page
* fault handler resets PC of faulting context to re-execute page-faulting instruction

Sometimes, notifying the process

* fault handler changes the saved context to transfer control to a user-mode handler upon returning
* handler must be registered with the OS
* unix signals or Windows user-mode AsyncProcedure Calls (APCs)
  * SIGALRM, SIGHUP, SIGTERM, SIGSEGV...

### Fault termination

For unrecoverable ones, the kernel may kill the user process

* sometimes, the kernel halts the process, write process state to file, destroy the process
* in Unix, it's the default action for many signals (e.g., SIGSEGV)

For faults in the kernel (the handler can detect if the fault happens in kernel mode)

* they are fatal faults and crash the OS
* Unix panic, Windows "blue screen of death"
* kernel is halted, state dumped to a core file
* this is protecting the system from further damage

### Interrupts expose synchronization problems

* an interrupt can occur at any time
* a handler can interferes with interrupted program
* OS must be able to synchronize concurrent execution
* guarantee short instruction sequences execute atomically
  * e.g. by disabling interrupt, using atomic instructions

-----------------------------------------------------

Read more

* [Early interrupts handler · Linux Inside](https://0xax.gitbooks.io/linux-insides/content/Initialization/linux-initialization-2.html)
* [Exception Handling - Understanding the Linux Kernel, Second Edition [Book]](https://www.oreilly.com/library/view/understanding-the-linux/0596002130/ch04s05.html)
* [What is the difference between IVT and IDT?](https://stackoverflow.com/questions/11540095/what-is-the-difference-between-ivt-and-idt)
* [How signals work internally?](https://unix.stackexchange.com/questions/80044/how-signals-work-internally)
* [15 Interrupts and Exceptions](https://bob.cs.sonoma.edu/IntroCompOrg-x64/bookch15.html)

## Syscall

Program interacts with kernel using syscalls (system calls). It crosses the protection boundary.

CPU ISA provides a `syscall` instruction that

* causes an exception, which vectors to a handler run in kernel mode
* passes a parameter determining which system routine to call
* saves caller state (PC, registers, mode)
* returning from system call restores the state
  * requires architecture support to restore saved state, reset mode, and resume execution

The syscall may block if the required data is not ready.

Specific implementations differ. Other examples: `int` instruction, `sysenter` and `sysexit` instructions.

## Timer

OS uses timers to regain control periodically.

* generate interrupts periodically
* handled by the kernel to decide what runs next
* basis for OS scheduler, `preemption` (OS "forcibly" takes away CPU from a running process)
* prevent infinite loops
* basis for time-based functions

## File Descriptor

Processes has to have a way to name OS data, such as an opened file or a socket.

A file descriptor is an integer that is private to a process.
Kernel keeps track of which integer of which process corresponds to what data.

* a "capability" to operate on a file
* Unix file descriptors, Windows HANDLEs

## Monolithic Kernels vs Microkernels

For monolithic kernels, kernel is one program with everything. The syscall interface is the kernel interface.
The OS runs in kernel space. Linux is an example.

* easier and less overhead for each service to cooperate
* lack of internal isolation

For microkernels, the OS services are user programs. The kernel is minimal to run services. They communicate
via interprocess communication (IPC).

* more isolation
* usually worse performance

Mac OS and Windows do hybrid kernel.

## Resources

* [Operating Systems: Three Easy Pieces](https://pages.cs.wisc.edu/~remzi/OSTEP/) is a free textbook
* [The Linux Kernel documentation](https://www.kernel.org/doc/html/latest/index.html) is the best place for questions related to current Linux kernel, if any
* [kernel - Linux source code - Bootlin](https://elixir.bootlin.com/linux/latest/source/kernel) is the code of Linux kernel implementations
