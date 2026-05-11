---
source: web
fetched_at: '2026-05-11T19:58:20Z'
url: https://www.softwarecraftsperson.com/posts/learn-large-language-models-karpathy-resources/
title: 'Start Here to Learn Large Language Models: Best Andrej Karpathy Resources
  | Software Craftsperson'
domain: softwarecraftsperson.com
---

Large Language models have evolved over the last decade but there is still time to learn and understand them. Let me share some resources I found useful.

## Andrej Karpathy - Intro to Large Language Models #

An excellent introduction video recorded by Andrej Karpathy, one of the co-founders of the world’s most notorious AI company, OpenAI, which he left in 2024 to found Eureka Labs.

[1hr Talk] Intro to Large Language Models

Talks about mechanistic interpretability. Explains how nobody can really explain how the parameters influence the model’s predictive behaviour but can iteratively tweak and optimise the params and measure the prediction accuracy.

Explains the different stages of creating a large language model through:

### Stage 1 - Pretraining #

- obtaining large data - 10TB+ of text, if internet is your source, then probably low quality data

- Get a large cluster of GPUs, in his example he states about 6000 GPUs (now you know why they are so expensive)

- Compress the text through the neural network, burn your millions of dollars for using the cluster and wait for a couple of days

- Obtain the base model !

Simples!

### Stage 2 - Finetuning #

- Write labeling instructions - what type of response is good, what’s not, etc

- Hire large number of people to optimise the model. This involves, collecting 100,000+ high quality Q&A responses to tune the base model through feedback. Basically reinforcement learning through human feedback . This a lot quicker and cheaper than buying GPUs and burning money.

- This training results in the assistant model

- Researchers then continue running evaluations and once satisfied, deploys the model, monitors for misbehaviours

- Repeat from step 1

#### Labeller workflow optimisation #

Andrej specifically explained that sometimes instead of answering a question, it is easier for a labeller to choose the best among a couple of answers from the model. This comparison and scoring is another way of fine-tuning.

### Chatbot leaderboard #

Andrej gives a shoutout to Chatbot Arena !

### LLM Scaling Law #

The performance or intelligence of an LLM comes down to two factors:

- N , the number of parameters in the neural network

- D , the amount of text used to train the model

There is cost of the training which is not a factor that’s included at all!

You can read more about Training Compute - optimal large language models .

### Demo #

Andrei’s demo explanation is fantastic - explains how the model actually uses tools behind the scenes to get the job done, like a calculator, a graph library, etc. The job being what the user asks it to do.

## Stanford Machine Learning | Building a large language model #

Stanford University | Machine Learning | Building a Large Language Model (LLM)

## Andrei Karpathy - Neural Networks - Zero to Hero #

This is a fantastic playlist of Andrej taking viewers through building a large language model from scratch.

The YouTube Playlist of Andrej’s Videos

## Andrej Karpathy - Reproduce GPT-2 #

This video to create GPT-2 with 124M parameters is part of the playlist shared earlier, but worth mentioning separately as it is an excellent engineering lesson.

## Andrej Karpathy - Deep Dive into LLMs like ChatGPT #

Similar to the earlier video but it is 4 long hours! So your afternoon sorted.

Andrej Karpathy - Deep Dive into LLMs like ChatGPT

## Andrej Karpathy - How I use LLMs #

Andrej Karpathy on How he uses LLMs

## Stumbled upon this one #

A Substack for those learning more about the Buzz of AI
