import unittest

from pathlib import Path

tmp_folder_path = Path(__file__).parent / "delete_after_tests"

class BaseCase(unittest.TestCase):
    """Unit tests for config files"""

    @classmethod
    def setUpClass(cls):
        Path(tmp_folder_path).mkdir(parents=True, exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        import shutil
        if tmp_folder_path.exists() and tmp_folder_path.is_dir():
            shutil.rmtree(tmp_folder_path)

    def test_deep_exclude(self):
        from sciunit.base import deep_exclude

        test_state = {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5}
        test_exclude = [("a", "b"), ("c", "d")]
        deep_exclude(test_state, test_exclude)

    def test_default(self):
        # TODO
        pass

    def test_SciUnit(self):
        from sciunit.base import SciUnit

        sciunitObj = SciUnit()
        self.assertIsInstance(sciunitObj.properties(), dict)
        self.assertIsInstance(sciunitObj.__getstate__(), dict)
        self.assertIsInstance(sciunitObj.json(), str)
        sciunitObj.json(string=False)
        self.assertIsInstance(sciunitObj._class, dict)
        sciunitObj.testState = "testState"
        SciUnit.state_hide.append("testState")
        self.assertFalse("testState" in sciunitObj.__getstate__())

    def test_Versioned(self):
        from git import Repo
        from sciunit.base import Versioned

        ver = Versioned()

        # Testing .get_remote()
        # 1. Checking our sciunit .git repo
        # (to make sure .get_remote() works with real repos too!)
        self.assertEqual("origin", ver.get_remote("I am not a remote").name)
        self.assertEqual("origin", ver.get_remote().name)
        # 2. Checking NO .git repo
        self.assertEqual(None, ver.get_remote(repo=None))
        # 3. Checking a .git repo without remotes
        git_repo = Repo.init(tmp_folder_path / "git_repo")
        self.assertEqual(None, ver.get_remote(repo=git_repo))
        # 4. Checking a .git repo with remotes
        origin = git_repo.create_remote("origin", "https://origin.com")
        beta = git_repo.create_remote('beta', "https://beta.com")
        self.assertEqual(origin, ver.get_remote(repo=git_repo))
        self.assertEqual(origin, ver.get_remote("not a remote", repo=git_repo))
        self.assertEqual(beta, ver.get_remote("beta", repo=git_repo))

        # Testing .get_repo()
        self.assertIsInstance(ver.get_repo(), Repo)

        # Testing .get_remote_url()
        self.assertIsInstance(ver.get_remote_url("I am not a remote"), str)

    def test_OldVersioned(self):
        from git import Repo
        from sciunit.base import Versioned

        ver = Versioned()

        # Testing .old_get_remote()
        # 1. Checking our sciunit .git repo
        # (to make sure .old_get_remote() works with real repos too!)
        self.assertEqual("origin", ver.old_get_remote("I am not a remote").name)
        self.assertEqual("origin", ver.old_get_remote().name)
        # 2. Checking NO .git repo
        self.assertEqual(None, ver.old_get_remote(repo=None))
        # 3. Checking a .git repo without remotes
        git_repo = Repo.init(tmp_folder_path / "git_repo_old")
        # @Rick, this should pass!
        self.assertRaises(IndexError, lambda: ver.old_get_remote(repo=git_repo))
        # 4. Checking a .git repo with remotes
        origin = git_repo.create_remote("origin", "https://origin.com")
        beta = git_repo.create_remote('beta', "https://beta.com")
        self.assertEqual(origin, ver.old_get_remote(repo=git_repo))
        self.assertEqual(origin, ver.old_get_remote("not a remote", repo=git_repo))
        self.assertEqual(beta, ver.old_get_remote("beta", repo=git_repo))

if __name__ == "__main__":
    unittest.main()
