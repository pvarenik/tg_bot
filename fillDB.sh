#!/bin/bash

source .env
export IFS="~"
content=$(cat content.txt)
for joke in $content; do
  echo $joke
  export PGPASSWORD=$PGPASSWORD; psql -c "INSERT INTO public.test (jokes) VALUES('$joke')" -d postgres -U postgres
done