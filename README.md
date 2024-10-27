# AI-Testing
## A Finite State Machine based automatic integration test case generation and execution framework

## Maintaining test suites becomes challenging
**Increased Code Complexity**: As software evolves, new features, dependencies, and interactions between components are introduced. This complexity makes it harder to ensure that tests cover all scenarios and interactions correctly.

**Test Suite Bloat**: Over time, more test cases are added to accommodate new functionality, which can lead to a large, unwieldy test suite. A bloated test suite is harder to run efficiently, maintain, and update, especially when many tests overlap or become redundant.

**Frequent Code Changes**: In a growing system, code is updated frequently to add features, fix bugs, or refactor existing code. Each change can potentially break existing tests or make them obsolete, requiring frequent updates to the test suite. Many developers choose to "test later" or skip the testing process altogether if deadlines are approchaing.

**Test Code Quality**: As the test suite grows, test code itself can accumulate "technical debt" if not carefully maintained. Poorly written or duplicated tests become harder to debug, maintain, or refactor, compounding with the system's growth.

**Performance and Execution Time**: A large test suite often leads to longer execution times, making it harder to run tests frequently. Developers may avoid running tests if they're slow, which reduces the likelihood of catching issues early and increases the maintenance burden when bugs are detected later.

**Evolving Requirements**: As features evolve or get deprecated, related test cases may need updates, which can be complex if tests are deeply interconnected or rely on deprecated parts of the codebase.

##  AI-Testing addresses these challenges
*"Every computer program is a state machine." -- Alan Turing*

AI-Testing is a framework that generate and execute integration tests based on a Finite State Machine (FSM) model of the system under test. It helps developers quickly build a comprehensive set of test cases as long as system behavior is defined.

### Key Features
- **Automated Test Case Generation**: Automatically generates test cases based on the FSM model, ensuring comprehensive coverage of the system's behavior.
- **Efficient Test Suite Management**: Employs various coverage strategies to cover more code with fewer tests, minimizing redundant and overlapping test cases.
- **Test-Driven Development (TDD)**: Generates test cases automatically when the system changes. Once the design is finalized, the test suites are ready, even before the code is written.
- **Codeless Testing**: Eliminates the need to write test code; the framework generates test code based on the FSM model.
- **Corner Case Discovering**: Automatically identifies corner cases and edge cases that are often overlooked.
- **Characterization Test**: Unsure of the expected behavior of a system? AI-Testing can help characterize the system's behavior.
- **Extensibility**: The framework is extensible and can be highly customized to meet specific testing needs.


## Basic concept

**System Under Test**
The System Under Test (SUT) is the target software system or service to be tested or verified. It can be modeled as a finite set of states and transitions between these states, based on inputs or events. Therefore, the SUT must expose a set of interfaces to receive events or retrieve data from external sources. The states of the SUT must also be observable.

**State**
A state is a feature vector consisting of $N$ properties, describing the SUT across $N$ dimensions. The states of an SUT are deterministic and finite; at any given time, the SUT occupies a single, specific state. Transitions between two states are deterministic as well; for example, if the SUT receives `eventA` while in `stateX`, it should always transition to `stateY`.


**Event**
An event is a set of data accepted by the SUT that triggers a state change. For example, an event could be a request sent to the SUT. Although the values of data might be unlimited, we should abstract them into a finite set of equivalence classes. For instance, an "add new user" event may have a `username` field, which can be any string. However, we can categorize it into equivalence classes like `valid` or `invalid`. For more granular control, `invalid` could include classes like `too long`, `contains invalid characters`, or `already exists`, etc. The specific values (e.g., "Alice" or "Bob") are not relevant within these classes.

**Finite State Machine**
The SUT can be modeled as a Finite State Machine (FSM) with a finite number of states and transitions as represented as a 4-tuple: $M=(Q,  \Sigma, \delta, q_0)$
Where:
- $Q$ is a finite set of states
- $\Sigma$ is a finite set of input symbols (events)
- $\delta$ is the transition function, typically defined as $\delta: Q \times \Sigma \rightarrow Q$. This function specifies the next state given the current state and input event. When the SUT implements this transition function, we also consider interactions between the SUT and external components. For example, the SUT might send a response upon completing event processing or issue notifications to downstream systems.
- $q_0 \in Q$ is the initial state of the SUT, usually a clean system just after boot.


