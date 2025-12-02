docker cp data_original/title.basics.tsv namenode:/title.basics.tsv
docker cp data_original/title.ratings.tsv namenode:/title.ratings.tsv
docker exec -it namenode bash -c "hdfs dfs -mkdir -p /datalake/landing/"
docker exec -it namenode bash -c "hdfs dfs -put /title.basics.tsv /datalake/landing/title.basics.tsv"
docker exec -it namenode bash -c "hdfs dfs -put /title.ratings.tsv /datalake/landing/title.ratings.tsv"
docker cp pipeline_spark.py spark-master:/opt/   
docker exec spark-master bash -c "                                            
/spark/bin/spark-submit \
--master spark://spark-master:7077 \
/opt/pipeline_spark.py"