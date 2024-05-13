#!/bin/bash

source .env
export IFS="~"
content=$(cat content.txt)
for joke in $content; do
  echo $joke
  export PGPASSWORD=$DATABASE_PASSWORD; psql -c "INSERT INTO public.jokes (jokes) VALUES('$joke')" -d $DATABASE_NAME -U $DATABASE_USER -h $DATABASE_HOST
done