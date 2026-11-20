---
name: blotato-instagram-comment-to-dm
description: Create and test a Blotato keyword-triggered private reply to an Instagram Reel comment.
---

# Reply to an Instagram Reel comment by DM

## Copy into Claude or Codex

```text
Use Blotato to set up a comment-to-DM on my professional Instagram test
account. Ask me for my handle, the published test Reel, and the URL of a
resource I control. Use CLIPGUIDE26 as the keyword. Send this private
reply followed by my URL: "Thanks for asking! Here's the faceless video guide."

Show me the account, trigger scope, keyword, and complete message.
After I confirm, create the automation inactive. Give me the automation ID
and wait for separate approval before activating it.
```

## Run and verify

1. Resolve the test account and look for existing rules that could match the same keyword. Blotato matches keywords as case-insensitive substrings.
2. Target the test Reel if Blotato can select it. If the Reel cannot be selected, ask before using the account-wide comment trigger on the dedicated test account.
3. Show the draft settings and wait for approval. Use `blotato_create_automation` to create the inactive rule. Confirm its status and return its ID. Activate only after the user approves that step.
4. From a second account, comment with the keyword and verify the private reply contains the right resource link. Check Message Requests if needed. Try an unrelated comment to confirm it receives no reply.
5. Disable the test rule and verify it is inactive.

[Blotato DM walkthrough](https://www.blotato.com/blog/how-to-sell-dm-automation) · [Blotato MCP guide](https://www.blotato.com/codex)
