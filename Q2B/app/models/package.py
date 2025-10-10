from mongoengine import Document, StringField, IntField, FloatField

class Package(Document):
    meta = {'collection': 'package'}
    hotel_name = StringField(max_length=30)
    duration = IntField()
    unit_cost = FloatField()
    image_url = StringField(max_length=30)
    description = StringField(max_length=500)
    
    def packageCost(self):
        return self.unit_cost * self.duration
    
    @staticmethod
    def getPackage(hotel_name):
        return Package.objects(hotel_name=hotel_name).first()
        
    @staticmethod
    def getAllPackages():
        return Package.objects()
        
    @staticmethod
    def createPackage(hotel_name, duration, unit_cost, image_url, description):
        return Package(hotel_name=hotel_name, duration=duration, unit_cost=unit_cost, image_url=image_url, description=description).save()