We can reasonably assume the SUT is a **Deterministic Finite Automaton (DFA)**, meaning each state and triggering event corresponds to exactly one transition, so the transition function $\delta$ is deterministic. However, this does not imply that there is only one path from a source state to a target state; different events applied to the same source state may lead to the same target state. When considering sequences of events, the number of paths from a source state to a target state increases even further.

The SUT may also rely on external data sources to determine the next state. For example, a loan system might need to query a user's credit score to decide whether to approve or reject a loan request. Similarly, most systems load configuration files from disk when they start processes. While such data is independent of the SUT's internal state, it still needs to be considered when generating test cases, as it impacts state transitions.


## How does it work
**Test Generator**
The test case generator creates test cases based on the state transitions defined in the finite state machine graph. The test case follows the GIVEN-WHEN-THEN style, the source state is the GIVEN, the trigger event is the WHEN, and the target state is the THEN. The directed pair of transitions (the target state of the 1st transition is the source state of the 2nd transition) links a path, in which the state changes are continued. So we can combine a series of test cases in a chain like GIVEN-WHEN-THEN-WHEN-THEN..., which saves a lot of repeated work of making the system to a certain state and testing the behavior under that state.
There are multiple strategies to generate test cases, including but not limited to node coverage, edge coverage, and path coverage. Node coverage ensures that all states in the FSM are tested, edge coverage focuses on testing all transitions, and path coverage aims to test all possible paths. For example, in a simple flowchart, node coverage would test each decision point, edge coverage would test each transition between points, and path coverage would test every possible route through the flowchart. The programmer can customize their own strategy by extending the `Strategy` class.
The test cases are generated in a format that can be executed by a test runner, such as JUnit or PyUnit. They can also be written in a human readable format , such as Gherkin or Cucumber to be review and operated by non-technical people. Classes derived from `CaseWriter` are responsible for writing test cases in different formats.

```{mermaid}
flowchart TD
    D[/"Design Document  fa:fa-file"/]
    A("API list fa:fa-list")
    S(("State list fa:fa-list"))
    M[["State Transitions"]]
    G["Generator fa:fa-gears
    Generates test scripts
    base on the state machine"]:::ait-process
    T[\"Test Cases  fa:fa-check"\]:::test-script
    CA[\Write executable test scripts/]
    CB[\Write  human readable test scripts/]
    classDef ait-process fill: #f96
    classDef test-script, stroke:green

    D-->A-->M
    D-->S-->M
    M-->G
    G-->SA((Strategy A))
    G-->SB((Strategy B))
    G-->SC((Strategy C))
    SA-->CA
    SB-->CA
    SC-->CA
    SA-->CB
    SB-->CB
    SC-->CB
    CA-->T
    CB-->T
```

**Characterization Test**
As the system evolves, it becomes increasingly complicated to obtain a complete and accurate state machine. *Characterization test* is reverse engineering a system to work out a state machine graph, particularly useful for legacy systems. The `Explorer` process begins from a given state with a set of defined events. It tries all the events on the known states and repeats this process until no new state is discovered. For instance, if the system starts in State A, the test will apply all possible events to see if it transitions to new states like State B or State C, and continues this until all states are explored.
The *characterization test* assumes the current system is correct, even if the behavior is not fully worked as designd or is hard to understand. It provides a baseline of the system's behavior, which can be used to compare against future changes. The test generates a state machine graph by observing the system's behavior, it may discover many corner cases which are never thought of before.

```{mermaid}
flowchart TD
    A("API list fa:fa-list")
    S(("Initial state"))
    E["Explorer fa:fa-gears
    Repeatedly applies all the events on all the known states"]:::ait-process
    M[["State Transitions"]]

    classDef ait-process fill: #f96

    A-->Exploring
    S-->Exploring
    subgraph "Exploring"
    direction LR
    E--events--->SUT
    SUT--states--->E
    end
    Exploring--->M

```
