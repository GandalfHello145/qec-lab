# PyMatching integration

QEC-Lab keeps PyMatching as an optional dependency. The base package remains a
small dependency-free mathematical scaffold, while the `matching` extra enables
minimum-weight perfect matching decoding.

Install with

```bash
pip install -e .[matching]
```

## Adapter design

The internal `MatchingGraph` object stores string-labelled detector nodes,
boundary nodes, and weighted fault edges. The PyMatching adapter converts this to
`pymatching.Matching` as follows:

- finite detector nodes receive consecutive integer indices;
- an edge between two finite detector nodes becomes `Matching.add_edge`;
- an edge with one finite endpoint and one boundary endpoint becomes
  `Matching.add_boundary_edge` using PyMatching's virtual boundary convention;
- each QEC-Lab `fault_id` is mapped to an integer PyMatching `fault_ids` value;
- decoding returns QEC-Lab fault-id strings.

This keeps high-level scientific output readable while using PyMatching's fast
MWPM implementation internally.

## Perfect syndrome repetition-code decoding

```python
from qec_lab import decode_repetition_syndrome

faults = decode_repetition_syndrome(
    syndrome=(0, 1, 1, 0),
    physical_error_rate=0.1,
)
print(faults)
```

Expected result:

```text
('x2',)
```

## Phenomenological repeated-syndrome decoding

For measurement errors, QEC-Lab decodes detection events rather than raw
syndromes. A measurement fault at check `c0` between rounds `t0` and `t1` creates
matching defects at `d:t0:c0` and `d:t1:c0`.

```python
from qec_lab import decode_phenomenological_detection_events

faults = decode_phenomenological_detection_events(
    detection_events=((1, 0), (1, 0)),
    physical_error_rate=0.001,
    measurement_error_rate=0.2,
)
print(faults)
```

Expected result:

```text
('measurement:t0:c0',)
```

## Phenomenological logical-error-rate estimation

The adapter can now run an end-to-end repeated-syndrome experiment:

1. sample data errors and measurement errors over several rounds;
2. compute measured syndromes and detection events;
3. decode the detection events with PyMatching;
4. apply decoded data-fault corrections to the final data state;
5. estimate the logical failure rate.

```python
from qec_lab import estimate_phenomenological_logical_error_rate_with_pymatching

result = estimate_phenomenological_logical_error_rate_with_pymatching(
    distance=3,
    rounds=3,
    physical_error_rate=0.01,
    measurement_error_rate=0.01,
    trials=100,
    seed=123,
)
print(result.logical_error_rate)
```

This is the first project-level MWPM benchmark loop. It is still a 1D repetition
code benchmark, but it exercises the same software interface that will later be
used for surface-code matching graphs.

## Demo script

```bash
python experiments/pymatching_phenomenological_demo.py
```

If PyMatching is not installed, the script prints an installation hint and exits
with status code 1.

## Mathematical convention

PyMatching's edge weights are log-likelihood ratios. QEC-Lab therefore uses

```text
w_i = log((1-p_i)/p_i)
```

for an independent fault with probability `p_i`. This convention agrees with the
PyMatching documentation and with the matching-decoder literature.
