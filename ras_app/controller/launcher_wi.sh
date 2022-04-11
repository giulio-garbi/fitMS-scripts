#!/bin/bash

#python3 makeMtxs.py /home/giulio/fitMS-scripts/ras_app/ras_teastore_server/three_tier.mat < ~/out.all.8.txt
#git add /home/giulio/fitMS-scripts/ras_app/ras_teastore_server/three_tier.mat
#git commit -m "New mat"
#git push

echo "--- 74 6 ---" >> ~/errors.txt
JAVA_HOME=/usr/lib/java/jdk-15.0.2 python3 ts_imp_sys.py 74 0.01 6 > ~/out.74.6.txt 2>>errors.txt
python3 makeMtxs.py /home/giulio/fitMS-scripts/ras_app/ras_teastore_server/three_tier_wi.mat < ~/out.74.6.txt

for i in 3 34 73 4 43 70 6 23 67 7 44 63 10 18 62 12 50 61 15
do 
	echo "--- $i 6 ---" >> ~/errors.txt
	JAVA_HOME=/usr/lib/java/jdk-15.0.2 python3 ts_imp_sys.py $i 0.01 6 > ~/out.$i.6.txt 2>>errors.txt
	python3 makeMtxsMerge.py /home/giulio/fitMS-scripts/ras_app/ras_teastore_server/three_tier_wi.mat /home/giulio/fitMS-scripts/ras_app/ras_teastore_server/three_tier_wi.mat < ~/out.$i.6.txt
done