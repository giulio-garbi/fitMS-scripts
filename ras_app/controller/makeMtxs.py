import sys
import numpy as np
import scipy
from scipy.io import savemat

def mtx2str(name, data):
	return name+" = ["+";".join(" ".join(str(x) for x in ln) for ln in data)+"];"

if __name__ == '__main__':
	outfn = sys.argv[1]
	Cli = []
	RTm = []
	RTmCI = []
	Tm = []
	TmCI = []
	NC = []
	NT = []
	entryNames = np.array(["Client", "persistence", "webui"], dtype=object)
	taskNames = np.array(["Client", "all"], dtype=object)
	record = False
	for line in sys.stdin:
		if line.startswith("True"):
			record = True
			parts = line.strip().split()
			Cli.append([int(parts[1])])
			RTm.append([0.0]*3)
			RTmCI.append([[0.0, 0.0]]*3)
			Tm.append([0.0]*3)
			TmCI.append([[0.0, 0.0]]*3)
			NC.append([float('inf'), int(parts[2])])
			NT.append([float('inf'), float('inf')])
		elif line.startswith("-----"):
			record = False
		elif record:
			parts = line.strip().split()
			if len(parts) > 0:
				if parts[0] == 'rt':
					if parts[1].startswith("Client"):
						RTm[-1][0] = float(parts[2])
						RTmCI[-1][0] = [float(parts[3][1:-1]), float(parts[4][:-1])]
					elif parts[1].startswith("persistence"):
						RTm[-1][1] = float(parts[2])
						RTmCI[-1][1] = [float(parts[3][1:-1]), float(parts[4][:-1])]
						#elif parts[1].startswith("auth"):
						#	RTm[-1][2] = float(parts[2])
						#	RTmCI[-1][2] = [float(parts[3][1:-1]), float(parts[4][:-1])]
						#elif parts[1].startswith("image"):
						#	RTm[-1][3] = float(parts[2])
						#	RTmCI[-1][3] = [float(parts[3][1:-1]), float(parts[4][:-1])]
					elif parts[1].startswith("webui"):
						RTm[-1][2] = float(parts[2])
						RTmCI[-1][2] = [float(parts[3][1:-1]), float(parts[4][:-1])]
				elif parts[0] == 'thr':
					if parts[1].startswith("Client"):
						Tm[-1][0] = float(parts[2])
						TmCI[-1][0] = [float(parts[3][1:-1]), float(parts[4][:-1])]
					elif parts[1].startswith("persistence"):
						Tm[-1][1] = float(parts[2])
						TmCI[-1][1] = [float(parts[3][1:-1]), float(parts[4][:-1])]
						#elif parts[1].startswith("auth"):
						#	Tm[-1][2] = float(parts[2])
						#	TmCI[-1][2] = [float(parts[3][1:-1]), float(parts[4][:-1])]
						#elif parts[1].startswith("image"):
						#	Tm[-1][3] = float(parts[2])
						#	TmCI[-1][3] = [float(parts[3][1:-1]), float(parts[4][:-1])]
					elif parts[1].startswith("webui"):
						Tm[-1][2] = float(parts[2])
						TmCI[-1][2] = [float(parts[3][1:-1]), float(parts[4][:-1])]
	savemat(outfn,{'Cli':np.array(Cli), 'RTm':np.array(RTm), 'RTmCI':np.array(RTmCI), 'Tm':np.array(Tm), \
		'TmCI':np.array(TmCI), 'NC':np.array(NC), 'NT':np.array(NT), 'entryNames':entryNames, \
		'taskNames':taskNames})