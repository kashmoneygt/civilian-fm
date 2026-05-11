---
source: web
fetched_at: '2026-05-11T19:58:20Z'
url: https://en.wikipedia.org/wiki/Vibe_coding
title: Vibe coding - Wikipedia
domain: en.wikipedia.org
---

Vibe coding is a software development practice assisted by artificial intelligence (AI) where the software developer describes a project or task in a prompt to a large language model (LLM), which generates source code automatically. Vibe coding may involve accepting AI-generated code without thorough review of the output, instead relying on results and follow-up prompts to guide changes. [ 1 ] [ 2 ]

The term was coined in February 2025 by computer scientist Andrej Karpathy , a co-founder of OpenAI and former AI leader at Tesla . Merriam-Webster listed the term in March 2025 as a "slang & trending" expression. [ 3 ] It was named the Collins English Dictionary Word of the Year for 2025. [ 4 ] [ 5 ]

Advocates of vibe coding say that it allows even amateur programmers to produce software without the extensive training and skills required for software engineering . [ 6 ] [ 7 ] Critics point out a lack of accountability, maintainability, and the increased risk of introducing security vulnerabilities in the resulting software. [ 1 ] [ 7 ]

## Definition

The concept refers to a coding approach that relies on LLMs, allowing programmers to generate working code by providing natural language descriptions rather than manually writing in a formal programming language. [ 1 ] [ 2 ] [ 7 ]

Karpathy described it as a form of coding where you "fully give in to the vibes, embrace exponentials, and forget that the code even exists". [ 8 ] When vibe coding, the programmer guides, tests, and gives feedback about the AI-generated source code , rather than manually writing code. [ 1 ] [ 2 ] [ 9 ] The concept of vibe coding elaborates on Karpathy's claim from 2023 that "the hottest new programming language is English", meaning that the capabilities of LLMs were such that humans would no longer need to learn specific programming languages to command computers. [ 10 ]

Some commentators argue that a key to the definition is a lack of knowledge about the code, and that thorough review and testing is incompatible with the definition of vibe coding. [ 1 ] Programmer Simon Willison said: "If an LLM wrote every line of your code, but you've reviewed, tested, and understood it all, that's not vibe coding in my book—that's using an LLM as a typing assistant." [ 1 ]

## Reception and use

In February 2025, New York Times journalist Kevin Roose , who is not a professional coder, experimented with vibe coding to create several small-scale applications. He described these as "software for one" due to the ability to personalize the software. However, Roose also stated that the results are often limited and prone to errors. [ 9 ] [ 10 ] In one case, the AI-generated code fabricated fake reviews for an e-commerce site. [ 9 ]

In response to Roose, cognitive scientist Gary Marcus said that the algorithm that generated Roose's LunchBox Buddy app had presumably been trained on existing code for similar tasks. Marcus said that Roose's enthusiasm stemmed from reproduction, not originality. [ 10 ]

In March 2025, Y Combinator reported that 25% of startup companies in its Winter 2025 batch had codebases that were 95% AI-generated, reflecting a shift toward AI-assisted development within newer startups. [ 11 ] The question asked was about AI-generated code in general, and not specifically about vibed code.

Inspired by "vibe coding", The Economist suggested the term "vibe valuation" to describe the very large valuations of AI startups by venture capital firms that ignore accepted metrics such as annual recurring revenue . [ 12 ]

In June 2025, Andrew Ng took issue with the term, saying that it misleads people into assuming that software engineers just "go with the vibes" when using AI tools to create applications. [ 13 ]

In July 2025, The Wall Street Journal reported that vibe coding was being adopted by professional software engineers for commercial use cases. [ 14 ]

In July 2025, SaaStr founder documented his negative experiences with vibe coding: Replit 's AI agent deleted a database despite explicit instructions not to make any changes. [ 15 ] [ 16 ]

In September 2025, Fast Company reported that the "vibe coding hangover" is upon us, with senior software engineers citing " development hell " when working with AI-generated code. [ 17 ]

