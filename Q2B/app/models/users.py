from mongoengine import Document, StringField 
from flask_login import UserMixin


class User(UserMixin, Document):
    meta = {'collection': 'appUsers'}
    email = StringField(max_length=30)
    password = StringField()
    name = StringField()
    avatar = StringField()
    
    @staticmethod
    def getUser(email):
        return User.objects(email=email).first()

    @staticmethod
    def getUserById(user_id):
        return User.objects(pk=user_id).first()
    
    @staticmethod 
    def createUser(email, name, password):
        user = User.getUser(email)
        if not user:
            user = User(email=email, name=name, password=password, avatar = "").save()
        return user  

    @staticmethod
    def addAvatar(user, filename):
        user.avatar = filename
        user.save()



