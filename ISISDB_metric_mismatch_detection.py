
"""

Python script developed for detecting P2P link metric mismatches between two ends of an ISIS adjacency, by parsing "show isis database detail" output.  
	Justification - ISIS metric not matched on both ends of links may result in Assymetric routing & also unforseen bandwith utilization issues.
Script also detects any routers which has got max-metric value on its interface, which might be a result of Config error or LDP SYNC issues.
	Justification - We have seen such max-metric values causing traffic not to take valid path resulting in outages in customer network and rechability issues.

Author : Sudeep Valengattil
Email  : svalenga@cisco.com

"""


from time import perf_counter
start = perf_counter()


hostdir = {}
name = str
output = set()
maxmetric = set()

with open ('bbr01mtpkca_isisdb.txt', 'r') as f:      ###  Point file system path/filename to text file containing ISIS DB detail output"

	for line in f:

		if "00-00" in line:
			a = line.split()
			name = a[0].strip("*")
			hostdir.setdefault(name)
			hostdir[name] = []
		elif "Metric: 0" not in line and "Metric:" and "IS-Extended" in line:

			b = line.split()
			tempb = {b[-1][:-3]:b[1]}
			hostdir[name].append(tempb)

print ("\n==================================================================")
print ("\n          Start of ISIS Metric Validation Script\n")
print ("==================================================================\n")

for keys in hostdir:
	for i in range (len(hostdir[keys])):
		for i1 in hostdir[keys][i]:

			node = keys[:-6]
			peers = i1
			peer = i1+".00-00"
			cost =  hostdir[keys][i][i1]

			try:
				if {node:cost} not in hostdir[peer]:
					outs = "Metric Mismatch detected for Router " + peers + " Adjacency to " + node
					output.add(outs)
				else:
					continue
			except KeyError:
					exception = "Exception Occurred for " + peer + " to " + node + " . Please check."
					output.add(exception)

crr = dtr = bbr = acr = other = commercial = 0

for logs in output:
	print (logs)

	if "crr" in logs:
		crr = crr+1
	elif "dtr" in logs:
		dtr = dtr+1
	elif "acr" in logs or "cts" in logs:
		acr = acr+1
	elif "bbr" in logs or "BCR" in logs or "bcr" in logs:
		bbr=bbr+1
	elif "cw" in logs or "CW" in logs:
		commercial = commercial+1
	else:
		other = other+1


for keys in hostdir:
	for i in hostdir[keys]:
		for value in i.values():
			if "16777214" in value:
				maxmetric.add(keys[:-6])
			else:
				pass



print ("\n============================== RESULT - SUMMARY =====================================")

print ("\n\n\nBackbone Router Links = '"+  str(bbr) + "' Core Router links = '" + str(crr) + "' Distribution Router links = '" + str(dtr) + 
"' Access Router links = '" + str(acr) + "' Commercial = '" + str(commercial) + "' Others = '" + str(other) + "'")

print ("\nTotal Mistmatches/Exceptions detected is " + str(len(output)))

print ("\nBelow routers have got MAX-METRIC on their interface. Either Config error or MPLS LDP SYNC issues.  Please check\n")
print (maxmetric)

end = perf_counter() 
print ('\nElapsed time for script execution is ' + str(int(end - start)) + ' seconds\n')

print ("\n====================================================================================\n")

