#!/bin/bash

#python3 makeMtxs.py /home/giulio/fitMS-scripts/ras_app/ras_teastore_server/three_tier.mat < ~/out.all.8.txt
#git add /home/giulio/fitMS-scripts/ras_app/ras_teastore_server/three_tier.mat
#git commit -m "New mat"
#git push

for i in 45 30 18 43 28 33 20 40 35 23 25 38
do 
	JAVA_HOME=/usr/lib/java/jdk-15.0.2 python3 ts_imp_sys.py $i 0.01 4 > ~/out.$i.4.txt
	{ cat ~/out.all.8.txt ; tail -n 30 `ls -d ~/out*.4.txt -tr` ; } | python3 makeMtxs.py /home/giulio/fitMS-scripts/ras_app/ras_teastore_server/three_tier.mat 
	#git add /home/giulio/fitMS-scripts/ras_app/ras_teastore_server/three_tier.mat
	#git commit -m "New mat"
	#git push
done 

for i in 38 113 75 44 106 81 50 100 69 56 94 63 88
do 
	JAVA_HOME=/usr/lib/java/jdk-15.0.2 python3 ts_imp_sys.py $i 0.01 10 > ~/out.$i.10.txt
	{ cat ~/out.all.8.txt ; tail -n 30 `ls -d ~/out*.4.txt -tr` ; tail -n 30 `ls -d ~/out*.10.txt -tr` ; } | python3 makeMtxs.py /home/giulio/fitMS-scripts/ras_app/ras_teastore_server/three_tier.mat 
	#git add /home/giulio/fitMS-scripts/ras_app/ras_teastore_server/three_tier.mat
	#git commit -m "New mat"
	#git push
done