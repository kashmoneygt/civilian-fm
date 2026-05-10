We are experimenting with the idea of steering a base model away from its mean response. Steering away from the mean is what creates value.

An example is: You ask Gemini or ChatGPT how to pay 0 taxes, and it tells you that you should simply pay your taxes. It doesn't find unique, creative examples on how to reduce your tax burden.

This is based on a few core principles:
1. A trained base model represents the internet, aka the mean
2. A post-trained model is a harnessed version of a particular base model, intentionally steered away from the mean via post training
3. A post-trained model has to outperform the base model for a post-trained model to make sense (ex: ChatGPT UI is optimized for chat completion, but gpt4o API call is not)

Previously in AI, we saw two ways of steering the base model away from the mean:
1. Sequential workflows (prompt chaining) like n8n
2. Finetuning (changing weights in specific layers of the neural net while freezing others)

Now, we're seeing agentic LLMs, which represent post-trained versions of the base LLM. They are simply implemented as a Python container running on a CPU machine (not GPU or TPU). The main idea is that you give the agent a personality and some skills. The end goal is to steer away the base model from the mean via tone, personality, objective, etc. (steering / harness engineering).

Here's an example of Google's ADK (agent development kit):

```py
from google.adk import Agent
from google.adk.tools import google_search

agent = Agent(
    name="researcher",
    model="gemini-flash-latest",
    instruction="You help users research topics thoroughly.",
    tools=[google_search],
)
```

We can think of Claude Code, OpenClaw, OpenCode and Codex all as python containers with markdown files - there is deterministic Python logic that steers the base language model so they can do a subset of tasks better than the mean (think the "grep" skill).

However, we should address a fundamental limit of language models - the limited context window. The more "important context" markdown files we have, the more the model regresses to the mean.

There's a sweet spot that is more art than science - if you post train something, that might make it hallucinate more. So the dilemma is - if you don't provide enough context in whatever fashion (skills.md and personality.md), it will stay too close to the mean. If you provide TOO much context, it will regress back to the mean. This entire thing is non-deterministic.

We want to work on a product for our "Palantir for civilians" goal where we can think about this into 3 steps:

1. Deterministic step where we get information from the public web via a crawler.
    - This should be able to pull from sources like YouTube (C-SPAN videos), LinkedIn, etc.
2. Create agentic containers
    - An agentic container that uses my crawler's outputs as a skill
    - Produces a graph using karpthy's LLM wiki (markdown file / skill / harness)
    - Open question: How to store agent personalities? free github private repo?
3. Define input/output of agentic container
    - We see what the sweet spot is in terms of too little or too much context
    - Each problem space requires different context window lengths

A few use cases we came up with are:

- I want to apply for a permit (without steering, it will go to a general construction code)
- I want to get a liquor store in Cherokee County (sometimes this information can only be found by calling the county and getting information from the lady)
- I want to reduce my tax burden

For the last use case, imagine that our crawler can go to each car manufacturer's website and extract the Section 179 Deduction. For example, Tesla's CyberTruck purchase page says:
"Qualifying businesses may claim a deduction of up to $31,300 when purchasing a new Tesla vehicle with a gross vehicle weight rating (GVWR) of at least 6,000 pounds. To qualify for the tax deduction, vehicles must be operated for legitimate business use >50% the time."

The whole goal is that we should be able to have access to information that rich people have. If we can save 15K in taxes every year for 10 years, that's 150K and with inflation, 200K. If we invest that into the S&P, my dad can end up with an extra $1M dollars, which can cover down payments for kids, retirement done, new store location, etc.

Please spell out how we can create a dashboard that covers all our use cases - crawling from YouTube URLs and search queries, organizing this content into LLM wiki, creating agentic containers, and comparing outputs (default system prompt, system prompt with lots of context, and agentic container). I prefer to use Python where possible, and I want to iterate quickly.
