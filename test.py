import unittest
from budget_app import app, db
from budget_app.forms import RegistrationForm, LoginForm, PostForm

class ItemTests(unittest.TestCase):

    # Setup and teardown
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    # Helper methods
    def login_diff(self, username,password , confirm_password):
        self.app.post("/register", form=RegistrationForm(username=username, password=password, confirm_password = confirm_password, submit = True), follow_redirects=True)
        return self.app.post('/login', form=LoginForm(username=username, password=password, submit = True), follow_redirects=True)
    
    
    def login(self, username, password):
        self.app.post("/register", data=RegistrationForm(username=username, password=password ,confirm_password = password ), follow_redirects=True)
        return self.app.post('/login', data=LoginForm(username=username, password=password), follow_redirects=True)
    #A closer way to what you send me
    def add_post(self, title, content, quantity):
        return self.app.post("/post/new", data=PostForm(title=title, content=content, price=quantity), follow_redirects=True)
    #What I think should work on the code, since the submit is what send the POST request
    def add_post_diff(self, title, content, quantity):
        return self.app.post("/post/new", data=PostForm(title=title, content=content, price=quantity, submit = True), follow_redirects=True)

    def delete_item(self, post_id):
        return self.app.post("/post/<int:post_id>/delete", data=dict(post_id=post_id), follow_redirects=True)

    # Test adding item
    def test_add_post(self):
        self.login('testuser', 'testpassword')
        response = self.add_post('Test', "contnet try",10)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Item added successfully!', response.data)


    def test_add_post_diff(self):
        self.login('testuser', 'testpassword')
        response = self.add_post('Test', "contnet try",10)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Item added successfully!', response.data)

    # # Test adding item with special characters
    # def test_add_item_with_special_characters(self):
    #     self.login('testuser', 'testpassword')
    #     response = self.add_item('Test @Item!', 5)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn(b'Item added successfully!', response.data)

    # # Test deleting item
    # def test_delete_item(self):
    #     self.login('testuser', 'testpassword')
    #     self.add_item('Test Item', 10)
    #     response = self.delete_item('Test Item')
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn(b'Item deleted successfully!', response.data)

    # # Test deleting non-existent item
    # def test_delete_nonexistent_item(self):
    #     self.login('testuser', 'testpassword')
    #     response = self.delete_item('Nonexistent Item')
    #     self.assertEqual(response.status_code, 404)
    #     self.assertIn(b'Item not found', response.data)

    # # Test deleting item with special characters
    # def test_delete_item_with_special_characters(self):
    #     self.login('testuser', 'testpassword')
    #     self.add_item('Test @Item!', 5)
    #     response = self.delete_item('Test @Item!')
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn(b'Item deleted successfully!', response.data)

if __name__ == "__main__":
    unittest.main()
