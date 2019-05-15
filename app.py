import pickle
import json
from flask import Flask, request, Response

app = Flask(__name__)  # Мы создаем экземпляр этого класса.


def db_read():
    try:
        pickle_in = open('data.pickle', 'rb')
    except IOError:
        return {}
    data = pickle.load(pickle_in)  # Загружает объект из файла
    pickle_in.close()
    return data


def db_write(data):
    pickle_out = open('data.pickle', 'wb')
    pickle.dump(data, pickle_out)  # Записывает сериализованный объект в файл
    pickle_out.close()


def get_max_id(data):
    print('get_max_id== ', data)
    if data:
        return max(data, key=int)
    else:
        return 0


def get_all_users():
    print(request.args)  # Для доступа к параметрам, представленным в URL ( ?key=value )
    all_users = db_read()
    js = json.dumps(all_users)  # Сериализует obj в строку JSON-формата.

    return Response(js, status=200, mimetype='application/json')


def get_user(id):
    db = db_read()
    if id in db:
        result = db[id]
        result['id'] = id
        return Response(json.dumps(result), status=200, mimetype='application/json')
    else:
        return Response('{"status": "error", "error": "unknown id"}', status=404, mimetype='application/json')


def create_user():
    try:
        # data заполняется если flask что-то непонял
        # data = json.loads(request.data)   # десериализует s (экземпляр str, содержащий документ JSON) в объект Python.
        data = request.args
    except Exception as e:
        print(e)
        return Response({'status': 'ERROR', 'error': e}, status=400)
    if 'name' not in data or 'age' not in data:
        return Response('{"status": "error","error":"Bad request"}',
                        status=400,
                        mimetype='application/json')
    # example_dict = {'name': 'Ivan', 'age': 33}
    db = db_read()
    print('db:  ', db)
    new_id = get_max_id(db) + 1
    print('new_id:  ', new_id)
    db[new_id] = {'name': data['name'], 'age': data['age']}
    db_write(db)
    return Response('{"Success": "ok"}',
                    status=200,
                    mimetype='application/json')


def update_user(id):
    data = request.args
    if 'name' not in data and 'age' not in data:
        return Response('{"status": "error", "error": "age of name missing"}', status=400, mimetype='application/json')
    db = db_read()
    if id not in db:
        return Response('{"status": "error", "error": "unknown id"}', status=404, mimetype='application/json')
    if 'name' in data:
        db[id]['name'] = data['name']
    if 'age' in data:
        db[id]['age'] = data['age']
    db_write(db)
    return Response('{"status": "ok"}', status=200, mimetype='application/json')


def remove_user(id):
    db = db_read()
    if id not in db:
        return Response('{"status": "error", "error": "unknown id"}', status=404, mimetype='application/json')
    del db[id]
    db_write(db)
    return Response('{"status": "ok"}', status=200, mimetype='application/json')


def clear_users():
    db_write({})
    return Response('{"status": "ok"}', status=200, mimetype='application/json')

# curl -X GET http://127.0.0.1:8080/users/
# curl -X GET http://127.0.0.1:8080/users/1
# curl -X PATCH http://127.0.0.1:8080/users/1?name=ddd
# curl -X DELETE http://127.0.0.1:8080/users/1
# Используем декоратор route() чтобы сообщить Flask, какой URL должен запускать нашу функцию
@app.route('/users/', methods=['GET', 'POST', 'DELETE'])
def users():
    if request.method == 'GET':
        return get_all_users()
    elif request.method == 'DELETE':
        return clear_users()
    elif request.method == 'POST':
        return create_user()
    else:
        pass


@app.route('/users/<id>', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def user(id):
    try:
        id = int(id)
    except ValueError:
        return Response('{"status": "error", "error": "invalid id"}', status=400, mimetype='application/json')
    if request.method == 'GET':
        return get_user(id)
    elif request.method == 'PATCH':
        return update_user(id)
    elif request.method == 'DELETE':
        return remove_user(id)
    else:
        pass


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
