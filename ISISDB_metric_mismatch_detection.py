
"""

Python script developed for detecting P2P link metric mismatches between two ends of an ISIS adjacency, by parsing "show isis database level 1|2 detail" output.  
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
metric0 = set()
lanlinks = set()

with open ('wisconsin_crreuclwi.txt', 'r') as f:      ###  Point file system path/filename to text file containing ISIS DB detail output for a single Level "

### Below code parse the ISIS database and builds a directory called hostdir where all needed info is stored.


	for line in f:

		if "-00" in line:
			a = line.split()
			name = a[0].strip("*")
			hostdir.setdefault(name)
			hostdir[name] = []

		# elif "Metric" in line and name[:-6] in line:    ### Below code was initially made to detect routers having LAN mode on certain interfaces and resulting in DIS adj.
		# 	c = line.split()                              ### Disabled now, as a code as  below was made to solve this problem.
		# 	d = c[-1][:-3]
		# 	# print (name)
		# 	lanlinks.add(d)

		elif "Metric:" and "IS-Extended" in line:

			b = line.split()
			tempb = {b[-1]:b[1]}
			hostdir[name].append(tempb)

### Below code deals with issues of false alarms generate due to DIS election happening on LAN mode. DIS adjacencies will result in Metric=0 adjacencies which makes calc to go wrong
### Below helps by detecting such states and modify the values in hostdir to make it look like P2P adjancencies.

for key in hostdir:
	if key.endswith(".00-00"):
		for i in range (len(hostdir[key])):
			for i1 in hostdir[key][i]:
				if key[:-6] in i1:
					for i2 in range (len(hostdir[i1+"-00"])):
						for i3 in (hostdir[i1+"-00"][i2]):
							for i4 in (hostdir[i1+"-00"][i2]):
								if key[:-6] not in i4:
									hostdir[i1+"-00"][i2][i3] = hostdir[key][i][i1]
				
				
print ("\n==========================================================================================================================")
print ("\n          \t\tStart of ISIS Metric Validation Script\n")
print ("==========================================================================================================================\n")

for keys in hostdir:
	for i in range (len(hostdir[keys])):
		for i1 in hostdir[keys][i]:

			# print (keys)
			# print (i1)

			node = keys[:-3]
			peers = i1
			peer = i1+"-00"
			cost =  hostdir[keys][i][i1]

			try:

				if node == peers:
					pass

				elif node[:-6] in peer[:-3]:
					pass
				elif {node:cost} not in hostdir[peer]:
					o = [peers[:-3], node[:-3]]
					# outs = "Metric Mismatch detected for Router " + peers[:-3] + " Adjacency to " + node[:-3]
					outs = "\tMetric mismatch detected for ISIS adjacency between " + str(sorted(o))
					output.add(outs)
				else:
					continue
			except KeyError:
					o1 = [peer, node]
					# exception = "Exception Occurred for " + peer + " to " + node + " . Please check."
					exception = "\tException occurred for adjacency between " + str(sorted(o1))
					output.add(exception)

### Below code is needed only for segregating devices based on its role in network and shaare summary report. ###

core = dist = access = backbone = other = commercial = 0

for line in output:
	print (line)
	if "cw" in line or "CW" in line:
		commercial+=1
	elif "cts" in line or "CTS" in line or "acr" in line or "ACR" in line:
		access+=1
	elif "dtr" in line or "DTR" in line or "CRR" in line or "crr" in line:
		core+=1
	elif "prr" in line or "PRR" in line or "bbr" in line or "BBR" in line or "BCR" in line:
		backbone+=1
	else:
		other+=1

### Below code is needed to detect routers in network, which has max-metric appled due to reasons like config error or mpls ldp sync issues ###

for keys in hostdir:
	for i in hostdir[keys]:
		for value in i.values():
			if "16777214" in value:
				maxmetric.add(keys[:-6])
			else:
				pass

print ("\n\n================================================= RESULT - SUMMARY ======================================================")

print ("\n\n\nBackbone Router Links = '"+  str(backbone) + "' Core Router links = '" + str(core) +  
"' Access Router links = '" + str(access) + "' Commercial = '" + str(commercial) + "' Others = '" + str(other) + "'")

print ("\n\t - Total Mistmatches/Exceptions detected is " + str(len(output)))

print ("\nRouters that have got MAX-METRIC on their interface. Either Config error or MPLS LDP SYNC issues.  \n")

if len(maxmetric) == 0:
	print ("\t - Result is None. No devices found")
else:
	print ("\t" + str(maxmetric))

# print ("\nBelow routers have got LAN links resulting in metric to show as '0' for DIS. This may cause script to misidentify certain valid connections as Mismatches.")
# print ("Having LAN mode on P2P links is not a recommended configuration and can be corrected\n")

# print ("\t" + str(lanlinks))

end = perf_counter() 
print ('\n\n\n!! Elapsed time for script execution is ' + str(int(end - start)) + ' seconds !!\n')

print ("==========================================================================================================================\n")
