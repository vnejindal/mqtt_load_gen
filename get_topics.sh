

rm topic*.txt
cat sub.txt | grep Report | grep TEST_VNE_REPORT | awk {'print $1'} > topics.txt
cat topics.txt | cut -f 3 -d '/' | sort > topic1.txt
uniq topic1.txt > topic2.txt
cat topic2.txt | wc -l