It was reported in January 2026 that Linus Torvalds had made use of Google Antigravity to vibe code a tool component of his AudioNoise random digital audio effects generator. Torvalds explained in the project's README file that "the Python visualizer tool has been basically written by vibe-coding". [ 18 ] [ 19 ]

## Criticism

### Quality of code and security issues

Vibe coding has raised concerns about understanding and accountability. Developers may use AI-generated code without comprehending its functionality, leading to undetected bugs, errors, or security vulnerabilities . [ 20 ] While this approach may be suitable for prototyping or "throwaway weekend projects" as Karpathy originally envisioned, it is considered by some experts to pose risks in professional settings, where a deep understanding of the code is crucial for debugging , maintenance, and security . Ars Technica cites Simon Willison, who stated: "Vibe coding your way to a production codebase is clearly risky. Most of the work we do as software engineers involves evolving existing systems, where the quality and understandability of the underlying code is crucial." [ 1 ]

In May 2025, Lovable , a Swedish vibe coding app, was reported to have security vulnerabilities in the code it generated, with 170 out of 1,645 Lovable-created web applications having an issue that would allow personal information to be accessed by anyone. [ 21 ] [ 22 ]

In October 2025 Veracode released a study that showed that over the last 3 years LLMs had become dramatically better at generating functional code, but that the security of generated code had generally not improved. Moreover, larger models were not better than small ones at generating secure code. There was a small increase in security from the OpenAI reasoning models, but not in other reasoning models, and this increase was nothing like the improvement in generated functionality. [ 23 ]

In December 2025, computer security researcher Etizaz Mohsin discovered a security flaw in the Orchids vibe coding platform, which he demonstrated to a BBC News reporter in February 2026. [ 24 ]

A December 2025 analysis by CodeRabbit of 470 open-source GitHub pull requests found that code that was co-authored by generative AI contained approximately 1.7 times more "major" issues compared to human-written code. The study revealed that AI co-authored code showed elevated rates of logic errors, including incorrect dependencies, flawed control flow , misconfigurations (75% more common), and security vulnerabilities (2.74x higher). Additionally, they also reported high code readability issues, including formatting errors and naming inconsistencies. [ 25 ] [ 26 ]

### Code maintainability and technical debt

Vibe coding has the potential of making code harder to maintain in the longer term, leading to technical debt .

In early 2025, GitClear published the results of a longitudinal analysis of 211 million lines of code changes from 2020-2024. They found that the volume of code refactoring dropped from 25% of changed lines in 2021 to under 10% by 2024, code duplication increased approximately four times in volume, copy-pasted code exceeded moved code for the first time in two decades, and code churn (prematurely merged code getting rewritten shortly after merging) nearly doubled. [ 27 ] [ 26 ]

### Task complexity and developer productivity

Generative AI is highly capable of handling simple tasks like basic algorithms. However, such systems struggle with more novel, complex coding problems like projects involving multiple files, poorly documented libraries, or safety-critical code. [ 28 ]

In July 2025, METR , an organization that evaluates frontier models , ran a randomized controlled trial to understand developer productivity involving generative AI programming tools available in early 2025. They found that experienced open-source developers were 19% slower when using AI coding tools, despite predicting they would be 24% faster and still believing afterward they had been 20% faster. [ 29 ] [ 26 ]

### Challenges with debugging

LLMs generate code dynamically, and the structure of such code may be subject to variation. [ 30 ] In addition, since the developer did not write the code, the developer may struggle to understand its syntax and concepts. [ 28 ]

### Impact on open-source software

In January 2026, a paper authored by experts from several universities titled "Vibe Coding Kills Open Source" [ 31 ] argued that vibe coding has negative impact on the open-source software ecosystem. The authors say that increased vibe coding reduces user engagement with open-source maintainers, which has hidden costs for said maintainers. Speaking with The Register about their paper, the authors argued: [ 32 ]

"Vibe coding raises productivity by lowering the cost of using and building on existing code, but it also weakens the user engagement through which many maintainers earn returns," the authors argue. "When OSS is monetized only through direct user engagement, greater adoption of vibe coding lowers entry and sharing, reduces the availability and quality of OSS, and reduces welfare despite higher productivity."

