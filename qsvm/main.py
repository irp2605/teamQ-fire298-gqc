# Main script of the qsvm.
# Imports the data for training. Imports the data for validation and testing
# and kfolds it into k=5.
# Computes the ROC curve of the qsvm and the AUC, saves the ROC plot.
import warnings
from time import perf_counter

from qiskit.providers.aer import AerSimulator
from qiskit.utils import algorithm_globals
from qiskit_machine_learning.kernels import QuantumKernel

from sklearn.svm import SVC

from .terminal_colors import tcols
from . import qdata as qd
from . import util
from .feature_map_circuits import u2Reuploading

#TODO good way to import any backend required (mock, noise model, or real)
# without having if-statement imports.

# Warnings are suppressed since qiskit aqua obfuscates the output of this
# script otherwise (IBM's fault not ours.)
warnings.filterwarnings("ignore", category=DeprecationWarning)

seed = 12345
# Ensure same global behaviour.
algorithm_globals.random_seed = seed


def main(args):
    qdata = qd.qdata(
        args["data_folder"],
        args["norm"],
        args["nevents"],
        args["model_path"],
        train_events=4,
        valid_events=4,
        test_events=4,
    )

    train_features = qdata.get_latent_space("train")
    train_labels = qdata.ae_data.trtarget
    test_features = qdata.get_latent_space("test")
    test_labels = qdata.ae_data.tetarget

    feature_map = u2Reuploading(nqubits=8, nfeatures=args["feature_dim"])
    #FIXME Virtual to physical qubits, ordering is from 0->(n_qubits-1)
    #initial_layout = [9,8,11,14,16,19,22,25]
    initial_layout = None
    # TODO make the config adjustable from  argparse
    # FIXME if I choose sim_type = 'ideal' then it errors due to unexpected 
    # keyword argument 'seed_transpiler'
    config = {'seed_transpiler':seed, 'seed_simulator':seed ,
              'optimization_level':3, 'initial_layout':initial_layout,
              'shots':5000}
    quantum_instance = util.configure_quantum_instance(
        ibmq_token=args["ibmq_token"],
        sim_type = args["sim_type"],
        backend_name= args["backend_name"],
        **config
    )
    #print(quantum_instance)
    kernel = QuantumKernel(feature_map=feature_map, 
                           quantum_instance=quantum_instance)

    qc_transpiled = util.get_quatum_kernel_circuit(quantum_kernel=kernel, 
                                                   path='.')
    #TODO errors for the moment. Need to port to AerSimulator.from_backend()
    #util.save_circuit_physical_layout(qc_transpiled,quantum_instance.backend,
    #                                  '.')
    #print(len(initial_layout))
    print(len(train_features[0]))
    print(feature_map.num_qubits)
    quantum_kernel_matrix = kernel.evaluate(x_vec = train_features)
    
    qsvm = SVC(kernel='precomputed', C=args["c_param"])

    print(tcols.OKCYAN + "Training the QSVM..." + tcols.ENDC)
    util.print_model_info(args["model_path"], qdata, qsvm)

    train_time_init = perf_counter()
    qsvm.fit(quantum_kernel_matrix, train_labels)
    train_time_fina = perf_counter()
    print(f"Training completed in: {train_time_fina-train_time_init:.2e} s")

    train_acc = qsvm.score(quantum_kernel_matrix, train_labels)
    #evaluate test kernel matrix
    kernel_matrix_test = kernel.evaluate(x_vec=test_features,y_vec=train_features)
    test_acc = qsvm.score(kernel_matrix_test, test_labels)
    util.print_accuracies(test_acc, train_acc)

    #TODO change naming convention to include simulation type
    args["output_folder"] = args["output_folder"] + f"_c={qsvm.C}"
    util.create_output_folder(args["output_folder"])
    util.save_qsvm(qsvm, "models/" + args["output_folder"] + "/model")