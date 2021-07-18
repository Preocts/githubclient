# Create branch, add file, and make pull request using GitHub API

In the endless search for inches of improvement, automation often rises to the challenge. One such improvement I was looking for was to reduce the steps I took on a daily process within git an GitHub. This process involved a simple situation; throughout the week I would need to create a mark-down document, add it into a central repository, and make a pull request. I had already created a template of the document which had a few metadata fields that, programmatically, were filled in automatically. Automating the git routine was the challenge to be overcome here.

To start, let us break the challenge down into the pieces that we need to accomplish and then look at each step in detail. While my code was done in Python and is linked at the end of this write-up, the steps below will focus more on the API of GitHub. This means if you know how to send an HTTPS request in the language of your choice, you can use this write-up.

### Steps to accomplish the goal (duplicating the manual actions):

1. Create a new branch in the repo, using `main` as the base-branch
   - `git checkout main`
   - `git pull upstream main`
   - `git checkout -b summary04022021`
1. Copy my template file into the repo, renaming it
   - `cp ~/templates/daily.md summary04022021.md`
   - *An existing python script would be used here to update the few pieces of metadata using a csv source file*
1. Add the file to the stage
   - `git add summary04022021.md`
1. Commit the change
   - `git commit -m "Week summary file"`
1. Push the changes to GitHub
   - `git push upstream HEAD`
1. Log into GitHub and create a pull request
   - *Button clicks, copy/paste a standard PR message, add some labels, and submit*

In total, the process would take 5 to 10 minutes of my day depending on if GitHub wanted to force me to dig my password out or not. Perfect for a little automation!

Below I'll walk though each of the steps as they translate to actions with the API. The payloads and routes will be detailed in each.

*Note: This automation works for existing repos with at least one existing branch. It will not work without extra steps on an empty repo.*

---

## Getting started: Accessing the API

### Authentication

We need to authenticate ourselves with GitHub. Under this example the repo we want to interact with is a public repo, so no extra invites or setup is needed beyond our own GitHub account. We just need a personal OAuth token.

You can create one in your GitHub's personal account settings `Developer settings` -> `Personal Access Tokens`. There are a wide selection of permissions to select from when creating a token. For this project the only permission we need this OAuth key to have is `public_repo`.

Create a token and save it in your `.env` file, or preferred method of loading secrets. *Remember, this token is a password into your account. Don't keep it in anything that is being committed to your repo.*

### Headers

With the token secured, the next step is to define your headers. Simple enough for our application. We want to tell GitHub we're using their v3 API, who we are, and what our authorization token is.

```json
{
    "Accept": "application.vnd.github.v3+json",
    "User-Agent": "[YOUR GITHUB NAME HERE]",
    "Authorization": "token [YOUR PERSONAL ACCESS TOKEN HERE]"
}
```

To send the two types of requests we'll need, POST and GET, to GitHub I just used Python's `https.client` library, which is a built-in. Again, any method will work here. You just need to send a POST or GET HTTPS request and have the ability to consume the JSON response as we'll need to carry some information from each step forward to the next.

### API v3 routes and payload

A quick outline to some of the `[values]` I outline in the steps below:
- `[owner]` : This is the orginization or owner of the repo, the first value in the URL when you navigate to the repo of choice.
- `[repo]` : This it the actual repository name

```
https://api.github.com/Preocts/gitclient/branches/main

is

https://api.github.com/[owner]/[repo]/branches/[branch_name]
```

Payloads can either be parameters, added to the URL of the call, or provided as a json object to the route.

---

## Create a branch and getting a branch SHA
---

To create the branch in GitHub we actually are creating a new reference point in the history of the repo. Each reference needs a starting point in the history which is the branch the new branch is created from. The API wants the first, our new branch, in the form of a branch name and the latter, the base branch, in the form of a SHA. So we have two steps to accomplish here.

### Getting the base branch SHA

Getting a branch SHA is a straight-forward. We make a GET request to the endpoint pointed at our base branch and receive a JSON object back that has the `sha` within it. This `sha` value will be used again in many of the steps to reference this point in the repo's history.

**GET Route:** `https://api.github.com/repos/[owner]/[repo]/branches/[base_branch_name]`