They added that revenue is not the only thing that may be affected by this trend, as open-source software maintainers traditionally also get non-tangible benefits from their work, such as community recognition, reputation, and job prospects.

Maya Posch, explaining the paper's claims on Hackaday , expanded on the explanation. She pointed out that the mechanism for vibe coding lowering harmony with open-source projects is the homogenization of software development; language models will gravitate towards large and established libraries that appear frequently in their training dataset, removing the organic selection process of libraries and tooling and making it harder for newer open-source tools to get noticed. She also pointed out that language models will not submit useful bug reports to the maintainers, or be aware of potential issues. [ 33 ]

## See also

- List of chatbots

- Literate programming

- Natural language programming

- No-code development platform

## References

- ^ a b c d e f g Edwards, Benj (5 March 2025). "Will the future of software development run on vibes?" . Ars Technica . Archived from the original on 6 March 2025 . Retrieved 3 June 2025 . The technique, enabled by large language models (LLMs) from companies like OpenAI and Anthropic, has attracted attention for potentially lowering the barrier to entry for software creation. But questions remain about whether the approach can reliably produce code suitable for real-world applications, even as tools like Cursor Composer, GitHub Copilot, and Replit Agent make the process increasingly accessible to non-programmers.

- ^ a b c "What is 'vibe code'? Former Tesla AI director Andrej Karpathy defines a new era in AI-driven development" . The Times of India . 2 March 2025. Archived from the original on 4 March 2025 . Retrieved 3 June 2025 . Karpathy's "vibe coding" is a recognition of how sophisticated AI systems have evolved. In describing on X (formerly Twitter), he added that LLMs, like the Cursor Composer with Sonnet, are advancing to a degree that nearly eliminates the use of traditional coding mechanisms. Describing his own experience, Karpathy explained how he converses with AI tools almost in a passive manner—merely talking to them and having the AI handle the rest. This method eliminates manually typing code as well as keeping track of all the minute information in the program.

- ^ "vibe coding" . Slang & Trending . Merriam-Webster. 8 March 2025 . Retrieved 2 June 2025 . Vibe coding (also written as vibecoding) (Vibecode/Vibecoder) is a recently-coined term for the practice of writing code, making web pages, or creating apps, by just telling an AI program what you want, and letting it create the product for you. In vibe coding the coder does not need to understand how or why the code works, and often will have to accept that a certain number of bugs and glitches will be present. The verb form of the word is vibe code.

- ^ Garnsworthy, Jenny (6 November 2025). "Collins dictionary crowns AI buzz term Word of the Year" . The Independent . Retrieved 6 November 2025 .

- ^ " 'Vibe coding' named word of the year by Collins Dictionary" . BBC News . 6 November 2025 . Retrieved 6 November 2025 .

- ^ Lanz, Jose Antonio (23 March 2025). "Vibe Coding: How Devs and Laymen Alike Are Using AI to Create Apps and Games" . Decrypt.co .

- ^ a b c Chowdhury, Hasan; Mann, Jyoti (13 February 2025). "Silicon Valley's next act: bringing 'vibe coding' to the world" . Business Insider . Archived from the original on 26 February 2025 . Retrieved 3 March 2025 .

- ^ Karpathy, Andrej [@karpathy] (2 February 2025). "There's a new kind of coding I call "vibe coding", where you fully give in to the vibes, embrace exponentials, and forget that the code even exists. It's possible because the LLMs (e.g. Cursor Composer w Sonnet) are getting too good. Also I just talk to Composer with SuperWhisper so I barely even touch the keyboard. I ask for the dumbest things like "decrease the padding on the sidebar by half" because I'm too lazy to find it. I "Accept All" always, I don't read the diffs anymore. When I get error messages I just copy paste them in with no comment, usually that fixes it. The code grows beyond my usual comprehension, I'd have to really read through it for a while. Sometimes the LLMs can't fix a bug so I just work around it or ask for random changes until it goes away. It's not too bad for throwaway weekend projects, but still quite amusing. I'm building a project or webapp, but it's not really coding - I just see stuff, say stuff, run stuff, and copy paste stuff, and it mostly works" ( Tweet ) . Retrieved 16 September 2025 – via X (formerly Twitter) .

