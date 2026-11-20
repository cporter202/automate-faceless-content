# Blotato skills for faceless video creators

Create your clip in ViralWave Studio, then use Blotato in Claude or Codex to handle scheduling and Instagram keyword replies. You can also run either skill on its own with an existing clip or Reel.

1. Connect a test social profile in Blotato on a plan with MCP access. Use a professional Instagram profile for the DM example.
2. Follow the [Claude setup guide](https://www.blotato.com/claude) or [Codex setup guide](https://www.blotato.com/codex). Ask your assistant to list your connected accounts and check that the test profile appears.
3. Open a skill and paste its example prompt. If your client supports local skills, you can also load the skill directory and provide the same inputs.

| Skill | What you supply | What you verify |
| --- | --- | --- |
| [Schedule a finished clip](#schedule-a-finished-clip) | A test account, a short video, and a future time with timezone | The right clip appears in the calendar at that time |
| [Set up an Instagram comment-to-DM](#set-up-instagram-comment-to-dm) | A professional Instagram test account, a test Reel, and a resource URL | A matching comment gets the intended private reply |

## From ViralWave Studio to Blotato

1. Follow the [ViralWave first-video guide](../../guides/getting-started/your-first-video.md) to make a short vertical video and export it as an MP4. Choose a resource URL you control and a distinct keyword, such as `CLIPGUIDE26`.
2. Use the scheduling prompt below with your exported clip. For this walkthrough, replace the sample caption with `Comment CLIPGUIDE26 and I'll DM you the faceless video guide.` Use the exact future time you approve and check that the clip is queued.
3. For an end-to-end test, let the scheduled clip publish on your test account. Open the published Reel and use the DM prompt below with that Reel, the same keyword, and your resource URL.
4. Review the inactive rule and approve activation. Comment with the keyword from a second account, verify the DM and link, then disable the rule after your test.

## Schedule a finished clip

```text
Use Blotato to schedule one finished clip on my connected Instagram test
account. Ask me for the account handle, my video file or accessible video
URL, and a future date and time with timezone. Use this caption:
"Behind the scenes of my faceless video workflow."

Show me the selected account, video, caption, and exact time with timezone.
Wait for me to confirm. Schedule for that exact future time. If Blotato
cannot use that time, stop. Check the submission status before reporting
the submission ID and whether it is scheduled.
```

Check the calendar for the correct clip, account, and exact time. Remove the post before it goes live if it was only a test.

[Open the full SKILL.md](blotato-schedule-video/SKILL.md) · [View raw skill file](https://raw.githubusercontent.com/cporter202/automate-faceless-content/blotato-partner-preview/skills/blotato/blotato-schedule-video/SKILL.md)

## Set up Instagram comment-to-DM

```text
Use Blotato to set up a comment-to-DM on my professional Instagram test
account. Ask me for my handle, the published test Reel, and the URL of a
resource I control. Use CLIPGUIDE26 as the keyword. Send this private
reply followed by my URL: "Thanks for asking! Here's the faceless video guide."

Target only the test Reel. If it cannot be selected, ask before using
an account-wide trigger. Show me the account, scope, keyword, and message.
After I confirm, create the automation inactive. Give me the automation ID
and wait for separate approval before activating it.
```

After approving activation, comment with the keyword from a second account and check for the private reply. Disable the rule after the test.

[Open the full SKILL.md](blotato-instagram-comment-to-dm/SKILL.md) · [View raw skill file](https://raw.githubusercontent.com/cporter202/automate-faceless-content/blotato-partner-preview/skills/blotato/blotato-instagram-comment-to-dm/SKILL.md)

[Back to the faceless video guide](../../README.md)
