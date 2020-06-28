* Prod 최초 실행
```bash
docker-compose -f docker-compose.prod.yml up -d --build
docker-compose -f docker-compose.prod.yml exec web python manage.py makemigration --noinput
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate --noinput
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --no-input
docker-compose -f docker-compose.prod.yml exec web python manage.py loaddata backup.json
```
* Prod 초기화 재실행
```bash
docker-compose -f docker-compose.prod.yml down -v
docker-compose -f docker-compose.prod.yml exec web python manage.py makemigrations --noinput
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate --noinput
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --no-input --clear
docker-compose -f docker-compose.prod.yml exec web python manage.py loaddata backup.json
```
* model 변경후 해야할 작업

```bash
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

* log
```bash
docker-compose logs -f
```


* backup
```bash
docker-compose exec web python manage.py dumpdata --indent 2 > backup.json
docker-compose exec web python manage.py loaddata backup.json
```

* init db
```bash
rm migrate/000*
docker-compose exec web python manage.py flush
```

* error on loaddata
```bash
docker-compose exec web python manage.py dumpdata --natural-foreign \
   --exclude auth.permission --exclude contenttypes \
   --indent 4 > backup.json
```

* code-server
```bash
docker run -d --rm -e PASSWORD=spring -p 0.0.0.0:10104:10104 -v "${HOME}/.local/share/code-server:/home/spring/.local/share/co-server" -v "$PWD:/home/spring" codercom/code-server:v2
```

* build
```bash
docker-compose build web
docker-compose up -d web
```

* pgAdmin4
```bash
docker run --rm -d -p 5050:5050 thajeztah/pgadmin4
```