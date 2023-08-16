from django.db import models

class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    is_something = models.BooleanField(default=False)
    avg_score = models.FloatField(default=0.0)

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

class MyData(models.Model):
    user_input = models.CharField(max_length=100)
    processed_result = models.CharField(max_length=100)

    def __str__(self):
        return self.user_input

