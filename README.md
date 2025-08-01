# AgentK-1_0
Autonomous local-first AI CLI agent that builds its own tools and evolves with every task. It works how agents should work. Whatever the task is it will find the way to succeed. Doing this in a completely transparent way, not a black box.

# AgentK

AgentK started as a tiny “smart DOS” — a local CLI assistant using an LLM API.  
At first, it could only talk and run powershell. Then I gave it the ability to read files. Then write them, the ability to see the outcome of its actions. Then to create and use its own tools.

What surprised me was how well it used them. After a time it was acting on my computer like that command prompt is its natural habitat. During stress tests, I asked it to migrate itself into Excel. Then to generate a GUI for its own CLI logic.  
It did both. Imperfectly but fully, and with no intervention during execution.

It doesn’t just run commands. It observes results, adapts, and continues.
It’s local-first, open-source, and designed to evolve.
Unlike “black box” agents that hide their logic, AgentK is a glass box: every command, decision, mistake, and output is visible. You see what it sees — and how it thinks.

→ Give it a folder. It gives you solutions.

## What it can do
AgentK doesn’t come preloaded with “features.” It grows them.

It starts as a 50KB seed — a local-first CLI agent with just the basics: talk, see files, create files. But give it a task, and it will grow the tools it needs.

Want a little image assistant?  
→ It’ll build image resizing, grayscale converters, ASCII renderers, even free text-to-image toolchains.

Want it to learn how to browse the web?  
→ It’ll try.

Want it to spin up a small local language model and talk to it?  
→ It’ll do that too.

Drop it into an existing codebase?  
→ It will explore, learn, and start extending it.

AgentK doesn’t hallucinate its own world. It acts on what it sees. A directory becomes its environment. A missing tool becomes something to build.

It builds. It adapts. It works from the ground up.

## 🧠 How it works
AgentK runs in autonomous cycles — like a tiny operating system for your tasks.

Each time you give it a goal, it enters a structured loop:
Understands your instruction using its LLM core
Plans what needs to be done
Uses built-in tools or builds new ones
Executes them locally
Observes the results
Adapts if needed — then loops again

This loop is transparent. Every file it creates, every command it runs, and every conclusion it draws is visible and traceable. AgentK doesn’t hide logic — it shows its reasoning and reacts in real time.

It ships with a small set of built-in commands:

Listing directories and files
Creating and sending files in one step
Replacing specific lines inside existing files
Executing PowerShell commands (a favorite when simplicity matters)

Everything else? AgentK builds it from scratch.

It organizes its mind like this:
priming_prompt.txt – fixed personality and behavior seed
log.txt – raw cli export of anything this iteration of the agent did
memory.txt – summary of past tasks, serving as long-term memory
handlers/ – folder where it creates or discovers its own tools
.md files – self-written docs, one per tool, placed alongside each
There is no plugin store. No GUI toggles.
If it needs something, it builds it. If it breaks something, it fixes it.

## ⚠️ Caution / Safety Notice
AgentK is not a toy or a chatbot. It is an autonomous, system-level agent with direct access to your machine.

It can:
Read, write, and delete any file your user account can access
Execute PowerShell commands — including admin-level ones, if run with elevation
Build and run new tools in real time
Learn how to browse the internet — and act on what it finds

If launched with administrator privileges, it can even modify system settings or partition tables.

It is strongly advised to use AgentK in a sandboxed environment.
It doesn’t hide what it’s doing — but its actions are real, fast, and sometimes irreversible.

That said: during a full month of development and continuous testing — including early unstable builds — nothing catastrophic ever happened.
The worst? It once closed a YouTube tab I was watching.
I had asked it to list active processes. It correctly identified Chrome as the top resource hog, asked if I wanted it closed — but at that stage, the CLI tool wasn’t advanced enough to capture my reply. So it assumed “yes,” and shut it down. Still:

You are responsible for what AgentK does on your machine.
I take no responsibility for any damage, data loss, or unintended consequences.

## 🧰 Setup & Usage
AgentK runs locally, but it connects to an LLM via API to understand and execute your tasks.

By default, it uses Moonshot’s Kimi K2 — a powerful, tool-savvy model explicitly designed for agent-style behavior.
It’s also incredibly cost-effective: even with active daily use, a $10 top-up is nearly impossible to burn through in a week.
To use AgentK, you’ll need a Moonshot API key.

