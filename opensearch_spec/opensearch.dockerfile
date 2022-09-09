# Run this file locally as a standalone container if you need to debug or find unsurfaced errors in the opensearch cluster
## Note: Version number should  be the same as the cloud deployed version of opensearch

FROM opensearchproject/opensearch:1.0.1
    
ENV cluster.name=opensearch-cluster
ENV node.name=opensearch-main
ENV node.master=true
ENV discovery.type=single-node
ENV bootstrap.memory_lock=true 
ENV OPENSEARCH_JAVA_OPTS="-Xms512m -Xmx512m" 
ENV http.cors.allow-origin=*
ENV http.cors.enabled=true
ENV http.cors.allow-headers=X-Requested-With,X-Auth-Token,Content-Type,Content-Length,Authorization
ENV http.cors.allow-credentials=true

