import unittest

from budget_app import app, db

from budget_app.models import User, Post

from flask_bcrypt import generate_password_hash

 

class ItemTests(unittest.TestCase):

 

    def setUp(self):

        app.config['TESTING'] = True

        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

        app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing

        self.app = app.test_client()

        with app.app_context():

            
            db.create_all()

            hashed_password = generate_password_hash('testpassword').decode('utf-8')

            user = User(username='testuser', email='test@example.com', password=hashed_password)

            db.session.add(user)

            db.session.commit()

 

    def tearDown(self):

        with app.app_context():

            db.session.remove()

            db.drop_all()

 

    def login(self, email, password):

        response = self.app.post('/login', data=dict(

            email=email,

            password=password

        ), follow_redirects=True)

        return response

 

    def add_post(self, title, content, price):

        response = self.app.post('/post/new', data=dict(

            title=title,

            content=content,

            price=price

        ), follow_redirects=True)

        return response

 

    def delete_post(self, post_id):

        response = self.app.post(f'/post/{post_id}/delete', follow_redirects=True)

        return response

 

    def test_add_post(self):

        self.login('test@example.com', 'testpassword')

        response = self.add_post('Test Post', 'This is a test post.', 10)

        self.assertEqual(response.status_code, 200)

        post = Post.query.filter_by(title='Test Post').first()

        self.assertIsNotNone(post)

        self.assertIn(b'Your post as been created!', response.data)

 

    def test_delete_post(self):

        self.login('test@example.com', 'testpassword')

        self.add_post('Test Post', 'This is a test post.', 10)

        post = Post.query.filter_by(title='Test Post').first()

        self.assertIsNotNone(post)

        response = self.delete_post(post.id)

        self.assertEqual(response.status_code, 200)

        post = Post.query.get(post.id)

        self.assertIsNone(post)

 

if __name__ == "__main__":

    unittest.main()