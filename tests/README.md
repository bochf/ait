# Test Finite State Machine

Consider a simple system consisting with 5 events, 4 states and their transistions described below:

```python
state_transitions = {
    "Start": {
        "Initialize": "Running",
        "Reset": "Start"
    },
    "Running": {
        "Pause": "Paused",
        "Stop": "Stopped"
    },
    "Paused": {
        "Resume": "Running",
        "Stop": "Stopped"
    },
    "Stopped": {
        "Reset": "Start"
    }
}


   ┌──Reset ─┐
   │         │
   │     ┌───▼───┐
   └─────┤ Start ◄─────────────┐
         └───┬───┘             │
             │                 │
           Init              Reset
             │                 │
         ┌───▼───┐        ┌────┴────┐
   ┌─────►Running├──Stop──► Stopped │
   │     └───┬───┘        └────▲────┘
   │         │                 │
Resume     Pause               │
   │         │                 │
   │     ┌───▼───┐             │
   └─────┤Paused ├───Stop──────┘
         └───────┘
```
