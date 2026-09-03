# Execution Boundary

Algo-TF creates deterministic decisions and child order intents. It does not expose buy, sell,
trade, or order-placement API endpoints. The execution-engine adapter is the only component
permitted to submit an intent across the broker boundary.

Design-bundle imports must declare `ROOT_EXECUTION_ENGINE_ONLY` and `auto_send: false`. The
compiler rejects any other boundary declaration. A compiled mandate remains proposal-only until
explicit approval and arming; the scheduler then persists an intent for the execution engine to
independently validate.
