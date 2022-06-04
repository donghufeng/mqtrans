from mindquantum.core import gates as mgates
from mindquantum.core import Circuit as mcircuit


def params_trans(pr, pr_table, to_qiskit=True):
    from qiskit.circuit import Parameter
    if to_qiskit:
        out = None
        for k, v in pr.items():
            if k not in pr_table:
                pr_table[k] = Parameter(k)
            if out is None:
                out = pr_table[k] * v
            else:
                out += pr_table[k] * v
        out += pr.const
        return out


def self_herm_non_params(gate, circ, to_qiskit=True):
    from qiskit.circuit import library as qlib
    qgate_map = {
        'X': qlib.XGate,
        'Y': qlib.YGate,
        'Z': qlib.ZGate,
        'H': qlib.HGate,
        'SWAP': qlib.SwapGate,
        'ISWAP': qlib.iSwapGate,
    }
    if to_qiskit:
        ctrls = gate.ctrl_qubits
        objs = gate.obj_qubits
        g = qgate_map[gate.name.upper()]()
        if ctrls:
            g = g.control(len(ctrls))
        circ.append(g, ctrls + objs, [])


def t_gate_trans(gate, circ, to_qiskit=True):
    from qiskit.circuit import library as qlib
    if to_qiskit:
        ctrls = gate.ctrl_qubits
        objs = gate.obj_qubits
        if gate.hermitianed:
            g = qlib.TdgGate()
        else:
            g = qlib.TGate()
        if ctrls:
            g = g.control(len(ctrls))
        circ.append(g, ctrls + objs, [])


def s_gate_trans(gate, circ, to_qiskit=True):
    from qiskit.circuit import library as qlib
    if to_qiskit:
        ctrls = gate.ctrl_qubits
        objs = gate.obj_qubits
        if gate.hermitianed:
            g = qlib.SdgGate()
        else:
            g = qlib.SGate()
        if ctrls:
            g = g.control(len(ctrls))
        circ.append(g, ctrls + objs, [])


def oppo_params_gate_trans(gate, circ, pr_table, to_qiskit=True):
    from qiskit.circuit import library as qlib
    qgate_map = {
        'RX': qlib.RXGate,
        'RY': qlib.RYGate,
        'RZ': qlib.RZGate,
        'ZZ': qlib.RZZGate,
        'YY': qlib.RYYGate,
        'XX': qlib.RXXGate,
        'PS': qlib.PhaseGate,
    }
    if to_qiskit:
        ctrls = gate.ctrl_qubits
        objs = gate.obj_qubits
        if gate.parameterized:
            g = qgate_map[gate.name.upper()](params_trans(
                gate.coeff, pr_table))
        else:
            g = qgate_map[gate.name.upper()](gate.coeff.const)
        if ctrls:
            g = g.control(len(ctrls))
        circ.append(g, ctrls + objs, [])


def to_qiskit(circuit: mcircuit):
    from qiskit import QuantumCircuit
    qcircuit = QuantumCircuit(circuit.n_qubits)
    pr_table = {}
    for g in circuit:
        if isinstance(g, (mgates.XGate, mgates.YGate, mgates.ZGate,
                          mgates.HGate, mgates.SWAPGate)):
            self_herm_non_params(g, qcircuit)
        elif isinstance(g, mgates.TGate):
            t_gate_trans(g, qcircuit)
        elif isinstance(g, mgates.SGate):
            t_gate_trans(g, qcircuit)
        elif isinstance(g, (mgates.RX, mgates.RY, mgates.RZ, mgates.ZZ,
                            mgates.YY, mgates.XX, mgates.PhaseShift)):
            oppo_params_gate_trans(g, qcircuit, pr_table)
        else:
            raise ValueError(f"Do not know how to convert {g} to qiskit.")
    return qcircuit


if __name__ == '__main__':
    import numpy as np

    circ = mcircuit() + mgates.X.on(0) + mgates.X.on(0, [1, 2])
    circ.y(2)
    circ.y(2, [3, 4, 5, 6])
    circ.z(2)
    circ.z(2, [3, 4, 5, 6])
    circ.h(2)
    circ.h(2, [3, 4, 5, 6])
    circ.swap([0, 2])
    circ.swap([0, 2], [1, 3])
    circ += mgates.T(0)
    circ += mgates.T(0, [1, 2])
    circ += mgates.T(0).hermitian()
    circ += mgates.T(0, [1, 2]).hermitian()
    circ += mgates.RX('a').on(0, [1, 2])
    circ += mgates.RX(np.pi).on(0, [1, 2])
    circ += mgates.RX('a').on(0)
    circ += mgates.RX(1.2).on(0)
    circ += mgates.XX('a').on([0, 2], [1, 3])

    q_circ = to_qiskit(circ)
    print(circ)
    print(q_circ)
