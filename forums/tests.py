from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from accounts.models import User
from forums.models import Discussion, Comment


class ForumTest(APITestCase):
    fixtures = ["users.json", "discussion.json"]
    endpoint = "/forums/"
    client = APIClient()

    def regular_user_login(self):
        user = User.objects.get(id=2)
        self.client.force_authenticate(user)

    def super_admin_login(self):
        admin = User.objects.get(id=1)
        self.client.force_authenticate(admin)

    def _create_discussion(self, id):
        self.regular_user_login()
        post = Discussion.objects.create(
            user=User.objects.get(id=id), title="New", content="Content"
        )
        return f"{self.endpoint}{post.id}/"

    def test_user_can_create_discussion(self):
        self.regular_user_login()
        data = {
            "title": "Regular",
            "content": "No content",
            "category": "FinTech",
            "tags": "premium, friendly"
        }
        response = self.client.post(self.endpoint, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_can_update_own_discussion(self):
        url = self._create_discussion(2)
        data = {"title": "Newer"}

        response = self.client.patch(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("title"), data.get("title"))

    def test_user_cannot_update_others_discussion(self):
        url = self._create_discussion(1)
        data = {"title": "Newer"}

        response = self.client.patch(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_can_delete_own_discussion(self):
        url = self._create_discussion(2)
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Discussion.objects.all().count(), 2)

    def test_user_cannot_delete_others_discussion(self):
        url = self._create_discussion(1)
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_can_list_all_discussions(self):
        self.regular_user_login()
        response = self.client.get(self.endpoint, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("count"), 2)

    def test_user_can_list_all_own_discussions(self):
        self.regular_user_login()
        url = f"{self.endpoint}mine/"
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("count"), 1)

    def test_user_can_add_comment(self):
        self.regular_user_login()
        data = {"content": "New comment"}
        url = "/forums/1/add-comment/"
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.all().count(), 2)

    def test_user_cannot_update_others_comment(self):
        self.regular_user_login()
        Comment.objects.create(
            user=User.objects.get(id=2), content="New Comment", post=Discussion.objects.get(id=1))

        self.super_admin_login()
        data = {"content": "Changed comment"}
        url = "/forums/1/add-comment/"

        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.all().count(), 3)
        self.assertNotEqual(Comment.objects.all().count(), 2)

    def test_user_can_update_own_comment(self):
        self.regular_user_login()
        Comment.objects.create(
            user=User.objects.get(id=2), content="New Comment", post=Discussion.objects.get(id=1))

        data = {"content": "Changed comment"}
        url = "/forums/1/add-comment/"

        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Comment.objects.all().count(), 2)
        self.assertNotEqual(Comment.objects.all().count(), 3)

    def test_user_cannot_delete_others_comment(self):
        self.regular_user_login()
        comment = Comment.objects.create(
            user=User.objects.get(id=1), content="New Comment", post=Discussion.objects.get(id=1))

        data = {"comment_id": comment.id}
        url = "/forums/1/delete-comment/"

        response = self.client.delete(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Comment.objects.all().count(), 2)
        self.assertNotEqual(Comment.objects.all().count(), 1)


    def test_user_can_delete_own_comment(self):
        self.regular_user_login()
        comment = Comment.objects.create(
            user=User.objects.get(id=2), content="New Comment", post=Discussion.objects.get(id=1))

        data = {"comment_id": comment.id}
        url = "/forums/1/delete-comment/"

        response = self.client.delete(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Comment.objects.all().count(), 1)
        self.assertNotEqual(Comment.objects.all().count(), 2)

    def test_user_can_like_discussion(self):
        self.regular_user_login()
        url = "/forums/1/like-unlike/"
        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("likes"), 2)

    def test_user_can_unlike_discussion(self):
        self.regular_user_login()
        url = "/forums/2/like-unlike/"
        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("likes"), 2)
