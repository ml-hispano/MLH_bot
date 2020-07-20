import unittest
import src.use_cases as u
from src.persistence import users_db, DBUser

ALICE = 10
BOB = 20

class UseCasesTestFixture(unittest.TestCase):

    def setUp(self):
        users_db.purge()

    def test_AliceGiveTacoToBob(self):
        #given
        self.assertEqual(5, DBUser(ALICE).remaining_tacos())
        self.assertEqual(0, DBUser(BOB).owned_tacos())

        #when
        u.give_tacos(ALICE, BOB, 1)

        #then
        self.assertEqual(4, DBUser(ALICE).remaining_tacos())
        self.assertEqual(1, DBUser(BOB).owned_tacos())

#    def tearDown(self):

if __name__ == '__main__':
    unittest.main() 
