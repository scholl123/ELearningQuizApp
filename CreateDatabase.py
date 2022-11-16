from pymongo import MongoClient
import json

if __name__ == '__main__':
    with open('mongo_db_config.json') as f:
        settings = json.load(f)
    print('Connecting to database.')
    client = MongoClient(settings['db_address'], port=settings['db_port'])
    client.drop_database('ELearnApp')
    db = client.ELearnApp
    collections = ['User', 'Questions', 'Progress', 'Badges']
    indices = [[('uid', 1)], [('qid', 1)], [('uid', 1)], [('bid', 1)]]
    for i, col in enumerate(collections):
        print(f'Loading {col}.')
        with open('Examples/' + col + '.json') as f:
            file_data = json.load(f)
        db[col].insert_many(file_data)
        db[col].create_index(indices[i], unique=True)
    print('Done.')
