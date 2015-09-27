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
    
    """
    Loads up to 1000 comments since last processing.
    """
    def populate(self):
        try:
            self.last_comment_id = session.query(subreddit)\
                                    .filter_by(website='reddit')\
                                    .first().last_comment
        except:
            self.last_comment_id = 0
            logging.warning('CommentQueue: last_comment_id failed init: 0')
        while(True):
            comments = r.get_comments(self.enabled_subreddits,limit=None)
            for cm in comments:
                if cm.author.name != self.botname:
                    if not self.first_comment:
                        if self.last_comment_id <= 0:
                            self.last_comment_id = int(cm.id,36)
                            logging.warning('commentQueue: last_comment_id'+\
                                            'repaired: {0}'\
                                            .format(int(cm.id,36)))
                        t_last_comment_id = int(cm.id,36)
                        self.first_comment = True
                    if int(cm.id,36) <= self.last_comment_id:
                        self.last_comment_id = t_last_comment_id
                        return
                    try:
                        self.queue[cm.subreddit.display_name].append(cm)
                    except KeyError:
                        self.queue[cm.subreddit.display_name] = [cm]
                    else:
                        logging.info('commentQueue: add: {0} - {1}'\
                                    .format(cm.name, int(cm.id,36))
        
class SubmissionQueue:
    """
    Queue of all to be processed submissions.
    """
    def __init__(self, _enabled_subreddits, _botname, _last_submission_id):
        self.queue = {}
        self.enabled_subreddits = '+'.join(_enabled_subreddits)
        self.botname = _botname
        self.last_submission_id = _last_submission_id
        self.first_submissions = False
    """
    Loads up to 1000 submissions since last processing.
    """
    def populate(self):
        try:
            self.last_submission_id = session.query(subreddit)\
                                    .filter_by(website='reddit')\
                                    .first().last_submission
        except:
            self.last_submission_id = 0
            logging.warning('SubmissionQueue: last_submission_id failed init: 0')
        while(True):
            subreddits = r.get_subreddit(self._enabled_subreddits)
            submissions = subreddits.get_new(limit=None))
            for subm in submissions:
                if subm.author.name != self.botname:
                    if not self.first_submission:
                        if self.last_submission_id <= 0:
                            self.last_submission_id = int(cm.id,36)
                            logging.warning('submissionQueue:'+\ 
                                            'last_submission_id repaired: {0}'\
                                            .format(int(cm.id,36)))
                        t_last_submission_id = int(cm.id,36)
                        self.first_submission = True
                    if int(cm.id,36) <= self.last_submission_id:
                        self.last_submission_id = t_last_submission_id
                        return
                    try:
                        self.queue[subm.subreddit.display_name].append(subm)
                    except KeyError:
                        self.queue[subm.subreddit.display_name] = [subm]
                    else:
                        logging.info('submissionQueue: add: {0} - {1}'
                                    .format(subm.name, int(subm.id,36))
            
class Polarbyte:
    def __init__(self, cfg_file):
        self.OAuth2 = cfg_file['oauth2']
        self.praw = praw.Reddit(cfg_file['reddit']['user_agent'])
        self.signature = cfg_file['reddit']['signature']
        self.botname = cfg_file['oauth2']
        self.enabled_subreddits = [e.strip() for e in cfg_file['reddit']['enabled_subreddits'].split(',')]
        authenticate()

    def authenticate(self):
        try:
            r.set_oauth_app_info(client_id = self.OAuth2['client_id'],
                                 client_secret = self.OAuth2['client_secret'],
                                 redirect_uri = self.OAuth2['redirect_uri'])
            r.refresh_access_information(self.OAuth2['refresh_token'])
        except Exception as e:
            logging.error('OAuth2: failed: {0}'.format(e))
        else:
            logging.info('OAuth2 authenticated')

    def collect(self):
        cmQueue = CommentQueue(self.enabled_subreddits, self.botname)
        smQueue = SubmissionQueue(self.enabled_subreddits, self.botname)
        
        



        updateLastestObjectIds(cmQueue.last_comment_id, smQueue.last_submission_id)
        session.commit()
    def submit(self):
    def addComment(self, _thing_id, _content, _submitted=False):
        last_id = _thing_id
        extra_len = len('\n\n--- continued below ---') + len(self.signature)
        while(True)
            if len(_content) <= 0:
                return
            content_parts = _content.split('\n')
            stiched_content = ''
            for part in content_parts:
                if len(stiched_content) + len(part) + extra_len <= 10000:
                    stiched_content += part
                
                
            current_content = _content[:10000 - extra_len]
        row = bot_comments()
        
    def addSubmission(self, _subreddit, _title, _author, _content, _type, _submitted=False):
        row = bot_submissions()
        if len(_title) + len(_author) + len(' []') > 300:
            row.title = '{0}... [{1}]'.format(_title[:300 - len(_author) - len(' []') - len('...')], _author)
        else:
            row.title = '{0} [{1}]'.format(_title, _author)
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
        else
            session.query(subreddit).filter_by(website='reddit').first()\
                .update({'last_submission':_last_submission_id,\
                         'last_comment':_last_comment_id})

def prepare_comment(_thing_id, _submitted, _content):
    last_id = _thing_id
    while(True):            
        _current_content = _content[:10000 - len('\n\n--- continued below ---') - len(cfg_file['reddit']['signature'])]
        if len(_content) == 0:
            return
        row = bot_comments()
        row.thing_id = last_id
        row.submitted = _submitted
        if _content[len(_current_content):] == '':
            row.content = _current_content + cfg_file['reddit']['signature']
        else:
            row.content = _current_content + '\n\n--- continued below ---' + cfg_file['reddit']['signature']
        session.add(row)
        session.commit()
        last_id = 'i' + str(session.query(bot_comments).order_by(desc(bot_comments.id)).first().id)
        _content = _content[len(_current_content):]
def guildwars2_filter_cm(comments, array_anet_names):
    for cm in comments:
        logging.info("comment")
        if cm.author.name in array_anet_names:
            logging.info("comment from anet: " + cm.name)
            row = bot_submissions()
            title = cm.link_title
            if (len(title) + len(cm.author.name) + 3) > 300:
                title = title[:300 - len(cm.author.name) - 3 - 3]
                title += '...'
            row.title = title + ' [' + cm.author.name + ']'
            row.type = 'link'
            row.subreddit = 'gw2devtrack'
            row.submitted = False
            row.content = cm.permalink.replace('//www.reddit.com','//np.reddit.com') + '?context=1000'
            session.add(row)
        continue # DISALLOWS COMMENTS TO BE PARSED FPR GW2 LINKS
        if re.search('http.*?:\/\/.*?guildwars2.com\/', cm.body) != None:
            logging.info("comment with gw2 link: " + cm.name)
            all_links = re.findall('http.*?:\/\/.*?guildwars2.com\/[^ \])\s]*', cm.body)
            for link in all_links:
                if link != '':
                    try:
                        prepare_comment(cm.name, False, guildwars2.locate_origin(link))
                    except Exception as e:
                        logging.error(e)
                        session.rollback()
                    else:
                        session.commit()
def guildwars2_filter_sm(submissions, array_anet_names):
    for sm in submissions:
        logging.info('submission')
        if sm.author.name in array_anet_names:
            logging.info("submission from anet: " + sm.name )
            row = bot_submissions()
            title = sm.title
            if (len(title) + len(sm.author.name) + 3) > 300:
                title = title[:300 - len(sm.author.name) - 3 - 3]
                title += '...'
            row.title = title + ' [' + sm.author.name + ']'
            row.type = 'link'
            row.subreddit = 'gw2devtrack'
            row.submitted = False
            row.content = sm.permalink.replace('//www.reddit.com','//np.reddit.com') + '?context=1000'
            session.add(row)
        if re.search('http.*?:\/\/.*?guildwars2.com\/', sm.selftext) != None:
            logging.info("submission with gw2 link in selftext: " + sm.name)
            all_links = re.findall('http.*?:\/\/.*?guildwars2.com\/[^ \])]*', sm.selftext)
            for link in all_links:
                if link != '':
                    try:
                        prepare_comment(sm.name, False, guildwars2.locate_origin(link))
                    except Exception as e:
                        session.rollback()
                        logging.error(e)
        session.commit()
        if re.search('http.*?:\/\/.*?guildwars2.com\/', sm.url) != None:
            logging.info("submission with gw2 link in url: " +  sm.name)
            all_links = re.findall('http.*?:\/\/.*?guildwars2.com\/[^ \])]*', sm.url)
            for link in all_links:
                if link != '':
                    try:
                        prepare_comment(sm.name, False, guildwars2.locate_origin(link))
                    except Exception as e:
                        logging.error(e)
                        session.rollback()
        session.commit()


def distribute_queues(comment_queue, submission_queue):
    anet_query = list(session.query(anet_member))
    anet_members = []
    for member in anet_query:
        anet_members.append(member.username)
    try:
        guildwars2_filter_cm(comment_queue['Guildwars2'], anet_members)
    except KeyError as e:
        pass
    except Exception as e:
        logging.error(e)
    try:
        guildwars2_filter_sm(submission_queue['Guildwars2'], anet_members)
    except KeyError as e:
        pass
    except Exception as e:
        logging.error(e)
def main():
    global r
    global search_comment_id
    global search_submission_id
    
    logging.config.fileConfig(path_to_cfg)
    
    r = praw.Reddit(cfg_file['reddit']['user_agent'])	
    enabled_subreddits = ['Guildwars2']
    while (True):
        try:
            authenticate(cfg_file['oauth2'])
        except Exception:
            logging.error('OAuth2 could not authenticate')
            continue
        else:
            logging.info('OAuth2 authenticated')
            break;

    while (True):
        try:
            subreddit_obj = session.query(subreddit).filter_by(website='reddit').first()
            search_comment_id = subreddit_obj.last_comment
            search_submission_id = subreddit_obj.last_submission
        except:
            logging.warning('search_comment_id and search_submission_id initialized with 0')
            search_comment_id = 0
            search_submission_id = 0

        submission_queue = {}
        comment_queue = {}
        try:
            comment_queue = load_recent_comments(enabled_subreddits)
            submission_queue = load_recent_submissions(enabled_subreddits)
            distribute_queues(comment_queue, submission_queue)
            last_ids = session.query(subreddit).filter_by(website="reddit").first()
            if last_ids == None:
                row = subreddit()
                row.website = 'reddit'
                row.last_submission = search_submission_id
                row.last_comment = search_comment_id
                #logging.info('last submission updated: ' + str(search_submission_id) + ' - last comment updated: ' + str(search_comment_id))
                session.add(row)
            else:
                session.query(subreddit).filter_by(website="reddit").update({'last_submission':search_submission_id,'last_comment':search_comment_id})
                #logging.info('last submission updated: ' + str(search_submission_id) + ' - last comment updated: ' + str(search_comment_id))
            session.commit()
        except KeyboardInterrupt:
            raise
        except Exception as e:
            logging.error(e)
            session.rollback()
        try:
            to_be_commented = session.query(bot_comments).filter_by(submitted=False).all()
            for tbcm in to_be_commented:
                cm_obj = r.get_info(thing_id=tbcm.thing_id)
                if tbcm.thing_id[:2] == 't3':
                    reply_obj = cm_obj.add_comment(tbcm.content)
                    session.query(bot_comments).filter_by(id=tbcm.id).update({'submitted':True,'submitted_id':reply_obj.name})
                    logging.info(str(tbcm.id) + ' in bot_comments submitted')
                elif tbcm.thing_id[:2] == 't1':
                    reply_obj = cm_obj.reply(tbcm.content)
                    session.query(bot_comments).filter_by(id=tbcm.id).update({'submitted':True,'submitted_id':reply_obj.name})
                    logging.info(str(tbcm.id) + ' in bot_comments submitted')
                elif tbcm.thing_id[:1] == 'i':
                    new_id = session.query(bot_comments).filter_by(id=tbcm.thing_id[1:]).first().submitted_id
                    if new_id != None:
                        session.query(bot_comments).filter_by(id=tbcm.id).update({'thing_id':new_id})
                session.commit()
        except Exception as e:
            logging.error(e)
            session.rollback()
        try:
            to_be_submitted = session.query(bot_submissions).filter_by(submitted=False).all()
            for tbsm in to_be_submitted:
                if tbsm.type == 'link':
                    r.submit(tbsm.subreddit,tbsm.title,url=tbsm.content)
                elif tbsm.type == 'self':
                    r.submit(tbsm.subreddit,tbsm.title,text=tbsm.content)
                session.query(bot_submissions).filter_by(id=tbsm.id).update({'submitted':True})
                logging.info(str(tbsm.id) + ' in bot_submissions submitted')
                session.commit()
        except Exception as e:
            logging.error(e)
            session.rollback()

if __name__ == '__main__':
    main()
