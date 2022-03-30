#!/bin/bash

for i in 15 45 30 18 43 28 33 20 40 35 23 25 38
do 
	JAVA_HOME=/usr/lib/java/jdk-15.0.2 python3 ts_imp_sys.py $i 0.01 4 > ~/out.$i.4.txt
done 

for i in 38 113 75 44 106 81 50 100 69 56 94 63 88
do 
	JAVA_HOME=/usr/lib/java/jdk-15.0.2 python3 ts_imp_sys.py $i 0.01 10 > ~/out.$i.10.txt
done