*Truncated response:*
```json
{
  "name": "main",
  "commit": {
    "sha": "7fd1a60b01f91b314f59955a4e4d4e80d8edf11d",
    "node_id": "MDY6Q29tbWl0N2ZkMWE2MGIwMWY5MWIzMTRmNTk5NTVhNGU0ZDRlODBkOGVkZjExZA==",
    "commit": {
        ...
    }
  }
}
```

### Creating a new branch

With the sha of our base branch in hand, we can create the payload needed for creating a new branch and POST that to GitHub.

*Payload:*
```json
{
    "ref": "refs/heads/[new_branch_name]",
    "sha": "7fd1a60b01f91b314f59955a4e4d4e80d8edf11d"
}
```

**POST Route:** `https://api.github.com/repos/[owner]/[repo]/git/refs`

You can see we used the SHA collected in the payload and included our own new branch name. This is creating a new reference *at the same point in the history* as our base branch. If you inspect the returned response for this step, you'll see the new branch even has the same `sha`.

## Create a blob
---

The next step in our manual process is to copy the template file into the repo's working directory. Through the API we'll do that by creating a blob, or binary large object. Blobs can be a lot of things but, for this situation, ours is just a simple plain-text file.

Making a blob in a repo just requires our repo information and the actual file contents. By default, GitHub will assume the blob is encoded in utf-8. If needed, base64 can be used.

The response will contain a SHA for the blob, we need that for the next step.

*Payload:*
```json
{
    "owner": "[REPO OWNER]",
    "repo": "[REPO NAME]",
    "content": "[FILE CONTENT HERE]",
    "encoding": "utf-8"
}
```

**POST Route:** `https://api.github.com/repos/[owner]/[repo]/git/blobs`

*Response:*
```json
{
  "url": "https://api.github.com/repos/preoct/gitclient/git/blobs/3a0f86fb8db8eea7ccbb9a95f325ddbedfb25e15",
  "sha": "3a0f86fb8db8eea7ccbb9a95f325ddbedfb25e15"
}
```

## Create a tree
---

Now our blob just exists, without a home. This is the same as an untracked file in a working directory of a repo. GitHub knows the blob exists, but it isn't tracked in history and won't be committed. By creating a tree for this blob we will stage the blob within the repo. At the same time, this will give the blob a filename and filepath.

You'll notice we reuse the SHA from our base branch here as `base_branch`. Remember, that is because both our base branch and our new branch reference the same point of history in the repo.

In the `tree` object you can see how we give our blob a filename. If we wanted to put that file into a directory we could use `daily/documents/our_filename_here.md` and the request will place the file in `./daily/documents` of the repo. The `mode` here tells GitHub our blob in this tree is just a file. The `sha` is from the response of our create a blob step.

Once again, we're getting a `sha` back in the response that is needed for the next step.

*Payload:*
```json
{
    "base_tree": "7fd1a60b01f91b314f59955a4e4d4e80d8edf11d",
    "owner": "[REPO OWNER]",
    "repo": "[REPO NAME]",
    "tree": [
        {
            "path": "our_filename_here.md",
            "mode": "100644",
            "type": "blob",
            "sha": "3a0f86fb8db8eea7ccbb9a95f325ddbedfb25e15"
        }
    ]
}
```

**POST Route:** `https://api.github.com/repos/[owner]/[repo]/git/trees`

*Response:*
```json
{
  "sha": "cd8274d15fa3ae2ab983129fb037999f264ba9a7",
  "url": "https://api.github.com/repos/preocts/gitclient/trees/cd8274d15fa3ae2ab983129fb037999f264ba9a7",
  "tree": [
    {
      "path": "our_filename_here.md",
      "mode": "100644",
      "type": "blob",
      "size": 132,
      "sha": "7c258a9869f33c1e1e1f74fbb32f07c86cb5a75b",
      "url": "https://api.github.com/repos/preocts/gitclient/git/blobs/7c258a9869f33c1e1e1f74fbb32f07c86cb5a75b"
    }
  ],
  "truncated": true
}
```

## Commit
---

Now that we've put a file on the stage, it is time to make a commit. Commits want to know what the parent branch is, what tree is being committed, the all-important commit message, and who is making the commit.

Here we use the tree `sha` from the last request, the branch `sha` we've been using, and add our GitHub account name with email to wrap it all up.  The response is verbose but has the now expected `sha` of our commit for the next step.

