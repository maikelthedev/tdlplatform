import unittest

class TestCreatorMethods(unittest.TestCase):

    def test_nothing(self):
        self.assertEqual(1,1)

    # This is an integration test
    def test_create_test(self):
        """User calls the program with the option create or -c or --create
        that in turn creates a test in the mongoDB with the given name
        if the test already exists it tells the user it already exists and abort
        if it doesn't it creates the table and starts asking the user for questions
        """
        pass

    # This is an integration test
    def test_add_questions(self):
        """The user calls it with add -a --add or similar and a test_name, the creator
        finds the test in the mongodb and starts asking for questions until the user
        stops introducing more"""
        pass

    # This is an integration test
    def test_configure_db(self):
        """On a first run of the program asks for the credentials of the DB to use
        connects to it, tests the connection is possible and creates then deletes
        a table to ensure it has reading/writting rights"""

    def test_question_added(self):
        """Test that introduced a question it is added correctly in the DB"""
        pass

    def test_question_deleted(self):
        """Test that chosen a question it is deleted correctly from the DB"""
        pass

    def test_question_modified(self):
        """Test that given a question to edit it is altered in the DB"""
        pass

if __name__ == '__main__':
    unittest.main()