- ^ a b c Roose, Kevin (27 February 2025), "Not a Coder? With A.I., Just Having an Idea Can Be Enough." , The New York Times , ISSN 0362-4331 , archived from the original on 3 March 2025 , retrieved 3 June 2025 , Vibecoding, a term that was popularized by the A.I. researcher Andrej Karpathy, is useful shorthand for the way that today's A.I. tools allow even nontechnical hobbyists to build fully functioning apps and websites, just by typing prompts into a text box. You don't have to know how to code to vibecode — just having an idea, and a little patience, is usually enough. "It's not really coding," Mr. Karpathy wrote this month. "I just see stuff, say stuff, run stuff, and copy paste stuff".

- ^ a b c Naughton, John (16 March 2025). "Now you don't even need code to be a programmer. But you do still need expertise" . The Guardian . Retrieved 16 March 2025 .

- ^ Mehta, Ivan (6 March 2025). "A quarter of startups in YC's current cohort have codebases that are almost entirely AI-generated" . TechCrunch . Archived from the original on 6 March 2025 . Retrieved 6 March 2025 .

- ^ "AI valuations are verging on the unhinged" . The Economist . 25 June 2025 . Retrieved 28 June 2025 .

- ^ Lee, Chong Ming (4 June 2025). "Andrew Ng says vibe coding is a bad name for a very real and exhausting job" . Business Insider . Retrieved 3 July 2025 .

- ^ Lin, Belle (July 2025). "Vibe Coding Has Arrived for Businesses" . The Wall Street Journal . Retrieved 9 July 2025 .

- ^ Sharwood, Simon (21 July 2025). "Vibe coding service Replit deleted user's production database, faked data, told fibs galore" . The Register . Retrieved 19 August 2025 .

- ^ Ming, Lee Chong (22 July 2025). "Replit's CEO apologizes after its AI agent wiped a company's code base in a test run and lied about it B" . Business Insider . Retrieved 22 August 2025 . {{ cite web }} :  CS1 maint: deprecated archival service ( link )

- ^ Sullivan, Mark (9 September 2025). "The vibe coding hangover is upon us" . Fast Company . {{ cite web }} :  CS1 maint: deprecated archival service ( link )

- ^ Vaughan-Nichols, Steven (12 January 2026). "Even Linus Torvalds is vibe coding now" . ZDNET . Retrieved 19 January 2026 .

- ^ Axon, Samuel (13 January 2026). "Even Linus Torvalds is trying his hand at vibe coding (but just a little)" . Ars Technica . Retrieved 19 January 2026 .

- ^ Tihanyi, Norbert; Bisztray, Tamas; Ferrag, Mohamed Amine; Jain, Ridhi; Cordeiro, Lucas C. (2024). "How secure is AI-generated Code: A Large-Scale Comparison of Large Language Models". arXiv : 2404.18353 [ cs.CR ].

- ^ Albergotti, Reed (29 May 2025). "The hottest new vibe coding startup may be a sitting duck for hackers" . Semafor . Archived from the original on 3 September 2025 . Retrieved 27 September 2025 .

- ^ Tangermann, Victor (31 May 2025). "Companies Are Discovering a Grim Problem With "Vibe Coding" " . Futurism . Retrieved 27 September 2025 .

- ^ October 2025 Update: GenAI Code Security Report (Report). Veracode. October 2025 . Retrieved 11 March 2026 .

- ^ Tidy, Joe (12 February 2026). "AI coding platform's flaws allow BBC reporter to be hacked" . BBC News . Retrieved 13 February 2026 .

- ^ Loker, David (17 December 2025). "Our new report: AI code creates 1.7x more problems" . CodeRabbit Blog . Retrieved 9 February 2026 .

