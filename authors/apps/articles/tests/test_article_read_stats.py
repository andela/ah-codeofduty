from ..models import ArticleStatistics
from .base import BaseTest


class StatsTestCase(BaseTest):
    """Class for testing reading stats"""

    def test_views_increase_upon_getting_article(self):
        """
        Method asserts that count increases after every view
        """
        response = self.create_article(self.token, self.test_article_data)
        print(response)
        old_count = ArticleStatistics.objects.count()
        url = self.ARTICLE
        self.client.get(url, format='json')
        new_count = ArticleStatistics.objects.count()
        self.assertNotEqual(old_count, new_count)
