# Creating a branch, adding a file, and making a pull request with Github API

In the endless search for inches of improvement, automation often rises to the challenge. This process involved a simple situation; throughout the week I would need to create a mark-down document, add it into a central repository, and make a pull request. The contents of the document are easy to template with just a few metadata fields that, programmatically, can be filled in automatically. Automating the git routine was the challenge to be overcome here.

So let us break the challenge down into the pieces that we need to accomplish and then look at each step in detail. While my code was done in Python and is linked at the end of this writeup, the steps below will focus more on the API steps. This means if you know how to send an HTTPS request in the language of your choice, you can use this writeup.

### Steps to accomplish the goal (duplicating the manual actions):

1. Create a new branch in the repo, using `main` as the base-branch
   - `git checkout -b summary04022021`
1. Copy my template file into the repo, renaming it
   - `cp ~/templates/daily.md summary04022021.md`
   - *An existing python would be used here to update the few pieces of metadata using a csv source file*
1. Add the file to the stage
   - `git add summary04022021.md`
1. Commit the change
   - `git commit -m "Week summary file"`
1. Push the changes to GitHub
   - `git push upstream HEAD`
1. Log into GitHub and create a pull request
   - *Button clicks, copy/paste a standard PR message, and submit*

In total, the process would take 10-15 minutes of my day. Perfect for a little automation!

---

Getting started, we need to connect and authenticate with GitHub. The best path to accomplish this with a personal OAuth token. You can create one in your GitHub's personal account settings `Developer settings` -> `Personal Access Tokens`. There are a wide selection of permissions to select from when creating a token. For this project the only permission we need this OAuth key to have is `public_repo`. Create a token and save it in your `.env` file, or preferred method of loading secrets. (hopefully not your committed code)

With the token secured, the next step is to define your headers. Simple enough for our application. We want to tell GitHub we're using their v3 API, who we are, and what our authorization is.

```json
{
    "Accept": "application.vnd.github.v3+json",
    "User-Agent": "[YOUR GITHUB NAME HERE]",
    "Authorization": "token [YOUR PERSONAL ACCESS TOKEN HERE]"
}
```

To send the two types of requests we'll need, POST and GET, to GitHub I just used Python's `https.client` library, which is a built-in. Again, any method will work here. You just need to send a POST or GET HTTPS request and have the ability to consume the JSON response as we'll need some information from each step to preform the next.

## API v3 routes and payload

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

To create the branch in GitHub we actually are creating a new reference point in the history of the repo. Each reference needs a starting point in the history which is the branch the new branch is created from. The API wants the first, our new branch, in the form of a branch name and the latter, the base branch, in the form of a SHA. So we have two steps to accomplish here.

**Getting the base branch SHA**

Thankfully getting a branch SHA is a straight-forward. We make a GET request to the correct endpoint and receive a JSON object back that has the `sha` within it.

*Route GET*
```
https://api.github.com/repos/[owner]/[repo]/branches/[branch_name]
```

This will return a chunk of data in JSON form. We are only interested in the `commit:sha` value as that's what we need to make a new branch in the next step.

*Truncated response*
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

**Creating a new branch**

With the sha of our base branch in hand, we can create the payload needed for creating a new branch and POST that to GitHub.

*Payload*
```json
{
    "ref": "refs/heads/[new_branch_name]",
    "sha": "7fd1a60b01f91b314f59955a4e4d4e80d8edf11d"
}
```

*Route POST*
```
https://api.github.com/repos/[owner]/[repo]/git/refs
```

You can see we used the SHA collected in the payload and included our own new branch name. This is creating a new reference *at the same point in the history* as our base branch.

## Making the file, create a blob

The next step in our manual process was to copy the template file into the repo's working directory. Through the API we'll do that in a two-step process of creating the blob, or binary large object, and then giving that object a name in the tree.  These two steps can be down in one, but I broke them out to keep things isolated.

Making a blob in a repo just requires what we have already and the actual file contents. If, like me, you are uploading a plain-text file then you can provide the contents in utf-8 encoding. If needed, you can also provide the content in base64 encoding.

*Payload*
```json
{
    "owner": "[REPO OWNER]",
    "repo": "[REPO NAME]",
    "content": "[FILE CONTENT HERE]",
    "encoding": "utf-8"
}
```

*Route POST*
```
https://api.github.com/repos/[owner]/[repo]/git/blobs
```

The response will contain a SHA for this blob, we need that for the next step.

*Response*
```json
{
  "url": "https://api.github.com/repos/preoct/gitclient/git/blobs/3a0f86fb8db8eea7ccbb9a95f325ddbedfb25e15",
  "sha": "3a0f86fb8db8eea7ccbb9a95f325ddbedfb25e15"
}
```

## Making a file, create a tree

Right now our blob just exists, without a home. This is the same as an untracked file in a working directory of a repo. GitHub knows the blob exists, but it isn't tracked in history. By creating a tree for this blob we will stage the blob and give it a file-path at the same time.

You'll notice we reuse the SHA from our base branch here as `base_branch`. That's because it's also the reference point of our new branch. They are at the same point in history right now, but that will change in two steps.

*Payload*
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

*Route POST*
```
https://api.github.com/repos/[owner]/[repo]/git/trees
```

*Response*
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

In the `tree` object you can see how we give our blob a filename. If we wanted to put that file into a directory we could use `daily/documents/our_filename_here.md` and the request will place the file in `./daily/documents` of the repo. The `mode` here tells GitHub our blob in this tree is just a file. The `sha` is from the response of our prior step.

Once again, we're getting a SHA back in the response that is needed for the next step.

## Commit

Now that we've put a file on the stage, it's time to make a commit. Commits want to know what the parent branch is, what tree is being committed, the all-important commit message, and who is making the commit.

*Payload*
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

*Route POST*
```
https://api.github.com/repos/[owner]/[repo]/git/commits
```

*Truncated Response*
```json
{
  "sha": "7638417db6d59f3c431d3e1f261cc637155684cd",
  ...
}
```

Here we use the tree `sha` from the last request, the branch `sha` we've been using, and add our GitHub account name with email to wrap it all up.  The response is verbose but has the now expected `sha` of our commit for the next step.

## Updating our new branch reference

To this point our new branch has been the same as the base branch we used to create it. Now that we have a new commit, or a new point in history, it's time to move the HEAD of our new branch forward to that commit.

This should look familiar, it's very similar to making a branch.

*Payload*
```json
{
    "ref": "refs/heads/[NEW BRANCH NAME]",
    "sha": "7638417db6d59f3c431d3e1f261cc637155684cd"
}
```

*Route POST*
```
https://api.github.com/repos/[owner]/[repo]/git/refs/heads/[NEW BRANCH NAME]
```

The `sha` here is from our commit. The branch name is the new branch we created in the first step.  With the reference updated and the HEAD of our new branch pointing at the commit containing our new file, it's time to make that pull request.

## Pull request into main branch

The pull request need to know which branch is our HEAD and which is the base. It will create a pull from HEAD -> base.  This is made easier since this endpoint doesn't want any `sha` values, just the names of the branches.

*Payload*
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

*Route POST*
```
https://api.github.com/repos/[owner]/[repo]/pulls
```

That's it. The pull request is in for review!

---

## API Documentation links
...