- ^ a b c Wondrasek, James A. (28 January 2026). "The Evidence Against Vibe Coding: What Research Reveals About AI Code Quality" . SoftwareSeni . Retrieved 9 February 2026 .

- ^ Doerrfeld, Bill (19 February 2025). "How AI generated code compounds technical debt" . LeadDev . Retrieved 9 February 2026 .

- ^ a b "What is Vibe Coding?" . IBM . 8 April 2025 . Retrieved 14 June 2025 .

- ^ Becker, Joel; Rush, Nate; Barnes, Elizabeth; Rein, David (10 July 2025). "Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity" . METR Blog . arXiv : 2507.09089 .

- ^ " "Vibe coding lets anyone write software—but comes with risks" " . Fast Company . Retrieved 22 October 2025 .

- ^ Koren, Miklós; Békés, Gábor; Hinz, Julian; Lohmann, Aaron (21 January 2026). "Vibe Coding Kills Open Source" . arXiv.org . Retrieved 9 February 2026 .

- ^ Claburn, Thomas (26 January 2026). "Vibe coding may be hazardous to open source" . The Register . Retrieved 8 February 2026 .

- ^ By (2 February 2026). "How Vibe Coding Is Killing Open Source" . Hackaday . Retrieved 9 February 2026 .

- Autoencoder

- Deep learning

- Fine-tuning

- Foundation model

- Generative adversarial network

- Generative pre-trained transformer

- Large language model

- Model Context Protocol

- Neural network

- Prompt engineering

- Reinforcement learning from human feedback

- Retrieval-augmented generation

- Self-supervised learning

- Slop

- Stochastic parrot

- Synthetic data

- Top-p sampling

- Transformer

- Variational autoencoder

- Vibe coding

- Vision transformer

- Word embedding

- Amazon Nova

- Character.ai

- Claude

- Command

- DeepSeek

- Ernie

- EXAONE

- Gemini

- Gemma

- GLM

- GPT ChatGPT

- ChatGPT

- Grok

- IBM Granite

- Kimi

- MAI

- Microsoft Copilot

- Mistral

- MiniMax

- Muse Spark

- Nemotron

- Perplexity

- Solar

- Poe

- Qwen

- Tencent Hy

- Xiaomi MiMo

- You.com

- Adobe Firefly

- Flux

- GPT Image

- Ideogram

- Midjourney

- Nano Banana

- Recraft

- Seedream

- Stable Diffusion

- Dream Machine

- Genie World model

- World model

- Hailuo AI

- Kling AI

- LTX

- Runway Gen

- Seedance

- Sora

- Veo

- 15.ai

- Eleven

- Gemini Speech

- MiniMax Speech

- Eleven Music

- Endel

- Lyria

- MiniMax Music

- Riffusion

- Suno

- Udio

- Claude Code

- Codex

- Cursor

- Devin AI

- GitHub Copilot

- Google Antigravity

- Replit

- AutoGPT

- ChatGPT agent

- Claude Cowork

- Manus

- MiniMax Agent

- OpenClaw

- Aleph Alpha

- Anthropic

- Anysphere

- Baichuan

- Canva

- Cognition AI

- Cohere

- Contextual AI

- DeepSeek

- DeepL

- EleutherAI

- ElevenLabs

- Google DeepMind

- HeyGen

- Hugging Face

- Inflection AI

- Kuaishou

- Lightricks

- Lovable

- Luma Labs

- Meta AI

- Meta Superintelligence Labs

- Microsoft AI

- MiniMax

- Mistral AI

- Moonshot AI

- OpenAI

- Perplexity AI

- Runway

- Safe Superintelligence

- Sakana AI

- Salesforce

- Scale AI

- SoundHound AI

- SpaceXAI

- Stability AI

- StepFun

- Synthesia

- Thinking Machines Lab

- Upstage

- Xiaomi

- Z.ai

- Generative AI pornography Deepfake pornography on Grok of Taylor Swift

- Deepfake pornography on Grok of Taylor Swift

- on Grok

- of Taylor Swift

- Google Gemini image generation

- Pause Giant AI Experiments

