
1. Bootstrap the DB
```bash
$ docker-compose up -d db

#create the database schema
$ docker-compose run --rm flaskapp /bin/bash -c "cd /opt/services/flaskapp/src && python -c  'import database; database.init_db()'"
```

2. Bring up the cluster
$ docker-compose up -d


3. Browse to localhost:8080 to see the app in action.


################## restart to include any changes #######################
docker-compose up -d --build


################## upload account types ###############

$ docker cp dump.sql aggregator_db_1:/docker-entrypoint-initdb.d/dump.sql

$ docker exec -u postgres aggregator_db_1 psql flaskapp_db postgres -f docker-entrypoint-initdb.d/dump.sql


################## PSQL into database ################## 
$ docker exec -it <postgres container id> bash
$ psql -U postgres flaskapp_db


DROP SCHEMA public CASCADE;
CREATE SCHEMA public;









