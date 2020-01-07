export "FLASK_APP=flaskr"
export "FLASK_ENV=development"

venv env
source "env/bin/activate"

full_path=$(realpath $0)
parent_path=$(dirname $full_path)

service postgresql start

sudo su - postgres bash -c "psql < $parent_path/setup.psql"
sudo su - postgres bash -c "psql trivia < $parent_path/trivia.psql"