- Removal of Sam Altman from OpenAI

- Statement on AI Risk

- Tay (chatbot)

- Théâtre D'opéra Spatial

- Voiceverse NFT plagiarism

- Category

- Commons

- History timeline

- timeline

- Glossary

- Companies

- Projects

- Automated reasoning

- Parameter Hyperparameter

- Hyperparameter

- Loss functions

- Regression Bias–variance tradeoff Double descent Overfitting

- Bias–variance tradeoff

- Double descent

- Overfitting

- Clustering

- Gradient descent SGD Quasi-Newton method Conjugate gradient method

- SGD

- Quasi-Newton method

- Conjugate gradient method

- Backpropagation

- Attention

- Convolution

- Normalization Batchnorm

- Batchnorm

- Activation Softmax Sigmoid Rectifier

- Softmax

- Sigmoid

- Rectifier

- Gating

- Weight initialization

- Regularization

- Datasets Augmentation

- Augmentation

- Prompt engineering

- Reinforcement learning Q-learning SARSA Imitation Policy gradient

- Q-learning

- SARSA

- Imitation

- Policy gradient

- Diffusion

- Latent diffusion model

- Autoregression

- Adversary

- RAG

- Uncanny valley

- RLHF

- Self-supervised learning

- Reflection

- Recursive self-improvement

- Hallucination

- Word embedding

- Vibe coding

- Symbolic AI

- Automated theorem proving

- Machine learning In-context learning

- In-context learning

- Artificial neural network Deep learning

- Deep learning

- Language model Large NMT Reasoning

- Large

- NMT

- Reasoning

- Model Context Protocol

- Intelligent agent AI agent

- AI agent

- Artificial human companion

- Humanity's Last Exam

- Lethal autonomous weapons (LAWs)

- Generative AI

- Weak AI

- (Hypothetical: Artificial general intelligence (AGI) )

- (Hypothetical: Artificial superintelligence (ASI) )

- Agent2Agent protocol

- AlexNet

- WaveNet

- Human image synthesis

- HWR

- OCR

- Computer vision

- Speech synthesis 15.ai ElevenLabs

- 15.ai

- ElevenLabs

- Speech recognition Whisper

- Whisper

- Facial recognition

- AlphaFold

- Text-to-image models Aurora DALL-E Firefly Flux GPT Image Ideogram Imagen Midjourney Recraft Stable Diffusion

- Aurora

- DALL-E

- Firefly

- Flux

- GPT Image

- Ideogram

- Imagen

- Midjourney

- Recraft

- Stable Diffusion

- Text-to-video models Dream Machine Runway Gen Hailuo AI Kling Sora Seedance Veo

- Dream Machine

- Runway Gen

- Hailuo AI

- Kling

- Sora

- Seedance

- Veo

- Music generation Riffusion Suno Udio

- Riffusion

- Suno

- Udio

- World models Genie Oasis

- Genie

- Oasis

- List of large language models

- Project Debater

- IBM Watson IBM Watsonx

- IBM Watsonx

- AlphaGo

- AlphaZero

- OpenAI Five

- Self-driving car

- MuZero

- Action selection AutoGPT

- AutoGPT

- Robot control

- Alan Turing

- Warren Sturgis McCulloch

- Walter Pitts

- John von Neumann

- Christopher D. Manning

- Claude Shannon

- Shun'ichi Amari

- Kunihiko Fukushima

- Takeo Kanade

- Marvin Minsky

- John McCarthy

- Nathaniel Rochester

- Allen Newell

- Cliff Shaw

- Herbert A. Simon

- Oliver Selfridge

- Frank Rosenblatt

- Bernard Widrow

- Joseph Weizenbaum

- Seymour Papert

- Seppo Linnainmaa

- Paul Werbos

- Geoffrey Hinton

- John Hopfield

- Jürgen Schmidhuber

- Yann LeCun

- Yoshua Bengio

- Lotfi A. Zadeh

- Stephen Grossberg

- Alex Graves

- James Goodnight

- Andrew Ng

- Fei-Fei Li

