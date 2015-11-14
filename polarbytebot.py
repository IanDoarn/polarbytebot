import praw
import sys, os
import re
import logging, logging.config, logging.handlers
import json
import guildwars2
#import webbrowser

from datetime import datetime
from models import bot_comments, bot_submissions, subreddit, anet_member
from models import session, cfg_file, path_to_cfg
from sqlalchemy import desc

#global reddit session
r = None

class CommentQueue:
    """
    Queue of all to be processed comments.
    """
    def __init__(self, _enabled_subreddits, _botname):
        self.queue = {}
        self.enabled_subreddits = '+'.join(_enabled_subreddits)
        self.botname = _botname
        self.last_comment_id = 0
        self.first_comment = False
        self.produced_posts = []
    """
    Loads up to 1000 comments since last processing.
    """
    def populate(self):
        global r
        try:
            self.last_comment_id = session.query(subreddit)\
                                    .filter_by(website='reddit')\
                                    .first().last_comment
        except:
            self.last_comment_id = 0
            logging.warning('CommentQueue: ' + \
                                'last_comment_id failed init: 0')
        while(True):
            comments = r.get_comments(self.enabled_subreddits,limit=None)
            for cm in comments:
                if cm.author == None:
                    self.last_comment_id = t_last_comment_id
                    logging.warning('CommentQueue: forced return on {0}'\
                                         .format(self.last_comment_id))
                    return self
                if cm.author.name != self.botname:
                    if not self.first_comment:
                        if self.last_comment_id <= 0:
                            self.last_comment_id = int(cm.id,36)
                            logging.warning('CommentQueue: last_comment_id '+\
                                            'repaired: {0}'\
                                            .format(int(cm.id,36)))
                        t_last_comment_id = int(cm.id,36)
                        self.first_comment = True
                    if int(cm.id,36) <= self.last_comment_id:
                        self.last_comment_id = t_last_comment_id
                        return self
                    try:
                        self.queue[cm.subreddit.display_name].append(cm)
                    except KeyError:
                        self.queue[cm.subreddit.display_name] = [cm]
                    finally:
                        logging.debug('commentQueue: add: {0} - {1}'\
                                    .format(cm.name, int(cm.id,36)))
        
    def distribute(self):
        arenanet_member = self.prepareDistribute()
        for key in self.queue:
            if key == 'Guildwars2':
                for post in guildwars2.process_comment(self.queue[key],arenanet_member):
                    self.produced_posts.append(post)
        return self

    def prepareDistribute(self):
        self.produced_posts = []
        anet_query = list(session.query(anet_member))
        anet_members = []
        for member in anet_query:
            anet_members.append(member.username)
        return (anet_members)

class SubmissionQueue:
    """
    Queue of all to be processed submissions.
    """
    def __init__(self, _enabled_subreddits, _botname):
        self.queue = {}
        self.enabled_subreddits = '+'.join(_enabled_subreddits)
        self.botname = _botname
        self.first_submission = False
        self.produced_posts = []
    """
    Loads up to 1000 submissions since last processing.
    """
    def populate(self):
        global r
        try:
            self.last_submission_id = session.query(subreddit)\
                                    .filter_by(website='reddit')\
                                    .first().last_submission
        except:
            self.last_submission_id = 0
            logging.warning('SubmissionQueue: ' + \
                                'last_submission_id failed init: 0')
        while(True):
            subreddits = r.get_subreddit(self.enabled_subreddits)
            submissions = subreddits.get_new(limit=None)
            for subm in submissions:
                if subm.author == None:
                    self.last_submission_id = t_last_submission_id
                    logging.warning('SubmissionQueue: forced return on {0}'\
                                         .format(self.last_submission_id))
                    return self
                if subm.author.name != self.botname:
                    if not self.first_submission:
                        if self.last_submission_id <= 0:
                            self.last_submission_id = int(subm.id,36)
                            logging.warning('submissionQueue: '+\
                                            'last_submission_id repaired: {0}'\
                                            .format(int(subm.id,36)))
                        t_last_submission_id = int(subm.id,36)
                        self.first_submission = True
                    if int(subm.id,36) <= self.last_submission_id:
                        self.last_submission_id = t_last_submission_id
                        return self
                    try:
                        self.queue[subm.subreddit.display_name].append(subm)
                    except KeyError:
                        self.queue[subm.subreddit.display_name] = [subm]
                    finally:
                        logging.debug('submissionQueue: add: {0} - {1}'
                                    .format(subm.name, int(subm.id,36)))
    def distribute(self):
        arenanet_member = self.prepareDistribute()
        for key in self.queue:
            if key == 'Guildwars2':
                for post in guildwars2.process_submission(self.queue[key],arenanet_member):
                    self.produced_posts.append(post)
        return self

    def prepareDistribute(self):
        self.produced_posts = []
        anet_query = list(session.query(anet_member))
        anet_members = []
        for member in anet_query:
            anet_members.append(member.username)
        return (anet_members)

