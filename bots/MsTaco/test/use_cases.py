import unittest
import src.use_cases as u
from src.persistence import users_db, DBUser

ALICE = 10
BOB = 20
CRIS = 20

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

    def test_AliceGiveTacoToBobWithUrl_conTextoAntesYDespues(self):
        #given
        self.assertEqual([], DBUser(BOB).urls())

        #when
        u.give_tacos(ALICE, BOB, 1, message="aqui https://github.com/ml-hispano/MLH_bot/issues/14 pueden ver el issue")

        #then
        self.assertEqual(['https://github.com/ml-hispano/MLH_bot/issues/14'], DBUser(BOB).urls())

    def test_AliceGiveTacoToBobWithUrl_conTextoAntes(self):
        #given
        self.assertEqual([], DBUser(BOB).urls())

        #when
        u.give_tacos(ALICE, BOB, 1, message="aqui pueden ver el issue https://github.com/ml-hispano/MLH_bot/issues/14")

        #then
        self.assertEqual(['https://github.com/ml-hispano/MLH_bot/issues/14'], DBUser(BOB).urls())

    def test_AliceGiveTacoToBobWithUrl_conTextoDespues(self):
        #given
        self.assertEqual([], DBUser(BOB).urls())

        #when
        u.give_tacos(ALICE, BOB, 1, message="https://github.com/ml-hispano/MLH_bot/issues/14 aqui pueden ver el issue")

        #then
        self.assertEqual(['https://github.com/ml-hispano/MLH_bot/issues/14'], DBUser(BOB).urls())

    def test_AliceGiveTacoToBobWithUrl_conUrlRepetida(self):
        #given
        self.assertEqual([], DBUser(BOB).urls())

        #when
        u.give_tacos(ALICE, BOB, 1, message="https://github.com/ml-hispano/MLH_bot/issues/14 aqui pueden ver el issue")
        u.give_tacos(CRIS, BOB, 1, message="aqui pueden ver el issue https://github.com/ml-hispano/MLH_bot/issues/14")

        #then
        self.assertEqual([
            'https://github.com/ml-hispano/MLH_bot/issues/14',
            'https://github.com/ml-hispano/MLH_bot/issues/14',
        ], DBUser(BOB).urls())

if __name__ == '__main__':
    unittest.main() 
