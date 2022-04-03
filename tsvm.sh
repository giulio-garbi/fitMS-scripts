# Ubuntu 21.10
cd 
sudo apt update
sudo apt install -y python3-pip memcached cgroup-tools build-essential 
sudo service memcached stop

##install docker
#sudo apt-get install ca-certificates curl gnupg lsb-release
#curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
#echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
#sudo apt-get update
#sudo apt-get install -y docker-ce docker-ce-cli containerd.io

##sudo groupadd docker
#sudo usermod -aG docker $USER
#newgrp docker 

python3 -m pip install scipy numpy psutil pymemcache cgroupspy requests #docker 


wget https://download.java.net/java/GA/jdk15.0.2/0d1cfde4252546c6931946de8db48ee2/7/GPL/openjdk-15.0.2_linux-x64_bin.tar.gz
sudo mkdir /usr/lib/java 
sudo tar -xvf openjdk-15.0.2_linux-x64_bin.tar.gz -C /usr/lib/java 
echo 'export PATH="$PATH:/usr/bin:/usr/lib/java/jdk-15.0.2/"' >> ~/.bashrc
echo 'JAVA_HOME="/usr/lib/java/jdk-15.0.2"' >> ~/.bashrc
wget https://dlcdn.apache.org/maven/maven-3/3.8.5/binaries/apache-maven-3.8.5-bin.tar.gz
tar xzvf apache-maven-3.8.5-bin.tar.gz
echo 'export PATH="$PATH:/home/giulio/apache-maven-3.8.5/bin/"' >> ~/.bashrc
source ~/.bashrc

sudo update-alternatives --install "/usr/bin/mvn" mvn "/home/giulio/apache-maven-3.8.5/bin/mvn" 0
sudo update-alternatives --install "/usr/bin/java" "java" "/usr/lib/java/jdk-15.0.2/bin/java" 0 
sudo update-alternatives --install "/usr/bin/javac" "javac" "/usr/lib/java/jdk-15.0.2/bin/javac" 0 
sudo update-alternatives --install "/usr/bin/javac" "javac" "/usr/lib/java/jdk-15.0.2/bin/javac" 0 
sudo update-alternatives --install "/usr/bin/javap" "javap" "/usr/lib/java/jdk-15.0.2/bin/javap" 0 
sudo update-alternatives --set java /usr/lib/java/jdk-15.0.2/bin/java 
sudo update-alternatives --set javac /usr/lib/java/jdk-15.0.2/bin/javac 
sudo update-alternatives --set javap /usr/lib/java/jdk-15.0.2/bin/javap 

#for x in giuliogarbi/teastore-recommender giuliogarbi/teastore-auth giuliogarbi/teastore-webui giuliogarbi/teastore-image giuliogarbi/teastore-persistence giuliogarbi/teastore-registry giuliogarbi/teastore-base giuliogarbi/teastore-kieker-rabbitmq giuliogarbi/teastore-db
#do
#	docker pull $x
#done
#
#docker network create teastore-network

cd 
git clone https://github.com/giulio-garbi/fitMS
#git clone https://github.com/giulio-garbi/fitMS-scripts
cd fitMS
cd jni_lib
JAVA_HOME="/usr/lib/java/jdk-15.0.2" ./gccInstr.sh
cd ..
mvn clean install
cd ../fitMS-scripts/ras_app
mvn clean package
cd controller

######## COMANDO, dentro screen
##  for i in 30 40 50 55 60 65 70; do JAVA_HOME=/usr/lib/java/jdk-15.0.2 python3 ts_imp_sys.py $i 0.01 1 > ~/out.$i.txt; done
## Visualizza con
## tail -n 30 `ls -d ~/out* -tr`