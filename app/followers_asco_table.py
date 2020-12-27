from app import db

##################################################
#       Followers/Followed association table
##################################################
# Auxiliary table - Followers association table.

followers = db.Table('followers',
                     db.Column('follower_id', db.Integer,
                               db.ForeignKey('user.id')),
                     db.Column('followed_id', db.Integer,
                               db.ForeignKey('user.id'))
                     )
