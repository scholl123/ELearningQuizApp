from pymongo import MongoClient
from hashlib import md5


class Database:

    def __init__(self, host: str = 'localhost', port: int = 27017):
        """Initiate database connection with given host and port.
        If none is given, use default settings on mongoDB installation."""
        client = MongoClient(host, port=port)
        self.db = client.ELearnApp

    def get_user_2(self, login: str, pw: str):
        """Return true if user:pw exists in db"""
        pw_hash = md5(pw.encode()).hexdigest()
        return self.db.User.find_one({'login': login, 'pw': pw_hash})

    def get_user_by_id(self, uid):
        return self.db.User.find_one({'uid': uid})

    def get_user(self, login: str, pw: str) -> dict:
        """Get user information as dict. But not login and pw."""
        pw_hash = md5(pw.encode()).hexdigest()
        doc = self.db.User.find_one({'login': login, 'pw': pw_hash})
        if doc is not None:
            return {k: doc[k] for k in {'uid', 'fname', 'lname'}}

    def set_user(self, u_dict: dict) -> int:
        """Create or update user information."""
        try:
            key = u_dict['uid']
        except KeyError:
            key = self.db.User.find().sort('uid', -1).limit(1)[0]['uid'] + 1  # get last index
            u_dict['uid'] = key
            missing_keys = {'login', 'pw'}.difference(u_dict.keys())
            if missing_keys:
                raise Exception(f'Cannot add new user. Missing keys: {missing_keys}')
            u_dict['pw'] = md5(u_dict['pw'].encode()).hexdigest()
        self.db.User.update_one({'uid': key}, {'$set': u_dict}, upsert=True)
        return key

    def get_questions(self, topic: str = None, num: int = 0,
                      qid: int = 0, diff: int = None):  # -> dict | list[dict]:
        """Return a random sample of questions from a given topic as list.
        If no number is given, return all questions of that topic.
        If a difficulty is given, return all questions of that topic with this difficulty.
        If a specific question id is given, return only dict of that question."""
        if qid:
            doc = self.db.Questions.find_one({'qid': qid})
            return {k: doc[k] for k in set(doc.keys()).difference({'_id'})}
        if diff is not None:
            pipeline = [{'$match': {'topic': topic, 'difficulty': diff}}]
        else:
            pipeline = [{'$match': {'topic': topic}}]
        if num:
            pipeline.append({'$sample': {'size': num}})
        docs = self.db.Questions.aggregate(pipeline)
        questions = [{k: d[k] for k in set(d.keys()).difference({'_id'})} for d in docs]
        return questions

    def set_question(self, q_dict: dict) -> int:
        """Tries to update an existing questions and difficulty.
        Creates a new db entry otherwise."""
        try:
            key = q_dict['qid']
            answered = q_dict['answered'][0]
            false = q_dict['answered'][1]
            q_dict['difficulty'] = int(false * 100 / answered) // 33
        except KeyError:
            key = self.db.Questions.find().sort('qid', -1).limit(1)[0]['qid'] + 1  # get last index
            q_dict['qid'] = key
            q_dict['answered'] = [0, 0]
            missing_keys = {'topic', 'question', 'answers',
                            'correct_index', 'difficulty'}.difference(q_dict.keys())
            if missing_keys:
                raise Exception(f'Cannot add new question. Missing keys: {missing_keys}')
        self.db.Questions.update_one({'qid': key}, {'$set': q_dict}, upsert=True)
        return key

    def get_progress(self, uid: int) -> dict:
        """Returns progress of a user as dict."""
        progress = self.db.Progress.find_one({'uid': uid})
        if progress is not None:
            return {k: progress[k] for k in set(progress.keys()).difference({'_id'})}

    def set_progress(self, p_dict: dict) -> int:
        """Create or update progress for a given user."""
        try:
            key = p_dict['uid']
        except KeyError:
            raise Exception('No user id was given!')
        self.db.Progress.update_one({'uid': key}, {'$set': p_dict}, upsert=True)
        return key

    def get_badges(self, bid: int = 0):  # -> dict | list[dict]:
        """Returns a single badge as dict, if a badge id is given.
        Otherwise, returns a list of all possible badges."""
        if bid:
            doc = self.db.Badges.find_one({'bid': bid})
            if doc is not None:
                return {k: doc[k] for k in set(doc.keys()).difference({'_id'})}
        docs = self.db.Badges.find({})
        badges = [{k: d[k] for k in set(d.keys()).difference({'_id'})} for d in docs]
        return badges

    def set_badge(self, b_dict: dict) -> int:
        """Tries to update an existing badge. Creates a new db entry otherwise."""
        try:
            key = b_dict['bid']
        except KeyError:
            key = self.db.Badges.find().sort('bid', -1).limit(1)[0]['bid'] + 1  # get last index
            b_dict['bid'] = key
            missing_keys = {'name', 'target'}.difference(b_dict.keys())
            if missing_keys:
                raise Exception(f'Cannot add new badge. Missing keys: {missing_keys}')
        self.db.Badges.update_one({'bid': key}, {'$set': b_dict}, upsert=True)
        return key

    def get_topics(self) -> dict:
        """Return all currently available Topics from the Collection Questions."""
        all_topics = self.db.Questions.distinct("topic")
        topic_number_questions = dict()
        for top in all_topics:
            topic_number_questions[top] = {
                "num_questions": len(self.get_questions(top)),
                "per_easy_questions": round(
                    len(self.get_questions(top, diff=0)) / len(self.get_questions(top)), 2) * 100,
                "per_medium_questions": round(
                    len(self.get_questions(top, diff=1)) / len(self.get_questions(top)), 2) * 100,
                "per_hard_questions": round(
                    len(self.get_questions(top, diff=2)) / len(self.get_questions(top)), 2) * 100
            }
        return topic_number_questions

    def update_progress(self, uid: int, quiz_results: dict) -> int:
        """Updates user progress after completing a quiz."""
        # TODO: update badges
        p_dict = self.get_progress(uid)
        try:
            topic = quiz_results['topic']
            num_questions = quiz_results['num_questions']
            correct = quiz_results['correct']
        except KeyError:
            raise KeyError('Quiz results information are missing! '
                           'Requires: topic, num_questions, correct')
        if topic in p_dict.keys():
            topic_list = p_dict[topic]
            topic_list.append({'timestamp': len(topic_list), 'num_questions': num_questions,
                               'correct': correct})
        else:
            topic_list = [{'timestamp': 0, 'num_questions': num_questions, 'correct': correct}]
        p_dict[topic] = topic_list
        self.set_progress(p_dict)
        return 0

    def get_user_statistics(self, uid: int):
        """Returns y axes for plotting. User progress measured in percentage of correct answers
        per quiz."""
        p_dict = self.get_progress(uid)
        user_topics = set(p_dict.keys()).difference({'uid', 'badges'})
        y_axes = dict()
        for topic in user_topics:
            y = [round(d['correct'] / d['num_questions'] * 100, 2) for d in p_dict[topic]]
            y_axes[topic] = y
        return y_axes


if __name__ == '__main__':
    # do some testing
    db = Database()
    print('User testing:')
    user = db.get_user('mm1', 'mm1')
    print(f'User information: {user}')
    db.set_user({'uid': 1, 'fname': 'Maxi'})
    user = db.get_user('mm1', 'mm1')
    print(f'Update user name: {user}')

    print('\nQuestion testing:')
    qs = db.get_questions('Machine Learning')
    print(f'Number of all ML questions: {len(qs)}')
    qs = db.get_questions('Machine Learning', 5)
    print(f'Got only 5 ML Questions: {len(qs) == 5}')
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
    db.set_progress({'uid': 1,
                     'Machine Learning': [{"timestamp": 0, "num_questions": 20, "correct": 14}]})
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

    print('\nGet Topic Testing:')
    get_topics = db.get_topics()
    print("The Topics and it's counts", get_topics)

    print('\nUpdate progress testing:')
    db.update_progress(1, {'topic': 'Machine Learning', 'num_questions': 666, 'correct': 444})
    print(f'Update user progress after quiz: {db.get_progress(1)}')

    print('\nUser statistic testing:')
    print(f'Show progress y axes: {db.get_user_statistics(1)}')

    print(db.get_user_2("mm1", "mm1"))
