# AI-Testing
*A Finite State Machine (FSM)-based automatic integration test case generation framework*

"Every computer program is a state machine." -- Alan Turing

The AI-Testing framework is a tool designed to automate the generation of integration test cases for software components that can be modeled using Finite State Machines. It helps developers quickly build a comprehensive set of test cases as long as system behavior is defined.

## Basic concept

**System Under Test**
The System Under Test(SUT) is the target software system or service to be tested/verified. It can be modeled as a finit number of states and transitions between these states based on inputs or events. Hince the SUT needs to expose a set of interfaces to receive events or fetch data from outside. The states of the SUT must be observeable.

**State**
The state is a feature vector consist of N properties which describes the SUT from N dimensions to be considered. The states of an SUT are deterministic, finite. The SUT is under a certain state at any time. The transition between 2 states is also deterministic, i.e. the SUT processes eventA under stateX should always transite to stateY.


**Event**
The event is a set of data accepts by the SUT that triggers state change. The data could be 
Finite State Machines are mathematical models used to represent the behavior of systems that can be in a finite number of states and transition between these states based on inputs or events. In the context of software, FSMs can represent the behavior of various components or systems.

Here's how such a framework might work:

Modeling: Developers or testers create models of the system or components under test using Finite State Machines. These models include states, transitions between states, and events or inputs triggering transitions.

Specification: The framework allows users to specify test coverage criteria, such as state coverage, transition coverage, or path coverage. This helps in ensuring that generated test cases adequately exercise different parts of the system's behavior.

Generation: Based on the FSM models and coverage criteria, the framework automatically generates integration test cases. These test cases simulate sequences of events or inputs to drive the system through different states and transitions, ensuring that the system behaves as expected under various scenarios.

Execution: Generated test cases can be executed against the actual system or components under test. The framework may provide utilities to automate test execution and collect results.

Analysis: After test execution, the framework may analyze the system's behavior and compare it against expected outcomes specified in the FSM models. Any discrepancies or failures are reported to users for further investigation.