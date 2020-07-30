import unittest
from src.persistence import users_db, DBUser

class PersistenceTestFixture(unittest.TestCase):

    def setUp(self):
        users_db.purge()
        self.db_user = DBUser(1)

    def test_AddTwoTacos(self):
        self.db_user.add_tacos(1)
        self.db_user.add_tacos(1)
        tacos = self.db_user.owned_tacos()
        self.assertEqual(2, tacos)

    def test_endWithOneTacoAfterAddingAndRemoving(self):
        self.db_user.add_tacos(2)
        self.db_user.remove_tacos(1)
        tacos = self.db_user.owned_tacos()
        self.assertEqual(2, tacos)

    def tearDown(self):
        del(self.db_user)


if __name__ == '__main__':
    unittest.main() 