import pennylane as qml
import numpy as np
from itertools import combinations

def twolocal(qubits, theta, reps = 2, entanglement = "linear"):
	
	for r in range(reps):
		for i in range(qubits):
			qml.RY(theta[r * qubits + i], wires = i)
		if entanglement == "linear":
			for i in range(qubits - 1):
				qml.CNOT(wires = [i, i + 1])
		elif entanglement == "full":
			for pair in list(combinations(range(qubits),2)):
				a = pair[0]
				b = pair[1]
				if (b < a): # Just in case...
					tmp = b
					b = a
					a = tmp
				qml.CNOT(wires = [a, b])
		else:
			raise Exception("Unknown entanglement pattern")

	
	for i in range(qubits):
		qml.RY(theta[reps * qubits + i], wires = i)


def treevf(qubits, theta, reps = 2):
	for r in range(reps):
		dim = int(np.log2(qubits))
		param_count = 0
		for i in range(dim):
			step = 2**i
			for j in np.arange(0,qubits,2*step):
				qml.RY(theta[r * qubits + param_count], wires = j)
				qml.RY(theta[r * qubits + param_count + 1], wires = j + step)
				param_count += 2
				qml.CNOT(wires = [j, j + step])

def stepc(qubits, theta, reps = 2):
	if (qubits != 4):
		raise Exception("stepc not implemented for qubits != 4")
	
	for r in range(reps):
		for i in range(4):
			qml.RY(theta[7 * r + i], wires = i)
	
		qml.CNOT(wires = [2,3])
		qml.RY(theta[7 * r + 4], wires = 2)
		qml.CNOT(wires = [0,2])
		qml.RY(theta[7 * r + 5],wires = 0)
		qml.CNOT(wires = [0,1])
		qml.RY(theta[7 * r + 6],wires = 0)