If you're using the installer version, the codebase is placed here:

%AppData%\Local\AgentK\
Inside that folder, open agentk.bat and set your key like this:

set MOONSHOT_API_KEY=your_key_here
python cli_tool.py
cls
That way, you won’t have to enter it manually on each launch.

### 📦 About the Installer
The installer will:
- Download and install Python (if missing)
- Install all required modules
- Copy AgentK’s ~50KB codebase to %AppData%\Local\AgentK\
- Add that folder to your system PATH

Why is that last part important?
Because it lets you use the bundled spawner:
dropk.bat

Type dropk in any directory, and AgentK’s codebase will appear there — ready to run.
It doesn’t auto-start. It just quietly moves in 🤭

### ⚙️ Support for OpenAI (GPT-4o) is possibly coming, as the development of this cli_tool was powered by that API originally. (But now i need to test how reliable it is)
Linux support is also in the works. Just needs a few days of testing before it ships.
More API backends will be added later — but only if they prove stable inside AgentK’s autonomous tool-building cycles. If not, they stay out. Reputations matter.


## 🛣️ Roadmap & Vision
AgentK is not just a local CLI agent. It’s a framework for building intelligent digital collaborators.

Here’s what’s coming next:

🌐 1. Shared AppStore (Collective Tool Library)
A decentralized repository where AgentK instances can share useful tools they’ve built — and download what others made.
Think of it as a kind of collective memory or distributed nervous system. If one AgentK writes a good PDF reader, others don’t need to reinvent it — they just fetch it.

This drastically speeds up problem-solving and lowers redundancy.

🧠 2. Multi-Agent Orchestration
For complex tasks, AgentK will take on the role of an orchestrator.
It will break down a goal into modular subtasks, and spawn specialized worker agents — each with their own system prompt, tools, and validation logic.

Each worker focuses solely on delivering a working result that matches the exact constraints given — freeing AgentK’s core from context overload and increasing reliability.

🔁 3. Communication Layer
A unified internal messaging system that allows multiple AgentKs — across platforms or roles — to talk to each other.

For example:
An Excel-based AgentK can request file insights from a Python-based AgentK
A worker AgentK can ask the orchestrator to spawn a validator
Future: Agents could even summon or awaken other agents when needed

Not every agent needs every tool — they can ask each other instead.

🧩 4. GUI and Excel-based AgentKs
In progress: the standalone GUI version AgentK built for itself (yes, really), and the Excel-integrated version that lets you chat with a spreadsheet-aware AI.

These versions are already functional — just undergoing final polishing before release.


## ❗ Troubleshooting & Known Issues
Even though AgentK is stable in daily use, a few quirks are worth noting:

⏳ 1. Slow first response (Moonshot API)
Sometimes, the very first reply from the LLM can take up to 1–2 minutes to arrive.
This delay seems to be related to Moonshot’s popularity and traffic load — at least that’s my current theory.
Subsequent replies are usually faster. Be patient, and let it warm up.

👻 2. “Ghost” CLI state
Occasionally, AgentK enters a state where the CLI window appears idle — as if nothing is happening —
but the log.txt shows that the LLM is actively writing code or discussing plans.

In this state:

- The agent believes it's acting
- The logs contain real intent and tool generation
- But files are not being created — execution silently fails

This usually causes confusion on the LLM side too, as it doesn't understand why the code it "wrote" is missing.
If AgentK manages to recover, it often either fixes the issue on its own —
or continues with a degraded, lower-quality version of the task.

Workaround: Restarting AgentK typically resets the cycle.

🔄 3. Output/reaction misalignment
Sometimes the CLI output appears out of order:

First, the command AgentK says it will run

Then its reaction to the result

And only after that the actual system output of the command

This is purely a visual bug in how output is displayed.
The command does run correctly, and the result is accurate.
Still, this can be confusing — and will be fixed in future updates.

## 📄 License
MIT License

Copyright (c) 2025 Viktor Kirschner

Permission is hereby granted, free of charge, to any person obtaining a copy  
of this software and associated documentation files (the "Software"), to deal  
in the Software without restriction, including without limitation the rights  
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell  
copies of the Software, and to permit persons to whom the Software is  
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all  
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR  
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,  
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE  
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER  
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,  
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE  
SOFTWARE.
