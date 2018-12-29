"""
Rating Serializers module
"""

from django.db.models import Sum, Avg

from rest_framework import serializers

from rest_framework.validators import UniqueTogetherValidator

from .models import Rating

from ..articles.serializers import ArticleSerializer
from ..articles.models import Article

from ..authentication.serializers import UserSerializer
from ..authentication.models import User


class RateSerializers(serializers.ModelSerializer):
    """
    Rate Serializer
    :params: serializers.ModelSerializer:
        parent class parameter
    """
    rating = serializers.IntegerField()
    rater = UserSerializer(read_only=True)
    article = ArticleSerializer(read_only=True)


    class Meta():
        """
        Meta class
        :adds more setting to the RateSerializer class:
        """
        model = Rating
        fields = ('rating', 'article', 'rater')

    def set_average_rating(self, obj, rating):
        average = rating
        try:
            ratings = Rating.objects.filter(article=obj.id)
            if ratings:
                average = ratings.all().aggregate(
                Avg('rating'))['rating__avg']
            obj.average_rating = average
            obj.save()
        except Exception as e:
            print(e)

    def create(self, validated_data):
        """
        :params: validated_data:
          ensures data being passed is going to be valid
        """
        # validate rating data
        rate = validated_data['rating']
        # get user and slug context from request
        slug = self.context.get('slug')
        user =  self.context.get('user')
        # validate user data
        validated_data['rater'] = user

        # check if article exists
        article = check_article_exists(slug)

        # validate article data
        validated_data['article'] = article

        # check for correct rating range
        if rate not in range(1, 6):
            raise serializers.ValidationError(
                'Error, rating is between 1 to 5')

        author = article.author
        # check if rater is the author of the article
        if author == user:
            raise serializers.ValidationError(
                'Error, you can\'t rate your own article')

        # check if user has ever rated the article
        # if not save the user rating
        # else update the rating
        rating_instance = None
        try:
            rating_instance = Rating.objects.get(rater=user, article=article)
        except:
            "Error, article does not exist"

        if rating_instance:
            """ Update the rating """
            rating_instance.rating = rate
            rating_instance.save()
        else:
            Rating.objects.create(**validated_data)

        self.set_average_rating(article, rate)

        return validated_data


def check_article_exists(slug):
    """
    Check if article exists
    :param: slug: article slug that verifies
      the article exits
    :return: article
    """
    try:
        article = Article.objects.get(slug=slug)
    except Article.DoesNotExist:
        raise serializers.ValidationError(
            'Error, Article does not exist')
    return article
