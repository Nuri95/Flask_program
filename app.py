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
    if data:
        return max(data, key=int)
    else:
        return 0


def get_all_users():
    print(request.args)  # Для доступа к параметрам, представленным в URL ( ?key=value )
    all_users = db_read()
    js = json.dumps(all_users)  # Сериализует obj в строку JSON-формата.

    return Response(js, status=200, mimetype='application/json')


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
    newid = get_max_id(db) + 1
    db[newid] = {'name': data['name'], 'age': data['age']}
    db_write(db)
    return Response('{"Success": "ok"}',
                    status=200,
                    mimetype='application/json')


def update_user():
    data = request.args
    if 'name' not in data and 'age' not in data:
        return Response('{"status": "error", "error": "age of name missing"}', status=400, mimetype='application/json')
    if 'id' not in data:
        return create_user()
    id = data['id']
    db = db_read()
    if id not in db:
        return Response('{"status": "error", "error": "unknown id"}', status=404, mimetype='application/json')
    if 'name' in data:
        db[id]['name'] = data['name']
    if 'age' in data:
        db[id]['age'] = data['age']
    db_write(db)
    return Response('{"status": "ok"}', status=200, mimetype='application/json')


def remove_user():
    data = request.args
    if 'id' not in data:
        return Response('{"status": "error", "error": "id missing"}', status=400, mimetype='application/json')
    id = data['id']
    db = db_read()
    if id not in db:
        return Response('{"status": "error", "error": "unknown id"}', status=404, mimetype='application/json')
    del db[id]
    db_write(db)
    return Response('{"status": "ok"}', status=200, mimetype='application/json')


# Используем декоратор route() чтобы сообщить Flask, какой URL должен запускать нашу функцию
@app.route('/users/', methods=['GET', 'POST', 'PATCH', 'DELETE'])
@app.route('/users/<id>', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def users(*args, **kwargs):
    if request.method == 'GET':
        return get_all_users()
    elif request.method == 'POST':
        return create_user()
    elif request.method == 'PATCH':
        return update_user()
    elif request.method == 'DELETE':
        return remove_user()
    else:
        pass


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
