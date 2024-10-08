from django.contrib.auth import get_user_model
from django.db import models

MSG_TYPES = [
    ("text","text"),
    ("link","link")
]

class Room(models.Model):
    user1 = models.ForeignKey(get_user_model(),on_delete=models.SET_NULL,null=True,blank=True,related_name="room_as_user1")
    user2 = models.ForeignKey(get_user_model(),on_delete=models.SET_NULL,null=True,blank=True,related_name="room_as_user2")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user1}-{self.user2}"

class Messages(models.Model):
    room = models.ForeignKey(Room,on_delete=models.CASCADE)
    sender = models.ForeignKey(get_user_model(),on_delete=models.SET_NULL,null=True,blank=True,related_name="sent_messages")
    receiver = models.ForeignKey(get_user_model(),on_delete=models.SET_NULL,null=True,blank=True,related_name="received_message")
    text = models.TextField(null=True,blank=True)
    type = models.CharField(max_length=100,choices=MSG_TYPES)
    link = models.FileField(upload_to="documents",null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    @property
    def get_data(self):
        if self.type == "text":
            return self.text
        else:
            return self.link.url #type:ignore