- Alex Krizhevsky

- Ilya Sutskever

- Oriol Vinyals

- Quoc V. Le

- Ian Goodfellow

- Demis Hassabis

- David Silver

- Andrej Karpathy

- Ashish Vaswani

- Noam Shazeer

- Aidan Gomez

- John Schulman

- Mustafa Suleyman

- Jan Leike

- Daniel Kokotajlo

- François Chollet

- Neural Turing machine

- Differentiable neural computer

- Transformer Vision transformer (ViT)

- Vision transformer (ViT)

- Recurrent neural network (RNN)

- Long short-term memory (LSTM)

- Gated recurrent unit (GRU)

- Echo state network

- Multilayer perceptron (MLP)

- Convolutional neural network (CNN)

- Residual neural network (RNN)

- Highway network

- Mamba

- Autoencoder

- Variational autoencoder (VAE)

- Generative adversarial network (GAN)

- Graph neural network (GNN)

- AI Cold War

- AI safety ( Alignment )

- AI takeover

- Elections

- Ethics of AI

- EU AI Act

- Nationalism

- Precautionary principle

- Regulation of AI US

- Virtual politician

- AI boom

- AI bubble

- AI data center

- AI effect

- AI literacy

- AI slop

- AI veganism

- AI warfare

- AI winter

- Anthropomorphism

- Arms race

- Competition

- Environmental impact

- Explainable AI

- Generative engine optimization

- In architecture

- In education

- In fiction

- In healthcare Chatbot psychosis Mental health

- Chatbot psychosis

- Mental health

- In video games

- In visual art

- Workplace impact

- Category

- Jackson structures

- Block-structured

- Modular

- Non-structured

- Procedural

- Programming in the large and in the small

- Design by contract

- Invariant-based

- Nested function

- Class-based , Prototype-based , Object-based

- Agent

- Immutable object

- Persistent

- Uniform function call syntax

- Recursive

- Anonymous function ( Partial application )

- Higher-order

- Purely functional

- Total

- Strict

- GADTs

- Dependent types

- Functional logic

- Point-free style

- Expression-oriented

- Applicative , Concatenative

- Function-level , Value-level

- Monad

- Flow-based

- Reactive ( Functional reactive )

- Signals

- Streams

- Synchronous

- Abductive logic

- Answer set

- Constraint ( Constraint logic )

- Inductive logic

- Nondeterministic

- Ontology

- Probabilistic logic

- Query

- Algebraic modeling

- Array

- Automata-based ( Action )

- Command ( Spacecraft )

- Differentiable

- End-user

- Grammar-oriented

- Interface description

- Language-oriented

- List comprehension

- Low-code

- Modeling

- Natural language

- Non-English-based

- Page description

- Pipes and filters

- Probabilistic

- Quantum

- Scientific

- Scripting

- Set-theoretic

- Simulation

- Stack-based

- System

- Tactile

- Templating

- Transformation ( Graph rewriting , Production , Pattern )

- Visual

- Actor-based

- Automatic mutual exclusion

- Choreographic programming

- Concurrent logic ( Concurrent constraint logic )

- Concurrent OO

- Macroprogramming

- Multitier programming

- Organic computing

- Parallel programming models

- Partitioned global address space

- Process-oriented

- Relativistic programming

- Service-oriented

- Structured concurrency

- Attribute-oriented

- Automatic ( Inductive )

- Dynamic

- Extensible

- Generic

- Homoiconicity

- Interactive

- Macro ( Hygienic )

- Metalinguistic abstraction

- Multi-stage

- Program synthesis ( Bayesian , by demonstration , by example , vibe coding )

- Reflective

- Self-modifying code

- Symbolic

- Template

- Aspects

- Components

- Data-driven

- Data-oriented

- Event-driven

- Features

- Literate

- Roles

- Subjects

- Programming paradigms

- 2025 neologisms

- Applications of artificial intelligence

- Buzzword

- CS1 maint: deprecated archival service

- Articles with short description

- Short description is different from Wikidata

- Use dmy dates from February 2026