class Polarbyte:
    def __init__(self, cfg_file):
        global r
        self.OAuth2 = cfg_file['oauth2']
        r = praw.Reddit(cfg_file['reddit']['user_agent'])
        self.signature = cfg_file['reddit']['signature']
        self.botname = cfg_file['oauth2']['username']
        self.enabled_subreddits = [e.strip() for e in\
                                     cfg_file['reddit']['enabled_subreddits']\
                                      .split(',')]
        self.forceAuthenticationAgain = True
        self.authenticate()
    def check(self):
        if self.forceAuthenticationAgain:
            self.authenticate()

    def authenticate(self):
        global r
        try:
            r.set_oauth_app_info(client_id = self.OAuth2['client_id'],
                                 client_secret = self.OAuth2['client_secret'],
                                 redirect_uri = self.OAuth2['redirect_uri'])
            r.refresh_access_information(self.OAuth2['refresh_token'])
        except Exception as e:
            self.forceAuthenticationAgain = True
            logging.error('OAuth2: failed: {0}'.format(e))
        else:
            self.forceAuthenticationAgain = False
            logging.info('OAuth2 authenticated')

    def collect(self):
        self.cmQueue = CommentQueue(self.enabled_subreddits, self.botname)\
                    .populate().distribute()
        self.smQueue = SubmissionQueue(self.enabled_subreddits, self.botname)\
                    .populate().distribute()
        self.updateLatestObjectIds(self.cmQueue.last_comment_id, self.smQueue.last_submission_id)
        session.commit()

    def processPosts(self):
        for post in self.smQueue.produced_posts:
            if post['type'] == 'link' or  post['type'] == 'self':
                self.addSubmission(post['subreddit'], post['title'], post['content'], post['type'], post['submitted'])
            elif post['type'] == 'comment':
                self.addComment(post['thing_id'], post['content'], post['submitted'])

    def submit(self):
        self.submitComments()
        self.submitSubmissions()

    def submitComments(self):
        global r
        to_be_commented = session.query(bot_comments).filter_by(submitted=False).all()
        for tbcm in to_be_commented:
            obj = r.get_info(thing_id=tbcm.thing_id)
            if tbcm.thing_id[:2] == 't3':
                try:
                    reply_obj = obj.add_comment(tbcm.content)
                except (praw.errors.InvalidSubmission):
                    self.updateSubmitted(bot_comments, tbcm.id, 'del-1')
                    logging.warning('submitComment: failed (parentDeleted): {0}'.format(tbcm.id))
                else:
                    self.updateSubmitted(bot_comments, tbcm.id, reply_obj.name)
                    logging.info('submitComment: submit: {0}'.format(tbcm.id))
            elif tbcm.thing_id[:2] == 't1':
                try:
                    reply_obj = obj.reply(tbcm.content)
                except (praw.errors.InvalidComment):
                    self.updateSubmitted(bot_comments, tbcm.id, 'del-1')
                    logging.warning('submitComment: failed (parentDeleted): {0}'.format(tbcm.id))
                else:
                    self.updateSubmitted(bot_comments, tbcm.id, reply_obj.name)
                    logging.info('submitComment: submit: {0}'.format(tbcm.id))
            elif tbcm.thing_id[:1] == 'i':
                new_id = self.searchSubmitted(bot_comments, tbcm.thing_id[1:])
                if new_id == 'del-1':
                    self.updateSubmitted(bot_comments, tbcm.id, 'del-1')
                if new_id != None:
                    self.updateThingId(bot_comments, tbcm.id, new_id)
            session.commit()

    def submitSubmissions(self):
        global r
        to_be_submitted = session.query(bot_submissions).filter_by(submitted=False).all()
        for tbsm in to_be_submitted:
            if tbsm.type == 'link':
                sub_obj = r.submit(tbsm.subreddit, tbsm.title, url=tbsm.content)
            elif tbsm.type == 'self':
                sub_obj = r.submit(tbsm.subreddit, tbsm.title, text=tbsm.content)
            #session.query(bot_submissions).filter_by(id=tbsm.id).update({'submitted':True})
            self.updateSubmitted(bot_submissions, tbsm.id, sub_obj.id)
            logging.info('submitSubmission: submit: {0}'.format(tbsm.id))
            session.commit()

    def addComment(self, _thing_id, _content, _submitted=False):
        last_id = _thing_id
        extra_len = len('\n\n--- continued below ---') + len(self.signature)
        while(True):
            if len(_content) <= 0:
                return
            content_parts = _content.split('\n')
            stiched_content = ''
            for part in content_parts:
                if len(stiched_content) + len(part+'\n') + extra_len <= 10000:
                    stiched_content += part+'\n'
                else:
                    break
            row = bot_comments()
            row.thing_id = last_id
            row.submitted = _submitted
            if _content[len(stiched_content):] == '':
                row.content = stiched_content + self.signature
            else:
                row.content = stiched_content + '\n\n--- continued below ---' + self.signature
            session.add(row)
            session.commit()
            last_id = 'i{}'.format(session.query(bot_comments).order_by(desc(bot_comments.id)).first().id)
            _content = _content[len(stiched_content):]

    def addSubmission(self, _subreddit, _title, _content, _type, _submitted=False):
        row = bot_submissions()
        row.title = _title
        row.type = _type
        row.subreddit = _subreddit
        row.content = _content
        row.submitted = _submitted
        session.add(row)
        session.commit()
    
    def updateLatestObjectIds(self, _last_comment_id, _last_submission_id):
        lastIds = session.query(subreddit).filter_by(website='reddit').first()
        if lastIds == None:
            row = subreddit()
            row.website = 'reddit'
            row.last_comment = _last_comment_id
            row.last_submission = _last_submission_id
            session.add(row)
        else:
            session.query(subreddit).filter_by(website='reddit')\
                .update({'last_submission':_last_submission_id,\
                         'last_comment':_last_comment_id})
    def updateSubmitted(self, _table, _search_id, _submit_id):
        session.query(_table).filter_by(id=_search_id)\
            .update({'submitted':True,'submitted_id':_submit_id})
    def searchSubmitted(self, _table, _search_id):
        return session.query(_table).filter_by(id=_search_id).first().submitted_id
    def updateThingId(self, _table, _search_id, _new_id):
        session.query(_table).filter_by(id=_search_id).update({'thing_id':_new_id})

def main():
    global r   
    logging.config.fileConfig(path_to_cfg,disable_existing_loggers=False)
    bot = Polarbyte(cfg_file)
    forceAuthAgain = False
    while(True):
        try:
            bot.check()
            bot.collect()
            bot.processPosts()
            bot.submit()
        except praw.errors.OAuthScopeRequired as e:
            logging.error(e)
            bot.forceAuthenticationAgain = True
        except Exception as e:
            #print(vars(e))
            logging.error(e)
            session.rollback()
     
if __name__ == '__main__':
    main()