*Payload:*
```json
{
    "message": "Auto commit by automation!",
    "author": {
        "name": "[YOUR GITHUB NAME]",
        "email": "[YOUR GITHUB EMAIL]"
    },
    "parents": ["7fd1a60b01f91b314f59955a4e4d4e80d8edf11d"],
    "tree": "cd8274d15fa3ae2ab983129fb037999f264ba9a7"
}
```

**POST Route:** `https://api.github.com/repos/[owner]/[repo]/git/commits`

*Truncated Response:*
```json
{
  "sha": "7638417db6d59f3c431d3e1f261cc637155684cd",
  ...
}
```

## Updating our new branch reference
---

Up to this point, our new branch has been the same as the base branch we used to create it. Now that we have a new commit, or a new point in history, it is time to move the HEAD of our new branch forward to that commit.

The `sha` here is from our commit. The branch name is the new branch we created in the first step.

*Payload:*
```json
{
    "ref": "refs/heads/[NEW BRANCH NAME]",
    "sha": "7638417db6d59f3c431d3e1f261cc637155684cd"
}
```

**POST Route:** `https://api.github.com/repos/[owner]/[repo]/git/refs/heads/[NEW BRANCH NAME]`

## Pull request into main branch
---

With the reference updated and the HEAD of our new branch pointing at the commit containing our new file, it's time to make that pull request. The pull request need to know which branch is our HEAD and which is the base. It will create a pull from HEAD -> base. This step doesn't want any of the `sha` values we've been using, just the names of the branches.

In the response there will be an `number` returned. For the final step, adding labels to the pull request, we'll need that number.

*Payload:*
```json
{
    "owner": "[REPO OWNER]",
    "repo": "[REPO NAME]",
    "title": "Good title for automated PR",
    "body": "Everyone likes cat memes in the PR body, right?",
    "maintainer_can_modify": true,
    "head": "[NEW BRANCH NAME]",
    "base": "main"
}
```

**POST Route:** `https://api.github.com/repos/[owner]/[repo]/pulls`

*Truncated Response:*
```json
{
  "url": "https://api.github.com/repos/preocts/gitclient/pulls/42",
  ...
  "number": 42,
  "state": "open",
  "locked": true,
  "title": "Good title for automated PR",
  ...
}
```

## Add labels to pull request
---

The final step on the eight legged journey is to add a few labels to our pull request to make our reviewing team happy. To do this we need the `number` of the issue we'll be adding labels too. "Issue?" you may ask? Fun trivia fact: All pull requests in GitHub are issues, though not all issues are pull requests!

Labels are provided in an array of strings. The API will helpfully create any label not already in existance with this call.

*Payload:*
```json
{
  "labels": [
    "Review",
    "Weekly"
  ]
}
```

**POST Route:** `https://api.github.com/repos/[owner]/[repo]/issues/[ISSUE NUMBER]/labels`

With that, we've automated the entire manual process and can now fire off the template file with a single script run whenever needed.  An added bonus to this automation is that we don't need to keep a copy of the target repo on our local machine.

---

## API Documentation links

The entire process is fairly straight-forward to execute, once you've dug through enough of the GitHub documentation to know all the little steps. Finding the correct steps proved to be the tricky part of this task. GitHub has **a lot** of features.  Below is a list of the links I used for each of the steps above.  You'll find more details on the API route, response examples, and code examples.

1. [GitHub API Documentation - Get a Branch](https://docs.github.com/en/rest/reference/repos#get-a-branch)
1. [GitHub API Documentation - Create a reference](https://docs.github.com/en/rest/reference/git#create-a-reference)
1. [GitHub API Documentation - Create a blob](https://docs.github.com/en/rest/reference/git#create-a-blob)
1. [GitHub API Documentation - Create a tree](https://docs.github.com/en/rest/reference/git#create-a-tree)
1. [GitHub API Documentation - Create a commit](https://docs.github.com/en/rest/reference/git#create-a-commit)
1. [GitHub API Documentation - Update a reference](https://docs.github.com/en/rest/reference/git#update-a-reference)
1. [GitHub API Documentation - Create a pull request](https://docs.github.com/en/rest/reference/pulls#create-a-pull-request)
1. [GitHub API Documentation - Add labels to an issue](https://docs.github.com/en/rest/reference/issues#add-labels-to-an-issue)
