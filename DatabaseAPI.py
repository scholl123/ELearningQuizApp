from pymongo import MongoClient
from hashlib import md5


class Database:

    def __init__(self, host='localhost', port=27017):
        """Initiate database connection with given host and port.
        If none is given, use default settings on mongoDB installation."""
        client = MongoClient(host, port=port)
        self.db = client.ELearnApp

    def get_user(self, login, pw):
        """Get user information as dict. But not login and pw."""
        pw_hash = md5(pw.encode()).hexdigest()
        doc = self.db.User.find_one({'login': login, 'pw': pw_hash})
        return {k: doc[k] for k in {'uid', 'fname', 'lname'}}

    def set_user(self, u_dict):
        # TODO: implement account creation
        pass

    def get_questions(self, topic=None, num=0, qid=0):
        """Return a random sample of questions from a given topic as list.
        If no number is given, return all questions of that topic.
        If a specific question id is given, return only dict of that question."""
        if qid:
            doc = self.db.Questions.find_one({'qid': qid})
            return {k: doc[k] for k in set(doc.keys()).difference({'_id'})}
        pipeline = [{'$match': {'topic': topic}}]
        if num:
            pipeline.append({'$sample': {'size': num}})
        docs = self.db.Questions.aggregate(pipeline)
        questions = [{k: d[k] for k in set(d.keys()).difference({'_id'})} for d in docs]
        return questions

    def set_question(self, q_dict):
        """Tries to update an existing questions and difficulty.
        Creates a new db entry otherwise."""
        try:
            key = q_dict['qid']
            answered = q_dict['answered'][0]
            false = q_dict['answered'][1]
            q_dict['difficulty'] = int(false*100/answered) // 33
        except KeyError:
            key = self.db.Questions.find().sort('qid', -1).limit(1)[0]['qid'] + 1  # get last index
            q_dict['qid'] = key
            q_dict['answered'] = [0, 0]
        self.db.Questions.update_one({'qid': key}, {'$set': q_dict}, upsert=True)
        return 0

    def get_progress(self, uid):
        """Returns progress of a user as dict."""
        progress = self.db.Progress.find_one({'uid': uid})
        return {k: progress[k] for k in set(progress.keys()).difference({'_id'})}

    def set_progress(self, p_dict):
        """Tries to update existing progress for a given user.
           Creates a new db entry otherwise for that specific user."""
        try:
            key = p_dict['uid']
        except KeyError:
            raise Exception('No user id was given!')
        self.db.Progress.update_one({'uid': key}, {'$set': p_dict}, upsert=True)
        return 0

    def get_badges(self, bid=0):
        """Returns a single badge as dict, if a badge id is given.
        Otherwise, returns a list of all possible badges."""
        if bid:
            doc = self.db.Badges.find_one({'bid': bid})
            return {k: doc[k] for k in set(doc.keys()).difference({'_id'})}
        docs = self.db.Badges.find({})
        badges = [{k: d[k] for k in set(d.keys()).difference({'_id'})} for d in docs]
        return badges

    def set_badge(self, b_dict):
        """Tries to update an existing badge. Creates a new db entry otherwise."""
        try:
            key = b_dict['bid']
        except KeyError:
            key = self.db.Badges.find().sort('bid', -1).limit(1)[0]['bid'] + 1  # get last index
            b_dict['bid'] = key
        self.db.Badges.update_one({'bid': key}, {'$set': b_dict}, upsert=True)
        return 0

    def get_user_statistics(self, uid):
        # TODO: compute user evaluation
        pass


if __name__ == '__main__':
    # do some testing
    db = Database()

    print('User testing:')
    user = db.get_user('mm1', 'mm1')
    print(f'User information: {user}')

    print('\nQuestion testing:')
    qs = db.get_questions('Machine Learning')
    print(f'Number of all ML questions: {len(qs)}')
    qs = db.get_questions('Machine Learning', 5)
    print(f'Got only 5 ML Questions: {len(qs)==5}')
    print(f'Let`s look these 5 random questions: {qs}')

    db.set_question({'topic': 'Machine Learning', 'question': 'Yo test',
                     'answers': ['a', 'b'],
                     'correct_index': 0, 'difficulty': 0})
    last_question_id = db.db.Questions.find().sort('qid', -1).limit(1)[0]['qid']
    print(f'Create new dummy question: {db.get_questions(qid=last_question_id)}')
    db.set_question({'qid': last_question_id, 'answered': [100, 78]})
    print(f'And modify it: {db.get_questions(qid=last_question_id)}')

    print('\nProgress testing:')
    pg = db.get_progress(1)
    print(f'Progress from user with id 1: {pg}')
    db.set_progress({'uid': 1, 'Machine Learning': [110, 25]})
    print(f'Modify user progress: {db.get_progress(1)}')

    print('\nBadge testing:')
    bg = db.get_badges()
    print(f'Number of all badges: {len(bg)}')
    print(f'First badges is: {bg[0]}')
    db.set_badge({'name': 'Finish 1000 quizzes', 'target': 100})
    last_badge_id = db.db.Badges.find().sort('bid', -1).limit(1)[0]['bid']
    print(f'Add a new badge: {db.get_badges(bid=last_badge_id)}')
    db.set_badge({'bid': last_badge_id, 'target': 1000})
    print(f'And modify it: {db.get_badges(bid=last_badge_id)}')
