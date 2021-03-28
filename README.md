# gitclient

Quick and easy method to take a template file and add it to a repo on a new branch, including pull request for review.

No error catching so if the API call fails it falls straight through.

Leverages http.client for HTTPSConnection.

---

### Example Usage

```python
Usage:
    from gitclient import GitClient

    ...
    # Code to load/create template file as string, utf-8
    ...

    client = GitClient(
        name="YOUR GITHUB NAME",
        email="ASSOCIATED EMAIL",
        owner="REPO-OWNER",  # (github.com/[OWNER]/[REPONAME])
        repo="REPO-NAME",
        oauth="[OAuth Secret Token]",
    )
    client.send_template(
        base_branch="main",
        new_branch="my_cool_branch,
        file_name="cool_template_file.md",
        file_contents="# Hello World",
        pr_title="Pull request Title",
        pr_content="Pull request message",
    )
```

---

API documentation references in each method.

Spring-boarded by this gist: [https://gist.github.com/auwsome/123ae1f493dfd9b08434](https://gist.github.com/auwsome/123ae1f493dfd9b08434)
