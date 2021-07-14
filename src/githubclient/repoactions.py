"""
GitHub Actions for Repos

Author: Preocts (Preocts#8196)
"""
from githubclient.apiclient import APIClient


class RepoActions(APIClient):
    """Actions for repos in GitHub"""

    def __init__(self, repo_owner: str, repo_name: str, num_pools: int = 10) -> None:
        """Create client class. num_pools = https pool manager"""
        super().__init__(num_pools=num_pools)
        self.repo = repo_name
        self.owner = repo_owner

    def get_branch(self, branch_name: str) -> str:
        """Get a branch"""
        # https://docs.github.com/en/rest/reference/repos#get-a-branch

        self.logger.debug("Requesting SHA of branch: %s", branch_name)
        endpoint = f"/repos/{self.owner}/{self.repo}/branches/{branch_name}"

        result = self.git_get(endpoint)

        sha = result.get("commit", {}).get("sha", "")

        return sha

    def create_branch(self, base_branch: str, new_branch: str) -> str:
        """Creates branch from base branch, return SHA of new branch"""
        # https://docs.github.com/en/rest/reference/git#create-a-reference

        self.logger.debug("Creating Branch")
        endpoint = f"/repos/{self.owner}/{self.repo}/git/refs"
        payload = {
            "ref": f"refs/heads/{new_branch}",
            "sha": self.get_branch(base_branch),
        }
        result = self.git_post(endpoint, payload)

        return result.get("object", {}).get("sha", "")
